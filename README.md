
Automation to setup a performance test cluster on AWS with:

* Couchbase Server nodes
* Sync Gateway nodes
* Gateload and/or Gatling nodes

Uses a Cloudformation template to spin up all instances.

## Install pre-requisites

**Python Dependencies**

```
$ pip install ansible
$ pip install boto
$ pip install troposphere
$ pip install awscli
```

Alternatively, you can use the [Docker image](https://github.com/couchbaselabs/perfcluster-aws/wiki/Running-under-Docker) which has all the pre-requisites pre-installed.

**Add boto configuration**

```
$ cat >> ~/.boto
[Credentials]
aws_access_key_id = CDABGHEFCDABGHEFCDAB
aws_secret_access_key = ABGHEFCDABGHEFCDABGHEFCDABGHEFCDABGHEFCDAB
^D
```

(and replace fake credentials above with your real credentials)

**Add AWS env variables**

```
$ export AWS_ACCESS_KEY_ID=CDABGHEFCDABGHEFCDAB
$ export AWS_SECRET_ACCESS_KEY=ABGHEFCDABGHEFCDABGHEFCDABGHEFCDABGHEFCDAB
```

## How to generate CloudFormation template

This uses [troposphere](https://github.com/cloudtools/troposphere) to generate the Cloudformation template (a json file).

The Cloudformation config is declared via a Python DSL, which then generates the Cloudformation Json.

Generate template after changes to the python file:

```
$ python cloudformation_template.py > cloudformation_template.json
```

## Install steps

### Kick off EC2 instances

**Via AWS CLI**

```
aws cloudformation create-stack --stack-name CouchbasePerfCluster --region us-east-1 \
--template-body "file://cloudformation_template.json" \
--parameters "ParameterKey=KeyName,ParameterValue=<your_keypair_name>"
```

Alternatively, it can be kicked off via the AWS web UI with the restriction that the AWS cloudformation_template.json file must be uploaded to [S3](http://couchbase-mobile.s3.amazonaws.com/perfcluster-aws/cloudformation_template.json).

### Provision EC2 instances

* `cd ansible/playbooks`
* `export KEYNAME=key_yourkeyname` 
* Run command
```
ansible-playbook -l $KEYNAME install-go.yml && \
ansible-playbook -l $KEYNAME install-couchbase-server-3.0.3.yml && \
ansible-playbook -l $KEYNAME build-sync-gateway.yml && \
ansible-playbook -l $KEYNAME build-gateload.yml && \
ansible-playbook -l $KEYNAME install-sync-gateway-service.yml && \
ansible-playbook -l $KEYNAME install-splunkforwarder.yml
```

To use a different Sync Gateway branch:

Replace:

```
ansible-playbook -l $KEYNAME build-sync-gateway.yml
```

with:

```
ansible-playbook -l $KEYNAME build-sync-gateway.yml --extra-vars "branch=feature/distributed_cache_stale_ok"
```

If you are testing the Sync Gateway distributed cache branch, one extra step is needed:

```
ansible-playbook -l $KEYNAME configure-sync-gateway-writer.yml
```

### Starting Gateload tests

```
$ cd ../..
$ python generate_gateload_configs.py  # generates and uploads gateload configs with correct SG IP / user offset
$ cd ansible/playbooks
$ ansible-playbook -l $KEYNAME start-gateload.yml
```

### Starting Gatling tests

```
$ ansible-playbook -l $KEYNAME configure-gatling.yml
$ ansible-playbook -l $KEYNAME run-gatling-theme.yml
```

### View Gatelod test output

* Sync Gateway expvars on $HOST:4985/_expvar

* Gateload expvars $HOST:9876/debug/var

* Gateload expvar snapshots

    * ssh into gateload, and `ls expvar*` to see snapshots

    * ssh into gateload, and run `screen -r gateload` to view gateload logs

## Viewing instances by type

To view all couchbase servers:

```
$ ansible tag_Type_couchbaseserver --list-hosts
```

The same can be done for Sync Gateways and Gateload instances.  Here are the full list of tag filters:

* tag_Type_couchbaseserver
* tag_Type_syncgateway
* tag_Type_gateload

## Collecting expvar output

```
while [ 1 ]
do
    outfile=$(date +%s)
    curl localhost:9876/debug/vars -o ${outfile}.json
    echo "Saved output to $outfile"
    sleep 60
done
```

## Addional Notes

If you need to deploy multiple perf runner clusters into the same AWS account, by default the ansible playbooks will process the hosts across all the clusters. You can partition the hosts by passing a SUBSET parameter on the command line.

For example if you have provisioned each cluster using a different IAM use account, you could partition the hosts by the IAM user key pair name e.g. If a users key pair name is 'my_keypair' then the following command will partition the host groups to only those provisioned by that user.

```
$ ansible-playbook -l key_my_keypair hello-world.yml
```

## Viewing data on Splunk

Note: The data collected by the unix app is by default placed into a separate index called ‘os’ so it will not be searchable within splunk unless you either go through the UNIX app, or include the following in your search query: “index=os” or “index=os OR index=main” (don’t paste doublequotes)
