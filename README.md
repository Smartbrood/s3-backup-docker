# s3-backup-docker
Python script for backup to AWS S3 in Docker


## Usage

```
optional arguments:
  -h, --help       show this help message and exit
  -t, --datestamp  Add datestamp to S3 object key. Useful when bucket
                   versioning is disabled.
  -d, --daemon     Start in daemon mode.
  -v, --verbose    increase output verbosity
```


Example of docker-compose.yml:

```
version: '3'
services:
  backup:
    container_name: s3-backup
    build: smartbrood/s3-backup
    command: "-d -t"
    environment:
      S3_BACKUP_BUCKET:      "your_s3_bucket_name"
      S3_BACKUP_SOURCE:      "/backup"
      S3_BACKUP_TIME_OF_DAY: "01:00"
      S3_BACKUP_DAILY_KEY:   "backup/daily/backup.tar.gz"
      S3_BACKUP_WEEKLY_KEY:  "backup/weekly/backup.tar.gz"
      S3_BACKUP_MONTHLY_KEY: "backup/monthly/backup.tar.gz"
    volumes:
      - /your_home_dir/.aws/credentials:/root/.aws/credentials:ro
      - /backup_from_host_dir:/backup
```
