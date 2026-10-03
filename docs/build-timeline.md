# Build timeline and evidence

The main rebuild spans approximately 20–28 September 2026, supporting the author's account of **about a week** working with Codex and GPT on RougarouOS. Follow-up maintenance and publication testing continued in October. This is elapsed calendar time, not measured hands-on effort or an AI productivity benchmark.

The author supplied the re-IP sequence and the estimate of one hour for manually changing the Proxmox nodes. Filtered package histories, pve1 task metadata, configuration modification times and dated workspace reports provide the remaining chronology. Raw private logs, command histories and workspace state are excluded from this repository.

| Date | Evidence and supported claim |
|---|---|
| September 20 | On pve1, `/etc/network/interfaces` was last modified at 20:12 CDT; storage configuration at 20:59; Corosync and the now-empty HA resource file at 21:05. These file times are consistent with the author's re-IP account. They do not establish each command or a 53-minute outage. |
| September 23 | Package histories show the 8.4.21 preparation update and the move to Proxmox 9.2.20. pve1's major-upgrade transaction begins at 23:23 local time. Saved pre-upgrade configuration already has the new management addresses and local/NFS storage. |
| September 27 | Proxmox task metadata records guest creation and SDN reloads. Workspace records cover the EVPN MTU retest, backups of the original four guests, their conversion to Rocky and Kubernetes validation. |
| September 28 | Records cover PowerDNS/SDN integration, the wiki, monitoring improvements, shared HTTPS, VIP allocation and the worker-pause election test. This is the dated baseline of the operations wiki. |
| October 1 | Package histories record the maintenance update from Proxmox 9.2.20 to 9.2.21. |
| October 3 | Mail-relay repair delivered ten queued reports. A separate fresh two-VM Kubernetes/wiki acceptance run tested deployment, HTTPS, content update and rollback; its VMs were removed afterward. |

pve1 uses `America/Chicago`; the file timestamps above are converted from UTC to CDT. For example, `2026-09-21T01:12:14Z` is September 20 at 20:12 CDT. Workspace modification dates and report content support a sequence but may reflect later edits, copying or documentation work. They are weaker evidence than an explicit successful task or test result.

## Re-IP order supplied by the author

1. Give RougarouOS a second NIC to retain an administration path.
2. Change the switch management address.
3. Move the network gateway.
4. Re-IP NFS, Proxmox and other workloads. The two Proxmox nodes were changed manually, taking about an hour of work.
5. Update Grafana/Prometheus targets and remaining servers.

The new management network is `172.27.85.0/24`, replacing `192.168.1.0/24` because common remote networks overlapped it during VPN use. There is no measured end-to-end downtime record for this sequence.

## What was not recovered

Ceph purge and upgrade-checker command entries exist, but they do not establish a complete data-evacuation procedure, the exact `pve8to9` findings or measured service downtime. The article therefore does not reconstruct those as a copy-and-paste procedure.

The old Ceph configuration placed the client-facing public network on the management LAN and replication on the direct link. The article explains that distinction and the author's observed 1 GbE constraint without claiming that a monitor proxied storage data or publishing an invented throughput measurement.

## Codex, GPT and RougarouOS

The author's attribution is firsthand: Codex and GPT, used through RougarouOS, helped with configuration, scripts, diagnosis, deployment, validation and documentation. Retained workspaces include the Rocky/Kubernetes build, EVPN validation, DNS integration, wiki publisher, gateway migration, VIP tests, egress tests, observability and mail repair.

The manual node re-IP and architecture decisions remain the author's work. No exact model version, autonomous completion rate, counterfactual time saving or line count is inferred from file timestamps.
