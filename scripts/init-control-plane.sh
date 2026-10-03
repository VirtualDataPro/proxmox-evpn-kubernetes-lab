#!/usr/bin/env bash
# Run on a fresh prepared control plane. Join tokens remain private.
set -euo pipefail
: "${NODE_IP:?Set NODE_IP to this control plane static address}"
: "${API_ENDPOINT:=$NODE_IP}"
: "${POD_CIDR:=10.244.0.0/16}"
: "${SERVICE_CIDR:=10.96.0.0/12}"
cat > /tmp/guide-kubeadm.yaml <<CONFIG
apiVersion: kubeadm.k8s.io/v1beta4
kind: InitConfiguration
localAPIEndpoint:
  advertiseAddress: "$NODE_IP"
nodeRegistration:
  criSocket: unix:///run/containerd/containerd.sock
---
apiVersion: kubeadm.k8s.io/v1beta4
kind: ClusterConfiguration
kubernetesVersion: v1.35.9
controlPlaneEndpoint: "$API_ENDPOINT:6443"
apiServer:
  certSANs: ["$API_ENDPOINT", "$NODE_IP"]
networking:
  podSubnet: "$POD_CIDR"
  serviceSubnet: "$SERVICE_CIDR"
proxy:
  disabled: true
---
apiVersion: kubelet.config.k8s.io/v1beta1
kind: KubeletConfiguration
cgroupDriver: systemd
CONFIG
sudo kubeadm init --config /tmp/guide-kubeadm.yaml
install -d -m 700 "$HOME/.kube"
sudo install -o "$(id -u)" -g "$(id -g)" -m 600 /etc/kubernetes/admin.conf "$HOME/.kube/config"
echo 'Create a short-lived worker join command with: sudo kubeadm token create --ttl 30m --print-join-command'
