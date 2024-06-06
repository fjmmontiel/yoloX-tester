IMAGE_NAME_BACKEND = yolox-backend
IMAGE_NAME_FRONTEND = yolox-frontend
IMAGE_VERSION_BACKEND = $(shell cat backend/version.txt)
IMAGE_VERSION_FRONTEND = $(shell cat frontend/version.txt)

DOCKER_FULL_NAME_BACKEND = ${IMAGE_NAME_BACKEND}:${IMAGE_VERSION_BACKEND}
DOCKER_FULL_NAME_FRONTEND = ${IMAGE_NAME_FRONTEND}:${IMAGE_VERSION_FRONTEND}

.PHONY: build-back build-front

build-back:
	docker buildx build --build-arg APP_VERSION=${IMAGE_NAME_BACKEND} -t ${DOCKER_FULL_NAME_BACKEND} -f DockerfileBackend .

build-front:
	docker build --build-arg APP_VERSION=${IMAGE_NAME_FRONTEND} -t ${DOCKER_FULL_NAME_FRONTEND} -f DockerfileFrontend .
