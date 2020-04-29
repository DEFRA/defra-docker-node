# Set default values for build arguments
ARG DOCKERFILE_VERSION=1.0.0
ARG NODE_VERSION=12.16.0

FROM node:$NODE_VERSION-alpine AS production

ARG NODE_VERSION
ARG DOCKERFILE_VERSION

ENV NODE_ENV production

# Set global npm dependencies to be stored under the node user directory
ENV NPM_CONFIG_PREFIX=/home/node/.npm-global
ENV PATH=$PATH:/home/node/.npm-global/bin

# We need a basic init process to handle signals and reap zombie processes, tini handles that
RUN apk update && apk add --no-cache tini=~0.18
ENTRYPOINT ["/sbin/tini", "--"]

# Never run as root, default to the node user (created by the base Node image)
USER node

# Default workdir should be owned by the default user
WORKDIR /home/node

# Label images to aid searching
LABEL uk.gov.defra.node.node-version=$NODE_VERSION \
      uk.gov.defra.node.version=$DOCKERFILE_VERSION

FROM production AS development

ENV NODE_ENV development

# node-gyp is a common requirement for NPM packages. It must be installed as root.
USER root
RUN apk update && \
    apk add --no-cache git=~2.24 && \
    apk add --no-cache --virtual .gyp python=~2.7 make=~4.2 g++=~9.2
# Pact dependencies are not included in Alpine image for contract testing
RUN  apk --no-cache add ca-certificates wget bash \
    && wget -q -O /etc/apk/keys/sgerrand.rsa.pub https://alpine-pkgs.sgerrand.com/sgerrand.rsa.pub \
    && wget https://github.com/sgerrand/alpine-pkg-glibc/releases/download/2.29-r0/glibc-2.29-r0.apk \
    && apk add glibc-2.29-r0.apk
USER node
