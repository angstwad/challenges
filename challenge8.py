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
import argparse
import os
import sys
import os.path

DEFAULT_HTML = \
    """<!DOCTYPE html>
    <html>
    <head>
        <title>Challenge Ate</title>
    </head>
    <body>
        <h1>Challenge 8, hey-oh!</h1><br/>
        <h3>i <3 internets</h3>
    </body>
    </html>
    """

pyrax.set_credential_file(
    os.path.expanduser('~/.rackspace_cloud_credentials'))
cf = pyrax.cloudfiles
dns = pyrax.cloud_dns


def add_subdom_rcd(dom, subdom, pub_uri):
    print "Adding CNAME record."
    record = {
        'type': 'CNAME',
        'name': '%s.%s' % (subdom, dom.name),
        'data': pub_uri[7:]
    }
    return dns.add_record(dom, record)


def get_dom(domain):
    print "Looking for domain %s." % domain
    dom = [dom for dom in dns.list() if dom.name == domain]
    if len(dom) > 0:
        return dom[0]
    else:
        print "Domain not found in Cloud DNS."
        sys.exit(1)


def set_web_index(cont):
    print "Setting index page in container."
    cont.set_web_index_page("index.html")


def upload_index(args, cont):
    print "Preparing to upload file."
    if not args.from_file:
        print "No file specified, uploading default."
        with open('challenge8.tmp', 'w') as f:
            f.write(DEFAULT_HTML)
        cont.upload_file('challenge8.tmp', obj_name='index.html',
                         content_type='text/html')
        os.remove('challenge8.tmp')
    else:
        print "Uploading specified file: %s" % args.from_file[0]
        cont.upload_file(os.path.abspath(args.from_file[0]),
                         obj_name='index.html')


def make_public(cont):
    print "Making public."
    cont.make_public()
    return cont.cdn_uri


def create_public_cont(cont_name):
    print "Creating container."
    return cf.create_container(cont_name)


def parse_args():
    parser = argparse.ArgumentParser(
        description='Challenge 8: Create container, make it public, upload a '
                    'web file, enable static website in container, add CNAME '
                    'DNS record for the container\'s CDN URL.')
    parser.add_argument('domain', nargs=1,
                        help='Domain onto which to add CNAME DNS record for '
                             'your public container.')
    parser.add_argument('-s', '--subdomain', nargs=1, default=['challenge8'],
                        help='Manually specify a subdomain to add to the '
                             'domain, or accept the default \'challenge8\'')
    parser.add_argument('-f', '--from-file', nargs=1,
                        help='Specify HTML file to be the index of your new '
                             'container.')
    parser.add_argument('-c', '--container', nargs=1, default=['challenge8'],
                        help='Optional container name.')
    return parser.parse_args()


def main():
    args = parse_args()
    cont = create_public_cont(args.container[0])
    pub_uri = make_public(cont)
    upload_index(args, cont)
    set_web_index(cont)
    dom = get_dom(args.domain[0])
    rec = add_subdom_rcd(dom, args.subdomain[0], pub_uri)

    print "Record created.  View the web page at: %s" % rec[0].name


if __name__ == '__main__':
    main()
