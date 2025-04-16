# Set default values for build arguments
ARG DEFRA_VERSION=2.7.0
ARG BASE_VERSION=22.14.0-alpine3.21

FROM node:$BASE_VERSION AS production

ARG BASE_VERSION
ARG DEFRA_VERSION

ENV NODE_ENV=production

# Set global npm dependencies to be stored under the node user directory
ENV NPM_CONFIG_PREFIX=/home/node/.npm-global
ENV PATH=$PATH:/home/node/.npm-global/bin
ENV NODE_EXTRA_CA_CERTS=/usr/local/share/ca-certificates/internal-ca.crt

RUN apk add --no-cache tini ca-certificates

# Install Internal CA certificate
COPY certificates/internal-ca.crt /usr/local/share/ca-certificates/internal-ca.crt
RUN chmod 644 /usr/local/share/ca-certificates/internal-ca.crt && update-ca-certificates

# We need a basic init process to handle signals and reap zombie processes, tini handles that
ENTRYPOINT ["/sbin/tini", "--"]

# Never run as root, default to the node user (created by the base Node image)
USER node

# Default workdir should be owned by the default user
WORKDIR /home/node

# Label images to aid searching
LABEL uk.gov.defra.node.node-version=$BASE_VERSION \
      uk.gov.defra.node.version=$DEFRA_VERSION \
      uk.gov.defra.node.repository=defradigital/node

FROM production AS development

ENV NODE_ENV=development

LABEL uk.gov.defra.node.repository=defradigital/node-development

# Install common dependencies not included in the base alpine image
USER root

# node-gyp is a common requirement for NPM packages.
RUN apk add --no-cache bash 'g++' git make 'python3'
# Pact contract testing
ADD https://alpine-pkgs.sgerrand.com/sgerrand.rsa.pub /etc/apk/keys/sgerrand.rsa.pub
ADD https://github.com/sgerrand/alpine-pkg-glibc/releases/download/2.35-r1/glibc-2.35-r1.apk glibc-2.35-r1.apk
RUN apk add --no-cache glibc-2.35-r1.apk

USER node
