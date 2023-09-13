FROM nvidia/cuda:11.3.1-base-ubuntu20.04

# Install python 3.9
RUN apt-get update && apt-get install software-properties-common -y
RUN add-apt-repository ppa:deadsnakes/ppa
RUN apt-get install python3.9 -y
RUN apt-get install -y python3.9-distutils

# Add Python 3.9 to the available alternatives
RUN update-alternatives --install /usr/bin/python python /usr/bin/python3.9 1
RUN update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.9 1

# Set Python 3.9 as the default python
RUN update-alternatives --set python /usr/bin/python3.9

# Install pip
RUN apt install python3-pip -y
RUN python -m pip install --upgrade pip
RUN pip install --upgrade setuptools

# Install requirements
WORKDIR /usr/local/src/kfp/components
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
