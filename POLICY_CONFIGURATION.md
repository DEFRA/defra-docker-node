# Anchore Grype configuration and ignored vulnerabilities
Anchore Grype is configured to report vulnerabilities that are of medium severity or higher.  Please see the official Anchore Grype documentation on [policy](https://docs.anchore.com/current/docs/engine/general/concepts/policy/) and [policy checks](https://docs.anchore.com/current/docs/overview/concepts/policy/policy_checks/) for details of the syntax.

## Known issues
The following issues have been added to the policies exclusion list

| CVE Report    |Type      | Component | Reason       | Date |
| ------------- | -------  |----------| ------------- | -----------------  |
|[CVE-2021-27498](https://nvd.nist.gov/vuln/detail/CVE-2021-27498), [CVE-2021-27500](https://nvd.nist.gov/vuln/detail/CVE-2021-27500), [CVE-2021-27478](https://nvd.nist.gov/vuln/detail/CVE-2021-27478), [CVE-2021-27482](https://nvd.nist.gov/vuln/detail/CVE-2021-27482)| NPM | [opener](https://github.com/domenic/opener) | Binary only used by `npm` command line and is not exploitable in a production image | Updated 31/05/2022 |
