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

pyrax.set_credential_file(
    os.path.expanduser('~/.rackspace_cloud_credentials'))
cs = pyrax.cloudservers
lb = pyrax.cloud_loadbalancers


def print_lb_info(lb):
    print """
Load Balancer Info:
Name: %s
Status: %s
Nodes: %s
IPs: %s
Algorith: %s
Protocol: %s
""" % (lb.name, lb.status, lb.nodes, lb.virtual_ips, lb.algorithm, lb.protocol)


def build_loadbal(name, servers):
    nodes = [lb.Node(server.networks['private'][0],
                     port=80, condition="ENABLED")
             for server in servers]
    vip = lb.VirtualIP(type="PUBLIC")
    print "Creating load balancer."
    LB = lb.create(name, port=80, protocol="HTTP", nodes=nodes,
                   virtual_ips=[vip])
    while True:
        print "Waiting for load balancer to build..."
        LB.get()
        if 'ACTIVE' in LB.status:
            print "Load balancer is built."
            return LB
        else:
            time.sleep(10)


def wait_for_servers(servers):
    active = []
    error = []
    print "Waiting for servers to come online..."
    while servers:
        for server in servers:
            server.get()
            if 'ACTIVE' in server.status:
                print "Server is active: %s" % server.name
                active.append(server)
                servers.remove(server)
            elif 'ERROR' in server.status:
                print "\033[.31mServer errored out: %s\033[.31m" % server.name
                error.append(server)
                servers.remove(server)
            else:
                print "%s status: %s" % (server.name, server.status)
        time.sleep(15)
    if error:
        print "\033[.31mThe following servers errored out: %s\033[.31m" \
              % tuple(error)
        print "Proceeding with the remaining active servers."
        return active
    elif active:
        return active
    else:
        print "Something super-unexpected happened."
        exit(1)


def create_servers(args, img, flv):
    servers = []
    for x in range(len(args.server)):
        print "Starting build of server %s." % args.server[x]
        servers.append(cs.servers.create(args.server[x], img, flv))
    return servers


def parse_args():
    parser = argparse.ArgumentParser(
        description='Challenge 7: Create servers, a load balancer, and place '
                    'the servers under the LB.')
    parser.add_argument('-s', '--server', nargs='+',
                        default=['server1', 'server2'],
                        help='Name of server(s)')
    parser.add_argument('--lb', nargs=1, default=['some-loadbal'],
                        help='Name of LB')
    return parser.parse_args()


def main():
    args = parse_args()
    img = [img for img in cs.images.list() if 'Ubuntu 12.04' in img.name][0]
    ram512 = [flavor for flavor in cs.flavors.list() if flavor.id == '2'][0]

    servers = create_servers(args, img, ram512)
    servers = wait_for_servers(servers)

    lb = build_loadbal(args.lb[0], servers)
    print_lb_info(lb)


if __name__ == '__main__':
    main()
