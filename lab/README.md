# Disposable Hetzner Rocky 10 test harness

This harness is deliberately not self-provisioning. Create one labeled,
disposable Rocky 10 x86 VM using the approved Bitbull-Ideas Hetzner workflow,
then place its temporary inventory and SSH configuration outside the role tree.
No credentials, generated state, or provider resources belong in Git.

Run from `/workspace/ansible` after approval:

```bash
ansible-playbook -i "$LAB_DIR/inventory.ini" lab/site.yml \
  -e @"$LAB_DIR/secrets.yml" --private-key "$LAB_DIR/id_ed25519"
```

The playbook exercises install, health, bucket/user provisioning, and upgrade.
Set `rustfs_lab_upgrade_version` and its checksum in the external secrets file.
The external cleanup command must delete the VM, firewall, volumes, and labels
created for this run. Verify deletion with the provider API before reporting.
