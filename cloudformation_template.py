
# Python script to generate the cloudformation template json file
# This is not strictly needed, but it takes the pain out of writing a
# cloudformation template by hand.  It also allows for DRY approaches
# to maintaining cloudformation templates.

from troposphere import Ref, Template, Parameter, Output, Join, GetAtt
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
sg = ec2.SecurityGroup('MySecurityGroup')
sg.GroupDescription = "Allow access to MyInstance"
sg.SecurityGroupIngress = [
    ec2.SecurityGroupRule(
        IpProtocol="tcp",
        FromPort="22",
        ToPort="22",
        CidrIp="0.0.0.0/0",
    )]

# Add security group to template
t.add_resource(sg)

# Instances
instance = ec2.Instance("myinstance")
instance.ImageId = "ami-951945d0"
instance.InstanceType = "t1.micro"
instance.SecurityGroups = [Ref(sg)]
t.add_resource(instance)

# Add output to template
t.add_output(Output(
    "InstanceAccess",
    Description="Command to use to SSH to instance",
    Value=Join("", ["ssh -i ", Ref(keyname_param), " ubuntu|ec2-user|root@", GetAtt(instance, "PublicDnsName")])
))

print(t.to_json())

