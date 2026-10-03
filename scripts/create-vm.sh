#!/usr/bin/env bash
# Run on the chosen Proxmox host. Creates a NEW VM; never overwrites one.
set -euo pipefail
: "${VM_ID:?Choose an unused cluster-wide VM ID}"
: "${VM_NAME:?Set a hostname}"
: "${VM_IP:?Reserve an unused VNet IPv4 address first}"
: "${STORAGE:?Set the host-local VM storage ID}"
: "${CLOUD_IMAGE:?Set the path to the verified Rocky GenericCloud qcow2}"
: "${IMAGE_SHA256:?Set its published SHA256}"
: "${SSH_PUBLIC_KEY:?Set the path to your SSH public key, never a private key}"
: "${VNET:=vnetk8s}"
: "${GATEWAY:=10.60.10.1}"
: "${DNS_SERVERS:=10.60.20.53 10.60.20.54}"
case "$VM_ID" in *[!0-9]*|'') echo 'VM_ID must be numeric'; exit 1;; esac
pvesh get /cluster/resources --type vm --output-format json |
  python3 -c 'import json,sys; wanted=int(sys.argv[1]); assert all(x["vmid"] != wanted for x in json.load(sys.stdin)), "VM ID already exists"' "$VM_ID"
[ -r "$CLOUD_IMAGE" ] && [ -r "$SSH_PUBLIC_KEY" ]
if grep -q 'PRIVATE KEY' "$SSH_PUBLIC_KEY"; then echo 'Refusing private key'; exit 1; fi
printf '%s  %s\n' "$IMAGE_SHA256" "$CLOUD_IMAGE" | sha256sum --check
qm create "$VM_ID" --name "$VM_NAME" --cores 2 --memory 4096 \
  --cpu host --ostype l26 --scsihw virtio-scsi-single \
  --scsi0 "$STORAGE:0,import-from=$CLOUD_IMAGE" \
  --ide2 "$STORAGE:cloudinit" --boot order=scsi0 \
  --net0 "virtio,bridge=$VNET,mtu=1500" \
  --ipconfig0 "ip=$VM_IP/24,gw=$GATEWAY" --nameserver "$DNS_SERVERS" \
  --ciuser labadmin --sshkeys "$SSH_PUBLIC_KEY" \
  --agent enabled=1 --serial0 socket --vga serial0 --tags guide-build
qm resize "$VM_ID" scsi0 32G
qm start "$VM_ID"
