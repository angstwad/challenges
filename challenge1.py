# Copyright 2013 Paul Durivage <pauldurivage@gmail.com>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import pyrax
import os
import threading
import time

pyrax.set_credential_file(os.path.expanduser(
    '~/.rackspace_cloud_credentials'))
cs = pyrax.cloudservers
semaphore = threading.Semaphore()
MAX_SERVERS = 3


def thread_print(stmt):
    with semaphore:
        print stmt


def create_servers(cs, img, flav, num):
    name = '%s%d' % ('server', num)
    thread_print("Starting build of %s" % name)
    server = cs.servers.create(name, img, flav)
    while True:
        server.get()
        if server.status == 'ACTIVE':
            thread_print("""
Name: %s
IP: %s
Pass: %s
""" % (server.name, server.networks['public'], server.adminPass))
            break
        else:
            thread_print("Waiting on %s to become active..." % name)
            time.sleep(20)


def main():
    ubuntu_img = [img for img in cs.images.list()
                  if "Ubuntu 12.04" in img.name][0]
    flavor_512 = [flavor for flavor in cs.flavors.list()
                  if flavor.ram == 512][0]

    threads = [threading.Thread(target=create_servers,
                                args=[cs, ubuntu_img, flavor_512, num])
               for num in range(1, MAX_SERVERS + 1)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()


if __name__ == '__main__':
    main()
