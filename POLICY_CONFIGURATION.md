# Anchore Engine policy and excluded vulnerabilities
The Anchore Engine [policy file](anchore-policy.json) is configured to report vulnerabilities that are of medium severity or higher.  Please see the official Anchore Engine documentation on [policy](https://docs.anchore.com/current/docs/engine/general/concepts/policy/) and [policy checks](https://docs.anchore.com/current/docs/overview/concepts/policy/policy_checks/) for details of the syntax.

## Known issues
The following issues have been added to the policies exclusion list

| CVE Report    |Type      | Component | Reason       | Date |
| ------------- | -------  |----------| ------------- | -----------------  |
| [CVE-2021-27290 (github)](https://github.com/advisories/GHSA-vx3p-948g-6vhq) | NPM | [ssri](https://github.com/zkat/ssri) | binary only used by npm installation for npm command line activities, i.e. npm install, and is not used by running applications | 14/04/2021 |
| [CVE-2021-27290 (NIST)](https://nvd.nist.gov/vuln/detail/CVE-2021-27290) | NPM | [ssri](https://github.com/zkat/ssri) | same issue as above detected as different reports | 14/04/2021 |
