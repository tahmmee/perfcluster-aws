
Automation to setup a performance test cluster on AWS with:

* Couchbase Server nodes
* Sync Gateway nodes
* Gateload and/or Gatling nodes

Uses a Cloudformation template to spin up all instances.

## How to generate CloudFormation template

This uses [troposphere](https://github.com/cloudtools/troposphere) to generate the Cloudformation template (a json file).

The Cloudformation config is declared via a Python DSL, which then generates the Cloudformation Json.

One time setup:

```
$ pip install troposphere
$ pip install boto
```

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

* Choose the `syncgateway0` Sync Gateway instance, and add the following tag to it: 
  * Key: CacheType
  * Value: writer
* Find the internal ip of one of the couchcbase server instances via the AWS web UI
* Open `/ansible/playbooks/files/sync_gateway_config.json` and change db/server and db/remote_cache/server to have the couchbase server ip found in previous step
* `ansible-playbook install-go.yml` 
* `ansible-playbook build-sync-gateway.yml`
* `ansible-playbook build-gateload.yml`  
* `ansible-playbook install-sync-gateway-service.yml`
* Manually setup Couchbase Server
    * Choose any of the couchbase servers
    * Login with Administrator / <instance_id> (eg, i-8d572871)
    * Join all couchbase server nodes into cluster
        * Choose Add Server
	* Add the **private ip** of the other couchbase servers, and for the password field, use the instance_id of the server being added
    * Rebalance
    * Create buckets: bucket-1 and bucket-2.  Use 50% RAM for each.
* Manually SSH into cache writer machine (find the ip via `ansible tag_CacheType_writer --list-hosts`), change config to cache writer == true 
    * ssh centos@<ip>
    * sudo bash && su - sync_gateway
    * vi ~/sync_gateway.json
* `ansible-playbook start-sync-gateway.yml`
* Hand modify each gateload config:
    * Have correct sync gateway ip
    * Have correct UserOffset
* Kick off gateloads

## Viewing instances by type

To view all couchbase servers:

```
$ ansible tag_Type_couchbaseserver --list-hosts
```

The same can be done for Sync Gateways and Gateload instances.  Here are the full list of tag filters:

* tag_Type_couchbaseserver
* tag_Type_syncgateway
* tag_Type_gateload

## Automating Gateload config creation

** Gateload <-> Sync Gateway mapping **

* Find a list of ip's of all the sync gateway machines
* Fina the ip of the writer and remove from the list (`ansible tag_CacheType_writer --list-hosts`)
* Find a list of ip's of all the gateload machines
* Assert that list_sync_gateways and list_gateloads are of the same length
* Assign each gateload a sync gateway
* Assign each gateload a user offset (iterate over gateloads and bump by 13K)
* For each gateload
  * Generate gateload config from a template
    * Use assigned Sync Gateway ip
    * Use assigned user offset
  * Upload gateload config to gateload machine
