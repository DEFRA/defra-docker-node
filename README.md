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
| 20.20.0       | 20.20.0-alpine3.23 |
| 22.22.0       | 22.22.0-alpine3.23 |
| 24.13.1       | 24.13.1-alpine3.23 |

Two parent images are created for each version:

- defra-node
- defra-node-development

It is recommended that services use [multi-stage builds](https://docs.docker.com/develop/develop-images/multistage-build) to produce production and development images, each extending the appropriate parent, from a single Dockerfile.

### Example files

[Examples](https://github.com/DEFRA/defra-docker-node/tree/master/examples) are provided to show how parent images can be extended for different types of services. These should be a good starting point for building Node services conforming to Defra standards.

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

In addition a commit to the master branch will push the images to the [defradigital](https://hub.docker.com/u/defradigital) organisation in Docker Hub using the version tag specified in the [JOB.env](JOB.env) file. This version tag is expected to be manually updated on each release.

In addition to the version, the images will also be tagged with the contents of the `tags` array from [image-matrix.json](image-matrix.json) when pushed to Docker Hub.

## Image vulnerability scanning

A GitHub Action runs a nightly scan of the images published to Docker using [Anchore Grype](https://github.com/anchore/grype/) and [Aqua Trivy](https://www.aquasec.com/products/trivy/). The latest images for each supported Node.js version are scanned.

New images are also scanned before release on any push to a branch.

This ensures Defra services that use the parent images are starting from a known secure foundation, and can limit patching to only newly added libraries.

For more details see [Image Scanning](IMAGE_SCANNING.md)

## Automated version updates

The [auto-update](/.github/workflows/auto-update.yml) workflow runs nightly to check for new versions of Node.js and their associated Alpine images. If a new version is found, the workflow will create a pull request to update to the latest version.

These updates are scoped to the Node.js versions listed in the [image-matrix.json](image-matrix.json) file.

## Convenience script

A simple convenience script [bump](./bump) is provided to substitute version in the files `Dockerfile`, `README.md`, and `image-matrix.json`.

The 'from' and 'to' values to substitute are separated by a colon, and multiple arguments must be separated by a space.

i.e. `./bump 16.13.0:16.18.1 14.18.1:14.21.1` will replace all instances of `16.13.0` with `16.18.1` and all instances of `14.18.1` with `14.21.1`.

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
