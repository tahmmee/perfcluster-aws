
"""

This attempts to automate the the Gateload config creation

* Find a list of ip's of all the sync gateway machines (`ansible tag_Type_syncgateway --list-hosts`)
* Find the ip of the writer and remove from the list (`ansible tag_CacheType_writer --list-hosts`)
* Find a list of ip's of all the gateload machines
* Assert that list_sync_gateways and list_gateloads are of the same length
* Assign each gateload a sync gateway
* Assign each gateload a user offset (iterate over gateloads and bump by 13K)
* For each gateload
  * Generate gateload config from a template
    * Use assigned Sync Gateway ip
    * Use assigned user offset
  * Upload gateload config to gateload machine


"""

import subprocess
import json
import os
from jinja2 import Template

def sync_gateways():
    """
    Get the list of sync gateway private ip addresses
    """
    tag = "tag_Type_syncgateway"
    private_ips = []
    instance_list = public_ip_addresses_for_tag(tag)
    print "sync gw instance_list: {}".format(instance_list)
    for public_ip in instance_list:
        if len(public_ip) == 0:
            continue
        print "sync gw public ip: {}".format(public_ip)
        cmd = "./inventory/ec2.py --host {}".format(public_ip)
        result = subprocess.check_output(cmd, shell=True)
        result_json = json.loads(result)
        private_ip = result_json["ec2_private_ip_address"]
        print "sync gw private ip: {}".format(private_ip)

        # skip the cache writer
        cache_tag = "ec2_tag_CacheType"
        if result_json.has_key(cache_tag) and result_json[cache_tag] == "writer":
            print "Skipping cache writer: {}".format(public_ip)
            continue

        private_ips.append(private_ip)

    return private_ips


def public_ip_addresses_for_tag(tag):
    cmd = "ansible {} --list-hosts".format(tag)
    result = subprocess.check_output(cmd, shell=True)
    instance_list = result.split("\n")
    instance_list = [x.strip() for x in instance_list]
    return instance_list

def gateloads():
    tag = "tag_Type_gateload"
    gateload_dicts = []
    instance_list = public_ip_addresses_for_tag(tag)

    for public_ip in instance_list:
        if len(public_ip) == 0:
            continue
        print "gateload public ip: {}".format(public_ip)
        cmd = "./inventory/ec2.py --host {}".format(public_ip)
        result = subprocess.check_output(cmd, shell=True)
        result_json = json.loads(result)
        gateload_dicts.append(result_json)

    return gateload_dicts

def render_gateload_template(sync_gateway_private_ip, user_offset):
        # run template to produce file
        gateload_config = open("files/gateload_config.json")
        template = Template(gateload_config.read())
        rendered = template.render(
            sync_gateway_private_ip=sync_gateway_private_ip,
            user_offset=user_offset
        )
        return rendered 

def upload_gateload_config(gateload_ec2_id, sync_gateway_private_ip, user_offset):
    
    rendered = render_gateload_template(
        sync_gateway_private_ip,
        user_offset
    )
    print rendered

    outfile = os.path.join("/tmp", gateload_ec2_id) 
    with open(outfile, 'w') as f:
        f.write(rendered)
    print "Wrote to file: {}".format(outfile)

    # transfer file to remote host
    cmd = 'ansible {} -m copy -a "src={} dest=/home/centos/gateload_config.json" --user centos'.format(gateload_ec2_id, outfile)
    result = subprocess.check_output(cmd, shell=True)
    print "File transfer result: {}".format(result)


def main():

    os.chdir("ansible/playbooks")

    sync_gateway_ips = sync_gateways()

    gateload_dicts = gateloads()
    
    for idx, gateload_dict in enumerate(gateload_dicts):
        
        # calculate the user offset 
        user_offset = idx * 13000 
        # assign a sync gateway to this gateload, get its ip
        # upload only on remote hosts with sync_gateway_ips
        if gateload_dict["ec2_private_ip_address"] in sync_gateway_ips:
            gateload_ec2_id = gateload_dict["ec2_id"]

            upload_gateload_config(
                gateload_ec2_id,
                gateload_dict["ec2_private_ip_address"],
                user_offset
            )

    print "Finished successfully"

if __name__ == "__main__":
    main()

