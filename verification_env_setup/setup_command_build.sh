docker build \
--platform linux/amd64 \
-f Dockerfile \
--tag syosil-icarus-img \
--target syosil-base \
--build-arg USERNAME=$USER-docker \
--tag syosil-ubuntu-image \
. ; \
docker image prune -f
