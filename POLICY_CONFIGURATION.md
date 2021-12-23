# Anchore Grype configuration and ignored vulnerabilities
Anchore Grype is configured to report vulnerabilities that are of medium severity or higher.  Please see the official Anchore Grype documentation on [policy](https://docs.anchore.com/current/docs/engine/general/concepts/policy/) and [policy checks](https://docs.anchore.com/current/docs/overview/concepts/policy/policy_checks/) for details of the syntax.

## Known issues
The following issues have been added to the policies exclusion list

| CVE Report    |Type      | Component | Reason       | Date |
| ------------- | -------  |----------| ------------- | -----------------  |
|[CVE-2021-3807](https://nvd.nist.gov/vuln/detail/CVE-2021-3807), [GHSA-93q8-gq69-wqmw](https://github.com/advisories/GHSA-93q8-gq69-wqmw)| NPM | [ansi-regex](https://github.com/chalk/ansi-regex) | Binary only used by `npm` command line and is not exploitable in a production image | Updated 23/12/2021 |
|[CVE-2021-43616](https://nvd.nist.gov/vuln/detail/CVE-2021-43616)| NPM | [npm](https://github.com/npm/cli) | Binary is the `npm` command line and is not exploitable in a production image | 23/12/2021 |
|[CVE-2020-8116](https://nvd.nist.gov/vuln/detail/CVE-2020-8116)| NPM | [dot-prop](https://github.com/sindresorhus/dot-prop) | Binary only used by `npm` command line and is not exploitable in a production image |  23/12/2021 |
|[CVE-2015-0903](https://nvd.nist.gov/vuln/detail/CVE-2015-0903)| NPM | [editor](https://github.com/substack/node-editor) | Binary only used by `npm` command line when launching [Maruo Editor](https://hide-maruo-co-jp.translate.goog/software/hidemaru.html?_x_tr_sl=ja&_x_tr_tl=en&_x_tr_hl=en&_x_tr_pto=sc) and is not exploitable in a production image |  23/12/2021 |
|[CVE-2021-3918](https://nvd.nist.gov/vuln/detail/CVE-2021-3918), [GHSA-896r-f27r-55mw](https://github.com/advisories/GHSA-896r-f27r-55mw)| NPM | [json-schema](https://github.com/kriszyp/json-schema) | Binary only used by `npm` command line and is not exploitable in a production image |  Updated 23/12/2021 |
|[CVE-2014-1936](https://nvd.nist.gov/vuln/detail/CVE-2014-1936), [CVE-2020-17753](https://nvd.nist.gov/vuln/detail/CVE-2020-17753)| NPM | [rc](https://github.com/dominictarr/rc) | False positive, the exploit is for the rc system package called by the npm package, which [does not exist in Alpine 3.14](https://pkgs.alpinelinux.org/packages?name=rc&branch=v3.14) |  23/12/2021 |
|[CVE-2021-29940](https://nvd.nist.gov/vuln/detail/CVE-2021-29940)| OS | [through](https://github.com/gretchenfrage/through) | Issue is in a Rust 'cargo' package reported in [February 2021](https://github.com/gretchenfrage/through/issues/1) and has yet to be addressed. Would require compilation of a Rust function by a library so low risk for a production application | 23/12/2021 |
