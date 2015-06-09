
FROM ansible/ubuntu14.04-ansible:stable

# Get dependencies
RUN apt-get update && apt-get install -y \
  git \
  python-pip 

# Install pip packages
RUN pip install troposphere && \
    pip install awscli && \
    pip install boto 

# Clone the aws-perfcluster repo
RUN cd /root && \
    git clone https://github.com/couchbaselabs/perfcluster-aws.git