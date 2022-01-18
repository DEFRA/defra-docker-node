
#  Image vulnerability scanning

The repository runs a vulnerability scan of the latest Docker hub parent image nightly, and the 'work in progress' image on push to a branch via the GitHub actions workflows [nightly-scan.yml](.github/workflows/nightly-scan.yml) and [scan-on-commit.yml](.github/workflows/scan-on-commit.yml) respectively.

Scheduled actions only run on the `master` repository branch so will run once, regardless of the number of branches.

Both workflows read settings from the file [JOB.env](JOB.env) to ensure the same Node.js, Alpine, and Defra versions are used during the image scan.

Scans are performed by [Anchore Grype](https://github.com/anchore/grype) using the configuration file [.grype.yaml](.grype.yaml) via the [Github Anchore Scan Action](https://github.com/anchore/scan-action).

The scan is configured to fail on vulnerabilities of `medium` or higher.

Details on the configuration file and exclusions can be found in [POLICY_CONFIGURATION.md](POLICY_CONFIGURATION.md).

## Addressing vulnerabilities

If the Grype scan finds a vulnerability the scan will fail and a report will be stored as an artifact against the failed GitHub [Action](https://github.com/DEFRA/defra-docker-node/actions).

There are two solutions to address an image vulnerability: patch the Dockerfile to upgrade the vulnerable library, or add the vulnerability to the exclusion list if deemed not exploitable.

### Adding a vulnerability to the exclusion list

Generally speaking the only vulnerabilities that are excluded are binaries used by the `npm` command line tool, as these are not exploitable in a running container, and are complicated to update.

The scan output and the artifacts on the GitHub Action log will provide details of the type and severity of the vulnerability, along with the CVE ID of the vulnerability.

To exclude the vulnerability add an item to the `.grype.yaml`'s `ignore` list. Full details on formatting the YAML can be found in the `grype` documenation under [Specifying Matches to Ignore](https://github.com/anchore/grype#specifying-matches-to-ignore).

The preferred option is to specify the CVE ID, along with the type of vulnerability and the package name itself. This makes it easier to tie the reported vulnerability to the file.

The example below shows the yaml to exclude the `CVE-2021-3807` vulnerability for the `npm` package `ansi-regex`, as well as the `npm` package itself as `CVE-2021-43616`:
```
ignore:
  - vulnerability: GHSA-93q8-gq69-wqmw
  - vulnerability: CVE-2021-3807
    package:
      type: npm
      name: ansi-regex
  - vulnerability:  CVE-2021-43616
    package:
      type: npm
      name: npm
```

Any exclusions should be recorded in the [POLICY_CONFIGURATION.md](POLICY_CONFIGURATION.md) with an explanation of why they are considered non-exploitable.

When updating an image to a newer version it is important to remove all existing ignores and only re-add ones that have still not been fixed to ensure the `.grype.yaml` file does not become cluttered with fixed vulnerabilities.

### Patching an Alpine package

If the vulnerability is for an Alpine package, check the CVE report to see if the issue is fixed in a newer version of the package. If so, check if the patched version of the package is available in [Alpine Linux](https://pkgs.alpinelinux.org/packages).

The Dockerfile will need to be updated to install the fixed version of the package.
There is already a line present in the [Dockerfile](./Dockerfile) that installs Alpine packages. The line, slightly simplified, is show below:

```
RUN apk update && apk add --no-cache tini && apk add ca-certificates && rm -rf /var/cache/apk/*
``` 

To install the new package you need to supply the name and minimum version to the `apk add` command. The syntax to install `libssl` at version `1.1.1` or greater would be:

```
apk add --no-cache 'libssl1.1>1.1.1'
```

Note that the `>` symbol will install versions `1.1.1` or greater, so acts like a `>=` operator. Also the `'` quotes around the package name and version are important, and leaving them out can lead to unintended behaviour.

The command should be placed after the `tini` installation, with a leading `&&`. The line above correctly updated would be:
```
RUN apk update && apk add --no-cache tini  && apk add --no-cache 'libssl1.1>1.1.1' && apk add ca-certificates && rm -rf /var/cache/apk/*
```
Sometimes a patch version contains letters, i.e. `1.1.1j-r0`, these should be matched with a `>1.1.1` where possible, rather than tying to a specific version with `=1.1.1j-r0`.

Further details on `apk` syntax can be found in the [Alpine package management documentation](https://wiki.alpinelinux.org/wiki/Alpine_Linux_package_management).

## Running an Anchore Grype scan locally

Install `grype` on your machine as per the instructions at https://github.com/anchore/grype.

First build the production image locally with a known tag as described in the [README.md](README.md), i.e.
```
docker build --no-cache --tag defra-node:latest --target=production .
```

Scan the tagged image, i.e. `defra-node:latest`, using  the `grype` configuration file `.grype.yaml`. 
```
grype defra-node:latest --fail-on medium
```
or
```
grype defra-node:latest --fail-on medium -o json > report.json
```
**Note:** the configuration file is in the default location so does not need specifying on the command line.

Full documentation on `grype`` be found at https://github.com/anchore/grype

## Upgrading Anchore Grype

Grype updates are frequent. To update grype on a *nix system run the update `curl` at  https://github.com/anchore/grype as super user, i.e.
```
sudo -i
curl -sSfL https://raw.githubusercontent.com/anchore/grype/main/install.sh | sh -s -- -b /usr/local/bin
exit
```
