import pyrax
import os
import argparse
import sys
import time

pyrax.set_credential_file(
    os.path.expanduser('~/.rackspace_cloud_credentials'))
cs = pyrax.cloudservers
lb = pyrax.cloud_loadbalancers
cf = pyrax.cloudfiles
dns = pyrax.cloud_dns


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
    clb = lb.create(name, port=80, protocol="HTTP", nodes=nodes,
                    virtual_ips=[vip])
    while True:
        print "Waiting for load balancer to build..."
        clb.get()
        if 'ACTIVE' in clb.status:
            print "Load balancer is built."
            return clb
        else:
            time.sleep(10)


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
                print "Server errored out: %s" % server.name
                error.append(server)
                servers.remove(server)
            else:
                print "%s status: %s, progress %d%%" % (server.name,
                                                        server.status,
                                                        server.progress)
        time.sleep(15)
    if error:
        print "The following servers errored out: %s" % tuple(error)
        print "Proceeding with the remaining active servers."
        return active
    elif active:
        return active
    else:
        print "Something super-unexpected happened."
        sys.exit(1)


def create_servers(args, img, flv):
    servers = []
    files = {'/root/.ssh/authorized_keys': args.key.read().strip()}
    for x in range(len(args.server)):
        print "Starting build of server %s." % args.server[x]
        servers.append(cs.servers.create(args.server[x], img, flv, files=files))
    return servers


def get_flavor(idx):
    print "Looking for flavor."
    if idx is not None:
        try:
            return [flv for flv in cs.flavors.list()][idx]
        except IndexError:
            print "Flavor not found"
            sys.exit(1)
    else:
        return [flv for flv in cs.flavors.list() if '512MB' in flv.name][0]


def get_image(idx):
    print "Looking for image."
    if idx is not None:
        try:
            return [img for img in cs.images.list()][idx]
        except IndexError:
            print "Image not found"
            sys.exit(1)
    else:
        return [img for img in cs.flavors.list()
                if 'Ubuntu 12.04' in img.name][0]


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
    parser = argparse.ArgumentParser(description='Challenge 10')
    parser.add_argument('-s', '--servers', nargs='*',
                        default=['server1', 'server2'],
                        help='Names of servers to build.  You may specifiy 1 '
                             'or more. (Default is 2 servers)')
    parser.add_argument('-i', '--image', type=int,
                        help='Image of servers to build.')
    parser.add_argument('-f', '--flavor', type=int,
                        help='Flavor (size) to build.')
    parser.add_argument('-l', '--loadbal', default='lb-chal10',
                        help='Name of load balancer')
    parser.add_argument('-k', '--key', nargs='?', type=argparse.FileType('r'),
                        help='SSH pubkey to upload to server')
    parser.add_argument('-L', '--list', action='store_true',
                        help='List the types of images/flavors')
    parser.add_argument('-d', '--fqdn',
                        help='REQUIRED! FQDN to apply to this host.')
    return parser.parse_args()


def main():
    args = parse_args()
    if args.list is True:
        list_action()
        sys.exit(0)
    elif not args.fqdn:
        print "You'll need to give us an FQDN.  Try 'challenge10.py --help'."
        sys.exit(1)
    domain = get_domain(args.fqdn)
    does_subdom_exist(domain, args.fqdn)
    image = get_image(args.image)
    flavor = get_flavor(args.flavor)
    servers = create_servers(args, image, flavor)
    servers = wait_for_servers(servers)
    clb = build_loadbal(args.loadbal, servers)


if __name__ == '__main__':
    main()
