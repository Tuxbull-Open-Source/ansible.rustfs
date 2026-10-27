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

## Documentation

`README.md` documents role usage only. `CHANGELOG.md` contains release and
change history. Keep public documentation generic and free of private
infrastructure details.
