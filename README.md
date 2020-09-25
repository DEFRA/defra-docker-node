# Docker Node

This repository contains Node parent Docker image source code for Defra.

The following table lists the versions of node available, and the parent node image they are based on:

| Node version  | Parent image      |
| ------------- | ----------------- |
| 8.17.0        | 8.17.0-alpine     |
| 12.18.3       | 12.18.3-alpine3.12|

Two parent images are created for each version:

- defra-node
- defra-node-development

It is recommended that services use [multi-stage builds](https://docs.docker.com/develop/develop-images/multistage-build) to produce production and development images, each extending the appropriate parent, from a single Dockerfile.

[Examples](./example) are provided to show how parent images can be extended for different types of services. These should be a good starting point for building Node services conforming to FFC standards.

## Internal CA certificates

The image includes the certificate for the internal [CA](https://en.wikipedia.org/wiki/Certificate_authority) so that traffic can traverse the network without encountering issues.

## Versioning

Images should be tagged according to the Dockerfile version and the version of Node on which the image is based. For example, for Dockerfile version `1.0.0` based on Node `12.16.0`, the built image would be tagged `1.0.0-node12.16.0`.

## Example files

`Dockerfile.web` - This is an example web project, that requires a build step to create some static files that are used by the web front end.

`Dockerfile.service` - This is an example project that doesn't expose any external ports (a message based service). There is also no build step in this Dockerfile.

## CI/CD
On commit to master Jenkins will build both `node` and `node-development` images and push them to the `defradigital` organisation in GitHub if the tag specified in `./Jenkinsfile` does not already exist in Docker Hub.

## Licence

THIS INFORMATION IS LICENSED UNDER THE CONDITIONS OF THE OPEN GOVERNMENT LICENCE found at:

<http://www.nationalarchives.gov.uk/doc/open-government-licence/version/3>

The following attribution statement MUST be cited in your products and applications when using this information.

> Contains public sector information licensed under the Open Government license v3

### About the licence

The Open Government Licence (OGL) was developed by the Controller of Her Majesty's Stationery Office (HMSO) to enable information providers in the public sector to license the use and re-use of their information under a common open licence.

It is designed to encourage use and re-use of information freely and flexibly, with only a few conditions.
