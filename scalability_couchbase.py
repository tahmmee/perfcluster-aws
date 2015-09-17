
# Python script to generate the cloudformation template json file
# This is not strictly needed, but it takes the pain out of writing a
# cloudformation template by hand.  It also allows for DRY approaches
# to maintaining cloudformation templates.

from troposphere import Ref, Template, Parameter, Output, Join, GetAtt, Tags
import troposphere.ec2 as ec2
import configuration

t = Template()

t.add_description(
    'Couchbase Servers'
)

keynameparameter = t.add_parameter(Parameter(
    'KeyNameParameter', Type='AWS::EC2::KeyPair::KeyName',
    Description='KeyName'
))

subnetidparameter = t.add_parameter(Parameter(
    'SubnetIdParameter', Type='AWS::EC2::Subnet::Id',
    Description='SubnetId'
))

securitygroupidparameter = t.add_parameter(Parameter(
    'SecurityGroupIdParameter', Type='AWS::EC2::SecurityGroup::Id',
    Description='SecurityGroupId'
))


# Couchbase Server Instances
for i in xrange(configuration.NUM_COUCHBASE_SERVERS_DATA):
    name = "couchbaseserverdata{}".format(i)
    instance = ec2.Instance(name)
    instance.ImageId = configuration.COUCHBASE_IMAGE
    instance.InstanceType = configuration.COUCHBASE_INSTANCE_TYPE
    instance.SecurityGroupIds = [ Ref(securitygroupidparameter)]
    instance.SubnetId = Ref(subnetidparameter)
    instance.KeyName = Ref(keynameparameter)
    instance.Tags=Tags(Name=name, Type="couchbaseserver_data")
    t.add_resource(instance)

for i in xrange(configuration.NUM_COUCHBASE_SERVERS_INDEX):
    name = "couchbaseserverindex{}".format(i)
    instance = ec2.Instance(name)
    instance.ImageId = configuration.COUCHBASE_IMAGE
    instance.InstanceType = configuration.COUCHBASE_INSTANCE_TYPE
    instance.SecurityGroupIds = [ Ref(securitygroupidparameter)]
    instance.SubnetId = Ref(subnetidparameter)
    instance.KeyName = Ref(keynameparameter)
    instance.Tags=Tags(Name=name, Type="couchbaseserver_index")
    t.add_resource(instance)


for i in xrange(configuration.NUM_COUCHBASE_SERVERS_QUERY):
    name = "couchbaseserverquery{}".format(i)
    instance = ec2.Instance(name)
    instance.ImageId = configuration.COUCHBASE_IMAGE
    instance.InstanceType = configuration.COUCHBASE_INSTANCE_TYPE
    instance.SecurityGroupIds = [ Ref(securitygroupidparameter)]
    instance.SubnetId = Ref(subnetidparameter)
    instance.KeyName = Ref(keynameparameter)
    instance.Tags=Tags(Name=name, Type="couchbaseserver_query")
    t.add_resource(instance)


for i in xrange(configuration.NUM_CLIENTS):
    name = "clients{}".format(i)
    instance = ec2.Instance(name)
    instance.ImageId = configuration.CLIENT_IMAGE
    instance.InstanceType = configuration.CLIENT_INSTANCE_TYPE
    instance.SecurityGroupIds = [ Ref(securitygroupidparameter)]
    instance.SubnetId = Ref(subnetidparameter)
    instance.KeyName = Ref(keynameparameter)
    instance.Tags=Tags(Name=name, Type="clients")
    t.add_resource(instance)


print(t.to_json())
