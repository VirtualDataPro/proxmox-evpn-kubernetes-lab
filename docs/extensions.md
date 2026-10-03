# Installed application extensions

These notes describe the installed four-node lab. The fresh two-VM wiki acceptance run did not rebuild or retest Ledger, NFS or the egress extension. Selected nonsecret policies are linked from the [lab reference](lab-reference.md).

## Two sites on one address

Gateway `architects-ledger/ledger-private` uses `10.50.10.100`. Ledger's HTTPS listener terminates TLS and an HTTPRoute selects `ledger-web:80`; the container serves HTTP on 8080. Wiki uses a TLS passthrough listener and TLSRoute to `lab-wiki:443`; Nginx serves TLS on 8443. Both names resolve to the VIP, and both HTTP listeners redirect to HTTPS.

To add a site, deploy and verify its ClusterIP Service first. Obtain its certificate through your trusted CA. Add a distinct hostname/listener to the maintained Gateway with the intended TLS mode and allowed route namespaces. Create the matching route and verify its conditions and an SNI-preserving HTTPS request before publishing DNS. Preserve other sites' listeners when editing a shared Gateway.

The pool and L2 policy select the Gateway's generated Service. Keep `externalTrafficPolicy: Cluster` for this setup; the announcing worker may not have a backend pod. See [Cilium L2 announcements](https://docs.cilium.io/en/stable/network/l2-announcements/). Source policy and application authentication are separate decisions.

## Persistent NFS for Ledger

Architect's Ledger moved from Docker to Kubernetes. Its static PV `architects-ledger-qnap` and PVC `architects-ledger/ledger-data` use `172.27.85.25:/NFS/kubernetes/architects-ledger`, RWX and `Retain`, with declared capacity 5 GiB. Three web replicas mount the files read-only with UID/GID 1000. StorageClass `ledger-qnap` uses `kubernetes.io/no-provisioner`.

Another PVC does not create a NAS directory or enforce a quota. Install NFS client support on consuming nodes and check NAS export permissions, filesystem ownership and restore procedures. Retain the data when changing Kubernetes objects; `Retain` does not create a backup. The web replicas still share one NAS dependency.

The static wiki reconstructs its content in `emptyDir` from immutable ConfigMaps and needs no PVC. Its source and dependency lock are the durable build inputs.

## Selected outbound jobs

`ledger-worker-egress` selects only namespace `architects-ledger` and label `app=ledger-worker`. Public IPv4 traffic uses worker3 and is SNATed to `10.50.10.14`. RFC1918, loopback and link-local destinations are excluded from that egress-gateway path. The wiki and Ledger web pods do not match the selector.

A separate NetworkPolicy allows CoreDNS on TCP/UDP 53 and public TCP 443, excluding those private/special ranges from the HTTPS rule. An egress-gateway exclusion changes routing; it does not deny traffic. Read all matching policies when evaluating access because policy allows can be additive.

The original probe ran on worker1. Public HTTPS returned 200; the tested public HTTP 80 and private-LAN attempts were blocked. worker3's NAT map showed the expected source translation. An Internet IP echo alone could not prove the chosen worker because upstream NAT rewrites the address again.

This extension requires Cilium egress-gateway and BPF masquerading settings plus correct labels and node reachability. The wiki-only bootstrap does not enable it. Consult [Cilium's egress gateway requirements](https://docs.cilium.io/en/stable/network/egress-gateway/egress-gateway/) before adding it. Repeat permit/deny probes from a selected pod on another node and inspect the selected gateway's NAT state.

## What the worker-pause test covers

The incoming VIP's lease moved from worker1 to worker3 at the 22.1-second sample; both sites returned HTTPS 200 by the 38-second sample. This was a controlled worker VM pause and recovery. It does not establish loss-of-host recovery, uninterrupted existing connections, control-plane HA or egress-node failover.

Firewalla's fixed next hop through pve1 remains. Part 3 is planned around replacing pve1's troubled boot drive and testing a floating upstream IP with Keepalived/VRRP during that maintenance window. The routing tests will include pve2, the return path and client recovery. The single Kubernetes control plane remains a separate dependency. No Keepalived configuration is deployed by this repository.
