#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@author: Andrey N. Petrov <andreynpetrov@gmail.com>
'''

usage = """
Backup to AWS S3.
"""

import argparse
import boto3
import os
import tarfile
import time
import sys

import schedule
import subprocess
import stat
import shutil


def make_tarfile(tar_filename, source):
    with tarfile.open(tar_filename, "w:gz") as tar:
        print("Start tar creation, source: %s." % source)
        for dirpath in source:
            if os.path.isdir(dirpath):
                tar.add(dirpath, arcname=os.path.basename(dirpath))


def cleanup(source, tar_filename):
    os.remove(tar_filename)
    for dirpath in source:
        for item in os.listdir(dirpath):
            path = os.path.join(dirpath, item)
            if os.path.isfile(path):
                os.unlink(path)
            elif os.path.isdir(path):
                shutil.rmtree(item)


def mariadb_dump(args, key):
    print("Start mariadb dumping.")
    with open("/root/.my.cnf", "w") as f:
        f.write("[mysqldump]\nuser=%s\npassword=%s" % (args.db_user, args.db_password))
        os.chmod("/root/.my.cnf", stat.S_IRUSR)

    ps = subprocess.Popen(
        'mysqldump -u %s -A -h %s -P %s > %s' % (args.db_user, args.db_host, args.db_port, args.dumpfile),
        shell=True
    )
    output = ps.communicate()[0]
    for line in output.splitlines():
        print line
    copy_to_bucket(args, key)


def postgresql_dump(args, key):
    print("Start postgresql dumping.")
    with open("/root/.pgpass", "w") as f:
        f.write("*:%s:*:%s:%s" % (args.db_port, args.db_user, args.db_password))
        os.chmod("/root/.pgpass", stat.S_IRUSR)

    ps = subprocess.Popen(
        ['pg_dump', '-U', args.db_user, '-Fc', '-h', args.db_host, '-p', args.db_port, '-f', args.dumpfile],
        stdout=subprocess.PIPE
    )
    output = ps.communicate()[0]
    for line in output.splitlines():
        print line
    copy_to_bucket(args, key)


def copy_to_bucket(args, key):
    make_tarfile(args.tar_filename, args.source)
    s3 = boto3.client('s3')
    if args.datestamp:
        l = key.split(".")
        l.insert(1, time.strftime("%d-%m-%Y", time.gmtime()))
        key = ".".join(l)
    print("Start upload to bucket: %s. Key: %s" % (args.bucket, key))
    s3.upload_file(args.tar_filename, args.bucket, key)
    cleanup(args.source, args.tar_filename)
    print("Finished.")


def parse_args():
    parser = argparse.ArgumentParser(
                    description=usage)
    parser.add_argument("-t", "--datestamp", help="Add datestamp to S3 object key. Useful when bucket versioning is disabled.",
                    action="store_true")
    parser.add_argument("-d", "--daemon", help="Start in daemon mode.",
                    action="store_true")
    parser.add_argument("-v", "--verbose", help="increase output verbosity",
                    action="store_true")

    return parser.parse_args()


def main():
    args = parse_args()

    if args.verbose:
        print("verbosity turned on")
    else:
        pass

    args.tar_filename = "/tmp/backup.tar.gz"    
    args.bucket = os.environ.get('S3_BACKUP_BUCKET')
    args.source = os.environ.get('S3_BACKUP_SOURCE', "/backup").split(";")

    args.dumpfile    = os.environ.get('S3_BACKUP_DUMPFILE')
    args.db_host     = os.environ.get('S3_BACKUP_DB_HOST')
    args.db_port     = os.environ.get('S3_BACKUP_DB_PORT')
    args.db_user     = os.environ.get('S3_BACKUP_DB_USER')
    args.db_password = os.environ.get('S3_BACKUP_DB_PASSWORD')

    db_type     = os.environ.get('S3_BACKUP_DB_TYPE')
    time_of_day = os.environ.get('S3_BACKUP_TIME_OF_DAY', "03:00")
    daily_key   = os.environ.get('S3_BACKUP_DAILY_KEY')
    weekly_key  = os.environ.get('S3_BACKUP_WEEKLY_KEY')
    monthly_key = os.environ.get('S3_BACKUP_MONTHLY_KEY')
 
    if not daily_key:
        print("Please setup S3_BACKUP_DAILY_KEY environment variable.")
        sys.exit()
        
    if not args.bucket:
        print("Please setup S3_BACKUP_BUCKET environment variable.")
        sys.exit()

    if db_type == "postgresql":
        sfunc = postgresql_dump
    elif db_type == "mariadb":
        sfunc = mariadb_dump
    else:
        sfunc = copy_to_bucket

    if args.daemon:
        schedule.every().day.at(time_of_day).do(sfunc, args, daily_key)
        if weekly_key:
            schedule.every().sunday.at(time_of_day).do(sfunc, args, weekly_key)
       
        while True:
            schedule.run_pending()
            time.sleep(1)

    else:
        sfunc(args, daily_key)


if __name__ == "__main__":
    main()
