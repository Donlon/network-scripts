#!/usr/bin/env python3
# coding:utf-8

import utils
import socket
import time


bad_payload = b'\x16\x03\x03\x00\xa4\x01\x00\x00\xa0\x03\x03\x5c\xf9\xda\x78\xc7' \
              b'\x56\x8e\xbb\x7b\xd9\x9d\xdb\xb6\x7d\x1f\xc7\x90\x30\x5a\xb7\x6c' \
              b'\x3a\x9b\xda\x32\x80\xc1\x0e\xf7\xcc\xf1\x64\x00\x00\x2a\xc0\x2c' \
              b'\xc0\x2b\xc0\x30\xc0\x2f\x00\x9f\x00\x9e\xc0\x24\xc0\x23\xc0\x28' \
              b'\xc0\x27\xc0\x0a\xc0\x09\xc0\x14\xc0\x13\x00\x9d\x00\x9c\x00\x3d' \
              b'\x00\x3c\x00\x35\x00\x2f\x00\x0a\x01\x00\x00\x4d\x00\x00\x00\x12' \
              b'\x00\x10\x00\x00\x0dpawww.bbc.com\x00\x0a\x00\x08\x00\x06\x00\x1d\x00\x17\x00\x18\x00\x0b' \
              b'\x00\x02\x01\x00\x00\x0d\x00\x14\x00\x12\x04\x01\x05\x01\x02\x01' \
              b'\x04\x03\x05\x03\x02\x03\x02\x02\x06\x01\x06\x03\x00\x23\x00\x00' \
              b'\x00\x17\x00\x00\xff\x01\x00\x01\x00'

RESULT_FAILED = -1
RESULT_RESET = 0
RESULT_SUCCEED = 1


def ttl_test(addr, ttl):
    s, sa = utils.create_socket(addr, False)

    try:
        s.connect(sa)
    except:
        return RESULT_FAILED

    s.setsockopt(socket.IPPROTO_IP, socket.IP_TTL, ttl)
    s.settimeout(2)

    try:
        s.sendall(bad_payload)

        s.recv(1024)
        s.close()
    except ConnectionResetError:
        print('Connection reset')
        return RESULT_RESET
    except socket.timeout:
        return RESULT_SUCCEED

    return RESULT_SUCCEED


def test_connection(addr):
    s, sa = utils.create_socket(addr, False)
    try:
        s.connect(sa)
    except:
        return False
    s.close()
    return True

def https_reset_test(host):
    port = 443
    addr = host, port

    if not test_connection(addr):
        print("Cannot connect to %s:%d" % (host, port))
        return

    lbound = 0
    rbound = 255

    while lbound + 1 != rbound:
        if lbound < 32 and 32 < rbound:
            mid = 32
        else:
            mid = int((lbound + rbound) / 2)
        print("testing with ttl=%d" % mid)
        res = ttl_test(addr, mid)
        if res == RESULT_SUCCEED:
            lbound = mid
        elif res == RESULT_RESET:
            rbound = mid
        elif RESULT_FAILED:
            print("Connection Failed, ttl=%d" % mid)
            time.sleep(3)
        else:
            print("Unexcepted result")
            return
            
        # time.sleep(1)

    print("lbound=%d" % lbound)


if __name__ == "__main__":
    host = input("Host (52.74.223.119): ")
    if not host:
        host = '52.74.223.119'
    https_reset_test(host)
