import pyrax
import os
import argparse
import sys

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
    args = argparse.ArgumentParser(description='Challenge 4: Add A record '
                                               'to FQDN in Cloud DNS')
    args.add_argument('domain', nargs='?', help='Fully qualified domain '
                                                'name to add A record to')
    args.add_argument('ip', nargs='?', help='IP address to add')
    return args.parse_args()


def main():
    args = parse_args()
    domain = get_dom(args.domain)
    record = add_rcd(domain, args.ip)
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