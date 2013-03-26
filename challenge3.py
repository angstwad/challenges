import pyrax
import os

pyrax.set_credential_file(
    os.path.expanduser('~/.rackspace_cloud_credentials'))


def main():
    pass


if __name__ == '__main__':
    main()
