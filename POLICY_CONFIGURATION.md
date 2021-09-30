# Anchore Engine policy and excluded vulnerabilities
The Anchore Engine [policy file](anchore-policy.json) is configured to report vulnerabilities that are of medium severity or higher.  Please see the official Anchore Engine documentation on [policy](https://docs.anchore.com/current/docs/engine/general/concepts/policy/) and [policy checks](https://docs.anchore.com/current/docs/overview/concepts/policy/policy_checks/) for details of the syntax.

## Known issues
The following issues have been added to the policies exclusion list

| CVE Report    |Type      | Component | Reason       | Date |
| ------------- | -------  |----------| ------------- | -----------------  |
|[CVE-2021-3807](https://github.com/advisories/GHSA-93q8-gq69-wqmw)| NPM | [ansi-regex](https://github.com/chalk/ansi-regex) | Present in Node.js `12.22.6`, not `14.18.0`. Binary only used by `npm` command line and is not exploitable in a production image | 28/09/2021 |
