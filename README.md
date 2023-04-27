# SpotBasePackage
Base library for controlling Boston Dynamics Spot robots programmatically

## Running Server and Client
For the server, run "docker build -t server ." in the spot-follow/server directory to build

For the client, run "docker build -t client ." in the spot-follow/client directory to build

To set up the network, run "docker network create spot-net"

Run "docker run --rm -it --env-file secrets/spot_account.env --name server --net spot-net server" to start the server

Run "docker run --rm -it --env-file secrets/spot_account.env --name client --net spot-net client" to start the client

The server will stop as soon as the client terminates its connection, so to delay this, add a time.sleep() to the end of the client.py

## Troubleshooting
exec ./launch.sh: no such file or directory

Solution: change the end of file character from CRLF to LF or vice versa on the Dockerfile and launch.sh files.


docker-compose build not working on Mac

Solution: For Mac M1/M2s, add "platform: linux/amd64" to the docker-compose.yml file after the env_file line. Also, remove "windows-curses==2.1.0; sys_platform == 'win32'" from the requirements.txt file.
