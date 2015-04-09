
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

# Create a security group
secGrpCouchbase = ec2.SecurityGroup('CouchbaseSecurityGroup')
secGrpCouchbase.GroupDescription = "Allow access to Couchbase Server"
secGrpCouchbase.SecurityGroupIngress = [
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
    )
]

# Add security group to template
t.add_resource(secGrpCouchbase)

cbIngressPorts = [
    {"FromPort": "4369", "ToPort": "4369" },
    {"FromPort": "5984", "ToPort": "5984" },
    {"FromPort": "11210", "ToPort": "11210" },
    {"FromPort": "11211", "ToPort": "11211" },
    {"FromPort": "21100", "ToPort": "21299" },
]

for cbIngressPort in cbIngressPorts:
    from_port = cbIngressPort["FromPort"]
    to_port = cbIngressPort["ToPort"]
    name = 'CouchbaseSecurityGroupIngress{}'.format(from_port)
    secGrpCbIngress = ec2.SecurityGroupIngress(name)
    secGrpCbIngress.GroupName = Ref(secGrpCouchbase)
    secGrpCbIngress.IpProtocol = "tcp"
    secGrpCbIngress.FromPort = from_port
    secGrpCbIngress.ToPort = to_port
    secGrpCbIngress.SourceSecurityGroupName = Ref(secGrpCouchbase)
    t.add_resource(secGrpCbIngress)

# Couchbase Server Instances
for i in xrange(3):
    name = "couchbaseserver{}".format(i)
    instance = ec2.Instance(name)
    instance.ImageId = "ami-403b4328"
    instance.InstanceType = "m1.large"
    instance.SecurityGroups = [Ref(secGrpCouchbase)]
    instance.KeyName = Ref(keyname_param)
    instance.Tags=Tags(Name=name)
    t.add_resource(instance)


print(t.to_json())

