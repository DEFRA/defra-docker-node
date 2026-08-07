#  Image vulnerability scanning

The repository scans the published Docker Hub image nightly via [nightly-scan.yml](.github/workflows/nightly-scan.yml), and the work in progress image on every push via [build-scan-push.yml](.github/workflows/build-scan-push.yml).

Scheduled actions only run on the `main` repository branch so will run once, regardless of the number of branches.

Both workflows read settings from the file [JOB.env](JOB.env) to ensure the same Node.js, Alpine, and Defra versions are used during the image scan.

Scans are performed by [Anchore Grype](https://github.com/anchore/grype) and [Aqua Trivy](https://www.aquasec.com/products/trivy/). Both scanners run in report-only mode. Neither decides on its own whether the build fails: their results are evaluated together by [scan-gate.py](.github/scripts/scan-gate.py) against a single policy held in [vulnerability-policy.yml](vulnerability-policy.yml).

This matters because the two scanners name the same vulnerability differently. Grype reports GHSA identifiers where Trivy reports CVE identifiers, so maintaining a separate ignore list for each meant recording the same decision twice in two vocabularies, and the two lists drifted. There is now one policy, one decision, and the gate reconciles the identifiers.

## What blocks a build

A finding blocks only if all of the following are true:

- it is `medium` severity or higher
- an upstream fix exists
- it is not covered by a scope in [vulnerability-policy.yml](vulnerability-policy.yml)
- it is not covered by an active exception in [vulnerability-policy.yml](vulnerability-policy.yml)

Everything else is still reported, in the job summary and in the repository Security tab, but does not block.

### Why unfixed vulnerabilities do not block

If there is no upstream fix, nothing done in this repository can resolve the finding. Failing the build in that situation does not make the image safer. It only prevents shipping whatever else the build contained, and it forces an exclusion to be added purely to unblock delivery. Those findings are reported and tracked instead.

### Why `main` is never blocked

The gate runs on `main` but cannot fail the build there. A rebuild of an unchanged commit must produce the same result today as it did yesterday, and vulnerability feeds update continuously, so gating `main` would mean a commit that passed on merge could start failing later with no change to the code.

Two things make that safe:

1. Base images are pinned by digest in [image-matrix.json](image-matrix.json), so rebuilding a given commit uses exactly the base image content that was scanned when the change was reviewed.
2. The nightly scan raises a GitHub issue when a published image develops a blocking finding, and the auto-update workflow opens a pull request to move to a fixed version.

The response to a newly disclosed vulnerability is to publish a fixed patch version, not to block the pipeline.

## Addressing vulnerabilities

Prefer these options in order.

### 1. Fix it

Most findings are resolved by moving to a newer version, which the [auto-update](.github/workflows/auto-update.yml) workflow does automatically:

- **Node itself**: bump `nodeVersion` in [image-matrix.json](image-matrix.json)
- **npm bundled dependencies**: bump `npmVersion` in [image-matrix.json](image-matrix.json). The base image ships an npm that lags its own dependencies, so the Dockerfile installs a pinned newer npm over it
- **Alpine packages**: check the CVE report for a fixed version, confirm it is available in [Alpine Linux](https://pkgs.alpinelinux.org/packages), then pin it on the `apk add` line in the [Dockerfile](Dockerfile)

To require a minimum version of an Alpine package, supply the name and version to `apk add`:

```
apk add --no-cache 'libssl1.1>1.1.1'
```

The `>` symbol installs version `1.1.1` or greater, so it behaves like `>=`. The quotes matter, and leaving them out can lead to unintended behaviour. Where a patch version contains letters, such as `1.1.1j-r0`, match it with `>1.1.1` rather than tying to the exact version. Further detail is in the [Alpine package management documentation](https://wiki.alpinelinux.org/wiki/Alpine_Linux_package_management).

### 2. Add a scope

Use a scope when a whole class of finding recurs and the reasoning is identical every time, rather than adding a fresh exception for each new identifier.

The repository has one scope, `npm-bundled-dependencies`, covering `/usr/local/lib/node_modules/npm/**`. These are dependencies bundled inside the npm CLI. They are not on the request path of a running service and are only reachable by invoking npm, which production services do not do at runtime. Before this scope existed, these findings made up the large majority of the exclusion list and were re-triaged by hand every time npm's dependency tree moved.

Scopes narrow the gate, they do not silence it. The npm scope still blocks on `critical`, and every scoped finding stays visible in the job summary and the Security tab.

Consuming services that do invoke npm at runtime should scan their own images, because this reasoning does not hold for them.

### 3. Add an exception

A last resort, for a specific vulnerability that cannot be fixed and does not belong to an existing scope:

```yaml
exceptions:
  - id: CVE-0000-00000
    aliases: [GHSA-0000-0000-0000]
    component: example-package
    reason: Why this is not exploitable in this image.
    owner: team-name
    added: 2026-01-01
    review_by: 2026-04-01
```

`aliases` should list the identifier the other scanner uses; the job summary shows both for any finding reported by each. Once `review_by` passes, the exception stops applying and the finding blocks again, so the list cannot quietly accumulate entries nobody has revisited. Exceptions that no longer match any finding are flagged as removable in the job summary.

## Running the gate locally

Install [grype](https://github.com/anchore/grype) and [trivy](https://github.com/aquasecurity/trivy), then build the production image locally as described in the [README.md](README.md):

```
docker build --no-cache --tag defra-node:latest --target=production .
```

Scan it with both tools and apply the policy:

```
grype defra-node:latest --by-cve -o json --file grype.json
trivy image --format json --output trivy.json defra-node:latest
python3 .github/scripts/scan-gate.py --grype grype.json --trivy trivy.json --image defra-node:latest
```

The script exits non-zero if anything blocks and prints the same summary the workflow produces. Note that the scanners are not given the policy directly, so running `grype --fail-on medium` on its own will report findings the policy does not treat as blocking.
