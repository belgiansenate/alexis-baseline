# Use the official CentOS 7 base image
FROM centos:7

# Set the working directory
WORKDIR /app

# Install necessary dependencies
RUN yum install -y epel-release && yum update -y && yum install -y python39 python39-pip

# Copy the requirements file and install dependencies
COPY requirements.txt .
RUN pip3.9 install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Set environment variables
ENV PYTHONUNBUFFERED 1

# Specify the command to run on container start
CMD ["python", "main.py"]
