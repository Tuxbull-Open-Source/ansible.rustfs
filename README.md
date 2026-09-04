# RustFS Ansible Role

Installs a pinned RustFS server and the official `rc` client, manages a systemd
service, provisions buckets and users idempotently, and publishes S3 and Console
through Nginx TLS SNI virtual hosts by default.

## Security model

RustFS always binds to the configured local **plain HTTP** addresses. TLS is
never configured in RustFS by this role. When enabled, Nginx terminates TLS on
one HTTPS port with separate SNI names for S3 and Console. The S3 proxy keeps
the original `Host`, disables request buffering, and uses HTTP/1.1; Console
proxying includes WebSocket upgrade headers.

Credentials must be supplied from Vault or another secret store. They are
written only to a root-owned mode `0600` environment file. Tasks that handle
credentials use `no_log: true`.

## Example

```yaml
- hosts: rustfs
  become: true
  roles:
    - role: rustfs
      rustfs_root_user: rustfsadmin
      rustfs_root_password: "{{ vault_rustfs_root_password }}"
      rustfs_checksum: "<sha256 from RustFS release SHA256SUMS>"
      rustfs_buckets:
        - {name: backups}
      rustfs_users:
        - access_key: backup-writer
          secret_key: "{{ vault_backup_secret }}"
```

Pin both `rustfs_version` and the SHA-256 checksum in production. `rustfs_users`
creates additional access identities with `rc admin user add`; policies can be
applied separately using the RustFS Admin API/`rc` for the installed release.

The proxy is enabled by default with a generated self-signed certificate. A
self-signed certificate has these attributes:

- RSA private key, 4096 bits, stored root-owned with mode `0600`.
- SHA-256 signed X.509 certificate.
- Valid for `rustfs_nginx_self_signed_days` days (365 by default).
- Common Name set to `rustfs_nginx_s3_server_name`.
- Subject Alternative Names containing both the S3 and Console hostnames.
- Stored by default at `/etc/pki/tls/certs/rustfs-selfsigned.crt` and
  `/etc/pki/tls/private/rustfs-selfsigned.key`.

Browsers and S3 clients will not trust this certificate automatically. It is
appropriate for internal testing when the CA/certificate is explicitly trusted,
but use a certificate issued by your organization or a public CA for normal
client access.

You can use your own certificate in either of two ways. For files already on the
managed host, set `rustfs_nginx_ssl_mode: existing_target` and point the path
variables at them. To copy files from the Ansible controller, use
`rustfs_nginx_ssl_mode: controller` and set the `*_source` variables:

```yaml
rustfs_nginx_ssl_mode: controller
rustfs_nginx_ssl_certificate: /etc/pki/tls/certs/rustfs-fullchain.pem
rustfs_nginx_ssl_certificate_key: /etc/pki/tls/private/rustfs.key
rustfs_nginx_ssl_certificate_source: files/rustfs-fullchain.pem
rustfs_nginx_ssl_certificate_key_source: files/rustfs.key
```

The certificate must cover both SNI names, either directly or through SANs. The
private key must never be committed to the repository; use Vault or another
approved secret/file distribution mechanism. To disable the proxy entirely,
set `rustfs_nginx_enabled: false`.

The optional proxy requires certificate paths already present on the target or
controller sources:

```yaml
rustfs_nginx_enabled: true
rustfs_nginx_s3_server_name: s3.example.net
rustfs_nginx_console_server_name: console.example.net
rustfs_nginx_ssl_certificate: /etc/pki/tls/certs/rustfs.pem
rustfs_nginx_ssl_certificate_key: /etc/pki/tls/private/rustfs.key
```

## Verification

```bash
ansible-playbook -i tests/inventory.ini tests/test.yml --syntax-check
ansible-lint .                 # if installed
```

Live Rocky 10 coverage is provided by `lab/README.md` and is intentionally
separate from the role; generated inventory, SSH config, credentials, and
provider state stay outside this tree.

## Sources and design provenance

* [RustFS Docker installation](https://docs.rustfs.com/en/installation/container/docker)
* [RustFS S3 protocol](https://docs.rustfs.com/en/administration/protocols/s3)
* [RustFS rc client](https://docs.rustfs.com/en/operations/rc)
* [RustFS releases](https://github.com/rustfs/rustfs/releases)
* [Reference public role](https://github.com/ricsanfre/ansible-role-rustfs) (MIT):
  release asset naming, `rc` installation, and role layout were reviewed;
  implementation here was written independently and TLS behavior deliberately
  differs to enforce the local-HTTP/Nginx-only requirement.

The requested Bitbull-Ideas `ansible.template` repository was checked via the
GitHub API and returned 404. No files were copied from it.
