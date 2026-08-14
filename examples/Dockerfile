# This uses the published Defra Node.js parent images from Docker Hub:
# https://github.com/DEFRA/defra-docker-node
#
# Two service archetypes are shown as separate targets, sharing the development setup below:
#   "web" (exposes a port, has a build step) and "service" (a message-based service with no
#   exposed port and no build step). Build/run only the target that matches your service, e.g.
#   `docker build --target production-web .`, and delete the stages for the archetype you don't
#   need once you've copied this into your own repo.
#
# There's no separate stage for running tests: run `npm test` directly, on the host or in CI,
# against the same source tree used by the "development" stage.

ARG PARENT_VERSION=3.1.4-node24.19.0
ARG PORT=3000

# Development stage (shared): installs all dependencies and copies in source.
FROM defradigital/node-development:$PARENT_VERSION AS development

ENV TZ="Europe/London"

ARG PORT
ENV PORT=${PORT}
EXPOSE ${PORT} 9229

COPY --chown=node:node package*.json ./
RUN npm ci --ignore-scripts
COPY --chown=node:node src/ ./src/

# Web archetype: runs a build step to create static files for the front end.
FROM development AS development-web
RUN npm run build
CMD [ "npm", "run", "start:watch" ]

# Service archetype: a message-based service with no build step.
FROM development AS development-service
CMD [ "npm", "run", "start:watch" ]

# Re-runs the build with NODE_ENV=production set, for an optimised production bundle.
FROM development-web AS production-build-web
ENV NODE_ENV=production
RUN npm run build

# Production stage (web): fresh production-only install, read-only application files.
FROM defradigital/node:$PARENT_VERSION AS production-web

ENV TZ="Europe/London"

ARG PORT
EXPOSE ${PORT}

# Switch to root temporarily to install production dependencies and lock down file permissions.
USER root

# Copy application artifacts and assign root ownership to prevent modification by other users.
COPY --from=production-build-web --chown=root:root /home/node/package*.json ./
COPY --from=production-build-web --chown=root:root /home/node/src/ ./src/

# Install node modules, remove write permissions, then drop back to the unprivileged user.
RUN npm ci --ignore-scripts --omit=dev && chmod -R a-w /home/node
USER node

# This is the command that is run for the production service. The parent image has an ENTRYPOINT that uses a lightweight
#   init program "tini" that handles signals. As long as we don't override the ENTRYPOINT the "tini" routine will handle signals and
#   orphaned processes
CMD [ "node", "src/index" ]

# Production stage (service): same pattern, no build step and no exposed port.
FROM defradigital/node:$PARENT_VERSION AS production-service

ENV TZ="Europe/London"

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

