#!/usr/bin/env bash
# Fresh Rocky Linux 9.8 nodes only. Recreates containerd configuration.
set -eu
sudo cloud-init status --wait || true
sudo dnf install -y dnf-plugins-core curl bind-utils qemu-guest-agent iproute-tc
sudo systemctl enable --now qemu-guest-agent
sudo dnf config-manager --add-repo https://download.docker.com/linux/centos/docker-ce.repo
sudo dnf install -y containerd.io-2.3.6-1.el9
sudo install -d /etc/containerd
sudo containerd config default | sudo tee /etc/containerd/config.toml >/dev/null
sudo sed -i 's/SystemdCgroup = false/SystemdCgroup = true/' /etc/containerd/config.toml
sudo tee /etc/modules-load.d/kubernetes.conf >/dev/null <<'EOF'
overlay
br_netfilter
EOF
sudo modprobe overlay
sudo modprobe br_netfilter
sudo tee /etc/sysctl.d/90-kubernetes.conf >/dev/null <<'EOF'
net.ipv4.ip_forward = 1
net.bridge.bridge-nf-call-iptables = 1
net.bridge.bridge-nf-call-ip6tables = 1
EOF
sudo sysctl --system >/dev/null
sudo swapoff -a
sudo sed -i '/^[^#].*\sswap\s/s/^/#/' /etc/fstab
sudo setenforce 0
sudo sed -i 's/^SELINUX=enforcing/SELINUX=permissive/' /etc/selinux/config
sudo mkdir -p /etc/NetworkManager/conf.d
sudo tee /etc/NetworkManager/conf.d/99-cilium.conf >/dev/null <<'EOF'
[keyfile]
unmanaged-devices=interface-name:cilium*;interface-name:lxc*;interface-name:docker*;interface-name:veth*
EOF
sudo nmcli general reload
sudo tee /etc/yum.repos.d/kubernetes.repo >/dev/null <<'EOF'
[kubernetes]
name=Kubernetes
baseurl=https://pkgs.k8s.io/core:/stable:/v1.35/rpm/
enabled=1
gpgcheck=1
gpgkey=https://pkgs.k8s.io/core:/stable:/v1.35/rpm/repodata/repomd.xml.key
exclude=kubelet kubeadm kubectl cri-tools kubernetes-cni
EOF
sudo dnf install -y kubelet-1.35.9 kubeadm-1.35.9 kubectl-1.35.9 --disableexcludes=kubernetes
sudo systemctl enable --now containerd kubelet
sudo kubeadm config images pull --kubernetes-version v1.35.9
