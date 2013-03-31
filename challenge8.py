import pyrax
import os
import argparse

pyrax.set_credential_file(
    os.path.expanduser('~/.rackspace_cloud_credentials'))
cf = pyrax.cloudfiles
dns = pyrax.cloud_dns


def create_container():
# cf.


def parse_args():
    parser = argparse.ArgumentParser(description='Challenge 8')
    parser.add_argument('domain', nargs=1, help='')
    parser.add_argument('subdomain', nargs=1, help='')
    return parser.parse_args()


def main():
    args = parse_args()


if __name__ == '__main__':
    main()
