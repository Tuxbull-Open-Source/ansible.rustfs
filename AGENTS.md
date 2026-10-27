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

### Release lifecycle and version policy

Use `vMAJOR.MINOR.PATCH` tags (three numeric components). Increment PATCH for
compatible fixes and documentation-only releases, MINOR for compatible new
features, and MAJOR for incompatible changes. Treat pre-1.0 compatibility
changes explicitly in the release notes. Role versions are independent of the
RustFS server and rc client versions in defaults/main.yml.

Follow this order; a successful import alone is not a complete release:

1. Inspect remote main, tags, GitHub Releases, and Galaxy versions. If a local
   tag differs from its remote counterpart, stop automatic tag synchronization
   and report both commits. Never force-fetch or silently rewrite a release tag.
2. Choose an unused version. Prepare a release PR containing its CHANGELOG.md
   entry and all intended code/documentation changes. Describe only changes
   actually included and tests actually performed. Keep release history out
   of README.md. While the PR is open, label the entry as pending publication.
3. Validate the changed files and relevant tests. Obtain maintainer review and
   merge; do not self-merge. Fetch main without overwriting tags and verify the
   approved changes and exact version entry are in the commit to be released.
4. Create an annotated tag on that verified main commit, then push only that
   tag. Read back both the remote tag object and its peeled commit. Do not tag
   an unmerged feature branch or move an existing tag to include later fixes.
5. Create a published GitHub Release for the exact tag, with release notes
   derived from its CHANGELOG.md entry. Set draft=false and prerelease=false
   for a stable release. Verify the release URL, tag, and publication state.
   A Git tag, GitHub Release, changelog entry, and Galaxy version are separate
   artifacts; none substitutes for the others.
6. Run the re-import procedure below, repair the download source if needed,
   and require Galaxy to expose the new tag with the exact release commit.
   Importing main can discover tags, but does not create a tag or a release.
7. Test the unpinned Galaxy FQN, the exact version-pinned Galaxy FQN, and the
   organization Git URL in fresh directories. Verify installed metadata and
   version; check the released changelog is included. Compare the pinned
   installation with the same Git tag, not a potentially newer main branch.
8. Report the release/tag URL, commit, changelog entry, Galaxy task/version,
   installation results, and cleanup. If any gate is blocked, report a pending
   release rather than claiming publication. Do not automatically bump another
   version after publication; choose the next version with the next change.

Published tags are immutable. Correct post-release omissions in a new patch
release. Preserve historical tags and document discrepancies rather than
rewriting consumers' existing version references.

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

### Manual import for maintainers

The following Bash recipe requires `curl`, `jq`, Python 3, and `ansible-galaxy`. Run it
from a trusted terminal with shell tracing disabled. Obtain your token after
logging in at <https://galaxy.ansible.com/ui/token/>. This updates the existing
Galaxy role from main; it does not create a tag or GitHub Release.

Use a subshell so the token and temporary files are cleaned up on exit. The
header is stored in a private temporary file rather than in curl's process
arguments. Do not paste tokens into commands, chat, or version control.

```bash
(
  set -eu
  set +x
  umask 077
  WORK="$(mktemp -d)"
  trap 'rm -rf "$WORK"; unset GALAXY_TOKEN' EXIT
  read -rsp 'Galaxy token: ' GALAXY_TOKEN
  printf '\n'
  printf 'Authorization: Token %s\n' "$GALAXY_TOKEN" > "$WORK/auth"
  unset GALAXY_TOKEN
  API='https://galaxy.ansible.com/api/v1'

  # Resolve the existing role; do not blindly reuse an old ID.
  curl -fsS "$API/roles/?namespace=tuxbull&name=rustfs" > "$WORK/role.json"
  ROLE_ID="$(jq -er '
    select(.count == 1) | .results[0] |
    select(.name == "rustfs" and .summary_fields.namespace.name == "tuxbull") |
    .id' "$WORK/role.json")"

  # Submit an asynchronous import using the organization as the clone source.
  curl -fsS -X POST "$API/imports/" \
    -H @"$WORK/auth" -H 'Content-Type: application/json' \
    --data '{
      "github_user":"tuxbull",
      "github_repo":"ansible.rustfs",
      "github_reference":"main",
      "alternate_clone_url":"https://github.com/Tuxbull-Open-Source/ansible.rustfs",
      "alternate_namespace_name":"tuxbull",
      "alternate_role_name":"rustfs"
    }' > "$WORK/import.json"
  # IDs exceed IEEE-754 precision; use Python integers, not jq arithmetic.
  IMPORT_ID="$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["results"][0]["id"])' "$WORK/import.json")"
  printf 'Import task: %s\n' "$IMPORT_ID"

  # Wait at most approximately five minutes, excluding HTTP request time.
  STATE='UNKNOWN'
  for attempt in $(seq 1 60); do
    curl -fsS --max-time 60 -H @"$WORK/auth" \
      "$API/imports/$IMPORT_ID/" > "$WORK/task.json"
    STATE="$(jq -er '.results[0].state' "$WORK/task.json")"
    case "$STATE" in
      SUCCESS) break ;;
      FAILED|CANCELED) break ;;
    esac
    sleep 5
  done
  if [ "$STATE" != SUCCESS ]; then
    printf 'Import did not succeed: %s\n' "$STATE" >&2
    jq '.results[0].summary_fields.task_messages' "$WORK/task.json"
    exit 1
  fi

  # Import success alone is insufficient: repair the CLI download owner.
  curl -fsS -X PUT "$API/roles/$ROLE_ID/" \
    -H @"$WORK/auth" -H 'Content-Type: application/json' \
    --data '{"github_user":"Tuxbull-Open-Source"}'
  curl -fsS "$API/roles/$ROLE_ID/" > "$WORK/verified.json"
  jq -e '
    .name == "rustfs" and .summary_fields.namespace.name == "tuxbull" and
    .github_user == "Tuxbull-Open-Source" and
    .github_repo == "ansible.rustfs" and .github_branch == "main"
  ' "$WORK/verified.json"
  jq '{name, github_user, github_repo, github_branch, commit}' "$WORK/verified.json"
  curl -fsS "$API/roles/$ROLE_ID/versions/" | jq '.results'

  # These installs must really succeed; temporary files are removed on exit.
  ansible-galaxy role install -p "$WORK/galaxy" tuxbull.rustfs
  ansible-galaxy role install -p "$WORK/git" \
    'git+https://github.com/Tuxbull-Open-Source/ansible.rustfs.git,main'
)
```

For a release, additionally perform the pinned installation check below.
For documentation-only updates without a new release, the unpinned Galaxy
installation still selects the latest existing release; the direct Git command
selects current main. Importing main does not update an immutable tag archive.
Do not expect those two installations to include identical documentation.
Record documentation-only changes under `Unreleased` in CHANGELOG.md; do not
create a release when the maintainer explicitly requests documentation only.

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
