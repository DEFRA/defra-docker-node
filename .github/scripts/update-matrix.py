#!/usr/bin/env python3
"""Refresh image-matrix.json and the files that must agree with it.

Tracks the Node patch version, the npm version, and the base image digest. The digest
is what makes a rebuild of an unchanged commit reproducible, so it is refreshed even
when the version strings have not moved.

Writes `updated=true|false`, `title` and `body` to $GITHUB_OUTPUT when running in Actions.
"""

import json
import os
import re
import subprocess
import sys
import urllib.request

MATRIX = "image-matrix.json"
NODE_INDEX = "https://nodejs.org/dist/index.json"
NPM_REGISTRY = "https://registry.npmjs.org/npm/latest"


def fetch_json(url):
    with urllib.request.urlopen(url, timeout=30) as response:
        return json.load(response)


def latest_node_versions():
    versions = {}
    for release in fetch_json(NODE_INDEX):
        version = release["version"].lstrip("v")
        major = int(version.split(".")[0])
        # index.json is newest first, so the first entry per major wins
        versions.setdefault(major, version)
    return versions


def resolve_digest(reference):
    result = subprocess.run(
        ["docker", "buildx", "imagetools", "inspect", reference,
         "--format", "{{.Manifest.Digest}}"],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        return None
    return result.stdout.strip() or None


def bump_patch(version):
    major, minor, patch = version.split(".")
    return f"{major}.{minor}.{int(patch) + 1}"


def replace_line(path, pattern, replacement):
    with open(path) as handle:
        content = handle.read()
    updated = re.sub(pattern, replacement, content, count=1, flags=re.MULTILINE)
    if updated != content:
        with open(path, "w") as handle:
            handle.write(updated)


def main():
    with open(MATRIX) as handle:
        matrix = json.load(handle)

    latest_node = latest_node_versions()
    latest_npm = fetch_json(NPM_REGISTRY)["version"]

    changes = []
    for entry in matrix:
        major = int(entry["nodeVersion"].split(".")[0])
        candidate = latest_node.get(major, entry["nodeVersion"])
        reference = f"node:{candidate}-alpine{entry['alpineVersion']}"

        digest = resolve_digest(reference)
        if digest is None:
            print(f"{reference} is not published yet; leaving Node {major} unchanged")
            candidate = entry["nodeVersion"]
            reference = f"node:{candidate}-alpine{entry['alpineVersion']}"
            digest = resolve_digest(reference) or entry.get("baseDigest")

        if candidate != entry["nodeVersion"]:
            changes.append(f"- Node {major}: {entry['nodeVersion']} -> {candidate}")
            entry["nodeVersion"] = candidate

        if latest_npm != entry.get("npmVersion"):
            changes.append(
                f"- Node {major} npm: {entry.get('npmVersion', 'unset')} -> {latest_npm}"
            )
            entry["npmVersion"] = latest_npm

        if digest and digest != entry.get("baseDigest"):
            changes.append(f"- Node {major} base digest: {reference} -> {digest}")
            entry["baseDigest"] = digest

    if not changes:
        emit(False, "", "")
        print("No updates required.")
        return 0

    with open(MATRIX, "w") as handle:
        json.dump(matrix, handle, indent=4)
        handle.write("\n")

    with open("JOB.env") as handle:
        job_env = handle.read()
    current_version = re.search(r"DEFRA_VERSION=([\d.]+)", job_env).group(1)
    new_version = bump_patch(current_version)
    replace_line("JOB.env", r"^DEFRA_VERSION=.*$", f"DEFRA_VERSION={new_version}")

    default = next(
        (e for e in matrix if "latest" in (e.get("tags") or [])), matrix[-1]
    )
    replace_line(
        "Dockerfile", r"^ARG DEFRA_VERSION=.*$", f"ARG DEFRA_VERSION={new_version}"
    )
    replace_line(
        "Dockerfile",
        r"^ARG BASE_VERSION=.*$",
        f"ARG BASE_VERSION={default['nodeVersion']}-alpine{default['alpineVersion']}",
    )
    replace_line(
        "Dockerfile", r"^ARG NPM_VERSION=.*$", f"ARG NPM_VERSION={default['npmVersion']}"
    )
    replace_line(
        "Dockerfile", r"^ARG BASE_DIGEST=.*$", f"ARG BASE_DIGEST={default['baseDigest']}"
    )

    update_readme(matrix)

    versions = ",".join(str(int(e["nodeVersion"].split(".")[0])) for e in matrix)
    emit(True, f"Update Node.js base image: {versions}", "\n".join(changes))
    print("\n".join(changes))
    return 0


def update_readme(matrix):
    with open("README.md") as handle:
        lines = handle.readlines()

    by_major = {int(e["nodeVersion"].split(".")[0]): e for e in matrix}
    for index, line in enumerate(lines):
        match = re.match(r"^\|\s*(\d+)\.\d+\.\d+\s*\|\s*\S+\s*\|\s*$", line)
        if not match:
            continue
        entry = by_major.get(int(match.group(1)))
        if entry:
            parent = f"{entry['nodeVersion']}-alpine{entry['alpineVersion']}"
            lines[index] = f"| {entry['nodeVersion']:<13} | {parent:<18} |\n"

    with open("README.md", "w") as handle:
        handle.writelines(lines)


def emit(updated, title, body):
    output = os.environ.get("GITHUB_OUTPUT")
    if not output:
        return
    with open(output, "a") as handle:
        handle.write(f"updated={str(updated).lower()}\n")
        handle.write(f"title={title}\n")
        handle.write("body<<POLICY_EOF\n")
        handle.write(body + "\n")
        handle.write("POLICY_EOF\n")


if __name__ == "__main__":
    sys.exit(main())
