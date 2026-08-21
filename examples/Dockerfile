ARG PARENT_VERSION=3.2.0-node24.19.0
ARG PORT=3000

FROM defradigital/node-development:$PARENT_VERSION AS development

ENV TZ="Europe/London"

ARG PORT
ENV PORT=${PORT}
EXPOSE ${PORT} 9229

COPY --chown=node:node package*.json ./
RUN npm ci --ignore-scripts
COPY --chown=node:node src/ ./src/

RUN npm run build
CMD [ "npm", "run", "start:watch" ]

# Re-runs the build with NODE_ENV=production set, for an optimised production bundle.
FROM development AS production-build
ENV NODE_ENV=production
RUN npm run build

# Production stage: fresh production-only install, read-only application files.
FROM defradigital/node:$PARENT_VERSION AS production

ENV TZ="Europe/London"

ARG PORT
EXPOSE ${PORT}

# Switch to root temporarily to install production dependencies and lock down file permissions.
USER root

# Copy application artifacts and assign root ownership to prevent modification by other users.
COPY --from=production-build --chown=root:root /home/node/package*.json ./
COPY --from=production-build --chown=root:root /home/node/src/ ./src/

# Install node modules, remove write permissions, then drop back to the unprivileged user.
RUN npm ci --ignore-scripts --omit=dev && chmod -R a-w /home/node
USER node

# This is the command that is run for the production service. The parent image has an ENTRYPOINT that uses a lightweight
#   init program "tini" that handles signals. As long as we don't override the ENTRYPOINT the "tini" routine will handle signals and
#   orphaned processes
CMD [ "node", "src/index" ]


