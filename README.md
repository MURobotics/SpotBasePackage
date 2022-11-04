# SpotBasePackage
Base library for controlling Boston Dynamics Spot robots programmatically

## Troubleshooting
exec ./launch.sh: no such file or directory
Solution: change the end of file character from CRLF to LF or vice versa on the Dockerfile and launch.sh files.

docker-compose build not working on Mac
Solution: For Mac M1/M2s, add "platform: linux/amd64" to the docker-compose.yml file after the env_file line. Also, remove "windows-curses==2.1.0; sys_platform == 'win32'" from the requirements.txt file.
