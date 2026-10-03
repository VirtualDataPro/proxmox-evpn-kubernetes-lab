# Configure the Proxmox network first

The host names, network prefixes and storage IDs below match the author’s installed lab. Adapt them to your own environment. The Kubernetes scripts assume a functioning Proxmox EVPN VNet and working outbound DNS/HTTPS. They do not change an existing host's management address, default route, SDN configuration, router, or firewall.

1. Prepare two Proxmox 9 hosts with FRRouting available. Follow the [Proxmox SDN prerequisites](https://pve.proxmox.com/pve-docs/chapter-pvesdn.html). Keep console access while changing host networking.
2. Configure direct NIC `enp1s0f1`: pve1 `10.0.0.1/30`, pve2 `10.0.0.2/30`, MTU 9000. Keep management on `vmbr0` at `172.27.85.11/.12`, with only its default gateway `172.27.85.1`. Adapt NIC names to your hardware.
3. From both ends, check peer ping and `ping -M do -s 8972 -c 3 <peer>`. Verify negotiated link speed independently; successful jumbo ping is not a throughput benchmark.
4. Datacenter → SDN → Options → Controllers: EVPN `evpnctrl`, AS 65000, nodes pve1, pve2, peers `10.0.0.1,10.0.0.2`.
5. Zones: EVPN `evpn1`, controller evpnctrl, VRF-VXLAN 10000, MTU 1500, IPAM pve. Exit nodes pve1, pve2; primary pve1; exit-node local routing disabled. DNS provider is optional for the basic connectivity build and requires its own credentials/configuration.
6. VNets: `evpntest` tag 10002 and `infranet` tag 10001, both in evpn1. Subnets respectively `10.50.10.0/24`, gateway `.1`, and `10.50.20.0/24`, gateway `.1`; SNAT enabled. Apply pending SDN changes cluster-wide only after reviewing them.
7. Verify `vtysh -c 'show bgp l2vpn evpn summary'`, VNet links, and `ip route show vrf vrf_evpn1` on both hosts. Two VNets in this VRF remain routed to one another; apply explicit policies for isolation.
8. Firewalla: routes `10.50.10.0/24` and `10.50.20.0/24` via `172.27.85.11`. This fixed next hop depends on pve1. Confirm router/client firewall policy permits your intended traffic. Test both directions and large packets before guest provisioning.
9. The installed guest DNS addresses are `10.50.20.53/.54`. Use your functioning resolvers if you have not built these DNS VMs. In this lab, public queries forward to the upstream router `172.27.85.1`; use no public resolver fallback here. Complete DNS ownership below before adding hostnames.

Configure through Proxmox and review the generated state. Selected SDN snapshots are linked in the [lab reference](lab-reference.md); do not replace an existing configuration wholesale with them.

## DNS ownership

PowerDNS owns forward `lab.local` and reverse `10.in-addr.arpa`. Each DNS VM serves authority on 5300 and Unbound on 53; Unbound uses local stub zones for those lab zones and forwards other names to Firewalla. DNS 2 receives signed transfers from writable DNS 1. Supply your own TSIG/API secrets privately; this repository does not provision those servers.

Firewalla conditional forwarding should target both DNS VMs for `lab.local`, `10.50.10.in-addr.arpa` and `20.50.10.in-addr.arpa`, not all reverse 10/8. Verify local and public lookups to exclude forwarding loops. DNS/IPAM registration is workflow-dependent: creating a static cloud-init address does not establish an A/PTR record. There is no external-dns controller in this build.

The walkthrough uses `wiki.guide.test` with curl `--resolve`, so it can be tested without changing live DNS. To publish your own internal hostname, replace it consistently in Gateway/TLSRoute, the publisher argument, the certificate SAN, and your DNS A record. Point the name at the VIP, not a pod IP. The installed `lab.local` suffix has special multicast-DNS behavior ([RFC 6762](https://www.rfc-editor.org/rfc/rfc6762)). New home labs can consider `home.arpa` ([RFC 8375](https://www.rfc-editor.org/rfc/rfc8375)) or a suitable domain they control.

## Guest SSH through the VRF

Use the Proxmox host carrying the VM as the jump host. `socat` must be installed on that host. Example SSH configuration (supply your authorized identities):

```sshconfig
Host guide-pve1
    HostName 172.27.85.11
    User root
Host guide-pve2
    HostName 172.27.85.12
    User root
Host guide-cp
    HostName 10.50.10.201
    User labadmin
    IdentityFile ~/.ssh/guide-key
    ProxyCommand ssh guide-pve1 ip vrf exec vrf_evpn1 socat STDIO TCP:%h:%p
Host guide-worker
    HostName 10.50.10.202
    User labadmin
    IdentityFile ~/.ssh/guide-key
    ProxyCommand ssh guide-pve2 ip vrf exec vrf_evpn1 socat STDIO TCP:%h:%p
```

Preserve normal host-key verification. Inspect direct routing if TCP resets while DNS/ping works; this lab has an observed asymmetric LAN/router path. A VRF jump supplies transport, not Kubernetes authorization.
