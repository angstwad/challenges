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
import sys
import time

pyrax.set_credential_file(
    os.path.expanduser('~/.rackspace_cloud_credentials'))
dns = pyrax.cloud_dns
cs = pyrax.cloudservers


def wait_for_servers(server):
    print "Waiting for server to come online."
    while True:
        server.get()
        if server.status == 'ACTIVE':
            print "Server is ACTIVE."
            return server
        elif server.status == 'ERROR':
            print "Server errored out...try building again!"
            sys.exit(1)
        else:
            time.sleep(20)
            print "Still waiting..."


def create_servers(fqdn, img, flv):
    print "Starting build of server '%s'." % fqdn
    return cs.servers.create(fqdn, img, flv)


def add_subdom_rcd(dom, fqdn, ip):
    print "Adding A record."
    record = {
        'type': 'A',
        'name': fqdn,
        'data': ip
    }
    return dom.add_record(record)


def does_subdom_exist(dom, fqdn):
    try:
        dom.find_record('A', name=fqdn)
    except pyrax.exc.DomainRecordNotFound:
        print ("OK: No duplicate A record entry in Cloud DNS for specified"
               " domain.")
    else:
        print ("The FQDN you provided aleady has a record name like "
               "the one you supplied.  Try a new FQDN!")
        sys.exit(1)

    try:
        dom.find_record('CNAME', name=fqdn)
    except pyrax.exc.DomainRecordNotFound:
        print ("OK: No duplicate CNAME record entry in Cloud DNS for specified"
               " domain.")
    else:
        print ("The FQDN you provided aleady has a record name like "
               "the one you supplied.  Try a new FQDN!")
        sys.exit(1)


def get_domain(fqdn):
    domain = ".".join(fqdn.split('.')[1:])
    print "Looking for domain %s." % domain
    dom = [dom for dom in dns.list() if dom.name == domain]
    if len(dom) > 0:
        return dom[0]
    else:
        print "Domain not found in Cloud DNS: %s" % domain
        sys.exit(1)


def get_flavor(idx):
    print "Looking for flavor."
    try:
        return [flv for flv in cs.flavors.list()][idx]
    except IndexError:
        print "Flavor not found"
        sys.exit(1)


def get_image(idx):
    print "Looking for image."
    try:
        return [img for img in cs.images.list()][idx]
    except IndexError:
        print "Image not found"
        sys.exit(1)


def list_action():
    print "Listing...this may take a moment.\n"
    print "Images:"
    print "Num    Image Name"
    for num, img in enumerate(cs.images.list()):
        print "%d      %s" % (num, img)
    print ""
    print "Flavors"
    print "Num    Flavor Name"
    for num, flv in enumerate(cs.flavors.list()):
        print "%d      %s" % (num, flv)
    print """
Please reference the images and flavors by their number when launching
an instance.
"""


def parse_args():
    parser = argparse.ArgumentParser(description='Challenge 9')
    parser.add_argument('-d', '--fqdn', nargs=1,
                        help='FQDN to use with this server')
    parser.add_argument('-i', '--image', nargs=1, type=int,
                        help='Name of server image to use')
    parser.add_argument('-f', '--flavor', nargs=1, type=int,
                        help='Flavor of server to use')
    parser.add_argument('-l', '--list', action='store_true',
                        help='List images and flavors')
    return parser.parse_args()


def main():
    args = parse_args()
    if args.list is True:
        list_action()
        sys.exit(0)
    else:
        if not args.fqdn or not args.flavor or not args.flavor:
            print "\nTry some arguments...try 'challenge9.py --help'\n"
            sys.exit(1)
    flavor = get_flavor(args.flavor[0])
    image = get_image(args.image[0])
    domain = get_domain(args.fqdn[0])
    does_subdom_exist(domain, args.fqdn[0])
    server = create_servers(args.fqdn[0], image, flavor)
    server = wait_for_servers(server)
    record = add_subdom_rcd(domain, args.fqdn[0], server.networks['public'][0])
    print "All done!"
    print """
Name:   %s
IP:     %s
Pass:   %s
FQDN:   %s
""" % (server.name, server.networks['public'][0],
       server.adminPass, record[0].name)


if __name__ == '__main__':
    main()
