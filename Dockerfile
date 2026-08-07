# Set default values for build arguments
ARG DEFRA_VERSION=3.1.2
ARG BASE_VERSION=24.19.0-alpine3.24
ARG NPM_VERSION=12.0.2
# Pinned by digest so a rebuild of the same commit produces the same image
ARG BASE_DIGEST=sha256:d32cdf619f63fe0471182d08996dd516c6275bb5fd31ae06e55a570bd9e1ad43

FROM node:$BASE_VERSION@$BASE_DIGEST AS production

ARG BASE_VERSION
ARG DEFRA_VERSION
ARG NPM_VERSION

ENV NODE_ENV=production

# Replace the npm bundled with the base image, which lags on its own dependencies
RUN npm install -g --prefix /usr/local npm@$NPM_VERSION && npm cache clean --force

# Set global npm dependencies to be stored under the node user directory
ENV NPM_CONFIG_PREFIX=/home/node/.npm-global
ENV PATH=$PATH:/home/node/.npm-global/bin
ENV NODE_EXTRA_CA_CERTS=/usr/local/share/ca-certificates/internal-ca.crt

RUN apk add --no-cache tini ca-certificates

# Install Internal CA certificate for firewall and Zscaler proxy
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

USER node
