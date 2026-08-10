![Build](https://github.com/defra/defra-docker-node/actions/workflows/build-scan-push.yml/badge.svg)
![Nightly Scan](https://github.com/defra/defra-docker-node/actions/workflows/nightly-scan.yml/badge.svg)
![Auto Update](https://github.com/defra/defra-docker-node/actions/workflows/auto-update.yml/badge.svg)
[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=DEFRA_defra-docker-node&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=DEFRA_defra-docker-node)
[![Bugs](https://sonarcloud.io/api/project_badges/measure?project=DEFRA_defra-docker-node&metric=bugs)](https://sonarcloud.io/summary/new_code?id=DEFRA_defra-docker-node)
[![Code Smells](https://sonarcloud.io/api/project_badges/measure?project=DEFRA_defra-docker-node&metric=code_smells)](https://sonarcloud.io/summary/new_code?id=DEFRA_defra-docker-node)
[![Duplicated Lines (%)](https://sonarcloud.io/api/project_badges/measure?project=DEFRA_defra-docker-node&metric=duplicated_lines_density)](https://sonarcloud.io/summary/new_code?id=DEFRA_defra-docker-node)

# Docker Node.js

This repository contains Node.js parent Docker image source code for Defra.

The following table lists the versions of node available, and the parent Node.js image they are based on:

| Node version  | Parent image       |
| ------------- | -----------------  |
| 22.23.1       | 22.23.1-alpine3.24 |
| 24.18.0       | 24.18.0-alpine3.24 |

Two parent images are created for each version:

- defra-node
- defra-node-development

It is recommended that services use [multi-stage builds](https://docs.docker.com/develop/develop-images/multistage-build) to produce production and development images, each extending the appropriate parent, from a single Dockerfile.

### Example files

[Examples](https://github.com/DEFRA/defra-docker-node/tree/main/examples) are provided to show how parent images can be extended for different types of services. These should be a good starting point for building Node services conforming to Defra standards.

`Dockerfile.web` - This is an example web project, that requires a build step to create some static files that are used by the web front end.

`Dockerfile.service` - This is an example project that doesn't expose any external ports (a message based service). There is also no build step in this Dockerfile.

## Supported Node.js versions

Services should use the latest LTS version of Node.js.

As such, the maintained parent images will align to the versions of LTS still receiving security updates.

## Internal CA certificates

The image includes the certificate for the internal [CA](https://en.wikipedia.org/wiki/Certificate_authority) so that traffic can traverse the network without encountering issues.

## Versioning

Images should be tagged according to the Dockerfile version and the version of Node on which the image is based. For example, for Dockerfile version `1.0.0` based on Node `12.16.0`, the built image would be tagged `1.0.0-node12.16.0`.

Any new features or changes to supported Node or Alpine versions will be published as `minor` version updates.  Any breaking changes to dependencies or how images can be consumed will be published as `major` updates.

## CI/CD

On commit GitHub Actions will build both `node` and `node-development` images for the Node.js versions listed in the [image-matrix.json](image-matrix.json) file, and perform a vulnerability scan as described below.

In addition a commit to the main branch will push the images to the [defradigital](https://hub.docker.com/u/defradigital) organisation in Docker Hub using the version tag specified in the [JOB.env](JOB.env) file. This tag is bumped automatically by the auto-update workflow (see below).

In addition to the version, the images will also be tagged with the contents of the `tags` array from [image-matrix.json](image-matrix.json) when pushed to Docker Hub.

## Image vulnerability scanning

A GitHub Action runs a nightly scan of the images published to Docker Hub using [Anchore Grype](https://github.com/anchore/grype/) and [Aqua Trivy](https://www.aquasec.com/products/trivy/), and every push to a branch scans the image before it can be released.

A build is only blocked by vulnerabilities that have a fix available, so unpatchable findings do not stop delivery. The nightly scan records every finding, fixable and unfixable, in a single tracking issue labelled `security-scan`.

For more details see [Image Scanning](IMAGE_SCANNING.md)

## Automated version updates

The [auto-update](/.github/workflows/auto-update.yml) workflow runs nightly. It checks for new releases of Node.js (and their Alpine images) and of the npm CLI, and when it finds one it opens a pull request that bumps the affected versions across the [image-matrix.json](image-matrix.json), [JOB.env](JOB.env), [Dockerfile](Dockerfile), [README.md](README.md) and the [examples](examples).

Because unfixable vulnerabilities no longer block a build (see [Image Scanning](IMAGE_SCANNING.md)), these pull requests normally pass the scan on their own. Once a reviewer approves, the PR merges automatically and the new images are published.

## Repository setup

The automation relies on a few repository settings:

- **Branch protection on `main`**: add `required-check` (from the build-scan-push workflow) as a required status check. It is a single, stable check that passes only when every image in the matrix has built and scanned cleanly, so it stays valid across version bumps. The individual matrix jobs are named per version and cannot be pinned directly.
- **Allow auto-merge**: enable it under *Settings → General → Pull Requests* so update PRs can merge once approved and green.
- **Pull request review**: keep review required. Update PRs still need a single human approval; the `required-check` gate is the security backstop.
- **`security-scan` label**: create it once. The nightly scan uses it to find and update its single tracking issue.
- **Secrets and variables**: `DOCKER_USERNAME`, `DOCKER_TOKEN`, `APP_ID`, `APP_PRIVATE_KEY` and the `PR_REVIEW_TEAM` variable are already configured and used by the workflows.

## Building images locally

To build the images locally, run:
```
docker build . --no-cache --target <target> .
```
(where `<target>` is either `development` or `production`).

This will build an image using the default `BASE_VERSION` as set in the [Dockerfile](Dockerfile).

## Licence

THIS INFORMATION IS LICENSED UNDER THE CONDITIONS OF THE OPEN GOVERNMENT LICENCE found at:

<http://www.nationalarchives.gov.uk/doc/open-government-licence/version/3>

The following attribution statement MUST be cited in your products and applications when using this information.

> Contains public sector information licensed under the Open Government license v3

### About the licence

The Open Government Licence (OGL) v3.0 was developed by the The National Archives to enable information providers in the public sector to license the use and re-use of their information under a common open licence.

It is designed to encourage use and re-use of information freely and flexibly, with only a few conditions.
