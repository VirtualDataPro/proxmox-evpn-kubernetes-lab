# Lab acceptance — 3 October 2026

The pinned bootstrap and wiki publisher were exercised on a separate two-VM Kubernetes cluster, one VM on each physical Proxmox host, using the existing EVPN network. The test used fresh checksum-verified Rocky 9.8 images, Kubernetes 1.35.9, containerd 2.3.6, Cilium 1.20.2 and Gateway API v1.6.1 experimental CRDs.

The test used `guide-cp` (VM 9310, `10.50.10.201`, pve1) and `guide-worker` (VM 9311, `10.50.10.202`, pve2), pod range `10.245.0.0/16` and Service range `10.112.0.0/12`. The test hostname was `wiki.guide.test`; the VIP was `10.50.10.210`. Requests used `curl --resolve`; no live DNS record was changed.

Both nodes became Ready; Cilium, Envoy, operators and CoreDNS were healthy. A strict MkDocs build passed. Two Nginx replicas occupied different physical hosts. Gateway and TLSRoute conditions passed, the Service received the reserved test VIP, and the L2 lease had a worker holder. HTTPS returned 200 with certificate verification; HTTP redirected 301. Access from an infrastructure DNS guest and RougarouOS on the management LAN passed. A pve1 VRF-originated curl timed out, so that source path remains unvalidated.

A second content revision and rollback both passed. A cross-host 1500-byte DF ping passed 3/3. Client-side apply exceeded the content ConfigMap annotation limit; server-side apply passed and is used throughout the guide. The disposable test VMs and disks were removed after ownership checks; the original cluster was rechecked afterward.

The test allowed workloads on its sole control plane to supply two physical scheduling domains. It did not establish control-plane HA, physical-host failure recovery, an independent SDN/DNS/router rebuild, or the optional egress/NFS extensions. Kubeadm warned about the vendor Rocky 5.14 kernel versus its upstream LTS allowlist; this is a lab result, not a production support certification.

The walkthrough uses the actual acceptance-run addresses and names. The running four-node cluster and its shared VIP `.100` are documented separately in the [lab reference](../docs/lab-reference.md). The selected reference snapshots describe that installed cluster and were not all applied during this fresh test. Private state, credentials, raw workspace logs and kubeconfigs remain excluded. Released test addresses and VM IDs must be checked for new use before repeating the run.

## Separate historical MTU result

A prior four-guest test repaired a 1600-byte guest/1500-byte uplink mismatch by using MTU 1500 for guests and VNets. All twelve directed guest paths and all four upstream paths passed their 1500-byte DF tests; 1501-byte DF packets were rejected locally as expected. Underlay capture showed no outer fragmentation. This is a summary of retained private evidence, not a new four-node acceptance run or proof of every external PMTU path.

## Original deployment records

The separate [four-node deployment lessons](../docs/deployment-lessons.md) summarize pre-conversion backups, original cluster health, pod DNS/MTU checks, the focused 39-action Cilium run, the broader run’s six failures and a NetworkManager route-recovery incident. These historical results do not expand the scope of the disposable two-VM acceptance run above.
