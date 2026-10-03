# My Proxmox Kubernetes Wiki

This site was built from Markdown and deployed through Proxmox EVPN and Cilium Gateway API.

## Deployment path

Markdown → MkDocs Material → compressed ConfigMaps → Nginx → ClusterIP Service → TLSRoute → shared VIP.

The content is rebuilt into an emptyDir on each pod start. The source repository holds the durable copy.
