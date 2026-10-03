# Monitoring, backups and notification delivery

This is a summary of the author's retained September 28 monitoring reports, October 3 mail-repair report and publication review. It is not an installer or a claim of continuous availability. The monitoring VM is `172.27.85.30`, outside Kubernetes; its own host and upstream dependencies still matter.

## What the dashboards measure

The September baseline recorded 32 Prometheus targets up, eight passing DNS probes and 22 rules evaluating successfully. The October 3 dashboard captures show populated 30-minute graphs, four Ready Kubernetes nodes, 23 running pods, 14 healthy Kubernetes scrape targets, 12 healthy Docker containers, two Proxmox nodes online and one disk needing sector review. These are observations at capture time.

Scrape success (`up`) establishes that Prometheus reached a target. DNS `probe_success` establishes the lookup result. The DNS probes cover both resolvers and Firewalla, including a lab record expected to resolve to `10.50.10.11` and external resolution. Neither counter establishes the complete health of a physical disk or application.

The retained hardware report identified pending/reallocated-sector attributes on pve1's boot SSD while overall SMART reported PASSED. The device was not in smartctl's drive database, so vendor-specific raw attributes need interpretation. The report did not run a disk repair, self-test or migration. The capture retains the review warning instead of presenting all infrastructure as healthy.

## Kubernetes and host access

Prometheus scrapes the API server, kubelet metrics, cAdvisor, resource metrics and kube-state-metrics. Metrics-server also supplies resource metrics used by the service dashboard. Prometheus and Homepage have separate scoped service accounts; no cluster-admin kubeconfig was copied into the Docker services.

Kubelet serving certificates were signed after checking each CSR's requester, signer, subject and exact DNS/IP SANs. Scrapes verify certificates. Serving CSRs still need an approval process at renewal; a certificate-expiry rule does not itself renew a certificate. See [kubeadm certificate management](https://kubernetes.io/docs/tasks/administer-cluster/kubeadm/kubeadm-certs/#kubelet-serving-certs).

Proxmox monitoring uses a privilege-separated PVEAuditor token. Its exporter verifies the hosts through a trust bundle of the installed server certificates; certificate rotation requires refreshing that bundle through an authenticated path. Do not respond to a certificate change by disabling verification.

Native host/SMART collectors and DNS blackbox probes extend coverage beyond Kubernetes. The intentional Redfish mock remains test data for scripts, not a source of real hardware health.

## Container operation

The September reliability work added or preserved healthchecks, pinned image digests, explicit resource limits and bounded JSON log rotation across 12 running containers. Compose configurations were validated. Existing data volumes were retained.

A healthcheck can report that a container is unhealthy while its process is still running. A restart policy alone does not repair that state. Container CPU/memory limits were chosen from observed lab use; the work was not a load test.

## Backups and mail are separate checks

Successful NFS backups preceded conversion of the original four Kubernetes guests from Debian to fresh Rocky boot disks; DNS backups are also recorded. Those archives were not restored as part of the article test.

The October 3 inspection of the enabled 03:00 `KNAPY` backup job lists VMs 104, 105, 107, 108, 109, 110, 111 and 112. It omits the six new Kubernetes/DNS VMs 120–125. That job therefore does not establish recurring protection for them. Other manual or external backups are a separate question. Check scheduled coverage and demonstrate a restore before claiming complete recovery.

The October 3 mail repair addressed legacy-sendmail backup reports attempting direct outbound port 25 delivery. Postfix was changed to an authenticated port-587 relay with verified TLS and protected credentials. Ten queued reports were accepted by the relay and confirmed in Gmail. Credentials, recipient addresses and queue contents are excluded here.

A working Proxmox notification target did not prove that the legacy-sendmail path worked. Likewise, the September Prometheus rules had no notification receiver configured. Successful backup mail does not establish delivery of Prometheus alerts. Test each notification path separately and monitor the monitoring service from a suitable independent location. See [Prometheus alerting architecture](https://prometheus.io/docs/alerting/latest/overview/).
