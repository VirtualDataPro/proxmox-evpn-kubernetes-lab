# Lessons from the original four-node deployment

These are summaries of retained private workspace records from the original deployment. They supplement the later disposable two-VM acceptance run; they do not expand the scope of that test. Published addresses match the lab; raw logs and private workspace state stay in the author package.

## Prepare a rollback before replacing a guest

The original build reused four Debian test VMs. Successful NFS backup jobs preceded conversion to fresh Rocky cloud-image boot disks. The old disks were detached and retained. Backup completion and disk retention are documented; backup restoration and rollback to those old disks were not exercised. The public provisioning script instead creates new VMs with unused IDs. Do not rerun a historical disk-conversion script against an existing Kubernetes node.

## Read the test counts and exclusions

The original cluster validation recorded four Ready nodes and four reachable Cilium health endpoints. Pod tests resolved an internal host name and the Kubernetes Service name. A cross-host pod DF ping passed twice with a 1472-byte payload, giving a 1500-byte IPv4 packet. A 1473-byte payload was rejected locally with MTU 1500. This proves the tested pod path and local size enforcement, not all external PMTU paths.

A focused no-policies Cilium run reported one successful test containing 39 actions; 134 tests and three scenarios were skipped. This was basic connectivity coverage, not network-policy conformance. An intermediate filter selected zero tests and zero actions; it contributes no validation evidence.

The broader run reported one of two tests failed: six of 81 actions failed, with 133 tests skipped. All six failures were HTTPS connections to the public resolver addresses 1.1.1.1 and 1.0.0.1. Connections to those addresses also failed from an infrastructure DNS guest outside Kubernetes. That observation supports an upstream restriction as the explanation; the broader run still failed. Use destinations allowed by your network, record exclusions, and test scoped egress policies separately.

## A DNS edit can disturb the packet path

A historical NetworkManager profile reapply disturbed Cilium routes. The next pod validation timed out on readiness and DNS. Restarting the Cilium DaemonSet completed across four agents; the subsequent pod check resolved internal, Service and external names and passed external HTTPS.

That restart was recovery from an observed incident, not a step required for every DNS update. Before changing a live node profile, inspect its managed interfaces and routes, preserve console access, and choose a change method that avoids unnecessary link reconfiguration. Afterward, check agent health and test from a pod. A successful lookup on the host alone does not establish pod DNS health.

The node-preparation script excludes Cilium interfaces from NetworkManager. Retain those exclusions and review their applicability to your guest distribution.
