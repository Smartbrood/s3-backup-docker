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


def make_tarfile(tar_filename, source):
    with tarfile.open(tar_filename, "w:gz") as tar:
        print("Start tar creation, source: %s." % source)
        for dir in source:
            if os.path.isdir(dir):
                tar.add(dir, arcname=os.path.basename(dir))


def copy_to_bucket(source, tar_filename, bucket, key, datestamp):
    make_tarfile(tar_filename, source)
    s3 = boto3.client('s3')
    if datestamp:
        l = key.split(".")
        l.insert(1, time.strftime("%d-%m-%Y", time.gmtime()))
        key = ".".join(l)
    print("Start upload to bucket: %s. Key: %s" % (bucket, key))
    s3.upload_file(tar_filename, bucket, key)
    os.remove(tar_filename)
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

    tar_filename = "/tmp/backup.tar.gz"    
    bucket = os.environ.get('S3_BACKUP_BUCKET')
    source = os.environ.get('S3_BACKUP_SOURCE', "/backup").split(";")
    time_of_day = os.environ.get('S3_BACKUP_TIME_OF_DAY', "01:00")
    daily_key = os.environ.get('S3_BACKUP_DAILY_KEY')
    weekly_key = os.environ.get('S3_BACKUP_WEEKLY_KEY')
    monthly_key = os.environ.get('S3_BACKUP_MONTHLY_KEY')
   
    if not daily_key:
        print("Please setup S3_BACKUP_DAILY_KEY environment variable.")
        sys.exit()
        
    if not bucket:
        print("Please setup S3_BACKUP_BUCKET environment variable.")
        sys.exit()

    if args.daemon:
        schedule.every().day.at(time_of_day).do(copy_to_bucket, source, tar_filename, bucket, daily_key, args.datestamp)
        if weekly_key:
            schedule.every().sunday.at(time_of_day).do(copy_to_bucket, source, tar_filename, bucket, weekly_key, args.datestamp)
        #if monthly_key:
        #    schedule.every(5).sundays.at(time_of_day).do(copy_to_bucket, source, tar_filename, bucket, monthly_key, args.datestamp)
       
        while True:
            schedule.run_pending()
            time.sleep(1)

    else:
        copy_to_bucket(source, tar_filename, bucket, daily_key, args.datestamp)


if __name__ == "__main__":
    main()
