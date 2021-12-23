# Description

Please include a summary of the changes i.e. Node.js version updates, libraries patched, or issues added to the policy file.

# Checklist:

- [ ] I have ensured the Defra version in the [JOB.env](../JOB.env) file matches that in the [Dockerfile](../Dockerfile)
- [ ] I have ensured the Node.js versions in the [image-matrix.json](../image-matrix.json) match the [Dockerfile](../Dockerfile) and the table in the [README.md](../README.md)
- [ ] I have added newly ignored vulnerabilities to the [POLICY_CONFIGURATION.md](../POLICY_CONFIGURATION.md)
- [ ] I have checked if previously identified vulnerabilities have been patched, and can be removed from the [.grype.yaml](../.grype.yaml) and [POLICY_CONFIGURATION.md](../POLICY_CONFIGURATION.md) files

