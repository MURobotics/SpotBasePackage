FROM python:3.6
# Building the docker image from a preexisting image (on dockerhub)

WORKDIR /usr/src/app
# Any instructions for building the container will be based off of this file location in the OS

COPY ./requirements.txt ./
# Copying requirements.txt from our source folder on the HOST (our) machine into the container at this location RELATIVE to the WORKDIR (i.e /usr/src/app/.)
RUN pip install --no-cache-dir -r requirements.txt
# Running inside the container a command at the location of the WORKDIR (i.e /usr/src/app)

#Get CreateSpot.py and SpotUtil.py from the spot-follow directory
COPY ./CreateSpot.py ./
COPY ./SpotUtil.py ./

COPY ./server .
# Copy over the source code into the WORKDIR (/usr/src/app)
RUN apt-get update -y && apt-get install x11-xserver-utils -y

RUN chmod +x launch.sh
# Final run command to allow a bash script file to have execute permission on the container

ENTRYPOINT [ "./launch.sh" ]