import pyrax
import os
import threading
import time

semaphore = threading.Semaphore()


def thread_print(stmt):
    with semaphore:
        print stmt


def create_servers(cs, img, flav, num):
    name = '%s%d' % ('server', num)
    thread_print("Starting build of %s" % name)
    server = cs.servers.create(name, img, flav)
    while True:
        server.get()
        if "public" in server.networks.keys():
            thread_print("""
Name: %s
IP: %s
Pass: %s
""" % (server.name, server.networks['public'], server.adminPass))
            break
        else:
            thread_print("Waiting on %s network info..." % name)
            time.sleep(20)


def main():
    pyrax.set_credential_file(os.path.expanduser(
        '~/.rackspace_cloud_credentials'))
    cs = pyrax.cloudservers
    ubuntu_img = [img for img in cs.images.list()
                  if "Ubuntu 12.04" in img.name][0]
    flavor_512 = [flavor for flavor in cs.flavors.list()
                  if flavor.ram == 512][0]
    svr1 = threading.Thread(target=create_servers,
                            args=[cs, ubuntu_img, flavor_512, 1])
    svr2 = threading.Thread(target=create_servers,
                            args=[cs, ubuntu_img, flavor_512, 2])
    svr3 = threading.Thread(target=create_servers,
                            args=[cs, ubuntu_img, flavor_512, 3])
    svr1.start()
    svr2.start()
    svr3.start()
    svr1.join()
    svr2.join()
    svr3.join()


if __name__ == '__main__':
    main()
