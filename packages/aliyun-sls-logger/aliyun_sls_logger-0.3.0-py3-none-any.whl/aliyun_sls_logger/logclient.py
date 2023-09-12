import asyncio
import logging
import time
from copy import copy
from itertools import cycle

import cramjam
import httpx
import orjson as json

from aliyun_sls_logger.auth import AUTH_VERSION_1, make_auth
from aliyun_sls_logger.logexception import LogException
from aliyun_sls_logger.util import base64_encodestring, get_host_ip, h_v_td, is_row_ip
from aliyun_sls_logger.version import API_VERSION, USER_AGENT

from .log_logs_raw_pb2 import LogGroupRaw as LogGroup
from .putlogsresponse import PutLogsResponse

logger = logging.getLogger(__name__)
CONNECTION_TIME_OUT = 120
MAX_LIST_PAGING_SIZE = 500
MAX_GET_LOG_PAGING_SIZE = 100

DEFAULT_QUERY_RETRY_COUNT = 5
DEFAULT_QUERY_RETRY_INTERVAL = 0.5

DEFAULT_REFRESH_RETRY_COUNT = 5
DEFAULT_REFRESH_RETRY_DELAY = 30
MIN_REFRESH_INTERVAL = 300

_auth_code_set = {"Unauthorized", "InvalidAccessKeyId.NotFound", 'SecurityToken.Expired', "InvalidAccessKeyId",
                  'SecurityTokenExpired'}
_auth_partial_code_set = {"Unauthorized", "InvalidAccessKeyId", "SecurityToken"}


def _is_auth_err(_, code, msg):
    if code in _auth_code_set:
        return True
    for m in _auth_partial_code_set:
        if m in code or m in msg:
            return True
    return False


def _apply_cn_keys_patch():
    """
    apply this patch due to an issue in http.client.parse_headers
    when there're multi-bytes in headers. it will truncate some headers.
    https://github.com/aliyun/aliyun-log-python-sdk/issues/79
    """
    import sys
    if sys.version_info[:2] == (3, 5):
        import http.client as hc
        old_parse = hc.parse_headers

        def parse_header(*args, **kwargs):
            fp = args[0]
            old_readline = fp.readline

            def new_readline(*args, **kwargs):
                ret = old_readline(*args, **kwargs)
                if ret.lower().startswith(b'x-log-query-info'):
                    return b'x-log-query-info: \r\n'
                return ret

            fp.readline = new_readline

            ret = old_parse(*args, **kwargs)
            return ret

        hc.parse_headers = parse_header


_apply_cn_keys_patch()


class LogClient:
    """ Construct the LogClient with endpoint, accessKeyId, accessKey.

        :type endpoint: string
        :param endpoint: log service host name, for example, ch-hangzhou.log.aliyuncs.com or https://cn-beijing.log.aliyuncs.com

        :type access_key_id: string
        :param access_key_id: aliyun accessKeyId

        :type access_key: string
        :param access_key: aliyun accessKey
        """
    __version__ = API_VERSION
    Version = __version__

    def __init__(self, endpoint, access_key_id, access_key, security_token=None, source=None,
                 auth_version=AUTH_VERSION_1, region=''):
        self._is_row_ip = is_row_ip(endpoint)
        self._setendpoint(endpoint)
        self._access_key_id = access_key_id
        self._access_key = access_key
        self._timeout = CONNECTION_TIME_OUT
        if source is None:
            self._source = get_host_ip(self._log_host)
        else:
            self._source = source
        self._security_token = security_token

        self._user_agent = USER_AGENT
        self._credentials_auto_refresher = None
        self._last_refresh = 0
        self._auth_version = auth_version
        self._region = region
        self._auth = make_auth(access_key_id, access_key, auth_version, region)
        self.client = httpx.AsyncClient()

    async def close(self):
        await self.client.aclose()

    async def _replace_credentials(self):
        delta = time.time() - self._last_refresh
        if delta < MIN_REFRESH_INTERVAL:
            logger.warning("refresh credentials wait, because of too frequent refresh")
            await asyncio.sleep(MIN_REFRESH_INTERVAL - delta)

        logger.info("refresh credentials, start")
        self._last_refresh = time.time()
        for _ in range(DEFAULT_REFRESH_RETRY_COUNT + 1):
            try:
                self._access_key_id, self._access_key, self._security_token = self._credentials_auto_refresher()
                self._auth = make_auth(self._access_key_id, self._access_key, self._auth_version, self._region)
            except Exception as ex:
                logger.error(
                    "failed to call _credentials_auto_refresher to refresh credentials, details: {0}".format(str(ex)))
                await asyncio.sleep(DEFAULT_REFRESH_RETRY_DELAY)
            else:
                logger.info("call _credentials_auto_refresher to auto refresh credentials successfully.")
                return

    def set_credentials_auto_refresher(self, refresher):
        self._credentials_auto_refresher = refresher

    @property
    def timeout(self):
        return self._timeout

    @timeout.setter
    def timeout(self, value):
        self._timeout = value

    def set_user_agent(self, user_agent):
        """
        set user agent

        :type user_agent: string
        :param user_agent: user agent

        :return: None

        """
        self._user_agent = user_agent

    def _setendpoint(self, endpoint):
        self.http_type = 'http://'
        self._port = 80

        endpoint = endpoint.strip()
        pos = endpoint.find('://')
        if pos != -1:
            self.http_type = endpoint[:pos + 3]
            endpoint = endpoint[pos + 3:]

        if self.http_type.lower() == 'https://':
            self._port = 443

        pos = endpoint.find('/')
        if pos != -1:
            endpoint = endpoint[:pos]
        pos = endpoint.find(':')
        if pos != -1:
            self._port = int(endpoint[pos + 1:])
            endpoint = endpoint[:pos]
        self._log_host = endpoint
        self._endpoint = endpoint + ':' + str(self._port)

    @staticmethod
    def _load_json(resp_status, resp_header, resp_body, request_id):
        if not resp_body:
            return None
        try:
            if isinstance(resp_body, str):
                return json.loads(resp_body.encode('utf-8'))

            return json.loads(resp_body)
        except Exception as ex:
            raise LogException('BadResponse',
                               'Bad json format:\n"%s"' % base64_encodestring(resp_body) + '\n' + repr(ex),
                               request_id, resp_status, resp_header, resp_body)

    async def _get_http_response(self, method, url, params, body, headers):  # ensure method, url, body is str
        try:
            headers['User-Agent'] = self._user_agent
            r = await getattr(self.client, method.lower())(url, params=params, data=body, headers=headers,
                                                           timeout=self._timeout)
            return r.status_code, r.content, r.headers
        except Exception as ex:
            raise LogException('LogRequestError', str(ex))

    async def _send_request(self, method, url, params, body, headers, respons_body_type='json'):
        (resp_status, resp_body, resp_header) = await self._get_http_response(method, url, params, body, headers)
        header = {}
        for key, value in resp_header.items():
            header[key] = value

        request_id = h_v_td(header, 'x-log-requestid', '')

        if resp_status == 200:
            if respons_body_type == 'json':
                ex_json = self._load_json(resp_status, resp_header, resp_body, request_id)
                # ex_json = convert_unicode_to_str(ex_json)
                return ex_json, header
            else:
                return resp_body, header

        ex_json = self._load_json(resp_status, resp_header, resp_body, request_id)
        # ex_json = Util.convert_unicode_to_str(ex_json)

        if 'errorCode' in ex_json and 'errorMessage' in ex_json:
            raise LogException(ex_json['errorCode'], ex_json['errorMessage'], request_id,
                               resp_status, resp_header, resp_body)
        else:
            ex_json = '. Return json is ' + str(ex_json) if ex_json else '.'
            raise LogException('LogRequestError',
                               'Request is failed. Http code is ' + str(resp_status) + ex_json, request_id,
                               resp_status, resp_header, resp_body)

    async def _send(self, method, project, body, resource, params, headers, respons_body_type='json'):
        if body:
            headers['Content-Length'] = str(len(body))
        else:
            headers['Content-Length'] = '0'
            headers["x-log-bodyrawsize"] = '0'

        headers['x-log-apiversion'] = API_VERSION
        if self._is_row_ip or not project:
            url = self.http_type + self._endpoint
        else:
            url = self.http_type + project + "." + self._endpoint

        if project:
            headers['Host'] = project + "." + self._log_host
        else:
            headers['Host'] = self._log_host

        retry_times = range(10) if 'log-cli-v-' not in self._user_agent else cycle(range(10))
        last_err = None
        url = url + resource
        for _ in retry_times:
            try:
                headers2 = copy(headers)
                params2 = copy(params)
                if self._security_token:
                    headers2["x-acs-security-token"] = self._security_token
                self._auth.sign_request(method, resource, params2, headers2, body)
                return await self._send_request(method, url, params2, body, headers2, respons_body_type)
            except LogException as ex:
                last_err = ex
                if ex.get_error_code() in ('InternalServerError', 'RequestTimeout') or ex.resp_status >= 500 \
                        or (ex.get_error_code() == 'LogRequestError'
                            and 'httpconnectionpool' in ex.get_error_message().lower()):
                    await asyncio.sleep(1)
                    continue
                elif self._credentials_auto_refresher and _is_auth_err(ex.resp_status, ex.get_error_code(),
                                                                       ex.get_error_message()):
                    if ex.get_error_code() not in ("SecurityToken.Expired", "SecurityTokenExpired"):
                        logger.warning(
                            "request with authentication error",
                            exc_info=True,
                            extra={"error_code": "AuthenticationError"},
                        )
                    await self._replace_credentials()
                    continue
                raise

        raise last_err

    async def put_logs(self, request):
        """ Put logs to log service. up to 512000 logs up to 10MB size
        Unsuccessful operation will cause an LogException.

        :type request: PutLogsRequest
        :param request: the PutLogs request parameters class

        :return: PutLogsResponse

        :raise: LogException
        """
        if len(request.get_log_items()) > 512000:
            raise LogException('InvalidLogSize',
                               "logItems' length exceeds maximum limitation: 512000 lines. now: {0}".format(
                                   len(request.get_log_items())))
        log_group = LogGroup()
        log_group.Topic = request.get_topic()
        if request.get_source():
            log_group.Source = request.get_source()
        else:
            if self._source == '127.0.0.1':
                self._source = get_host_ip(request.get_project() + '.' + self._log_host)
            log_group.Source = self._source
        for logItem in request.get_log_items():
            log = log_group.Logs.add()
            log.Time = logItem.get_time()
            contents = logItem.get_contents()
            for key, value in contents:
                content = log.Contents.add()
                content.Key = key.decode('utf-8') if isinstance(key, bytes) else key
                content.Value = value.encode('utf-8') if isinstance(value, str) else value
        if request.get_log_tags() is not None:
            tags = request.get_log_tags()
            for key, value in tags:
                pb_tag = log_group.LogTags.add()
                pb_tag.Key = key
                pb_tag.Value = value
        body = log_group.SerializeToString()

        if len(body) > 10 * 1024 * 1024:  # 10 MB
            raise LogException('InvalidLogSize',
                               "logItems' size exceeds maximum limitation: 10 MB. now: {0} MB.".format(
                                   len(body) / 1024.0 / 1024))

        headers = {'x-log-bodyrawsize': str(len(body)), 'Content-Type': 'application/x-protobuf'}
        is_compress = request.get_compress()

        compress_data = None
        if is_compress:
            headers['x-log-compresstype'] = 'lz4'
            # compress_data = bytes(lz4.block.compress(body))[4:]
            compress_data = bytes(cramjam.lz4.compress_block(body, store_size=False))

        params = {}
        logstore = request.get_logstore()
        project = request.get_project()
        if request.get_hash_key() is not None:
            resource = '/logstores/' + logstore + "/shards/route"
            params["key"] = request.get_hash_key()
        else:
            resource = '/logstores/' + logstore + "/shards/lb"

        if is_compress:
            (resp, header) = await self._send('POST', project, compress_data, resource, params, headers)
        else:
            (resp, header) = await self._send('POST', project, body, resource, params, headers)

        return PutLogsResponse(header, resp)
