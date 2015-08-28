
Automation to setup a performance test cluster on AWS with:

* Couchbase Server nodes

Uses a Cloudformation template to spin up all instances.

## Install pre-requisites
```
$ sudo apt-get update 
$ sudo apt-get install python-pip
$ sudo apt-get install python-dev
$ sudo apt-get install git

$ git clone https://github.com/couchbaselabs/perfcluster-aws.git
```
**Python Dependencies**

```
$ sudo pip install ansible
$ sudo pip install boto
$ sudo pip install troposphere
$ sudo pip install awscli
$ sudo pip install markupsafe
```

**Add boto configuration**

```
$ cat >> ~/.boto
[Credentials]
aws_access_key_id = CDABGHEFCDABGHEFCDAB
aws_secret_access_key = ABGHEFCDABGHEFCDABGHEFCDABGHEFCDABGHEFCDAB
^D
```
(and replace fake credentials above with your real credentials)
### Important Security Note:
Given this instance will contain your aws_access_key_id, aws_secret_access_key
and <your_keypair_name>.pem file, it is very important that you keep it secure by
using a securitygroup with only limited access.  Provding ssh access (port 22) from
your desktop machine should be all that is required.


**Add <your_keypair_name>.pem authentication**

```
$ scp -i <your_keypair_name>.pem <your_keypair_name>.pem ubuntu@11.22.33.44:/home/ubuntu
$ ssh -i <your_keypair_name>.pem ubuntu@11.22.33.44
$ ssh-agent bash
$ ssh-add <your_keypair_name>.pem
```

**Add AWS env variables**

```
$ export AWS_ACCESS_KEY_ID=CDABGHEFCDABGHEFCDAB
$ export AWS_SECRET_ACCESS_KEY=ABGHEFCDABGHEFCDABGHEFCDABGHEFCDABGHEFCDAB
```

## How to generate CloudFormation template

This uses [troposphere](https://github.com/cloudtools/troposphere) to generate the Cloudformation template (a json file).

The Cloudformation config is declared via a Python DSL, which then generates the Cloudformation Json.

First you need to add the ami that has an install of CB on it to the scalability_template.py.
Search for `TODO` and replace with the ami that you wish to use.

Generate template after changes to the python file:

```
$ python scalability_template.py > scalability_template.json
```

## Install steps

### Kick off EC2 instances

**Via AWS CLI**

```
aws cloudformation create-stack --stack-name ScalabilityPerfCluster --region eu-west-1 \
--template-body "file://scalability_template.json" \
--parameters "ParameterKey=KeyName,ParameterValue=<your_keypair_name>"
```

Note: CloudFormation is a top-level AWS service (i.e. like EC2 and VPC).  If you click on the CloudFormation service you should see the stack ScalabilityPerfCluster

### Provision EC2 instances

* `cd ansible/playbooks`
* `export KEYNAME=key_<your_keyname_name>` 
* Run command
```
ansible-playbook -l $KEYNAME scalability-configure-couchbase-cluster.yml
```

## Viewing instances by type

To view all couchbase servers:

```
$ ansible tag_Type_couchbaseserver --list-hosts
```