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
import time


pyrax.set_credential_file(
    os.path.expanduser('~/.rackspace_cloud_credentials'))
db = pyrax.cloud_databases


def parse_args():
    parser = argparse.ArgumentParser(description='Rackspace API Challenge 5: '
                                                 'Create a DB instance, DB, '
                                                 'user and password.')
    parser.add_argument('instance_name', nargs=1, help='Instance name')
    parser.add_argument('database_name', nargs=1, help='Database name')
    parser.add_argument('username', nargs=1, help='Username')
    parser.add_argument('password', nargs=1, help='Password')
    return parser.parse_args()


def add_user(inst, user, passwd, db):
    print "Adding user on DB."
    return inst.create_user(name=user, password=passwd, database_names=db)


def add_db(inst, db_name):
    print "Creating database on instance."
    return inst.create_database(db_name)


def wait_for_active(inst):
    while True:
        print "Waiting for instance to become active..."
        inst.get()
        if inst.status == 'ACTIVE':
            print "DB Active!"
            return inst
        else:
            time.sleep(10)


def create_inst(inst_name):
    print "Creating DB."
    return db.create(inst_name, flavor=1, volume=1)


def main():
    args = parse_args()
    inst = create_inst(args.instance_name[0])
    inst = wait_for_active(inst)
    db = add_db(inst, args.database_name[0])
    user = add_user(inst, args.username[0], args.password[0], db)
    print """
Instance Name: %s
Instance Addr: %s
DB:            %s
User:          %s
Pass:          %s
    """ % (inst.name, inst.hostname, db.name, user.name, args.password[0])


if __name__ == '__main__':
    main()
