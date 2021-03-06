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
import argparse
import time

pyrax.set_setting('identity_type', 'rackspace')
pyrax.set_credential_file(
    os.path.expanduser('~/.rackspace_cloud_credentials'))
cs = pyrax.cloudservers


def create_img(server):
    img_name = '%s%s' % (server.name, "_img")
    print "Creating image..."
    server.create_image(img_name)
    while True:
        print "Waiting for image to become active..."
        image = [img for img in cs.images.list() if img_name in img.name][0]
        if image.status == 'ACTIVE':
            return image
        else:
            time.sleep(10)
            image.get()


def create_server(args, image, flavor):
    print "Creating new server..."
    server = cs.servers.create(args.server_name[0], image, flavor)
    while True:
        print "Waiting for server to become active..."
        server.get()
        if server.status == 'ACTIVE':
            print """
Name: %s
IP: %s
Pass: %s
""" % (server.name, server.networks['public'], server.adminPass)
            break
        else:
            time.sleep(10)


def parse_args():
    parser = argparse.ArgumentParser(description='Rackspace API Challenge 2:'
                                                 'Image existing server and'
                                                 'launch a new server from'
                                                 'that image.')
    parser.add_argument('server_id', nargs=1, help="ID of server to clone")
    parser.add_argument('server_name', nargs=1, help="name of new server")
    return parser.parse_args()


def main():
    args = parse_args()

    server = cs.servers.get(args.server_id[0])
    image = create_img(server)

    flavor_512 = [flv for flv in cs.flavors.list() if flv.ram == 512][0]
    create_server(args, image, flavor_512)


if __name__ == '__main__':
    main()
