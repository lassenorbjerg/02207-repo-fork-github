PowerShell.exe -ExecutionPolicy Bypass -Command ^
"docker run -it ^
-e DISPLAY=host.docker.internal:0.0 ^
--mount source=$env:username-docker-workdir,target=/home/$env:username-docker ^
--name syosil-ubuntu-container ^
syosil-ubuntu-image"
