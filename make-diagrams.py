from pathlib import Path
from html import escape
import subprocess

OUT = Path(__file__).parent / 'diagrams'
OUT.mkdir(exist_ok=True)
INK, MUTED, GREEN, BLUE, ORANGE = '#152d37', '#526975', '#147d64', '#286ca6', '#a56420'

class Diagram:
    def __init__(self, title, subtitle, height=1100):
        self.height = height
        self.parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="{height}" viewBox="0 0 1600 {height}">',
                      '<defs><marker id="arrow" markerWidth="10" markerHeight="10" refX="8" refY="5" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10" fill="#526975"/></marker></defs>',
                      f'<rect width="1600" height="{height}" fill="#f6f9fb"/>']
        self.text(60, 62, title, 34, INK, '700')
        self.text(60, 103, subtitle, 21, MUTED)
    def text(self, x, y, value, size=22, color=INK, weight='400', anchor='start'):
        self.parts.append(f'<text x="{x}" y="{y}" font-family="DejaVu Sans, sans-serif" font-size="{size}" fill="{color}" font-weight="{weight}" text-anchor="{anchor}">{escape(value)}</text>')
    def group(self, x,y,w,h,title,color=BLUE):
        self.parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="20" fill="#edf3f7" stroke="{color}" stroke-width="2"/>')
        self.text(x+24,y+38,title,25,color,'700')
    def box(self,x,y,w,h,title,lines,color=GREEN):
        self.parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="12" fill="white" stroke="{color}" stroke-width="2"/>')
        self.text(x+18,y+32,title,23,color,'700')
        for i,line in enumerate(lines): self.text(x+18,y+64+i*28,line,20)
    def arrow(self, points, label=None, at=None, both=False, dash=False):
        pts=' '.join(f'{x},{y}' for x,y in points)
        attrs=' marker-start="url(#arrow)"' if both else ''
        if dash: attrs+=' stroke-dasharray="8 7"'
        self.parts.append(f'<polyline points="{pts}" fill="none" stroke="{MUTED}" stroke-width="3" marker-end="url(#arrow)"{attrs}/>')
        if label and at: self.text(*at,label,19,MUTED)
    def footer(self, lines):
        for i,line in enumerate(lines): self.text(60,self.height-65+i*27,line,18,MUTED)
    def save(self,name):
        svg=OUT/f'{name}.svg'
        svg.write_text('\n'.join(self.parts+['</svg>']))
        subprocess.run(['rsvg-convert','-o',str(OUT/f'{name}.png'),str(svg)],check=True)

d=Diagram('The Proxmox and Kubernetes lab','Illustrative example; addresses are placeholders • EVPN overlay on a direct 10 GbE underlay',1220)
d.box(60,145,390,125,'Clients',['Management / laptop LAN / VPN','DNS and routed application access'],BLUE)
d.box(550,145,470,125,'Upstream router • 192.0.2.1',['Routes both 10.60.x subnets via hv-a','Conditional DNS → dns-a / dns-b'],BLUE)
d.box(1120,145,420,125,'NAS • 192.0.2.25',['NFS → Example site persistent data','shared-nfs → shared files / backups'],ORANGE)
d.arrow([(450,208),(550,208)])
d.group(60,360,700,525,'hv-a • 192.0.2.11 • primary EVPN exit')
d.group(840,360,700,525,'hv-b • 192.0.2.12 • additional exit')
d.box(85,423,650,98,'dns-a • 10.60.20.53 • vnetinf',['PowerDNS primary + Unbound + DNS administration'])
d.box(865,423,650,98,'dns-b • 10.60.20.54 • vnetinf',['PowerDNS secondary + Unbound'])
d.box(85,545,650,98,'cp-a • 10.60.10.11 • vnetk8s',['Single Kubernetes control plane and etcd member'])
d.box(85,667,650,98,'node-a • 10.60.10.12 • vnetk8s',['Cilium / Envoy and application workloads'])
d.box(865,545,650,98,'node-b • 10.60.10.13 • vnetk8s',['Cilium / Envoy and application workloads'])
d.box(865,667,650,98,'node-c • 10.60.10.14 • vnetk8s',['Cilium / Envoy + selected Example site job egress'])
d.text(85,828,'VM disks: local-a • node-local LVM thin',20,MUTED)
d.text(865,828,'VM disks: local-b • node-local LVM thin',20,MUTED)
d.arrow([(700,270),(700,330),(410,330),(410,360)],'Management LAN / upstream exit',(70,323))
d.arrow([(960,270),(960,360)])
d.text(1070,326,'Management LAN',19,MUTED)
d.box(270,940,1060,105,'Direct 10 GbE link • enp1s0f1 • MTU 9000',['hv-a 10.255.255.1/30 ↔ hv-b 10.255.255.2/30 • BGP EVPN + VXLAN transport'],BLUE)
d.arrow([(410,885),(410,940)],both=True)
d.arrow([(1190,885),(1190,940)],both=True)
d.footer(['Zone evpndemo • ASN 65000 • VRF VNI 10000 • vnetinf VNI 10001 • vnetk8s VNI 10002',
          'Guest / pod MTU 1500. Single cable, hv-a upstream route, single control plane, and NAS remain failure dependencies.'])
d.save('01-network-topology')

d=Diagram('How clients reach the websites','DNS selects the shared VIP • Cilium routes by hostname/SNI • TLS ownership differs by application',1050)
d.box(60,170,410,120,'Client',['LAN / laptop / VPN','Uses Upstream router-backed lab DNS'],BLUE)
d.box(590,170,450,120,'DNS lookup',['wiki.demo.home.arpa and site.demo.home.arpa','Both return 10.60.10.100'],BLUE)
d.arrow([(470,230),(590,230)],'Resolve name',(477,209))
d.box(60,400,410,120,'Upstream router → hv-a',['10.60.10.0/24 routed via','192.0.2.11 → EVPN'],BLUE)
d.arrow([(265,290),(265,400)])
d.box(590,400,450,120,'Shared VIP • 10.60.10.100',['One elected worker announces ARP','Gateway Service → Cilium Envoy'])
d.arrow([(470,460),(590,460)],'TCP 443',(484,438))
d.box(1130,290,410,170,'Wiki • lab-wiki',['TLSRoute selects wiki SNI','TLS passthrough → Nginx :443','2 replicas across physical hosts'])
d.box(1130,575,410,170,'Example site • example-site',['TLS terminates at Cilium','HTTPRoute → site-web :80','3 web replicas → NAS NFS'])
d.arrow([(1040,460),(1080,460),(1080,375),(1130,375)])
d.arrow([(1040,460),(1080,460),(1080,660),(1130,660)])
d.box(590,730,450,120,'Control plane • cp-a',['Kubernetes Lease supports elections','API needed for ownership changes'],ORANGE)
d.arrow([(815,730),(815,520)],dash=True)
d.footer(['HTTPS source policy permits the documented management LAN, laptop LAN, and VPN; HTTP redirects to HTTPS.',
          'Measured worker failover: lease acquired ~22 s; both sites recovered by ~38 s. This does not prove physical-host HA.'])
d.save('02-application-access')

d=Diagram('DNS resolution and record ownership','PowerDNS owns lab records • Unbound resolves • Upstream router integrates clients',1080)
d.box(60,160,420,130,'LAN / VPN client',['Queries Upstream router','demo.home.arpa and reverse lookups'],BLUE)
d.box(590,160,430,130,'Upstream router • 192.0.2.1',['Lab names → dns-a / dns-b','Other names → external resolution'],BLUE)
d.arrow([(480,225),(590,225)])
d.box(120,400,580,145,'dns-a • 10.60.20.53',['Unbound :53 → local PowerDNS :5300','Writable authority; API on loopback :8081'])
d.box(900,400,580,145,'dns-b • 10.60.20.54',['Unbound :53 → local PowerDNS :5300','Secondary authority; TSIG zone transfers'])
d.arrow([(730,290),(730,345),(410,345),(410,400)],'Lab queries',(145,370))
d.arrow([(880,290),(880,345),(1190,345),(1190,400)])
d.arrow([(700,475),(900,475)],'Zone transfers',(709,449))
d.box(120,675,580,135,'Proxmox SDN DNS integration',['Each host tunnels localhost:18081 to API','Registration depends on provisioning workflow'],BLUE)
d.arrow([(410,675),(410,545)])
d.box(900,675,580,135,'Kubernetes CoreDNS • 10.112.0.10',['Internal Service names: cluster.local','No external-dns controller installed'],BLUE)
d.footer(['Unbound sends external questions back to Upstream router. Keep Upstream router lab forwarding conditional to avoid a DNS loop.',
          'Application A records are operator-managed. Forward only the two lab reverse prefixes, not the whole 10/8 tree.'])
d.save('03-dns-workflow')

d=Diagram('Build and verify the deployment','A reader workflow reconstructed from the runbooks • not a claim about the original command-by-command history',1030)
steps=[('1  Prepare Proxmox',['Migrate Ceph-dependent disks','Upgrade and verify quorum']),
       ('2  Verify the underlay',['10.255.255.1 ↔ 10.255.255.2','10 GbE • MTU 9000']),
       ('3  Configure EVPN / VNets',['Controller → zone → VNets','Apply; test across hosts']),
       ('4  Build DNS and routing',['Primary / secondary + Unbound','Upstream router routes and forwards']),
       ('5  Provision Rocky nodes',['Cloud-init • static addresses','Prepare runtime → kubeadm → Cilium']),
       ('6  Verify Kubernetes',['Nodes Ready; Cilium healthy','Cross-node pod traffic and DNS']),
       ('7  Deploy applications',['Wiki static build; Example site NFS','Services and readiness checks']),
       ('8  Publish and validate',['Gateway + VIP + TLS + policy','Test before DNS; verify failover'])]
coords=[(60,180),(570,180),(1080,180),(1080,435),(570,435),(60,435),(60,690),(570,690)]
for (title,lines),(x,y) in zip(steps,coords): d.box(x,y,460,140,title,lines)
for a,b in [([(520,250),(570,250)],None), ([(1030,250),(1080,250)],None), ([(1310,320),(1310,435)],None), ([(1080,505),(1030,505)],None), ([(570,505),(520,505)],None), ([(290,575),(290,690)],None), ([(520,760),(570,760)],None)]: d.arrow(a)
d.box(1080,690,460,140,'Then protect and operate',['Current backups / restore drills','Maintenance and monitoring'],ORANGE)
d.arrow([(1030,760),(1080,760)])
d.footer(['Retain configuration after each checkpoint. Back up stateful data separately from application manifests.',
          'Bootstrap/wiki code was lab-tested; public address and hostname substitutions require your own validation.'])
d.save('04-deployment-workflow')

d=Diagram('Re-IP the lab in stages','Illustrative staged migration • 198.51.100.0/24 → 192.0.2.0/24',930)
reip=[('1  Admin workstation second NIC',['Add the NIC before changing','the rest of the environment']),
      ('2  Switch management IP',['Update the switch address','before moving the gateway']),
      ('3  Network gateway',['Move the network gateway','to the new addressing']),
      ('4  NFS / Proxmox / workloads',['Update hosts manually; use tooling','to update dependent systems']),
      ('5  Monitoring and other servers',['Update Grafana / Prometheus targets','Re-IP the remaining servers'])]
for title,lines,x,y in [(reip[0][0],reip[0][1],60,180),(reip[1][0],reip[1][1],570,180),(reip[2][0],reip[2][1],1080,180),(reip[3][0],reip[3][1],1080,460),(reip[4][0],reip[4][1],570,460)]:
    d.box(x,y,460,150,title,lines)
d.arrow([(520,255),(570,255)])
d.arrow([(1030,255),(1080,255)])
d.arrow([(1310,330),(1310,460)])
d.arrow([(1080,535),(1030,535)])
d.box(60,460,460,150,'Reader verification',['Check storage, DNS, cluster health','and monitoring after changes'],ORANGE)
d.arrow([(570,535),(520,535)])
d.footer(['Illustrative migration order. Validate each dependency and record actual outages in your own environment.',
          'Second-NIC addresses, route selection, and exact switch/gateway cutover settings still need the original configuration.'])
d.save('05-reip-workflow')
print(f'Generated {len(list(OUT.glob("*.svg")))} SVGs and {len(list(OUT.glob("*.png")))} PNGs in {OUT}')
