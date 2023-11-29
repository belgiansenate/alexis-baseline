# Use the official CentOS 7 base image
FROM centos:7

# Set the working directory
WORKDIR /senbot-app

# Install necessary dependencies
RUN yum install -y epel-release
RUN yum update -y
RUN yum install python-pip
RUN yum install tar
RUN yum install gcc openssl-devel bzip2-devel libffi-devel zlib-devel
RUN wget https://www.python.org/ftp/python/3.9.6/Python-3.9.6.tgz
RUN ./configure --enable-optimizations
RUN make altinstall
RUN rm Python-3.9.6.tgz
RUN yum clean all
RUN rm -rf /var/cache/yum
RUN yum python3-pip


# Copy the requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Specify the command to run on container start
CMD ["python", "main.py"]
