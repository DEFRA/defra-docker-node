
#  Image vulnerability scanning

The repository runs a vulnerability scan of the latest Docker hub parent image nightly, and the 'work in progress' image on push to a branch via the GitHub actions workflows [nightly-scan.yml](.github/workflows/nightly-scan.yml) and [scan-on-commit.yml](.github/workflows/scan-on-commit.yml) respectively.

Scheduled actions only run on the `master` repository branch so will run once, regardless of the number of branches.

Both workflows read settings from the file [JOB.env](JOB.env) to ensure the same Node.js, Alpine, and Defra versions are used during the image scan.

Scans are performed by the [Anchore Engine CLI Tools](https://github.com/anchore/ci-tools) inline script using the policy file [anchore-policy.json](anchore-policy.json).
Details on the policy configuration and exclusions can be found in [POLICY_CONFIGURATION.md](POLICY_CONFIGURATION.md).

## Addressing vulnerabilities

If the Anchore scan finds a vulnerability the scan will fail and a report will be stored as an artifact against the failed GitHub [Action](https://github.com/DEFRA/defra-docker-node/actions).

There are two solutions to address an image vulnerability: patch the Dockerfile to upgrade the vulnerable library, or add the vulnerability to the exclusion list if deemed not exploitable.

### Adding a vulnerability to the exclusion list

Generally speaking the only vulnerabilities that are excluded are binaries used by the `npm` command line tool, as these are not exploitable in a running container, and are complicated to update.

The scan output on the GitHub Action log will provide details of the gate and trigger that has failed, along with the CVE ID of the vulnerability.

The vulnerability report also provides the CVE ID and package name in a file with the suffix `-vuln.json`, available in the failed Github Action's artifact.

To exclude the vulnerability add an item to the `anchore-policy.json`'s `whitelists` section.

The item will need a unique ID specified, the gate and trigger that has failed, and a trigger ID which comprises the CVE ID and package name separated with a `+`.

The below JSON shows the format to add an exclusion for a failure on the `vulnerabilities` gate, on trigger `package` for `CVE-2020-8116` against the `dot-prop` package:

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

Any exclusions should be recorded in the [POLICY_CONFIGURATION.md](POLICY_CONFIGURATION.md) with an explanation of why they are considered non-exploitable.

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

## Running an Anchore Engine scan locally

First build the production image locally with a known tag as described in the [README.md](README.md), i.e.
```
docker build --no-cache --tag defra-node:latest --target=production .
```

Scan the tagged image, i.e. `defra-node:latest`, using the Anchore hosted script and the policy file `anchore-policy.json`:
```
curl -s https://ci-tools.anchore.io/inline_scan-v0.9.3 | bash -s -- -r -f -b ./anchore-policy.json defra-node:latest
```

Full documentation on the inline scanning tool can be found at https://github.com/anchore/ci-tools.
