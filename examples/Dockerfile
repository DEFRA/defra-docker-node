# Allow parent image version to be set at build time
ARG PARENT_VERSION=3.1.4-node24.19.0

FROM defradigital/node:$PARENT_VERSION AS base

ENV TZ="Europe/London"

# Copy our package files so that our package install will do a clean install. This installs the exact versions of the packages
#   listed in package-lock.json, and does not update either the package-lock.json or the package.json file.
COPY --chown=node:node package*.json ./

# Development stage installs devDependencies and copies in source. We name this stage so we can refer to it in later stages.
FROM defradigital/node-development:$PARENT_VERSION AS development

# We copy the installed packages from the production "base" install that was the first stage.
COPY --from=base --chown=node:node /home/node/package*.json ./

# We run a full dev install to bring in any development packages
RUN npm ci --ignore-scripts
COPY --chown=node:node src/ ./src/

# Web archetype: exposes a port and runs a build step to create static files for the front end.
FROM development AS development-web

# Set the port that is going to be exposed later on in the Dockerfile as well.
ARG PORT=3000
ENV PORT=${PORT}

# Expose the PORT passed in to the Dockerfile, and also some development debugging ports that are used during development
EXPOSE ${PORT} 9229

# Run the build command to get the extra files needed for production. We also specify a command here,
#   as we can run this stage directly using either docker-compose files, or passing --target to the docker build command
RUN npm run build
CMD [ "npm", "run", "start:watch" ]

# Service archetype: a message-based service with no exposed ports and no build step.
FROM development AS development-service

# Expose some development debugging ports that are used during development
EXPOSE 9229 9230

# We specify a command here, as we can run this stage directly using either docker-compose files, or passing --target to the docker build command
CMD [ "npm", "run", "start:watch" ]

# Test stages copy in Jest configuration and declare the test task as the default command. We use the development-*
#   stages for this as they will have all the tools required installed and have everything ready to run tests.
FROM development-web AS test-web
COPY --chown=node:node jest.config.js ./jest.config.js
COPY --chown=node:node test/ ./test/
CMD [ "npm", "run", "test" ]

FROM development-service AS test-service
COPY --chown=node:node jest.config.js ./jest.config.js
COPY --chown=node:node test/ ./test/
CMD [ "npm", "run", "test" ]

# Production stage (web) exposes the service port, copies in built app code and declares the Node app as the default command.
FROM base AS production-web

# Switch to root temporarily to install production dependencies and lock down file permissions.
USER root

ARG PORT=3000
EXPOSE ${PORT}

# Copy application artifacts and assign root ownership to prevent modification by other users.
COPY --from=development-web --chown=root:root /home/node/package*.json ./
COPY --from=development-web --chown=root:root /home/node/src/ ./src/

# Install node modules, remove write permissions, then drop back to the unprivileged user.
RUN npm ci --ignore-scripts --omit=dev && chmod -R a-w /home/node
USER node

# This is the command that is run for the production service. The parent image has an ENTRYPOINT that uses a lightweight
#   init program "tini" that handles signals. As long as we don't override the ENTRYPOINT the "tini" routine will handle signals and
#   orphaned processes
CMD [ "node", "src/index" ]

# Production stage (service) copies in built app code and declares the Node app as the default command. No port is exposed.
FROM base AS production-service

# Switch to root temporarily to install production dependencies and lock down file permissions.
USER root

# Copy application artifacts and assign root ownership to prevent modification by other users.
COPY --from=development-service --chown=root:root /home/node/package*.json ./
COPY --from=development-service --chown=root:root /home/node/src/ ./src/

# Install node modules, remove write permissions, then drop back to the unprivileged user.
RUN npm ci --ignore-scripts --omit=dev && chmod -R a-w /home/node
USER node

# This is the command that is run for the production service. The parent image has an ENTRYPOINT that uses a lightweight
#   init program "tini" that handles signals. As long as we don't override the ENTRYPOINT the "tini" routine will handle signals and
#   orphaned processes
CMD [ "node", "src/index" ]
