# Optional extension patterns

## A second site on the shared VIP

An illustrative Gateway `example-site/site-gateway` selects a one-address pool at10.60.10.100. Example site uses an HTTPS listener with TLS termination and an HTTPRoute to `site-web:80`. Wiki uses a TLS passthrough listener and TLSRoute to `lab-wiki:443`, where Nginx has the certificate. Both hostnames resolve to the same VIP. Each listener restricts allowed route namespaces, and a frontend Cilium policy restricts HTTPS sources to intended LAN/VPN ranges.

To add a site, deploy and verify its ClusterIP Service first. Generate its certificate through your trusted CA. Add a distinct hostname/listener to the maintained Gateway, with the intended TLS mode and namespace permissions, then create the matching route and DNS A record. Validate route conditions and curl with SNI before exposing it. Preserve existing listeners; do not replace a live Gateway with an older reference export.

Use distinct selectors and source policies for your own Gateway. Restrict the walkthrough's access separately before turning it into a durable service.

## Persistent NFS

The static wiki needs no PVC. Example site uses a static PV/PVC backed by NAS 192.0.2.25:/NFS/kubernetes/example-site, RWX and Retain, declared 5 GiB. Its three web replicas mount data read-only with UID/GID 1000. The storage class `static-nfs` uses `kubernetes.io/no-provisioner`; no CSI/dynamic provisioner is part of this design. Another PVC does not automatically create a directory or NAS quota. Install NFS client support on consumers and verify permissions, backup and restore independently.

## Scoped outbound jobs

An example egress policy can select only `example-site` pods labeled `app=scheduled-worker`. Their public traffic exits through node-c, SNAT address 10.60.10.14. RFC1918, loopback and link-local destinations are excluded. Separate NetworkPolicies allow CoreDNS and public HTTPS while denying tested HTTP 80/private LAN paths. An egress gateway selects a path; it does not replace traffic authorization.

An egress policy depends on matching labels, namespace, Cilium egress-gateway/BPF-masquerade settings and node reachability. The fresh wiki acceptance cluster did not enable or retest this extension. Reproduce selection and permit/deny probes before claiming it works in another environment. Validate a selected job on one node and inspect NAT state on the chosen egress node. No egress-node failover result is established by the fresh wiki test.

See the [Cilium egress gateway guide](https://docs.cilium.io/en/stable/network/egress-gateway/egress-gateway/) for requirements.

## Failure scope

A worker VIP-election test does not cover loss of Proxmox quorum, the sole API/etcd node, the direct cable, Upstream router's fixed next hop, DNS 1's writable API, NAS, or the chosen egress worker. Keep these dependencies visible in the architecture and recovery plan. A two-vote Proxmox cluster requires both nodes for quorum unless you implement an appropriate quorum design.
