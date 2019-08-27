
import requests
import socket
import socks
import threading
import time
import utils


test_port = input("Connect port (443):")
if not test_port:
    test_port = 443
else:
    test_port = int(test_port)

thread_count = input("Max thread count (50):")
if not thread_count:
    thread_count = 50
else:
    thread_count = int(thread_count)

test_list = []

# test_list += utils.load_addr_list('sn-iplist.txt')
# test_list += utils.load_addr_list('dns.gogle.com.txt')
# test_list += utils.load_addr_list('gogl-dns.list.txt')

# test_list += utils.load_addr_list('www.google.com_out_1566537550_ipv6.txt')
# test_list += utils.load_addr_list('www.youtube.com_out_1566543162_ipv6.txt')
test_list += utils.load_addr_list('www.google.com_out_1566793345_ipv6.txt')
# test_list.append('2001:da8:215:4078:250:56ff:fe97:654d')

test_result = [0] * len(test_list)


def test_addr(addr, port):
    print(addr)
    s, sa = utils.create_socket((addr, port))

    try:
        s.settimeout(5)
        t = time.time()

        s.connect(sa)

        elapsed = time.time() - t
        s.close()

        return elapsed * 1000
    except Exception as e:
        print(e)
        s.close()
        return -1


thread_count = min(thread_count, len(test_list))


def worker_main(id):
    index = id
    time.sleep(7 / thread_count * id)
    while index < len(test_list):
        res = test_addr(test_list[index], test_port)
        test_result[index] = res
        index += thread_count


def print_restlt():
    index = [i for i in range(len(test_list))]

    def k(i):
        return test_result[i]
    index.sort(key=k)

    print("\n\nresult:")
    print("SUCCEED:")
    for i in index:
        if test_result[i] > 0:
            print("%s: %d" % (test_list[i], test_result[i]))
    print("\n")
    print("FAILED:")
    for i in index:
        if test_result[i] <= 0:
            print("%s: %d" % (test_list[i], test_result[i]))


def write_result():
    index = [i for i in range(len(test_list))]

    def k(i):
        return test_result[i]
    index.sort(key=k)

    with open('test-out-%d.txt' % int(time.time()), 'w') as f:
        f.write("\n\nresult:" + '\n')
        f.write("SUCCEED:" + '\n')
        for i in index:
            if test_result[i] > 0:
                f.write("%s: %d" % (test_list[i], test_result[i]) + '\n')
        f.write("\n" + '\n')
        f.write("FAILED:" + '\n')
        for i in index:
            if test_result[i] <= 0:
                f.write("%s: %d" % (test_list[i], test_result[i]) + '\n')

def set_proxy():
    socks.set_default_proxy(socks.PROXY_TYPE_SOCKS5, "127.0.0.1", 2358)
    socket.socket = socks.socksocket


if __name__ == "__main__":
    print("main")
    # set_proxy()

    thread_list = [threading.Thread(target=worker_main, args=(i,))
                   for i in range(0, thread_count)]
    [thread.start() for thread in thread_list]
    [thread.join() for thread in thread_list]

    print_restlt()
    write_result()
    print("end")
