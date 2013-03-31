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
