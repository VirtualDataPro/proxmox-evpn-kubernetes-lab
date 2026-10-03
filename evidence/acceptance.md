# Lab acceptance and public-example scope

The pinned bootstrap and wiki publisher were exercised on a separate two-VM Kubernetes cluster, one VM on each physical Proxmox host, using the existing EVPN network. The test used fresh checksum-verified Rocky 9.8 images, Kubernetes 1.35.9, containerd 2.3.6, Cilium 1.20.2 and Gateway API v1.6.1 experimental CRDs.

Both nodes became Ready; Cilium, Envoy, operators and CoreDNS were healthy. A strict MkDocs build passed. Two Nginx replicas occupied different physical hosts. Gateway and TLSRoute conditions passed, the Service received the reserved test VIP, and the L2 lease had a worker holder. HTTPS returned200 with certificate verification; HTTP redirected 301. Access from an infrastructure guest and an administration VM passed. A host-VRF-originated curl timed out, so that source path remains unvalidated.

A second content revision and rollback both passed. A cross-host 1500-byte DF ping passed 3/3. Client-side apply exceeded the content ConfigMap annotation limit; server-side apply passed and is used throughout the guide. The disposable test VMs and disks were removed after ownership checks; the original cluster was rechecked afterward.

The test allowed workloads on its sole control plane to supply two physical scheduling domains. It did not establish control-plane HA, physical-host failure recovery, an independent SDN/DNS/router rebuild, or the optional egress/NFS extensions. Kubeadm warned about the vendor Rocky 5.14 kernel versus its upstream LTS allowlist; this is a lab result, not a production support certification.

All public addresses, hostnames, storage IDs and object identities were generalized after this run. The example configuration was not executed with those exact substituted values. Adapt and validate it in your own environment. Original internal topology exports, raw acceptance output, private state, credentials and screenshots are excluded from this public repository.

## Separate historical MTU result

A prior four-guest test repaired a 1600-byte guest/1500-byte uplink mismatch by using MTU 1500 for guests and VNets. All twelve directed guest paths and all four upstream paths passed their 1500-byte DF tests; 1501-byte DF packets were rejected locally as expected. Underlay capture showed no outer fragmentation. This is a summary of retained private evidence, not a new four-node acceptance run or proof of every external PMTU path.

## Original deployment records

The separate [four-node deployment lessons](../docs/deployment-lessons.md) summarize pre-conversion backups, original cluster health, pod DNS/MTU checks, the focused 39-action Cilium run, the broader run’s six failures and a NetworkManager route-recovery incident. These historical results do not expand the scope of the disposable two-VM acceptance run above.
