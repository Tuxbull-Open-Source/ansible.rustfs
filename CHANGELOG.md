# Changelog

All notable changes to this role are recorded here.

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
