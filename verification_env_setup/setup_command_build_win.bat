PowerShell.exe -ExecutionPolicy Bypass -Command ^
"docker build ^
-f Dockerfile ^
--target builder-icarus ^
--tag syosil-icarus-img ^
--target syosil-base ^
--build-arg USERNAME=$env:username-docker ^
--tag syosil-ubuntu-image ^
. ; ^
docker image prune -f"
