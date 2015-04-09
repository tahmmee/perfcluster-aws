
# Python script to generate the cloudformation template json file
# This is not strictly needed, but it takes the pain out of writing a
# cloudformation template by hand.  It also allows for DRY approaches
# to maintaining cloudformation templates.

from troposphere import Ref, Template, Parameter, Output, Join, GetAtt, Tags
import troposphere.ec2 as ec2

t = Template()

t.add_description(
    'An Ec2-classic stack with Couchbase Server, Sync Gateway + load testing tools '
)

#
# Parameters
#
keyname_param = t.add_parameter(Parameter(
    'KeyName', Type='String',
    Description='Name of an existing EC2 KeyPair to enable SSH access'
))
num_couchbase_servers = t.add_parameter(Parameter(
    'NumCouchbaseServers', Type='String',
    Description='How many Couchbase Server instances should be started?'
))


# Create a security group
sg = ec2.SecurityGroup('CouchbaseSecurityGroup')
sg.GroupDescription = "Allow access to Couchbase Server"
sg.SecurityGroupIngress = [
    ec2.SecurityGroupRule(
        IpProtocol="tcp",
        FromPort="22",
        ToPort="22",
        CidrIp="0.0.0.0/0",
    ),
    ec2.SecurityGroupRule(
        IpProtocol="tcp",
        FromPort="8091",
        ToPort="8091",
        CidrIp="0.0.0.0/0",
    ),
    ec2.SecurityGroupRule(
        IpProtocol="tcp",
        FromPort="4369",
        ToPort="4369",
        CidrIp="0.0.0.0/0",
    ),
    ec2.SecurityGroupRule(
        IpProtocol="tcp",
        FromPort="5984",
        ToPort="5984",
        CidrIp="0.0.0.0/0",
    ),
    ec2.SecurityGroupRule(
        IpProtocol="tcp",
        FromPort="8091",
        ToPort="8091",
        CidrIp="0.0.0.0/0",
    ),
    ec2.SecurityGroupRule(
        IpProtocol="tcp",
        FromPort="11210",
        ToPort="11210",
        CidrIp="0.0.0.0/0",
    ),
    ec2.SecurityGroupRule(
        IpProtocol="tcp",
        FromPort="11211",
        ToPort="11211",
        CidrIp="0.0.0.0/0",
    ),
    ec2.SecurityGroupRule(
        IpProtocol="tcp",
        FromPort="21100",
        ToPort="21299",
        CidrIp="0.0.0.0/0",
    )
]

# Add security group to template
t.add_resource(sg)

# Couchbase Server Instances
for i in xrange(3):
    name = "couchbaseserver{}".format(i)
    instance = ec2.Instance(name)
    instance.ImageId = "ami-403b4328"
    instance.InstanceType = "m1.large"
    instance.SecurityGroups = [Ref(sg)]
    instance.KeyName = Ref(keyname_param)
    instance.Tags=Tags(Name=name)
    t.add_resource(instance)

print(t.to_json())

