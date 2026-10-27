# Repository instructions

## Scope

This repository contains the reusable `tuxbull.rustfs` Ansible role. Keep the
role focused on installation, configuration, upgrades, provisioning, service
management, and optional Nginx TLS termination. Do not add repository-migration
notes, provider-specific setup instructions, credentials, generated state, or
live-target inventory to the role documentation.

## Local validation

The dispatcher expects the installed role directory basename to be `rustfs`.
Use the test helper with a temporary directory outside the repository:

```bash
HARNESS_DIR="$(mktemp -d)"
trap 'rm -rf "$HARNESS_DIR"' EXIT
python3 tests/scripts/prepare_harness.py "$HARNESS_DIR/roles/rustfs"
ANSIBLE_ROLES_PATH="$HARNESS_DIR/roles" \
  ansible-playbook -i tests/inventory.ini tests/test.yml --syntax-check
ANSIBLE_ROLES_PATH="$HARNESS_DIR/roles" \
  ansible-playbook -i tests/inventory.ini tests/test.yml --check
```

Also parse YAML, run `git diff --check`, and verify that shared tasks contain no
OS-specific selectors or package-manager logic. Do not commit the temporary
harness directory.

## Testing status

Run the following static checks from the repository root:

```bash
HARNESS_DIR="$(mktemp -d)"
trap 'rm -rf "$HARNESS_DIR"' EXIT
python3 tests/scripts/prepare_harness.py "$HARNESS_DIR/roles/rustfs"
python3 - <<'PY'
from pathlib import Path
import yaml
files = list(Path('.').rglob('*.yml')) + list(Path('.').rglob('*.yaml'))
for path in files:
    yaml.safe_load(path.read_text())
print(f'parsed {len(files)} YAML files')
PY
ANSIBLE_ROLES_PATH="$HARNESS_DIR/roles" ansible-playbook -i tests/inventory.ini tests/test.yml --syntax-check
ANSIBLE_ROLES_PATH="$HARNESS_DIR/roles" ansible-playbook -i tests/inventory.ini tests/test.yml --check
git diff --check
! grep -REn 'ansible_(os_family|distribution)|\b(Debian|RedHat|Rocky|AlmaLinux|apt|dnf|yum)\b' tasks/shared/
```

These checks cover YAML parsing, dispatcher selection for Debian and
RHEL-family facts, syntax, check mode, and the shared-task OS-neutrality rule.
They do not prove installation or live behavior.

## Live verification

Live testing is optional and is not tied to Hetzner or any other provider. Use
an approved disposable or existing test target that matches the supported OS
matrix. Before testing, confirm the target, access method, cost or impact,
cleanup plan, and required authorization.

Keep temporary inventories, SSH configuration and keys, credentials, provider
state, logs, and generated variables outside this repository. Do not put real
secrets in playbooks or documentation.

A live verification should independently check:

- OS facts and Ansible connectivity.
- Installation and package prerequisites.
- Enabled/running RustFS and optional Nginx services.
- Rendered configuration and service validation.
- RustFS health/readiness and functional bucket/user provisioning.
- Upgrade/convergence behavior.
- A second same-version run with no unexpected changes.
- Cleanup of every disposable target and credential created for the test.

Record durable change history in `CHANGELOG.md`; keep target-specific logs and
inventories outside Git.

## Dependencies

Controller-side Ansible collections are declared in
`collections/requirements.yml`. Role dependencies in `meta/main.yml` describe
other Ansible roles and are currently empty. Install collections from the
manifest rather than editing downloaded collection contents.

## Galaxy re-import and publication

Only publish with maintainer authorization. Keep these identities separate:

- GitHub source: `Tuxbull-Open-Source/ansible.rustfs`
- Galaxy namespace and operator: `tuxbull`
- Galaxy role: `tuxbull.rustfs`
- Role metadata: `namespace: tuxbull`, `role_name: rustfs`

Use the reviewed remote `main` branch. Versioned publication requires a
three-component SemVer tag, for example `v0.2.0`, on the intended commit.
Two-component tags such as `v0.11` are skipped. Never move or delete existing
tags without authorization. A changelog entry does not publish a version.

### Re-import procedure

Provide `GALAXY_TOKEN` through an approved secret store/environment. Never
print it, commit it, or enable shell tracing. Use the Galaxy REST API:

1. GET `https://galaxy.ansible.com/api/v1/roles/?namespace=tuxbull&name=rustfs`.
   Require exactly one matching role; verify its namespace and name and retain
   its ID. Do not assume an old role ID still identifies the correct role.
2. POST `https://galaxy.ansible.com/api/v1/imports/` with the following JSON,
   `Content-Type: application/json`, and an `Authorization` header consisting
   of `Token ` followed by the environment token:

   ```json
   {
     "github_user": "tuxbull",
     "github_repo": "ansible.rustfs",
     "github_reference": "main",
     "alternate_clone_url": "https://github.com/Tuxbull-Open-Source/ansible.rustfs",
     "alternate_namespace_name": "tuxbull",
     "alternate_role_name": "rustfs"
   }
   ```

3. Read the task ID from `results[0].id`. Poll
   `GET /api/v1/imports/<task-id>/` until `results[0].state` is `SUCCESS` or a
   terminal failure. Use a bounded timeout; HTTP 200 on submission is not
   completion. Inspect task messages on failure, rather than blindly retrying.
4. GET `/api/v1/roles/<role-id>/` and verify the namespace, role name,
   repository, branch, and imported commit. Compare the commit with
   `git ls-remote origin refs/heads/main`.
5. If `github_user` is not `Tuxbull-Open-Source`, correct only that field using
   the supported `PUT /api/v1/roles/<role-id>/` endpoint:

   ```json
   {"github_user": "Tuxbull-Open-Source"}
   ```

6. Read the exact role back. Require `github_user: Tuxbull-Open-Source`,
   `github_repo: ansible.rustfs`, and namespace/name `tuxbull.rustfs`.
7. GET `/api/v1/roles/<role-id>/versions/`. For a release, require the exact
   intended tag and commit, and verify its organization-based download URL.

**Important:** `alternate_clone_url` controls cloning during import, but the
importer can leave `github_user: tuxbull` in the download metadata. The Galaxy
CLI then builds a personal-repository URL that returns HTTP 404 despite an
import status of `SUCCESS`. Recheck and repair the source owner after every
import. This does not require deleting the role or changing namespace/provider
ownership. A direct organization-owner import returned HTTP 500 in this setup;
that error alone does not prove missing OAuth permissions.

### Required installation verification

Run actual installations into separate fresh temporary directories:

```bash
(
  set -eu
  CHECK_DIR="$(mktemp -d)"
  trap 'rm -rf "$CHECK_DIR"' EXIT
  ansible-galaxy role install -p "$CHECK_DIR/galaxy" tuxbull.rustfs
  ansible-galaxy role install -p "$CHECK_DIR/git" \
    'git+https://github.com/Tuxbull-Open-Source/ansible.rustfs.git,main'
  # Set to the exact tag being published; this is an example, not latest.
  RELEASE_TAG=v0.2.0
  ansible-galaxy role install -p "$CHECK_DIR/pinned" "tuxbull.rustfs,$RELEASE_TAG"
)
```

Before removing the temporary directories, inspect installed `meta/main.yml`
and `meta/.galaxy_install_info` and verify the requested version. The FQN
installs under `tuxbull.rustfs`; the direct Git command installs under
`ansible.rustfs`. An unpinned Galaxy install can select the latest release,
whereas direct Git uses `main`. Compare source files only when both resolve to
the same revision, excluding `.galaxy_install_info`.

Report success only after import completion, metadata read-back, version
lookup, and real installation tests. Installation proves distribution, not
live RustFS behavior. Keep this workflow in AGENTS.md, not in README.md.

## Documentation

`README.md` documents role usage only. `CHANGELOG.md` contains release and
change history. Keep public documentation generic and free of private
infrastructure details.
