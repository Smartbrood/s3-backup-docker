TODO
====

* terraform s3 bucket for backup
* iam role for access to s3 bucket
* docker-compose to test mysqldump


IAM Role¶
========

If you are running on Amazon EC2 and no credentials have been found by any of the providers above, boto3 will try to load credentials from the instance metadata service. In order to take advantage of this feature, you must have specified an IAM role to use when you launched your EC2 instance. For more information on how to configure IAM roles on EC2 instances, see the IAM Roles for Amazon EC2 guide.

Note that if you've launched an EC2 instance with an IAM role configured, there's no explicit configuration you need to set in boto3 to use these credentials. Boto3 will automatically use IAM role credentials if it does not find credentials in any of the other places listed above.


Assume Role Provider
====================

# In ~/.aws/credentials:
[development]
aws_access_key_id=foo
aws_access_key_id=bar

# In ~/.aws/config
[profile crossaccount]
role_arn=arn:aws:iam:...
source_profile=development
