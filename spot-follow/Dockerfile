FROM python:3.6
# Building the docker image from a preexisting image (on dockerhub)

# Create source & tmp build directory
RUN mkdir /tmpbuild
WORKDIR /tmpbuild

RUN apt-get update && apt-get install ffmpeg libsm6 libxext6 libvtk9-dev -y

RUN apt-get update && apt-get -y --no-install-recommends install \
    build-essential \
    clang \
    cmake \
    gdb \
    wget 

###################################################################################################################
# Download sources & setup supporting libraries that are needed to build VTK
###################################################################################################################
# Download & extract VTK
RUN wget http://www.vtk.org/files/release/9.0/VTK-9.0.0.tar.gz && tar -zxvf VTK-9.0.0.tar.gz

# Download, extract & build CMake
# http://www.vtk.org/Wiki/VTK/Configure_and_Build
RUN wget https://cmake.org/files/v3.29/cmake-3.29.2.tar.gz \
    && tar xzf cmake-3.29.2.tar.gz
RUN cd cmake-3.29.2 \
    && ./configure --prefix=/usr/local \
    && make \
    && make install

# Install OpenGL
# Debian, Ubuntu
# https://en.wikibooks.org/wiki/OpenGL_Programming/Installation/Linux
RUN apt-get update && apt-get install --yes build-essential libgl1-mesa-dev

# Download & build Tcl
# https://www.tcl.tk/doc/howto/compile.html#unix
RUN wget http://prdownloads.sourceforge.net/tcl/tcl8.6.6-src.tar.gz && tar -zxvf tcl8.6.6-src.tar.gz
RUN cd tcl8.6.6/unix && ./configure && make && make install

# Download & build Tk
# https://www.tcl.tk/doc/howto/compile.html
RUN wget http://prdownloads.sourceforge.net/tcl/tk8.6.6-src.tar.gz && tar -zxvf tk8.6.6-src.tar.gz
RUN cd tk8.6.6/unix && ./configure && make && make install
###################################################################################################################
# /end setup
###################################################################################################################

###################################################################################################################
# Building VTK with python interfaces
# http://ghoshbishakh.github.io/blog/blogpost/2016/03/05/buid-vtk.html
###################################################################################################################
RUN mkdir /vtk-build2
RUN cd /vtk-build2/ && cmake \
    -DCMAKE_BUILD_TYPE:STRING=Release \
    -DBUILD_TESTING:BOOL=OFF \
    -DVTK_WRAP_PYTHON:BOOL=ON \
    -DVTK_WRAP_PYTHON_SIP:BOOL=ON \
    -DVTK_WRAP_TCL:BOOL=ON \
    -DVTK_PYTHON_VERSION:STRING=3 \
    -DVTK_USE_TK:BOOL=ON \
  /tmpbuild/VTK-9.0.0

# Build VTK
RUN cd /vtk-build2/ && make

# Now install the python bindings
RUN cd /vtk-build2/Wrapping/Python && make && make install

# Set environment variable to add the VTK libs to the Shared Libraries
# http://tldp.org/HOWTO/Program-Library-HOWTO/shared-libraries.html
# export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/usr/local/lib:/vtk-build2/lib
ENV LD_LIBRARY_PATH $LD_LIBRARY_PATH:/usr/local/lib:/vtk-build2/lib
###################################################################################################################
# /end VTK Build
###################################################################################################################

# Create Mount points
# https://docs.docker.com/engine/reference/builder/#/volume
#
# - /vtk-build: directory is used to build the VTK library from with a container with ccmake
# - /out: directory is used for python to write output files (JPEG, PNG, etc)
#VOLUME ["/vtk-build", "/out"]
#VOLUME ["/out"]

# Create the possible mount points
RUN mkdir /out && mkdir /src

WORKDIR /usr/src/app
# Any instructions for building the container will be based off of this file location in the OS

# Creates a directory to store images taken by the cameras
RUN mkdir /usr/src/app/imgs

COPY requirements.txt ./
# Copying requirements.txt from our source folder on the HOST (our) machine into the container at this location RELATIVE to the WORKDIR (i.e /usr/src/app/.)
RUN pip install --no-cache-dir -r requirements.txt
# Running inside the container a command at the location of the WORKDIR (i.e /usr/src/app)
RUN apt-get update && apt-get install ffmpeg libsm6 libxext6  -y

COPY . .
# Copy over the source code into the WORKDIR (/usr/src/app)

RUN chmod +x launch.sh
# Final run command to allow a bash script file to have execute permission on the container
ENTRYPOINT [ "./launch.sh" ]
# Default command that will run ALWAYS when the container has started