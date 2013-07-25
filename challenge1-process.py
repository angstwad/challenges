import os
import time
import re
import threading
import multiprocessing
import argparse
import Queue

import pyrax


pyrax.http_debug = True
pyrax.set_credential_file(os.path.expanduser(
    '~/.rackspace_cloud_credentials'))
cs = pyrax.cloudservers
print_sema = multiprocessing.Semaphore()
list_sema = threading.Semaphore()
svr_list = []
done_svr_list = []


def thread_print(string):
    with print_sema:
        print(string)


def sema_list(x):
    with list_sema:
        svr_list.append(x)


class Worker(multiprocessing.Process):
    def __init__(self, task_queue, result_queue, passwd):
        multiprocessing.Process.__init__(self)
        self.task_queue = task_queue
        self.result_queue = result_queue
        self.passwd = passwd

    def run(self):
        print "Starting worker: %s" % self.name
        while True:
            try:
                next_svr_id = self.task_queue.get(timeout=2)
            except Queue.Empty:
                if self.task_queue.empty():
                    break
            svr = cs.servers.get(next_svr_id)
            if svr.status == 'ACTIVE':
                print "%s has an active server: %s" % (self.name, svr.name)
                svr.change_password(self.passwd)
                self.result_queue.put(svr.id)
                self.task_queue.task_done()
            elif svr.status == 'ERROR:':
                print "%s errored out, deleting."
                svr.delete()
                self.task_queue.task_done()
            else:
                print "%s in status %s, progress %s%%" % (svr.name, svr.status,
                                                          svr.progress)
                self.task_queue.put(svr.id)
                self.task_queue.task_done()
            time.sleep(5)
        return


def get_networks(serverids):
    servers = (cs.servers.get(s_id) for s_id in serverids)
    ips = []
    for server in servers:
        for ip in server.networks['public']:
            if re.match('((\d){1,3}\.){3}(\d){1,3}', ip):
                ips.append(ip)
    return ips


def create_server(img, flav, num):
    name = '%s%d' % ('siege', num)
    thread_print("Starting build of %s" % name)
    server = cs.servers.create(name, img, flav)
    sema_list(server.id)


def launch(passwd, num_svrs, flv):
    img = [img for img in cs.images.list()
           if "Ubuntu 12.04" in img.name][0]
    flv = [flavor for flavor in cs.flavors.list()
           if flavor.id == str(flv)][0]

    launchers = [threading.Thread(target=create_server, args=[img, flv, num])
                 for num in range(num_svrs)]
    print "Starting launchers."
    for launcher in launchers:
        launcher.start()
    print "Joining launchers."
    for launcher in launchers:
        launcher.join()

    print "Servers launched list: %s" % svr_list

    work_queue = multiprocessing.JoinableQueue()
    result_queue = multiprocessing.Queue()
    print "Creating work queue."
    for svr_id in svr_list:
        work_queue.put(svr_id)
    watch_workers = [Worker(work_queue, result_queue, passwd)
                     for x in range(int(num_svrs)/2 + 1)]
    print "Starting watch workers."
    for worker in watch_workers:
        worker.start()
    print "Joining work queue."
    work_queue.join()

    for server in svr_list:
        try:
            done_svr_list.append(result_queue.get_nowait())
        except Queue.Empty:
            pass


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-n', '--num-servers', default=5, type=int,
                        help="Default: 5")
    parser.add_argument('-f', '--flavor', default=2, type=int,
                        help="Choices: 2-8, default is 2")
    parser.add_argument('-p ', '--password', default="arbitrarypassword",
                        help='Default: arbitrarypassword')
    return parser.parse_args()


def main():
    args = parse_args()
    launch(args.password, args.num_servers, args.flavor)
    print "Done list %s" % done_svr_list
    ips = get_networks(done_svr_list)
    print "Network IPs: %s" % ips
    print "For fabric:"
    print ""
    for ip in ips:
        print ip,


if __name__ == '__main__':
    main()