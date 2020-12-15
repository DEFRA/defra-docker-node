# Docker Node

This repository contains Node parent Docker image source code for Defra.

The following table lists the versions of node available, and the parent node image they are based on:

| Node version  | Parent image       |
| ------------- | -----------------  |
| 12.18.3       | 12.18.3-alpine3.12 |
| 14.15.0       | '14.15.0-alpine3.12|

Two parent images are created for each version:

- defra-node
- defra-node-development

It is recommended that services use [multi-stage builds](https://docs.docker.com/develop/develop-images/multistage-build) to produce production and development images, each extending the appropriate parent, from a single Dockerfile.

[Examples](./example) are provided to show how parent images can be extended for different types of services. These should be a good starting point for building Node services conforming to FFC standards.

## Building images locally

To build the images locally, run:
```
docker build . --no-cache --target <target> .
```
(where <target> is either `development` or `production`).

This will build an image using the default `BASE_VERSION` as set in the [Dockerfile](Dockerfile).

## Internal CA certificates

The image includes the certificate for the internal [CA](https://en.wikipedia.org/wiki/Certificate_authority) so that traffic can traverse the network without encountering issues.

## Versioning

Images should be tagged according to the Dockerfile version and the version of Node on which the image is based. For example, for Dockerfile version `1.0.0` based on Node `12.16.0`, the built image would be tagged `1.0.0-node12.16.0`.

## Example files

`Dockerfile.web` - This is an example web project, that requires a build step to create some static files that are used by the web front end.

`Dockerfile.service` - This is an example project that doesn't expose any external ports (a message based service). There is also no build step in this Dockerfile.

## CI/CD

On commit to master Jenkins will build both `node` and `node-development` images and push them to the `defradigital` organisation in GitHub if the tag specified in the `version` map within the `./Jenkinsfile` does not already exist in Docker Hub.

This image uses the [Defra Docker Shared Jenkins library](https://github.com/DEFRA/defra-docker-jenkins) to abstract pipeline complexity from repository.  See repository for further usage details.

## Image Vulnerabilities - patching and exclusions

The repository runs a nightly scan of the latest parent image, and will scan images on commit to a branch.
Note that the scan is performed using version 1 of the [Anchore Scan Action](https://github.com/anchore/scan-action/tree/version1) as version 2 does not yet support policy files.

If the Anchore scan finds a vulnerability the scan will fail and a report will be stored as an artefact against the failed scan action at [Actions](https://github.com/DEFRA/defra-docker-node/actions).

There are two solutions to an image vulnerability. Patching the Dockerfile to upgrade the vulnerable library, or to add it to the exclusion list if it is not exploitable.

### Adding a vulnerability to the exclusion list

Generally speaking the only vulnerabilities that are excluded are binaries used by the npm command line tool, as these are not exploitable in a running container, and not straight forward to update.

The scan output on the GitHub Action log will provide details of the gate and trigger that has failed, along with the CVE ID of the vulnerability.

The vulnerability report will also provide the CVE ID and package name in the file with the suffix `-vuln.json`.
To exclude the vulnerability add an item to the `anchore-policy.json`'s `whitelists` section.

The item will need a unique ID specified, the gate and trigger that has failed, and a trigger ID which comprises the CVE ID and package name separated with a `+`.

The below JSON shows the format to add an exclusion for a failure on the `vulnerabilities` gate, on trigger `package` for `CVE-2020-8116` against the `dot-prop` package

```
"whitelists": [
{
    "id": "whitelist1",
    "name": "NPM binaries Whitelist",
    "version": "1_0",
    "items": [
        { "id": "item1", "gate": "vulnerabilities", "trigger": "package", "trigger_id": "CVE-2020-8116+dot-prop" }
    ]
}
```

### Patching an Alpine package

If the vulnerability is for an Alpine package, check the CVE report to see if the issue is fixed in a newer version of the package. If so, check if the patched version of the package is available in [Alpine Linux](https://pkgs.alpinelinux.org/packages).

The Dockerfile will need to be updated to install the specific version of the package.
There is already a line present in the [Dockerfile](./Dockerfile) that installs Alpine packages. A simplified version is show below:

```
RUN apk update && apk add --no-cache tini && apk add ca-certificates && rm -rf /var/cache/apk/*
``` 

To install a specific version of a package you need to know the name and minimum version of a package. The syntax to install `libssl` at version `1.1.1` or greater would be:

```
apk add --no-cache 'libssl1.1>1.1.1'
```

Note that the `>` symbol will install versions `1.1.1` or greater, so really acts like a `>=` operator.

The command should be placed after the `tini` installation, with a leading `&&`. The line above correctly updated would be:
```
RUN apk update && apk add --no-cache tini  && apk add --no-cache 'libssl1.1>1.1.1' && apk add ca-certificates && rm -rf /var/cache/apk/*
```


## Licence

THIS INFORMATION IS LICENSED UNDER THE CONDITIONS OF THE OPEN GOVERNMENT LICENCE found at:

<http://www.nationalarchives.gov.uk/doc/open-government-licence/version/3>

The following attribution statement MUST be cited in your products and applications when using this information.

> Contains public sector information licensed under the Open Government license v3

### About the licence

The Open Government Licence (OGL) was developed by the Controller of Her Majesty's Stationery Office (HMSO) to enable information providers in the public sector to license the use and re-use of their information under a common open licence.

It is designed to encourage use and re-use of information freely and flexibly, with only a few conditions.
