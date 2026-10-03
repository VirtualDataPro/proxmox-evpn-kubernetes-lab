#!/usr/bin/env bash
# Run as the control-plane operator after init-control-plane.sh.
set -euo pipefail
: "${NODE_IP:?Set NODE_IP to the control-plane address}"
: "${POD_CIDR:=10.244.0.0/16}"
CILIUM_CLI_VERSION=v0.20.1
CILIUM_VERSION=1.20.2
[ "$(uname -m)" = x86_64 ] || { echo 'This script targets x86_64'; exit 1; }
task_download=$(mktemp -d)
trap 'rm -rf "$task_download"' EXIT
cd "$task_download"
curl -fL --remote-name-all "https://github.com/cilium/cilium-cli/releases/download/$CILIUM_CLI_VERSION/cilium-linux-amd64.tar.gz"{,.sha256sum}
sha256sum --check cilium-linux-amd64.tar.gz.sha256sum
sudo tar xzf cilium-linux-amd64.tar.gz -C /usr/local/bin cilium
for resource in gatewayclasses gateways httproutes referencegrants grpcroutes backendtlspolicies tlsroutes; do
  kubectl apply --server-side -f "https://raw.githubusercontent.com/kubernetes-sigs/gateway-api/v1.6.1/config/crd/experimental/gateway.networking.k8s.io_${resource}.yaml"
done
cilium install --version "$CILIUM_VERSION" \
  --set routingMode=native --set autoDirectNodeRoutes=true \
  --set ipv4NativeRoutingCIDR="$POD_CIDR" --set ipam.mode=kubernetes \
  --set kubeProxyReplacement=true --set k8sServiceHost="$NODE_IP" \
  --set k8sServicePort=6443 --set mtu=1500 --set operator.replicas=2 \
  --set gatewayAPI.enabled=true --set l2announcements.enabled=true \
  --set k8sClientRateLimit.qps=20 --set k8sClientRateLimit.burst=40 \
  --set envoy.securityContext.capabilities.keepCapNetBindService=true
cilium status --wait --wait-duration 5m
