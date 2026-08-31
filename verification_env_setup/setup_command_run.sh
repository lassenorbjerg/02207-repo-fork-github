docker run -it \
--platform linux/amd64 \
-e DISPLAY=host.docker.internal:0.0 \
--mount source=$USER-docker-workdir,target=/home/$USER-docker \
--name syosil-ubuntu-container \
syosil-ubuntu-image
