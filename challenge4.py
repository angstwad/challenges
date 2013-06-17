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

pyrax.set_setting('identity_type', 'rackspace')
pyrax.set_credential_file(
    os.path.expanduser('~/.rackspace_cloud_credentials'))
dns = pyrax.cloud_dns


def add_rcd(dom, ip):
    record = {
        'type': 'A',
        'name': dom.name,
        'data': ip
    }
    return dns.add_records(dom, record)


def get_dom(domain):
    dom = [dom for dom in dns.list() if dom.name == domain]
    if len(dom) > 0:
        return dom[0]
    else:
        print "Domain not found in Cloud DNS."
        sys.exit(1)


def parse_args():
    parser = argparse.ArgumentParser(description='Challenge 4: Add A record '
                                                 'to FQDN in Cloud DNS')
    parser.add_argument('domain', nargs=1,
                        help='Fully qualified domain name to add A record to')
    parser.add_argument('ip', nargs=1, help='IP address to add')
    return parser.parse_args()


def main():
    args = parse_args()
    domain = get_dom(args.domain[0])
    record = add_rcd(domain, args.ip[0])
    if isinstance(record[0], pyrax.clouddns.CloudDNSRecord):
        print record
    else:
        print "There was a problem."
        sys.exit(1)


if __name__ == '__main__':
    try:
        main()
    except:
        raise
