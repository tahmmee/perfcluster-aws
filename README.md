
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
$ pip install boto
```

**Add boto configuration**

```
$ cat >> ~/.boto
[Credentials]
aws_access_key_id = $YOUR_AWS_KEY
aws_secret_access_key = $YOUR_AWS_SECRET_KEY
^D
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

* Generate cloudformation_template.json template as described above
* Upload cloudformation_template.json to s3.  Example: [cloudformation_template.json](http://couchbase-mobile.s3.amazonaws.com/perfcluster-aws/cloudformation_template.json)
* Go to the AWS Cloudformation web ui, anc create a stack based on cloudformation_template.json

### Provision EC2 instances

* Find the internal ip of one of the couchcbase server instances via the AWS web UI
* Open `/ansible/playbooks/files/sync_gateway_config.json` and change db/server and db/remote_cache/server to have the couchbase server ip found in previous step
* `ansible-playbook install-go.yml` 
* `ansible-playbook build-sync-gateway.yml`
* `ansible-playbook build-gateload.yml`  
* `ansible-playbook install-sync-gateway-service.yml`
* Manually setup Couchbase Server
    * Find public ip of couchbaseserver0
    * Login with Administrator / <instance_id> (eg, i-8d572871)
    * Join all couchbase server nodes into cluster
        * Choose Add Server
	* Add the **private ip** of couchbaseserver1 and couchbaseserver2, and for the password field, use the instance_id of the server being added
    * Rebalance
    * Create buckets: bucket-1 and bucket-2.  Use 50% RAM for each.
* `ansible-playbook configure-sync-gateway-writer.yml`
* `cd ../.. && python generate_gateload_configs.py` 
* Run gateload on all gateload machines via:
    * ssh in
    * `screen -S gateload`
    * `gateload -workload=gateload_config.json`
* Kick off script to collect expvar output (see below)

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
