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
    args = argparse.ArgumentParser(description='API Challenge 3: Upload a '
                                               'directory to named container')
    args.add_argument('container', nargs='?', help='name of remote container')
    args.add_argument('directory', nargs='?', help='local directory to upload')
    return args.parse_args()


def main():
    args = parse_args()
    container = get_container(args.container)
    upload = put_dir(args.directory, container)
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
    # except SystemExit as e:
    #     print e.message
    except KeyboardInterrupt:
        print "Exiting on keyboard interrupt."
        sys.exit(-1)
