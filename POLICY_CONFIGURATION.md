# Vulnerability scanning configuration

The scanning policy lives in [vulnerability-policy.yml](vulnerability-policy.yml). That file is the single source of truth: it is read directly by [scan-gate.py](.github/scripts/scan-gate.py), which decides what blocks a build, so the policy and the behaviour cannot disagree.

This page previously duplicated the exclusion list by hand and had fallen out of step with `.grype.yaml`, listing a single CVE while nine were actually excluded. Rather than maintain a second copy, read the current state from the policy file:

```bash
# what is currently excluded, and why
yq '.exceptions' vulnerability-policy.yml

# what classes of finding are scoped out of the gate
yq '.scopes' vulnerability-policy.yml
```

Every run of the gate also prints the active exceptions it applied, any that have expired, and any that no longer match a finding and can be deleted.

## Current position

Both scanners report `medium` severity and above. A finding blocks only when a fix is available and it is not covered by a scope or an exception. See [IMAGE_SCANNING.md](IMAGE_SCANNING.md) for the full rules and for guidance on which of the three remedies to reach for.

At the time of writing there are no exceptions. The recurring npm findings that previously filled the exclusion list are handled by pinning a current npm in the image and by the `npm-bundled-dependencies` scope, and unfixed Alpine findings no longer block because there is nothing the build can do about them.
