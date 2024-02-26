# Anchore Grype configuration and ignored vulnerabilities
Anchore Grype is configured to report vulnerabilities that are of medium severity or higher.  Please see the official Anchore Grype documentation on [policy](https://docs.anchore.com/current/docs/engine/general/concepts/policy/) and [policy checks](https://docs.anchore.com/current/docs/overview/concepts/policy/policy_checks/) for details of the syntax.

## Known issues
The following issues have been added to the policies exclusion list

| CVE Report    |Type      | Component | Reason       | Date |
| ------------- | -------  |----------| ------------- | -----------------  |
|[GHSA-c2qf-rxjj-qqgw](https://github.com/advisories/GHSA-c2qf-rxjj-qqgw)| NPM | [node-semver]https://github.com/npm/node-semver) | Required only to build for Node.js 16, the official docker image for Node.js 16 which is no longer maintained. | 13/11/2023 |
|[GHSA-78xj-cgh5-2h22](https://github.com/advisories/GHSA-78xj-cgh5-2h22)| NPM | [ip]https://github.com/indutny/ip) | Fix available in version `2.0.1` of `ip`, but not yet incorporated into `npm`. | 26/0/2024 |
