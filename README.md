
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

**Note: the full list of required packages and versions are listed in requirements.txt**

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
$ export AWS_ACCESS_KEY_ID="CDABGHEFCDABGHEFCDAB"
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

* Generate cloudformation_template.json template as described above
* Upload cloudformation_template.json to s3.  Example: [cloudformation_template.json](http://couchbase-mobile.s3.amazonaws.com/perfcluster-aws/cloudformation_template.json)
* Go to the AWS Cloudformation web ui, anc create a stack based on cloudformation_template.json

### Provision EC2 instances

* Find the private ip of one of the couchcbase server instances via the AWS web UI
* Open `/ansible/playbooks/files/sync_gateway_config.json` and change db/server and db/remote_cache/server to have the couchbase server ip found in previous step
* `ansible-playbook install-go.yml`
* `ansible-playbook install-couchbase-server.yml` 
* `ansible-playbook build-sync-gateway.yml`
* `ansible-playbook build-gateload.yml`  
* Manually setup Couchbase Server
    * For each couchbase server in AWS console
        * Find public ip and connect via browser 
        * Go through Setup Wizard
        * For Configure Server Hostname / Hostname, use the private IP of the instance
	* Create a small default bucket of 128 MB of RAM
	* If it's the first one, start a new cluster.  Otherwise, join an existing cluster via private ip.
    * Rebalance
    * Create buckets: bucket-1 and bucket-2.  Use 75% RAM for bucket-1, and remaining RAM for bucket-2.
* `ansible-playbook install-sync-gateway-service.yml`
* `ansible-playbook configure-sync-gateway-writer.yml` (only needed if testing against the distributed cache branch)
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

## Addional Notes

If you need to deploy multiple perf runner clusters into the same AWS account, by default the ansible playbooks will process the hosts across all the clusters. You can partition the hosts by passing a SUBSET parameter on the command line.

For example if you have provisioned each cluster using a different IAM use account, you could partition the hosts by the IAM user key pair name e.g. If a users key pair name is 'my_keypair' then the following command will partition the host groups to only those provisioned by that user.

```
$ ansible-playbook -l key_tleyden hello-world.yml
```
