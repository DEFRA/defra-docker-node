# Image vulnerability scanning

The parent images are scanned with [Anchore Grype](https://github.com/anchore/grype) and
[Aqua Trivy](https://www.aquasec.com/products/trivy/). Two scanners are used so a finding missed by
one is still likely to be caught by the other. Both read the Node.js, Alpine and Defra versions from
[JOB.env](JOB.env) so the same image is scanned everywhere.

Scanning happens in two places:

- **On every push to a branch** the freshly built production image is scanned by
  [build-scan-push.yml](.github/workflows/build-scan-push.yml). A branch cannot be released while a
  blocking vulnerability is present.
- **Nightly** the images already published to Docker Hub are scanned by
  [nightly-scan.yml](.github/workflows/nightly-scan.yml) to catch vulnerabilities disclosed after
  release.

## What blocks a build

The gate is deliberately narrow so that automation is not stalled by things we cannot act on:

- Only vulnerabilities of **medium severity or higher** are considered.
- Only vulnerabilities that have a **fix available** can block a build. Grype runs with `only-fixed`
  and Trivy with `ignore-unfixed`, so an unpatchable finding is reported but never blocks.
- The gate only fails **branch builds**. The `main` branch always builds and publishes, so a
  vulnerability disclosed between approval and merge can never stop a release. Anything found on
  `main` is surfaced by the nightly scan instead.

This means a pull request only fails when there is a real, actionable fix to apply, which is usually
delivered automatically by the base-image or npm update PR.

## The nightly tracking issue

The nightly scan does not fail the workflow. Instead it maintains a **single** issue labelled
`security-scan`, updated in place each night, with two sections:

- **Actionable — fix available**: findings that a version bump will clear.
- **Awareness — no fix available**: findings tracked for visibility only.

When a fixable vulnerability newly appears the issue is reopened and the review team is notified. A
night with nothing to report closes the issue. An open `security-scan` issue with entries in the
actionable section is therefore the single signal that a human needs to look.

## Addressing a vulnerability

There are two ways to deal with a blocking (fixable) vulnerability:

1. **Patch it** — the preferred option. Bump the base image, npm, or the affected Alpine package so
   the fix is actually applied. The [auto-update](.github/workflows/auto-update.yml) workflow does
   this automatically for Node.js, Alpine and npm.
2. **Grant a time-boxed exception** — only when a fix exists but genuinely cannot be applied yet.

### npm

The `npm` CLI ships its own bundled libraries, which are a frequent source of findings. Rather than
suppress them, the image installs a pinned, upgraded npm (`NPM_VERSION` in [JOB.env](JOB.env) and the
[Dockerfile](Dockerfile)), and the auto-update workflow keeps that version current. This fixes the
vulnerabilities at source instead of ignoring them.

### Patching an Alpine package

If a finding is for an Alpine package with a fix in a newer package version, install that version in
the [Dockerfile](Dockerfile). The existing `apk add` line can be extended, for example to require
`libssl` 1.1.1 or greater:

```
apk add --no-cache 'libssl1.1>1.1.1'
```

The `>` acts like `>=`, and the quotes are required.

### Adding a time-boxed exception

Exceptions live next to the code and both scanners have their own file:

- Trivy: [.trivyignore.yaml](.trivyignore.yaml). Every entry must carry a `statement` and an
  `expired_at` date, so the exception automatically stops applying and the finding blocks again if it
  has not been resolved by then.
- Grype: [.grype.yaml](.grype.yaml). Grype has no native expiry, so add a `review by yyyy-mm-dd` note
  to each entry and prune the list whenever the base image is bumped.

Only add an exception for a **fixable** finding. Unfixable findings are already handled by the gate
and reported by the nightly issue, so they must not be added here.

## Running a scan locally

Build the production image with a known tag:

```
docker build --no-cache --tag defra-node:latest --target=production .
```

Then run either scanner against it, mirroring the workflow settings:

```
grype defra-node:latest --fail-on medium --only-fixed
trivy image --ignore-unfixed --severity MEDIUM,HIGH,CRITICAL --ignorefile .trivyignore.yaml defra-node:latest
```

Grype automatically picks up [.grype.yaml](.grype.yaml) from the repository root.
