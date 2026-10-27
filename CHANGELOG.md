# Changelog

All notable changes to this role are recorded here.

## Unreleased

- Add a human-readable manual Galaxy import recipe with protected token input,
  task polling, download-source correction, and actual installation checks.
- Explain documentation-only imports without creating a new release.
- Restart RustFS before client provisioning when the rendered service environment
  or unit changes, so bucket/user reconciliation uses the newly configured root
  credentials.

## v0.2.1

- Document the ordered release workflow: changelog, review, immutable SemVer
  tag, GitHub Release, Galaxy import, and installation verification.
- Include the Galaxy re-import and source-owner repair instructions in the
  next release archive.
- Include the retrospective v0.2.0 changelog entry in the next release archive.
- No RustFS runtime behavior changes.

## v0.2.0

- Adopt three-component semantic versioning for Galaxy publication.
- Publish the existing role and documentation from commit
  `30c9ba23d3cb6c07056e281c587f47534f35367a` without runtime changes.
- Verify both unpinned and version-pinned Galaxy installation of `tuxbull.rustfs`.

This entry was added after publication. The immutable `v0.2.0` tag predates
this changelog correction. Earlier two-component tags are retained below as
historical labels, not as Galaxy semantic versions.

## v0.11
- Documentation cleanup
- Prepare Releases

## v0.10

- Initial RustFS Ansible role release.
- Installs the RustFS server and official `rc` client.
- Manages the systemd service, buckets, and access users.
- Supports optional Nginx TLS termination with separate S3 and Console SNI
  virtual hosts.
- Tested on Rocky Linux 10 with installation, upgrade, bucket/user
  provisioning, HTTPS endpoints, and idempotent convergence.
