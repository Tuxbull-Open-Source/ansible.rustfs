# RustFS Ansible Role

Installs a pinned RustFS server and the official `rc` client, manages a systemd
service, provisions buckets and users idempotently, and publishes S3 and Console
through Nginx TLS SNI virtual hosts by default.

Galaxy role name: `tuxbull.rustfs`

## Scope and security model

RustFS always binds to the configured local **plain HTTP** addresses. TLS is
never configured in RustFS by this role. Nginx terminates TLS on one HTTPS port
with separate SNI names for S3 and Console. The S3 proxy preserves the original
`Host` and request path, disables request buffering, and uses HTTP/1.1; Console
proxying includes WebSocket upgrade headers.

Credentials must be supplied from Ansible Vault or another secret store. They
are written only to a root-owned mode `0600` environment file. Tasks handling
credentials use `no_log: true`. Do not commit private keys, secret variables,
rendered environment files, or real infrastructure values.

## Quick-start example

```yaml
- hosts: rustfs
  become: true
  vars:
    rustfs_version: "1.0.0-rc.5"
    rustfs_checksum: "<64-hex-sha256-from-the-release>"
    rustfs_root_user: rustfsadmin
    rustfs_root_password: "{{ vault_rustfs_root_password }}"
    rustfs_nginx_s3_server_name: s3.example.com
    rustfs_nginx_console_server_name: console.example.com
    rustfs_buckets:
      - name: backups
      - name: artifacts
    rustfs_users:
      - access_key: backup-writer
        secret_key: "{{ vault_backup_writer_secret }}"
  roles:
    - tuxbull.rustfs
```

Pin both server/client versions and SHA-256 checksums in production. The role
ensures listed buckets and users exist; it does not delete objects, buckets, or
users when they are removed from variables.

## Complete variable reference

All role defaults are also documented inline in [`defaults/main.yml`](defaults/main.yml).
The following table is the authoritative user-facing summary. Values shown are
the defaults unless stated otherwise.

### RustFS release and client

| Variable | Type | Default | Description |
|---|---|---|---|
| `rustfs_version` | string | `1.0.0-rc.5` | Server release version; accepts the release version without `v`. |
| `rustfs_arch` | string | `x86_64` | Release architecture. |
| `rustfs_libc` | string | `musl` | Release libc variant; `musl` or `gnu` where published. |
| `rustfs_download_base_url` | string/URL | RustFS releases URL | Base URL for server archives. |
| `rustfs_checksum` | string | empty | Optional 64-hex SHA-256 checksum for the server archive; recommended. |
| `rustfs_manage_packages` | boolean | `true` | Install OS package prerequisites. |
| `rustfs_manage_install` | boolean | `true` | Download and install RustFS binaries. |
| `rustfs_manage_configuration` | boolean | `true` | Manage the account, directories, environment, and unit. |
| `rustfs_manage_service` | boolean | `true` | Enable, start, and health-check RustFS. |
| `rustfs_manage_provisioning` | boolean | `true` | Reconcile declared buckets and users when the client is installed. |
| `rustfs_manage_nginx` | boolean | `true` | Manage Nginx packages, certificates, configuration, and service. |
| `rustfs_install_client` | boolean | `true` | Install the official `rc` client. Required for bucket/user provisioning. |
| `rustfs_cli_version` | string | `v0.1.32` | `rc` client release tag. |
| `rustfs_cli_download_base_url` | string/URL | RustFS CLI releases URL | Base URL for client archives. |
| `rustfs_cli_checksum` | string | empty | Optional SHA-256 checksum for the client archive; recommended. |

### Service account, paths, and listeners

| Variable | Type | Default | Description |
|---|---|---|---|
| `rustfs_user` | string | `rustfs` | Unprivileged system service account. |
| `rustfs_group` | string | `rustfs` | Primary group for the service account. |
| `rustfs_uid` | integer | `10001` | Numeric UID; change if already allocated. |
| `rustfs_gid` | integer | `10001` | Numeric GID; change if already allocated. |
| `rustfs_config_dir` | path | `/etc/rustfs` | Configuration directory. |
| `rustfs_data_dir` | path | `/var/lib/rustfs` | Persistent object-storage data directory. Back it up before upgrades. |
| `rustfs_log_dir` | path | `/var/log/rustfs` | RustFS log directory. |
| `rustfs_server_bin` | path | `/usr/local/bin/rustfs` | Installed server binary. |
| `rustfs_client_bin` | path | `/usr/local/bin/rc` | Installed `rc` binary. |
| `rustfs_env_file` | path | `{{ rustfs_config_dir }}/rustfs.env` | Root-owned mode-0600 environment file. |
| `rustfs_api_address` | `host:port` | `127.0.0.1:9000` | S3/admin API bind address. Keep loopback when using Nginx. |
| `rustfs_console_address` | `host:port` | `127.0.0.1:9001` | Console bind address. |
| `rustfs_region` | string | `us-east-1` | S3 signing region. |
| `rustfs_console_enabled` | boolean | `true` | Enable the browser console. |
| `rustfs_logger_level` | string | `info` | Log level, for example `debug`, `info`, `warn`, or `error`. |

Example for a directly exposed API without the proxy:

```yaml
rustfs_nginx_enabled: false
rustfs_api_address: "0.0.0.0:9000"
rustfs_console_enabled: false
```

### Credentials and RustFS settings

| Variable | Type | Default | Description |
|---|---|---|---|
| `rustfs_root_user` | string/secret | empty | Root/admin access key; minimum three characters. |
| `rustfs_root_password` | string/secret | empty | Root/admin secret key; minimum twelve characters. Use Vault. |
| `rustfs_extra_env` | mapping | `{}` | Additional RustFS environment variables. |
| `rustfs_server_args` | list[string] | `[]` | Additional arguments appended to `ExecStart`. |

Example:

```yaml
rustfs_root_user: "{{ vault_rustfs_root_user }}"
rustfs_root_password: "{{ vault_rustfs_root_password }}"
rustfs_extra_env:
  RUSTFS_HEALTH_ENDPOINT_ENABLE: "true"
rustfs_server_args: []
```

### Buckets and additional users

| Variable | Type | Default | Description |
|---|---|---|---|
| `rustfs_buckets` | list[mapping] | `[]` | Buckets to ensure exist; each item requires `name`. No deletion is performed. |
| `rustfs_users` | list[mapping] | `[]` | Users to ensure exist; each item requires `access_key` and `secret_key`. No deletion or rotation is performed. |
| `rustfs_cli_alias` | string | `local` | Alias name in the `rc` configuration. |
| `rustfs_cli_validate_certs` | boolean | `true` | Client certificate-validation setting reserved for client operations. |
| `rustfs_api_url` | URL | `http://127.0.0.1:9000` | Endpoint used by `rc` provisioning commands. |
| `rustfs_client_retries` | integer | `30` | Health-check retry count. |
| `rustfs_client_delay` | integer/seconds | `2` | Delay between health-check attempts. |
| `rustfs_health_path` | path | `/health` | Health endpoint on the API listener. |

Example:

```yaml
rustfs_buckets:
  - name: backup-data
  - name: application-artifacts
rustfs_users:
  - access_key: backup-writer
    secret_key: "{{ vault_backup_writer_secret }}"
  - access_key: readonly-monitor
    secret_key: "{{ vault_readonly_monitor_secret }}"
```

The current role only reconciles presence. It deliberately does **not** delete
users/buckets or rotate secrets based on list changes. Policies and fine-grained
access permissions must currently be managed separately with RustFS `rc` or the
Admin API.

### Nginx and TLS

| Variable | Type | Default | Description |
|---|---|---|---|
| `rustfs_nginx_enabled` | boolean | `true` | Install/configure Nginx reverse proxy. |
| `rustfs_nginx_package` | string | `nginx` | Nginx package name. |
| `rustfs_nginx_s3_server_name` | hostname | `s3.example.invalid` | SNI hostname routed to port 9000. |
| `rustfs_nginx_console_server_name` | hostname | `console.example.invalid` | SNI hostname routed to port 9001. |
| `rustfs_nginx_listen_port` | integer | `443` | Shared HTTPS port for both SNI virtual hosts. |
| `rustfs_nginx_ssl_mode` | enum | `self_signed` | `self_signed`, `existing_target`, or `controller`. |
| `rustfs_nginx_ssl_certificate` | path | self-signed CRT path | Target certificate path. |
| `rustfs_nginx_ssl_certificate_key` | path | self-signed key path | Target private-key path; mode `0600`. |
| `rustfs_nginx_ssl_certificate_source` | controller path | empty | Source certificate, used in `controller` mode. |
| `rustfs_nginx_ssl_certificate_key_source` | controller path | empty | Source private key, used in `controller` mode. |
| `rustfs_nginx_self_signed_days` | integer/days | `365` | Self-signed validity period. |
| `rustfs_nginx_self_signed_key_size` | integer/bits | `4096` | Self-signed RSA key size. |
| `rustfs_nginx_config_path` | path | `/etc/nginx/conf.d/rustfs.conf` | Nginx virtual-host configuration path. |

Self-signed certificates include both SNI names as SANs, use an RSA 4096-bit
key, are SHA-256 signed, and are valid for 365 days by default. They are not
trusted automatically by browsers or S3 clients.

Use an existing certificate already present on the target:

```yaml
rustfs_nginx_ssl_mode: existing_target
rustfs_nginx_ssl_certificate: /etc/pki/tls/certs/rustfs-fullchain.pem
rustfs_nginx_ssl_certificate_key: /etc/pki/tls/private/rustfs.key
```

Or copy a certificate from the controller:

```yaml
rustfs_nginx_ssl_mode: controller
rustfs_nginx_ssl_certificate: /etc/pki/tls/certs/rustfs-fullchain.pem
rustfs_nginx_ssl_certificate_key: /etc/pki/tls/private/rustfs.key
rustfs_nginx_ssl_certificate_source: files/rustfs-fullchain.pem
rustfs_nginx_ssl_certificate_key_source: files/rustfs.key
```

The certificate must cover both SNI hostnames. Never commit the private key;
use Vault or an approved protected file distribution mechanism.

## Day-2 operations and limitations

Health and service checks:

```bash
systemctl status rustfs nginx
curl -fsS http://127.0.0.1:9000/health
curl -fsS http://127.0.0.1:9000/health/ready
curl -fsS http://127.0.0.1:9001/rustfs/console/health
journalctl -u rustfs -u nginx --since today
rc admin info cluster local --json
```

Upgrade procedure:

1. Back up `rustfs_data_dir` and record the current version/binary checksum.
2. Review the RustFS release notes and compatibility requirements.
3. Change `rustfs_version` and `rustfs_checksum` together.
4. Run the role against one canary host first.
5. Verify service state, readiness, `rc admin info cluster`, bucket access, and application S3 operations.
6. Roll back by restoring the previous binary/configuration and restarting only if the release-specific rollback procedure permits it.

Bucket operations:

```bash
rc bucket list local/
rc bucket info local/my-bucket
rc object list local/my-bucket
```

The role creates declared buckets but does not remove undeclared buckets. Empty a
bucket before deleting it manually; RustFS rejects deletion of non-empty buckets.

User operations:

```bash
rc admin user info local backup-writer
rc admin user list local
rc admin user add local new-client '<secret-from-vault>'
rc admin user rm local old-client
```

The role creates declared users but does not remove users omitted from
`rustfs_users`, rotate their secrets, or attach policies. Perform those actions
explicitly and validate the affected clients afterward.

Certificate operations:

- Replace/renew the certificate and key using the selected certificate mode.
- Validate with `nginx -t`.
- Reload Nginx with `systemctl reload nginx`.
- Verify both SNI endpoints and certificate SANs.

## Task dispatch and supported platforms

The role uses a deterministic numbered-task dispatcher. `tasks/main.yml` finds
all two-digit task basenames below `tasks/`, sorts and deduplicates them, and
`tasks/include-file.yml` selects the first implementation in this order:

1. distribution + full version
2. distribution + major version
3. distribution
4. `rhelAll` + full/major version, then `rhelAll`
5. `ansible_os_family`
6. `shared`

AlmaLinux, Rocky, and Red Hat use the `rhelAll` family. Debian-family package
and Nginx installation tasks are under `tasks/Debian/`; RHEL-family equivalents
are under `tasks/rhelAll/`. Shared tasks contain the platform-neutral release,
service, provisioning, and optional plain-HTTP/Nginx-TLS behavior. A more
specific file with the same basename shadows (replaces) the shared fallback;
it is not additive. Keep numbered basenames unique unless that shadowing is
intentional.

| Family | Package implementation | Coverage |
|---|---|---|
| Debian-family | `apt` | Debian and derivatives exposing `ansible_os_family: Debian` |
| RHEL-family | `dnf` | Rocky, AlmaLinux, Red Hat (`rhelAll`) |

The local harness copies the role into `harness/roles/rustfs` so its basename
matches the installed-role contract, then runs both Debian and Rocky fact sets.
It disables package, download, service, provisioning, and Nginx changes, so
these tests prove dispatch and syntax only—not installation or live behavior.
Install `community.crypto` before enabling Nginx TLS; the dependency is pinned
in [`collections/requirements.yml`](collections/requirements.yml).

## Testing status

Static verification currently passes:

```bash
python3 tests/scripts/prepare_harness.py
python3 - <<'PY'
from pathlib import Path
import yaml
files = list(Path('.').rglob('*.yml')) + list(Path('.').rglob('*.yaml'))
for path in files:
    yaml.safe_load(path.read_text())
print(f'parsed {len(files)} YAML files')
PY
ANSIBLE_ROLES_PATH=harness/roles ansible-playbook -i tests/inventory.ini tests/test.yml --syntax-check
ANSIBLE_ROLES_PATH=harness/roles ansible-playbook -i tests/inventory.ini tests/test.yml --check
git diff --check
# Focused scan: shared tasks must remain OS-neutral.
! grep -REn 'ansible_(os_family|distribution)|\b(Debian|RedHat|Rocky|AlmaLinux|apt|dnf|yum)\b' tasks/shared/
```

A disposable Rocky 10 Hetzner test was attempted, but SSH authentication
failed before the role ran because the VM key did not match the available key.
The VM was deleted and provider cleanup was verified. Live installation,
bucket/user lifecycle, upgrade, Nginx, TLS, and end-to-end idempotency are not
claimed as tested.

## Sources and design provenance

- [RustFS Docker installation](https://docs.rustfs.com/en/installation/container/docker)
- [RustFS S3 protocol](https://docs.rustfs.com/en/administration/protocols/s3)
- [RustFS CLI (`rc`)](https://docs.rustfs.com/en/operations/rc)
- [RustFS status checks](https://docs.rustfs.com/en/operations/status-check)
- [RustFS Nginx reverse proxy](https://docs.rustfs.com/en/developer/integration/reverse-proxy/nginx)
- [RustFS releases](https://github.com/rustfs/rustfs/releases)
- [Reference public role](https://github.com/ricsanfre/ansible-role-rustfs) (MIT), reviewed
  for release asset naming, `rc` installation, and role layout; no code was copied.

The requested Bitbull-Ideas `ansible.template` repository was checked via the
GitHub API and returned 404. No files were copied from it.
