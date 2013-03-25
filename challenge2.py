import pyrax
import os
import argparse
import time


pyrax.set_credential_file(
    os.path.expanduser('~/.rackspace_cloud_credentials'))
cs = pyrax.cloudservers


def create_img(server):
    img_name = '%s%s' % (server.name, "_img")
    print "Creating image..."
    server.create_image(img_name)
    while True:
        print "Waiting for image to become active..."
        image = [img for img in cs.images.list() if img_name in img.name][0]
        if image.status == 'ACTIVE':
            return image
        else:
            time.sleep(10)
            image.get()


def create_server(args, image, flavor):
    print "Creating new server..."
    server = cs.servers.create(args.server_name, image, flavor)
    while True:
        print "Waiting for server to become active..."
        server.get()
        if server.status == 'ACTIVE':
            print """
Name: %s
IP: %s
Pass: %s
""" % (server.name, server.networks['public'], server.adminPass)
            break
        else:
            time.sleep(10)


def parse_args():
    args = argparse.ArgumentParser()
    args.add_argument('server_id', nargs='?', help="ID of server to clone")
    args.add_argument('server_name', nargs='?', help="name of new server")
    return args.parse_args()


def main():
    args = parse_args()

    server = cs.servers.get(args.server_id)
    image = create_img(server)

    flavor_512 = [flv for flv in cs.flavors.list() if flv.ram == 512][0]
    create_server(args, image, flavor_512)


if __name__ == '__main__':
    main()
