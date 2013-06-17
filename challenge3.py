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

pyrax.set_setting('identity_type', 'rackspace')
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
    parser = argparse.ArgumentParser(
        description='API Challenge 3: Upload a directory to named container')
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
