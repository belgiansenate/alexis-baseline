# Use the official CentOS 7 base image
FROM centos:7

# Set the working directory
WORKDIR /senbot-app

# Install necessary dependencies
RUN yum install -y epel-release && yum update -y && \
    yum install python-pip && \
    yum install tar && \
    yum install gcc openssl-devel bzip2-devel libffi-devel zlib-devel && \
    wget https://www.python.org/ftp/python/3.9.6/Python-3.9.6.tgz && \
    ./configure --enable-optimizations && \
    make altinstall && \
    rm Python-3.9.6.tgz && \
    yum clean all && \
    rm -rf /var/cache/yum \
    yum python3-pip


# Copy the requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Specify the command to run on container start
CMD ["python", "main.py"]
