# Vulnerability scanning configuration and ignored vulnerabilities
[Anchore Grype](https://github.com/anchore/grype/) and [Aqua Trivy](https://www.aquasec.com/products/trivy/) are configured to report vulnerabilities that are of medium severity or higher.  

## Known issues
The following issues have been added to the policies exclusion list

| CVE Report    |Type      | Component | Date       | Reason        |
| ------------- | -------  | --------- | ---------- | ------------- |
|CVE-2024-21538 | ReDos    | npm       | 2025-04-30 | npm patched, waiting for new image release from Node |
