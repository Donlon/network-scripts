#!/usr/bin/env python3
# coding:utf-8

import os
import socket
import threading
import time
from random import randint, random

import requests
import utils

target_host = input("Target host (www.google.com): ")
if not target_host:
    target_host = 'www.google.com'

sampling_conut = input('Sampling count (10240): ')
if not sampling_conut:
    sampling_conut = 10240
else:
    sampling_conut = int(sampling_conut)

query_ipv6_in = input('Retrive AAAA record (N): ').lower()
if not query_ipv6_in:
    query_ipv6 = False
else:
    query_ipv6 = query_ipv6_in == 'y' or query_ipv6_in == 'true'

dns_list = utils.load_addr_list('dns.google.com_fast.txt')


def random_choose(src_list):
    return src_list[int(random() * len(src_list))]


def dns_handler(host):
    if (host == 'dns.google.com'):
        host = random_choose(dns_list)
    # print("Host: " + host)
    return host


utils.patch_dns(dns_handler)

utils.set_local_proxy()


def fetch_ip(host, edns_ip, session, q_ipv6=False):
    q_type = 'AAAA' if q_ipv6 else 'A'
    req = session.get("https://dns.google.com/resolve?name=%s&type=%s&edns_client_subnet=%s"
                      % (host, q_type, edns_ip))
    res = req.json()

    if res['Status'] != 0:
        return None
    qtype = res['Question'][0]['type']

    res_list = list()

    if 'Answer' in res:
        for v in res['Answer']:
            if v['type'] == qtype:
                ip = v['data']
                res_list.append(ip)
    return res_list
    # try:
    # except Exception as e:
    #     print(e)
    #     return ''


def format_ip(num):
    return "%d.%d.%d.%d" % ((num >> 24) % 256, (num >> 16) % 256, (num >> 8) % 256, num % 256)


retrieved_ip_list = list()
ip_list_lock = threading.Lock()

THREAD_COUNT = 150

work_current_count = 0
work_current_pos = 0
work_lock = threading.Lock()

work_increnent = int(256 * 256 * 256 * 256 / sampling_conut)

if not os.path.exists('out'):
    os.mkdir('out')
out_file = open('out//%s_out_%d%s.txt' % (target_host, int(time.time()), '_ipv6' if query_ipv6 else ''), 'w')
w_count = 0


def append_ip(ip):
    global w_count
    if not ip:
        return
    with ip_list_lock:
        if ip not in retrieved_ip_list:  # TODO: use dict to accelarate finding
            retrieved_ip_list.append(ip)
            out_file.write(ip + '\n')
            if w_count % 100 == 0:
                out_file.flush()
            w_count += 1
            print(ip)


def append_ip_list(ip_list):
    global w_count
    if not ip_list:
        return

    w = False
    with ip_list_lock:
        for ip in ip_list:
            if ip not in retrieved_ip_list:  # TODO: use dict to accelerate finding
                retrieved_ip_list.append(ip)
                w_count += 1

                print(ip)
                out_file.write(ip + '\n')
                w = w_count % 100 == 0

    if w:
        out_file.flush()


def take_ip_index():
    global work_current_count
    global work_current_pos

    if work_current_count >= sampling_conut:
        return

    with work_lock:
        count = work_current_count
        res = work_current_pos

        work_current_count += 1
        work_current_pos += work_increnent

    if count % 1000 == 0:
        print("  Working on %s" % format_ip(res))
        if count % 12 == 0:
            out_file.flush()
    return res


def worker_thread(id):
    session = requests.Session()

    while True:
        addr = take_ip_index()
        if not addr:
            return
        addr = format_ip(addr)

        ip = fetch_ip(target_host, addr, session, query_ipv6)
        if isinstance(ip, list):
            append_ip_list(ip)
        else:
            pass
            # append_ip(ip)


def watcher_thread():
    thread_list = [threading.Thread(target=worker_thread, args=(i,))
                   for i in range(0, THREAD_COUNT)]
    [th.start() for th in thread_list]
    [th.join() for th in thread_list]


if __name__ == "__main__":
    thread = threading.Thread(target=watcher_thread)
    thread.start()
    thread.join()
