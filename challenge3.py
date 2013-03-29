import pyrax
import os
import argparse
import sys
import time


pyrax.set_credential_file(
    os.path.expanduser('~/.rackspace_cloud_credentials'))
cf = pyrax.cloudfiles


def check_upload(tup):
    current = (cf.get_uploaded(tup[0]), tup[1])
    print '%s / %s' % current
    return current


def put_dir(directory, cont):
    abspath = os.path.abspath(directory)
    if os.path.isdir(abspath):
        return cf.upload_folder(abspath, container=cont)
    else:
        print('Directory argument not directory: \n'
              '%s' % abspath)


def get_container(container_name):
    return cf.create_container(container_name)


def parse_args():
    parser = argparse.ArgumentParser(description='API Challenge 3: Upload a '
                                                 'directory to named container')
    parser.add_argument('container', nargs=1, help='name of remote container')
    parser.add_argument('directory', nargs=1, help='local directory to upload')
    return parser.parse_args()


def main():
    args = parse_args()
    container = get_container(args.container[0])
    upload = put_dir(args.directory[0], container)
    while True:
        status = check_upload(upload)
        if status[0] == status[1]:
            print "Done!"
            break
        else:
            time.sleep(1)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print "Exiting on keyboard interrupt."
        sys.exit(-1)
