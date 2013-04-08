import pyrax
import os
import argparse
import sys


pyrax.set_credential_file(
    os.path.expanduser('~/.rackspace_cloud_credentials'))
cs = pyrax.cloudservers
lb = pyrax.cloud_loadbalancers
cf = pyrax.cloudfiles


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
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('-s', '--servers', nargs='*',
                        default=['server1', 'server2'],
                        help='Names of servers to build.  You may specifiy 1 '
                             'or more. (Default is 2 servers)')
    parser.add_argument('-i', '--image', type=int,
                        help='Image of servers to build.')
    parser.add_argument('-f', '--flavor', type=int,
                        help='Flavor (size) to build.')
    parser.add_argument('-l', '--loadbal', nargs=1, default='lb-chal10',
                        help='Name of load balancer')
    parser.add_argument('-k', '--key', nargs='?', type=argparse.FileType('r'),
                        default=sys.stdin, help='')
    parser.add_argument('-L', '--list', action='store_true',
                        help='List the types of images/flavors')
    return parser.parse_args()


def main():
    args = parse_args()
    if args.list is True:
        list_action()
        exit(0)


if __name__ == '__main__':
    main()
