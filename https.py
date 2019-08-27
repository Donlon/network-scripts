import requests

from utils import patch_dns
from utils import set_local_proxy


def dns_handler(host):
    if (host == 'dns.google.com'):
        host = ''
    return host



if __name__ == "__main__":
    patch_dns(dns_handler)
    set_local_proxy()

    response = requests.get('https://github.com/')