import base64
import hashlib
import hmac
import logging
import re
import socket

import six

logger = logging.getLogger(__name__)


def base64_encodestring(s):
    if isinstance(s, str):
        s = s.encode('utf8')
    return base64.encodebytes(s).decode('utf8')
def h_v_td(header, key, default):
    """
    get header value with title with default value
    try to get key from header and consider case sensitive
    e.g. header['x-log-abc'] or header['X-Log-Abc']
    :param header:
    :param key:
    :param default:
    :return:
    """
    if key not in header:
        key = key.title()

    return header.get(key, default)

def cal_md5(content):
    return hashlib.md5(content).hexdigest().upper()


def canonicalized_log_headers(headers):
    content = ''
    for key in sorted(six.iterkeys(headers)):
        if key[:6].lower() in ('x-log-', 'x-acs-'):  # x-log- header
            content += key + ':' + str(headers[key]) + "\n"
    return content


def canonicalized_resource(resource, params):
    if params:
        urlString = ''
        for key, value in sorted(six.iteritems(params)):
            urlString += u"{0}={1}&".format(
                key, value.decode('utf8') if isinstance(value, six.binary_type) else value)
        resource += '?' + urlString[:-1]
        if six.PY3:
            return resource
        else:
            return resource.encode('utf8')

    return resource


def hmac_sha1(content, key):
    if isinstance(content, six.text_type):  # hmac.new accept 8-bit str
        content = content.encode('utf-8')
    if isinstance(key, six.text_type):  # hmac.new accept 8-bit str
        key = key.encode('utf-8')

    hashed = hmac.new(key, content, hashlib.sha1).digest()
    return base64_encodestring(hashed).rstrip()


def is_row_ip(ip):
    iparray = ip.split('.')
    if len(iparray) != 4:
        return False
    for tmp in iparray:
        if not tmp.isdigit() or int(tmp) >= 256:
            return False
    pattern = re.compile(r'^[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}$')
    if pattern.match(ip):
        return True
    return False

def get_host_ip(logHost):
    """ If it is not match your local ip, you should fill the PutLogsRequest
    parameter source by yourself.
    """
    s = None
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect((logHost, 80))
        ip = s.getsockname()[0]
        return ip
    except Exception:
        return '127.0.0.1'
    finally:
        if s:
            s.close()
