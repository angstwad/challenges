import pyrax
import os
import argparse

pyrax.set_credential_file(
    os.path.expanduser('~/.rackspace_cloud_credentials'))
cf = pyrax.cloudfiles


def create_container(container):
    cont = cf.create_container(container)
    cont.make_public()
    return cont.cdn_uri


def parse_args():
    parser = argparse.ArgumentParser(description='Challenge 6: '
                                                 'Create a public container')
    parser.add_argument('-c', '--container', nargs='?', default='challenge6',
                        help='Container to create')
    return parser.parse_args()


def main():
    args = parse_args()
    pub_url = create_container(args.container)
    print """Public URL for container: %s
%s """ % (args.container, pub_url)


if __name__ == '__main__':
    main()
