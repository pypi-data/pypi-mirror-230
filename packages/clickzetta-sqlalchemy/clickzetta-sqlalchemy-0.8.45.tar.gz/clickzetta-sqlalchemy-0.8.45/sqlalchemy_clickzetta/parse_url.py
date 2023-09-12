import re
from sqlalchemy.engine.url import make_url

GROUP_DELIMITER = re.compile(r"\s*\,\s*")
KEY_VALUE_DELIMITER = re.compile(r"\s*\:\s*")
HTTP_PROTOCOL_DEFAULT_PORT = '80'
HTTP_PROTOCOL_PREFIX = 'http://'
HTTPS_PROTOCOL_DEFAULT_PORT = '443'
HTTPS_PROTOCOL_PREFIX = 'https://'



def parse_boolean(bool_string):
    bool_string = bool_string.lower()
    if bool_string == "true":
        return True
    elif bool_string == "false":
        return False
    else:
        raise ValueError()


def parse_url(origin_url):
    url = make_url(origin_url)
    query = dict(url.query)
    port = url.port

    instance = url.host.split('.')[0]
    length = len(instance) + 1
    protocol = None
    service = None
    if 'protocol' in query:
        protocol = query.pop('protocol')
        if protocol == 'http':
            if not port:
                service = HTTP_PROTOCOL_PREFIX + url.host[length:] + ':' + HTTP_PROTOCOL_DEFAULT_PORT
            else:
                service = HTTP_PROTOCOL_PREFIX + url.host[length:] + ':' + str(port)
        else:
            raise ValueError('protocol parameter must be http. Other protocols are not supported yet.')
    else:
        protocol = 'https'
        if not port:
            service = HTTPS_PROTOCOL_PREFIX + url.host[length:] + ':' + HTTPS_PROTOCOL_DEFAULT_PORT
        else:
            service = HTTPS_PROTOCOL_PREFIX + url.host[length:] + ':' + str(port)

    workspace = url.database
    username = url.username
    driver_name = url.drivername
    password = url.password
    schema = None
    magic_token = None

    if 'virtualcluster' in query or 'virtualCluster' in query or 'vcluster' in query:
        if 'virtualcluster' in query:
            vcluster = query.pop('virtualcluster')
        elif 'virtualCluster' in query:
            vcluster = query.pop('virtualCluster')
        else:
            vcluster = query.pop('vcluster')
    else:
        raise ValueError('url must have `virtualcluster` or `virtualCluster` or `vcluster` parameter.')

    if 'schema' in query:
        schema = query.pop('schema')

    if 'magic_token' in query:
        magic_token = query.pop('magic_token')

    return (
        service,
        username,
        driver_name,
        password,
        instance,
        workspace,
        vcluster,
        schema,
        magic_token,
        protocol,
    )
