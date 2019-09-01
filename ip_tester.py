import argparse
import os
import socket
import socks
import threading
import time
import utils


class IpTester:
    test_list = []
    work_lock = threading.Lock()

    # test_list += utils.load_addr_list('sn-iplist.txt')
    # test_list += utils.load_addr_list('dns.gogle.com.txt')
    # test_list += utils.load_addr_list('gogl-dns.list.txt')
    # test_list += utils.load_addr_list('www.google.com_out_1566537550_ipv6.txt')
    # test_list += utils.load_addr_list('www.google.com_out_1566793345_ipv6.txt')
    # test_list.append('2001:da8:215:4078:250:56ff:fe97:654d')

    def __init__(self, input_files, output_file, threads, port, timeout):
        self.output_filename = output_file
        self.thread_count = threads
        self.port = port
        self.timeout = timeout

        if isinstance(input_files, list):
            for fn in input_files:
                if not os.path.exists(fn):
                    print('input file %s not exists' % fn)
                self.test_list += utils.load_addr_list(fn)
        else:
            self.test_list += utils.load_addr_list(input_files)
            
        self.work_progress = 0
        self.work_count = len(self.test_list)

        self.result_index = [i for i in range(len(self.test_list))]
        self.test_result = [0] * len(self.test_list)

    def take_ip(self):
        if self.work_progress >= self.work_count:
            return None

        with self.work_lock:
            index = self.work_progress
            self.work_progress += 1

        if index % 20 == 0:
            print("  Working on %d: %s" % (index, self.test_list[index]))
        # if index % 12 == 0:
        #     out_file.flush()
        return index

    def test_addr(self, addr, port):
        print(addr)
        s, sa = utils.create_socket((addr, port))

        try:
            s.settimeout(self.timeout)
            t = time.time()

            s.connect(sa)

            elapsed = time.time() - t
            s.close()

            return elapsed * 1000
        except Exception as e:
            print(e)
            s.close()
            return -1

    # thread_count = min(thread_count, len(test_list))

    def worker_main(self, seq):
        time.sleep(7 / self.thread_count * seq)

        ip_index = self.take_ip()
        while ip_index is not None:
            res = self.test_addr(self.test_list[ip_index], self.port)
            self.test_result[ip_index] = res
            ip_index = self.take_ip()

    def sort_result(self):
        self.result_index.sort(key=lambda i: self.test_result[i])

    def print_result(self):
        index = self.result_index

        print("\n\nresult:")
        print("SUCCEED:")
        for i in index:
            if self.test_result[i] > 0:
                print("%s: %d" % (self.test_list[i], self.test_result[i]))
        print("\n")
        print("FAILED:")
        for i in index:
            if self.test_result[i] <= 0:
                print("%s: %d" % (self.test_list[i], self.test_result[i]))

    def write_result(self):
        index = self.result_index

        with open('%s.txt' % (self.output_filename.replace('$time$', str(int(time.time())))
                                                  .replace('%time%', str(int(time.time())))), 'w') as f:
            f.write("result:" + '\n')
            f.write("SUCCEED:" + '\n')
            for i in index:
                if self.test_result[i] > 0:
                    f.write("%s: %d" % (self.test_list[i], self.test_result[i]) + '\n')
            f.write("\n" + '\n')
            f.write("FAILED:" + '\n')
            for i in index:
                if self.test_result[i] <= 0:
                    f.write("%s: %d" % (self.test_list[i], self.test_result[i]) + '\n')

    def start(self):
        thread_list = [threading.Thread(target=self.worker_main, args=(i,))
                       for i in range(0, self.thread_count)]
        [thread.start() for thread in thread_list]
        [thread.join() for thread in thread_list]


def set_proxy():
    socks.set_default_proxy(socks.PROXY_TYPE_SOCKS5, "127.0.0.1", 2358)
    socket.socket = socks.socksocket


if __name__ == "__main__":
    print("main")
    # set_proxy()

    parser = argparse.ArgumentParser()
    # parser.add_argument('input', nargs='+', default=None, help="input files", action='append')
    parser.add_argument('-i', '--input', nargs='+', help="input files")
    parser.add_argument('-o', '--output', help="output file")
    parser.add_argument('-p', '--port', type=int, help="connect port")
    parser.add_argument('-n', '--threads', type=int, help='max thread count')
    parser.add_argument('-t', '--timeout', type=int, help="connection time out in seconds")
    parser.add_argument('-P', '--proxy', help="turn local proxy on", action='store_true')
    args = parser.parse_args()

    if args.proxy:
        set_proxy()

    if not args.input:
        args.input = input('Input files:')
        if not args.input:
            exit()

    if not args.output:
        args.output = input('Output files:')
        if not args.output:
            exit()

    if not args.port:
        test_port = input("Connect port (443):")
        if not test_port:
            args.port = 443
        else:
            args.port = int(test_port)

    if not args.threads:
        thread_count = input("Max thread count (50):")
        if not thread_count:
            args.threads = 50
        else:
            args.threads = int(thread_count)

    if not args.timeout:
        timeout_in = input("Timeout in seconds (5):")
        if not timeout_in:
            args.timeout = 5
        else:
            args.timeout = int(timeout_in)

    tester = IpTester(args.input, args.output, args.threads, args.port, args.timeout)

    tester.start()
    tester.print_result()
    tester.write_result()

    print("end")
