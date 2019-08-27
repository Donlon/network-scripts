def load_addr_list(filename):
    l = []
    with open(filename) as f:
        lines = f.readlines()
        for line in lines:
            if line:
                line = line.strip()
                if not line.startswith('#') and not line.startswith('//'):
                    l.append(line)
    return l


def patch_dns(handler):
    from urllib3.util import connection
    _orig_create_connection = connection.create_connection

    def patched_create_connection(address, *args, **kwargs):
        host, port = address
        res = _orig_create_connection((handler(host), port), *args, **kwargs)
        return res

    connection.create_connection = patched_create_connection

def set_local_proxy():
    import socket
    import socks
    socks.set_default_proxy(socks.PROXY_TYPE_SOCKS5, "127.0.0.1", 2358)
    socket.socket = socks.socksocket


def create_socket(addr, default_ipv6=True):
    import socket
    host, port = addr
    res = socket.getaddrinfo(host, port, socket.AF_UNSPEC if default_ipv6 else socket.AF_INET,
                             socket.SOCK_STREAM, 0, socket.AI_PASSIVE)[0]

    af, socktype, proto, _, sa = res 

    s = socket.socket(af, socktype, proto)  
    return s, sa
