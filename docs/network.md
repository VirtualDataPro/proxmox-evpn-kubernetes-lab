# Configure the Proxmox network first

All host names, network prefixes and storage names below are examples. The Kubernetes scripts assume a functioning Proxmox EVPN VNet and working outbound DNS/HTTPS. They do not change an existing host's management address, default route, SDN configuration, router, or firewall.

1. Prepare two Proxmox 9 hosts with FRRouting available. Follow the [Proxmox SDN prerequisites](https://pve.proxmox.com/pve-docs/chapter-pvesdn.html). Keep console access while changing host networking.
2. Configure direct NIC `enp1s0f1`: hv-a `10.255.255.1/30`, hv-b `10.255.255.2/30`, MTU 9000. Keep management on `vmbr0` at `192.0.2.11/.12`, with only its default gateway `192.0.2.1`. Adapt NIC names to your hardware.
3. From both ends, check peer ping and `ping -M do -s 8972 -c 3 <peer>`. Verify negotiated link speed independently; successful jumbo ping is not a throughput benchmark.
4. Datacenter → SDN → Options → Controllers: EVPN `evpnctl`, AS 65000, nodes hv-a, hv-b, peers `10.255.255.1,10.255.255.2`.
5. Zones: EVPN `evpndemo`, controller evpnctl, VRF-VXLAN 10000, MTU 1500, IPAM pve. Exit nodes hv-a, hv-b; primary hv-a; exit-node local routing disabled. DNS provider is optional for the basic connectivity build and requires its own credentials/configuration.
6. VNets: `vnetk8s` tag 10002 and `vnetinf` tag 10001, both in evpndemo. Subnets respectively `10.60.10.0/24`, gateway `.1`, and `10.60.20.0/24`, gateway `.1`; SNAT enabled. Apply pending SDN changes cluster-wide only after reviewing them.
7. Verify `vtysh -c 'show bgp l2vpn evpn summary'`, VNet links, and `ip route show vrf vrf_evpndemo` on both hosts. Two VNets in this VRF remain routed to one another; apply explicit policies for isolation.
8. Upstream router: routes `10.60.10.0/24` and `10.60.20.0/24` via `192.0.2.11`. This fixed next hop depends on hv-a. Confirm router/client firewall policy permits your intended traffic. Test both directions and large packets before guest provisioning.
9. The example guest DNS addresses are `10.60.20.53/.54`. Use your functioning resolvers if you have not built these DNS VMs. In this example, public queries forward to the upstream router `192.0.2.1`; use no public resolver fallback here. Complete DNS ownership below before adding hostnames.

This is an illustrative design. Configure through your own Proxmox UI and review the generated state; no live SDN exports are published here.

## DNS ownership

PowerDNS owns forward `demo.home.arpa` and reverse `10.in-addr.arpa`. Each DNS VM serves authority on 5300 and Unbound on 53; Unbound uses local stub zones for those lab zones and forwards other names to Upstream router. DNS 2 receives signed transfers from writable DNS 1. Supply your own TSIG/API secrets privately; this repository does not provision those servers.

Upstream router conditional forwarding should target both DNS VMs for `demo.home.arpa`, `10.60.10.in-addr.arpa` and `20.60.10.in-addr.arpa`, not all reverse 10/8. Verify local and public lookups to exclude forwarding loops. DNS/IPAM registration is workflow-dependent: creating a static cloud-init address does not establish an A/PTR record. There is no external-dns controller in this build.

The walkthrough uses `wiki.demo.test` with curl `--resolve`, so it can be tested without changing live DNS. To publish your own internal hostname, replace it consistently in Gateway/TLSRoute, the publisher argument, the certificate SAN, and your DNS A record. Point the name at the VIP, not a pod IP. An existing `demo.home.arpa` name can conflict with mDNS; new environments can choose a suitable domain they control.

## Guest SSH through the VRF

Use the Proxmox host carrying the VM as the jump host. `socat` must be installed on that host. Example SSH configuration (supply your authorized identities):

```sshconfig
Host guide-hv-a
    HostName 192.0.2.11
    User root
Host guide-hv-b
    HostName 192.0.2.12
    User root
Host guide-cp
    HostName 10.60.10.201
    User labadmin
    IdentityFile ~/.ssh/guide-key
    ProxyCommand ssh guide-hv-a ip vrf exec vrf_evpndemo socat STDIO TCP:%h:%p
Host guide-worker
    HostName 10.60.10.202
    User labadmin
    IdentityFile ~/.ssh/guide-key
    ProxyCommand ssh guide-hv-b ip vrf exec vrf_evpndemo socat STDIO TCP:%h:%p
```

Preserve normal host-key verification. Inspect direct routing if TCP resets while DNS/ping works; this lab has an observed asymmetric LAN/router path. A VRF jump supplies transport, not Kubernetes authorization.
