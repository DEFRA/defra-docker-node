# Anchore Engine policy and excluded vulnerabilities
The Anchore Engine [policy file](anchore-policy.json) is configured to report vulnerabilities that are of medium severity or higher.  Please see the official Anchore Engine documentation on [policy](https://docs.anchore.com/current/docs/engine/general/concepts/policy/) and [policy checks](https://docs.anchore.com/current/docs/overview/concepts/policy/policy_checks/) for details of the syntax.

## Known issues
The following issues have been added to the policies exclusion list

| CVE Report    |Type      | Component | Reason       | Date |
| ------------- | -------  |----------| ------------- | -----------------  |
| [CVE-2020-7788](https://nvd.nist.gov/vuln/detail/CVE-2020-7788) | NPM | [ini](https://github.com/npm/ini) | binary only used by npm installation for npm command line activities, i.e. npm install, and is not used by running applications | 04/01/2020 |
| [CVE-2020-7754](https://nvd.nist.gov/vuln/detail/CVE-2020-7754) | NPM      | [npm-user-validate](https://github.com/npm/npm-user-validate) | binary only used during npm user authentication, i.e. pushing a package to npmjs.com. No npm commands or authentication is required in production containers | 2/11/2020|

