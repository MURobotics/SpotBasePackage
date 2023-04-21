FROM python:3.6
# Building the docker image from a preexisting image (on dockerhub)

WORKDIR /usr/src/app
# Any instructions for building the container will be based off of this file location in the OS

COPY . .

ENTRYPOINT [ "./launch.sh" ]