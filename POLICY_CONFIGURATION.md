# Anchore Grype configuration and ignored vulnerabilities
Anchore Grype is configured to report vulnerabilities that are of medium severity or higher.  Please see the official Anchore Grype documentation on [policy](https://docs.anchore.com/current/docs/engine/general/concepts/policy/) and [policy checks](https://docs.anchore.com/current/docs/overview/concepts/policy/policy_checks/) for details of the syntax.

## Known issues
The following issues have been added to the policies exclusion list

| CVE Report    |Type      | Component | Reason       | Date |
| ------------- | -------  |----------| ------------- | -----------------  |
|[CVE-2023-2650](https://nvd.nist.gov/vuln/detail/CVE-2023-2650)| APK | openssl | Only exploitable by applications that use OBJ_obj2txt() directly, or use any of the OpenSSL subsystems OCSP, PKCS7/SMIME, CMS, CMP/CRMF or TS with no message size limit. This shouldn't be the case for typical applications that consume this base image. | 12/06/2023 |
|[CVE-2023-1255](https://nvd.nist.gov/vuln/detail/CVE-2023-1255)| APK | openssl | Only exploitable if an attacker can control the size and location of the ciphertext buffer being decrypted by an application using AES-XTS on 64 bit ARM. This shouldn't be exploitable by typical applications that consume this base image. | 02/06/2023 |
