#!/usr/bin/env python3
"""Apply vulnerability-policy.yml to Grype and Trivy results.

Both scanners run in report-only mode and their findings are evaluated here, so a
single policy governs both and the two cannot drift apart the way separate ignore
lists did. Exits non-zero if any finding blocks under the policy.

Local use:
    grype <image> -o json --file grype.json
    trivy image --format json --output trivy.json <image>
    python3 .github/scripts/scan-gate.py --grype grype.json --trivy trivy.json
"""

import argparse
import datetime
import json
import re
import sys
from dataclasses import dataclass, field

import yaml

SEVERITY_RANK = {
    "unknown": 0,
    "negligible": 1,
    "low": 2,
    "medium": 3,
    "high": 4,
    "critical": 5,
}


def rank(severity):
    return SEVERITY_RANK.get(str(severity).lower(), 0)


@dataclass
class Finding:
    scanner: str
    ident: str
    severity: str
    package: str
    version: str
    path: str
    fixed: bool
    fix_versions: str = ""
    aliases: set = field(default_factory=set)

    @property
    def ids(self):
        return {self.ident} | self.aliases


def normalise_path(path):
    if not path:
        return ""
    return path if path.startswith("/") else "/" + path


def parse_grype(path):
    with open(path) as handle:
        data = json.load(handle)

    findings = []
    for match in data.get("matches", []):
        vuln = match.get("vulnerability", {})
        artifact = match.get("artifact", {})
        locations = artifact.get("locations") or []
        fix = vuln.get("fix") or {}
        findings.append(
            Finding(
                scanner="grype",
                ident=vuln.get("id", ""),
                severity=vuln.get("severity", "unknown"),
                package=artifact.get("name", ""),
                version=artifact.get("version", ""),
                path=normalise_path(locations[0].get("path") if locations else ""),
                fixed=fix.get("state") == "fixed",
                fix_versions=",".join(fix.get("versions") or []),
                aliases={
                    related.get("id")
                    for related in match.get("relatedVulnerabilities", [])
                    if related.get("id")
                },
            )
        )
    return findings


def parse_trivy(path):
    with open(path) as handle:
        data = json.load(handle)

    findings = []
    for result in data.get("Results") or []:
        for vuln in result.get("Vulnerabilities") or []:
            fixed_version = vuln.get("FixedVersion") or ""
            findings.append(
                Finding(
                    scanner="trivy",
                    ident=vuln.get("VulnerabilityID", ""),
                    severity=vuln.get("Severity", "UNKNOWN"),
                    package=vuln.get("PkgName", ""),
                    version=vuln.get("InstalledVersion", ""),
                    path=normalise_path(vuln.get("PkgPath") or result.get("Target", "")),
                    fixed=bool(fixed_version),
                    fix_versions=fixed_version,
                )
            )
    return findings


def glob_to_regex(pattern):
    out = ""
    index = 0
    while index < len(pattern):
        if pattern.startswith("**", index):
            out += ".*"
            index += 2
        elif pattern[index] == "*":
            out += "[^/]*"
            index += 1
        elif pattern[index] == "?":
            out += "."
            index += 1
        else:
            out += re.escape(pattern[index])
            index += 1
    return re.compile("^" + out + "$")


def load_policy(path):
    with open(path) as handle:
        policy = yaml.safe_load(handle) or {}

    for scope in policy.get("scopes") or []:
        scope["_matchers"] = [glob_to_regex(p) for p in scope.get("paths", [])]
    return policy


def evaluate(findings, policy, today):
    gate = policy.get("gate") or {}
    threshold = rank(gate.get("severity", "medium"))
    only_fixed = gate.get("only_fixed", True)
    scopes = policy.get("scopes") or []
    exceptions = policy.get("exceptions") or []

    expired = []
    active_exceptions = []
    for exception in exceptions:
        review_by = exception.get("review_by")
        if review_by and _as_date(review_by) < today:
            expired.append(exception)
        else:
            active_exceptions.append(exception)

    used_exceptions = set()
    blocking, reported = [], []

    for finding in findings:
        if rank(finding.severity) < threshold:
            reported.append((finding, "below gate severity"))
            continue

        if only_fixed and not finding.fixed:
            reported.append((finding, "no upstream fix available"))
            continue

        matched_exception = _match_exception(finding, active_exceptions)
        if matched_exception:
            used_exceptions.add(matched_exception.get("id"))
            reported.append((finding, f"exception: {matched_exception.get('id')}"))
            continue

        scope = _match_scope(finding, scopes)
        if scope and rank(finding.severity) < rank(scope.get("gate_from", "critical")):
            reported.append((finding, f"scope: {scope.get('id')}"))
            continue

        blocking.append(finding)

    stale = [
        exception.get("id")
        for exception in active_exceptions
        if exception.get("id") not in used_exceptions
    ]
    return blocking, reported, expired, stale


def _as_date(value):
    if isinstance(value, datetime.date):
        return value
    return datetime.date.fromisoformat(str(value))


def _match_exception(finding, exceptions):
    for exception in exceptions:
        known = {exception.get("id")} | set(exception.get("aliases") or [])
        if finding.ids & known:
            return exception
    return None


def _match_scope(finding, scopes):
    for scope in scopes:
        if any(matcher.match(finding.path) for matcher in scope["_matchers"]):
            return scope
    return None


def dedupe(findings):
    """Merge the same vulnerability reported by both scanners under different IDs."""
    groups = []
    for finding in findings:
        for group in groups:
            same_package = group[0].package == finding.package
            if same_package and any(f.ids & finding.ids for f in group):
                group.append(finding)
                break
        else:
            groups.append([finding])

    merged = []
    for group in groups:
        worst = max(group, key=lambda f: rank(f.severity))
        identifiers = sorted({f.ident for f in group})
        merged.append(
            Finding(
                scanner=",".join(sorted({f.scanner for f in group})),
                ident=next(
                    (i for i in identifiers if i.startswith("CVE-")), identifiers[0]
                ),
                severity=worst.severity,
                package=worst.package,
                version=worst.version,
                path=worst.path,
                fixed=any(f.fixed for f in group),
                fix_versions=next((f.fix_versions for f in group if f.fix_versions), ""),
                aliases=set().union(*(f.ids for f in group)),
            )
        )

    return sorted(merged, key=lambda f: (-rank(f.severity), f.package, f.ident))


def render(blocking, reported, expired, stale, image):
    lines = [f"## Vulnerability gate: `{image}`", ""]

    if blocking:
        lines += [
            f"**{len(blocking)} finding(s) block this build.**",
            "",
            "| Severity | ID | Package | Installed | Fixed in | Scanner |",
            "| --- | --- | --- | --- | --- | --- |",
        ]
        for finding in blocking:
            lines.append(
                f"| {finding.severity} | {finding.ident} | {finding.package} | "
                f"{finding.version} | {finding.fix_versions or '-'} | {finding.scanner} |"
            )
    else:
        lines.append("**No blocking findings.**")

    lines += ["", f"<details><summary>Reported, not blocking ({len(reported)})</summary>", ""]
    lines += ["| Severity | ID | Package | Reason |", "| --- | --- | --- | --- |"]
    for finding, reason in reported:
        lines.append(
            f"| {finding.severity} | {finding.ident} | {finding.package} | {reason} |"
        )
    lines += ["", "</details>", ""]

    if expired:
        lines += ["### Expired exceptions", ""]
        for exception in expired:
            lines.append(
                f"- `{exception.get('id')}` review_by {exception.get('review_by')} "
                f"(owner: {exception.get('owner', 'unassigned')}) - no longer applied"
            )
        lines.append("")

    if stale:
        lines += [
            "### Exceptions matching nothing",
            "",
            "These can be removed from `vulnerability-policy.yml`:",
            "",
        ]
        lines += [f"- `{identifier}`" for identifier in stale]
        lines.append("")

    return "\n".join(lines)


SECURITY_SEVERITY = {
    "critical": "9.0",
    "high": "7.0",
    "medium": "5.0",
    "low": "3.0",
    "negligible": "1.0",
    "unknown": "0.0",
}


def build_sarif(blocking, reported, image):
    """Emit the policy-adjudicated view, so the Security tab matches the gate."""
    rules, results = [], []
    seen_rules = set()

    for finding, reason, level in [(f, "blocks the build", "error") for f in blocking] + [
        (f, reason, "note") for f, reason in reported
    ]:
        if finding.ident not in seen_rules:
            seen_rules.add(finding.ident)
            rules.append(
                {
                    "id": finding.ident,
                    "name": finding.ident,
                    "shortDescription": {
                        "text": f"{finding.severity} in {finding.package}"
                    },
                    "fullDescription": {
                        "text": f"{finding.ident} affects {finding.package} "
                        f"{finding.version} in {image}."
                    },
                    "help": {
                        "text": f"{finding.ident}: {finding.package} {finding.version}. "
                        f"Fixed in: {finding.fix_versions or 'no fix available'}.",
                        "markdown": f"**{finding.ident}** in `{finding.package}@"
                        f"{finding.version}`\n\nFixed in: "
                        f"{finding.fix_versions or '_no fix available_'}",
                    },
                    "properties": {
                        "security-severity": SECURITY_SEVERITY.get(
                            finding.severity.lower(), "0.0"
                        ),
                        "tags": ["security"],
                    },
                }
            )

        results.append(
            {
                "ruleId": finding.ident,
                "level": level,
                "message": {
                    "text": f"{finding.severity} {finding.ident} in {finding.package}@"
                    f"{finding.version} ({finding.path or 'os package'}) - {reason}."
                },
                "locations": [
                    {
                        "physicalLocation": {
                            "artifactLocation": {"uri": "Dockerfile"},
                            "region": {"startLine": 1},
                        }
                    }
                ],
            }
        )

    return {
        "$schema": "https://json.schemastore.org/sarif-2.1.0.json",
        "version": "2.1.0",
        "runs": [
            {
                "tool": {
                    "driver": {
                        "name": "defra-vulnerability-gate",
                        "informationUri": "https://github.com/DEFRA",
                        "rules": rules,
                    }
                },
                "results": results,
            }
        ],
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--grype", action="append", default=[])
    parser.add_argument("--trivy", action="append", default=[])
    parser.add_argument("--policy", default="vulnerability-policy.yml")
    parser.add_argument("--image", default="image")
    parser.add_argument("--summary", help="write markdown summary here")
    parser.add_argument("--json", help="write machine-readable result here")
    parser.add_argument("--sarif", help="write policy-adjudicated SARIF here")
    args = parser.parse_args()

    findings = []
    for path in args.grype:
        findings += parse_grype(path)
    for path in args.trivy:
        findings += parse_trivy(path)

    policy = load_policy(args.policy)
    blocking, reported, expired, stale = evaluate(
        findings, policy, datetime.date.today()
    )
    blocking = dedupe(blocking)

    summary = render(blocking, reported, expired, stale, args.image)
    print(summary)

    if args.summary:
        with open(args.summary, "a") as handle:
            handle.write(summary + "\n")

    if args.sarif:
        with open(args.sarif, "w") as handle:
            json.dump(build_sarif(blocking, reported, args.image), handle, indent=2)

    if args.json:
        with open(args.json, "w") as handle:
            json.dump(
                {
                    "image": args.image,
                    "blocking": [vars(f) | {"aliases": sorted(f.aliases)} for f in blocking],
                    "reported": len(reported),
                    "expired_exceptions": [e.get("id") for e in expired],
                    "stale_exceptions": stale,
                },
                handle,
                indent=2,
            )

    return 1 if blocking else 0


if __name__ == "__main__":
    sys.exit(main())
