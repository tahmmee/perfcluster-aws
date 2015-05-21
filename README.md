
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

** Via AWS CLI **

```
aws cloudformation create-stack --stack-name CouchbasePerfCluster --region us-east-1 \
--template-body "file://cloudformation_template.json" \
--parameters "ParameterKey=KeyName,ParameterValue=<your_keypair_name>"
```

Alternatively, it can be kicked off via the AWS web UI with the restriction that the AWS cloudformation_template.json file must be uploaded to [S3](http://couchbase-mobile.s3.amazonaws.com/perfcluster-aws/cloudformation_template.json).

### Provision EC2 instances

* Find the private ip of one of the couchcbase server instances via the AWS web UI
* Open `ansible/playbooks/files/sync_gateway_config.json` and change db/server and db/remote_cache/server to have the couchbase server ip found in previous step
* `cd ansible/playbooks`
* `export KEYNAME=key_yourkeyname` 
* `ansible-playbook -l $KEYNAME install-go.yml`
* `ansible-playbook -l $KEYNAME install-couchbase-server-3.0.3.yml` 
* `ansible-playbook -l $KEYNAME build-sync-gateway.yml`
    * To use a different branch: `ansible-playbook -l $KEYNAME build-sync-gateway.yml --extra-vars "branch=feature/distributed_cache_stale_ok"`
* `ansible-playbook -l $KEYNAME build-gateload.yml`  
* `ansible-playbook -l $KEYNAME install-sync-gateway-service.yml`
* `ansible-playbook -l $KEYNAME install-splunkforwarder.yml`

If you are testing the Sync Gateway distributed cache branch, one extra step is needed:

```
ansible-playbook -l $KEYNAME configure-sync-gateway-writer.yml
```

### Starting Gateload tests

```
* `cd ../.. && python generate_gateload_configs.py` 
* `cd ./ansible/playbooks && ansible-playbook -l $KEYNAME start-gateload.yml`
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

## Splunk setup

### One-time setup on Splunk Server

* Login via web admin ui to [http://ec2-54-237-61-203.compute-1.amazonaws.com:8000/](http://ec2-54-237-61-203.compute-1.amazonaws.com:8000/) 
* Go to Settings / Fending and receiving -> configure receiving
* Add receiver with port 9997 

### Installing Splunk forwarders

```
$ wget -O splunkforwarder-6.2.2-255606-linux-2.6-x86_64.rpm 'http://www.splunk.com/page/download_track?file=6.2.2/universalforwarder/linux/splunkforwarder-6.2.2-255606-linux-2.6-x86_64.rpm&ac=adwords-syslog&wget=true&name=wget&platform=Linux&architecture=x86_64&version=6.2.2&product=splunk&typed=release'
$ sudo rpm -i splunkforwarder-6.2.2-255606-linux-2.6-x86_64.rpm
$ sudo bash 
$ cd /opt/splunkforwarder/bin
$ ./splunk start --accept-license
```

### Add forward-server to Splunk forwarder

```
$ sudo bash
$ cd /opt/splunkforwarder/bin/ 
$ ./splunk add forward-server ec2-54-237-61-203.compute-1.amazonaws.com:9997
```

When prompted for `Splunk username`, which are the *local credentials* for the Splunk forwarder, not for the Splunk server, enter the default values:

* **Splunk username:** admin
* **Password:** changeme

Test the forwarder:

```
$ ./splunk list forward-server
Active forwards:
	ec2-54-237-61-203.compute-1.amazonaws.com:9997
Configured but inactive forwards:
	None
```

### Install and Configure UNIX app on Indexer and *nix forwarders

Extracted from [answers.splunk.com article](http://answers.splunk.com/answers/50082/how-do-i-configure-a-splunk-forwarder-on-linux.html)

***One-time setup on Splunk Server***

* Login via web admin ui to [http://ec2-54-237-61-203.compute-1.amazonaws.com:8000/](http://ec2-54-237-61-203.compute-1.amazonaws.com:8000/) 
* Go to Apps and hit the + button
* Search for ‘Splunk App for Unix and Linux’ and Install
* You will be prompted for your splunk.com account.
* Restart Splunk when prompted
* Go to Splunk App For Unix add-on, and in the popup, hit "Configure".  Then hit the "Save" button.

***Install Add-on to forwarder***

These steps will install the  "Splunk Add-on for Unix and Linux" on the Universal Forwarder.

* `wget http://couchbase-mobile.s3.amazonaws.com/perfcluster-aws/splunk_unix_linux_add_on/splunk-add-on-for-unix-and-linux_512.tgz`
* `tar -C /opt/splunkforwarder/etc/apps/ -xvf splunk-add-on-for-unix-and-linux_512.tgz`
* `mkdir /opt/splunkforwarder/etc/apps/Splunk_TA_nix/local`
* `cp /opt/splunkforwarder/etc/apps/Splunk_TA_nix/default/inputs.conf /opt/splunkforwarder/etc/apps/Splunk_TA_nix/local/`
* Edit local/inputs.conf to set disabled = 0 for the sections: vmstat.sh, iostat.sh, ps.sh, top.sh, netstat.sh, cpu.sh
* `/opt/splunkforwarder/bin/splunk restart`

Note: The data collected by the unix app is by default placed into a separate index called ‘os’ so it will not be searchable within splunk unless you either go through the UNIX app, or include the following in your search query: “index=os” or “index=os OR index=main” (don’t paste doublequotes)

Doc references: [Deploy and Use the Splunk Add-on for Unix and Linux](http://docs.splunk.com/Documentation/UnixAddOn/latest/User/Enabledataandscriptedinputs)




### Forward Sync Gw logs



### Forward Gateload logs
