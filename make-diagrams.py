"""Editable SVG figures and high-resolution PNGs for the Proxmox lab series."""
from pathlib import Path
from html import escape
import subprocess

OUT = Path(__file__).parent / 'diagrams'
OUT.mkdir(exist_ok=True)
INK, MUTED, TEAL, BLUE, AMBER = '#142f3d', '#536a76', '#087e80', '#2a62a2', '#9b6225'
BG, LINE = '#f7f9f7', '#d5dfdf'

class Figure:
    def __init__(self, number, title, subtitle, height=1000):
        self.h = height
        self.p = [f'<svg xmlns="http://www.w3.org/2000/svg" width="1400" height="{height}" viewBox="0 0 1400 {height}" role="img">',f'<title>{escape(title)}</title><desc>{escape(subtitle)}</desc>',
          '<defs><marker id="arr" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto-start-reverse"><path d="M0 0L10 5L0 10Z" fill="#536a76"/></marker></defs>',
          f'<rect width="1400" height="{height}" fill="{BG}"/>']
        self.text(52,48,'PROXMOX LAB  /  PART 2',18,TEAL,'700')
        self.text(1348,48,number,18,TEAL,'700','end')
        self.text(52,104,title,39,INK,'700')
        self.text(52,145,subtitle,23,MUTED)
    def text(self,x,y,t,size=24,color=INK,weight='400',anchor='start'):
        self.p.append(f'<text x="{x}" y="{y}" font-family="DejaVu Sans,sans-serif" font-size="{size}" font-weight="{weight}" fill="{color}" text-anchor="{anchor}">{escape(t)}</text>')
    def panel(self,x,y,w,h,title,color=BLUE):
        self.p.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="16" fill="#edf2f3" stroke="{LINE}" stroke-width="2"/>')
        self.text(x+24,y+40,title,27,color,'700')
    def box(self,x,y,w,h,title,lines=(),color=TEAL):
        self.p.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="10" fill="white" stroke="{LINE}" stroke-width="2"/><rect x="{x}" y="{y+12}" width="5" height="{h-24}" rx="2" fill="{color}"/>')
        self.text(x+22,y+37,title,25,color,'700')
        for i,t in enumerate(lines):self.text(x+22,y+73+i*31,t,22)
    def arrow(self,points,both=False,dash=False):
        points=' '.join(f'{x},{y}' for x,y in points)
        extra=(' marker-start="url(#arr)"' if both else '')+(' stroke-dasharray="9 7"' if dash else '')
        self.p.append(f'<polyline points="{points}" fill="none" stroke="{MUTED}" stroke-width="3" marker-end="url(#arr)"{extra}/>')
    def footer(self,a,b=''):
        self.p.append(f'<path d="M52 {self.h-91}H1348" stroke="{LINE}" stroke-width="2"/>')
        self.text(52,self.h-55,a,20,MUTED)
        if b:self.text(52,self.h-25,b,20,MUTED)
    def save(self,name):
        f=OUT/(name+'.svg');f.write_text('\n'.join(self.p+['</svg>']))
        subprocess.run(['rsvg-convert','-w','2100','-o',str(OUT/(name+'.png')),str(f)],check=True)

f=Figure('01','Two physical hosts, six lab VMs','Installed topology • Management, the direct underlay and guest networks have separate roles.',1090)
f.box(52,191,610,124,'Firewalla  /  172.27.85.1',['10.50.10.0/24 and 10.50.20.0/24','Static next hop: pve1 at 172.27.85.11'],BLUE)
f.box(738,191,610,124,'QNAP  /  172.27.85.25',['Shared NFS and backup storage','Ledger: /NFS/kubernetes/architects-ledger'],AMBER)
f.text(700,351,'MANAGEMENT LAN  172.27.85.0/24',21,MUTED,'700','middle')
f.p.append(f'<path d="M170 374H1225 M360 315V374 M1038 315V374" fill="none" stroke="{MUTED}" stroke-width="3"/>')
f.arrow([(170,374),(170,405)])
f.arrow([(1225,374),(1225,405)])
f.panel(52,405,610,436,'pve1  /  172.27.85.11')
f.panel(738,405,610,436,'pve2  /  172.27.85.12')
for x,rows in [(76,[('dns1  ·  10.50.20.53','infranet · DNS primary + Unbound'),('cp1  ·  10.50.10.11','evpntest · API + single-member etcd'),('worker1  ·  10.50.10.12','evpntest · application workloads')]),(762,[('dns2  ·  10.50.20.54','infranet · DNS secondary + Unbound'),('worker2  ·  10.50.10.13','evpntest · application workloads'),('worker3  ·  10.50.10.14','evpntest · workloads + selected egress')])]:
    for n,(title,line) in enumerate(rows):f.box(x,467+n*105,562,92,title,[line])
f.text(76,814,'VM disks: NVMe-Local-1',21,MUTED)
f.text(762,814,'VM disks: NVMe-Local-2',21,MUTED)
f.box(253,878,894,95,'Direct 10 GbE  /  enp1s0f1  /  MTU 9000',['10.0.0.1/30  ↔  10.0.0.2/30  ·  BGP EVPN + VXLAN'],BLUE)
f.arrow([(358,841),(358,878)],both=True);f.arrow([(1043,841),(1043,878)],both=True)
f.footer('evpn1: VRF VNI 10000  ·  infranet: VNI 10001  ·  evpntest: VNI 10002','Guest and pod MTU 1500. The primary exit, control plane, direct cable and storage remain dependencies.')
f.save('01-network-topology')

f=Figure('02','One VIP, two HTTPS backends','Installed websites • The elected worker and the application pod can be different nodes.',1070)
f.box(52,196,550,136,'Client uses lab DNS',['wiki.lab.local · ledger.lab.local','Both return 10.50.10.100'],BLUE)
f.box(798,196,550,136,'Firewalla routes to pve1',['172.27.85.11 → evpn1 → evpntest'],BLUE)
f.arrow([(602,253),(798,253)])
f.box(370,388,660,140,'Cilium Gateway  /  10.50.10.100',['LB-IPAM allocates · one worker answers ARP','Cilium Envoy selects the application by hostname'])
f.arrow([(1073,332),(1073,354),(890,354),(890,388)])
f.box(52,626,610,185,'wiki.lab.local  /  TLS passthrough',['TLSRoute → lab-wiki Service :443','Nginx terminates TLS on container port 8443','Two replicas across pve1 / pve2'])
f.box(738,626,610,185,'ledger.lab.local  /  TLS termination',['Certificate at Cilium · HTTPRoute selects backend','ledger-web Service :80 → web pods','Three web replicas · shared NFS'],BLUE)
f.arrow([(535,528),(535,576),(357,576),(357,626)]);f.arrow([(865,528),(865,576),(1043,576),(1043,626)])
f.text(700,867,'cp1 API supports Lease elections  ·  externalTrafficPolicy: Cluster',23,AMBER,'700','middle')
f.text(700,910,'HTTP redirects to HTTPS. Gateway source policy permits the intended LAN / VPN ranges.',21,MUTED,'400','middle')
f.footer('Worker-pause test: new holder observed at 22.1 s; both HTTPS sites returned 200 by 38 s.','A new announcer does not remove Firewalla’s fixed upstream next hop through pve1.')
f.save('02-application-access')

f=Figure('03','Lab DNS, from client to authority','Query routing, authoritative records, replication and Kubernetes Service discovery.',1130)
f.box(52,200,500,124,'LAN / VPN clients',['Use Firewalla for lab resolution','Lab names and reverse /24 prefixes'],BLUE)
f.box(738,200,610,124,'Firewalla  /  172.27.85.1',['Lab questions → dns1 and dns2','Public questions → configured external resolution'],BLUE)
f.arrow([(552,262),(738,262)])
f.box(52,435,610,178,'dns1  /  10.50.20.53',['Unbound :53 answers clients','Local lab questions → PowerDNS :5300','Writable primary; API on loopback :8081'])
f.box(738,435,610,178,'dns2  /  10.50.20.54',['Unbound :53 answers clients','Local lab questions → PowerDNS :5300','Secondary; receives signed zone transfers'])
f.arrow([(937,324),(937,377),(357,377),(357,435)]);f.arrow([(1110,324),(1110,435)])
f.text(700,659,'Primary → secondary: signed transfers of lab.local and 10.in-addr.arpa',21,MUTED,'400','middle')
f.box(52,750,610,156,'Proxmox SDN / IPAM',['Host-local tunnel → dns1 management API','Registration depends on provisioning workflow','Static cloud-init alone does not publish a record'],BLUE)
f.box(738,750,610,156,'Kubernetes CoreDNS  /  10.96.0.10',['Owns Service names under cluster.local','Other queries use the internal resolver pair','No external-dns controller publishes lab names'],BLUE)
f.arrow([(355,750),(355,690),(220,690),(220,613)],dash=True)
f.arrow([(1045,750),(1045,613)],dash=True)
f.footer('Unbound’s public upstream is Firewalla. Keep Firewalla’s lab forwarding conditional to avoid a loop.','Forward reverse 20.50.10.in-addr.arpa and 10.50.10.in-addr.arpa; do not redirect the entire 10/8 tree.')
f.save('03-dns-workflow')

f=Figure('04','Publish a wiki revision you can roll back','The source is durable; each pod reconstructs the generated site.',1040)
st=[(52,205,'1  Edit the Markdown',['Keep sources and dependency lock','Review content and links']), (738,205,'2  Build with strict checks',['MkDocs → generated HTML and assets','Keep private material outside the build']), (738,440,'3  Package the revision',['Compressed archive → immutable ConfigMaps','Digest-pinned Nginx image']), (52,440,'4  Validate and deploy',['Server-side dry run, then apply','Init container unpacks into emptyDir']), (52,675,'5  Verify the result',['Two physical-host placements','Check content, TLS and HTTP redirect']), (738,675,'6  Update or roll back',['Publish another content revision','Retain old ConfigMaps for rollout undo'])]
for x,y,t,lines in st:f.box(x,y,610,149,t,lines)
f.arrow([(662,276),(738,276)]);f.arrow([(1043,354),(1043,440)]);f.arrow([(738,515),(662,515)]);f.arrow([(357,589),(357,675)]);f.arrow([(662,750),(738,750)])
f.footer('The publisher manages wiki content and workload resources. TLS Secrets and Gateway configuration are separate.','Deployment rollback does not restore a changed shared ConfigMap, certificate, Gateway or DNS record.')
f.save('04-deployment-workflow')

f=Figure('05','Re-IP the lab while retaining an access path','192.168.1.0/24 → 172.27.85.0/24  ·  Prompted by overlapping networks while on VPN.',1080)
rows=[('1','Give RougarouOS a second NIC','Checkpoint: console access and the intended route are available.'),('2','Change the switch management address','Checkpoint: reach the switch on its new management address.'),('3','Move the network gateway','Checkpoint: management routing and external DNS / HTTPS work.'),('4','Move NFS, Proxmox and other workloads','Proxmox nodes: manual changes, about one hour of work.'),('5','Update monitoring and remaining servers','Checkpoint: revise targets, DNS, storage references and inventory.')]
for i,(n,t,sub) in enumerate(rows):
 y=196+i*151
 f.p.append(f'<circle cx="91" cy="{y+49}" r="30" fill="{TEAL}"/>');f.text(91,y+58,n,27,'white','700','middle')
 f.box(154,y,1194,119,t,[sub],BLUE)
 if i<4:f.arrow([(91,y+80),(91,y+121)])
f.footer('Sequence from the author’s account. Checkpoints are guidance for repeating it, not recovered command history.','The one-hour estimate covers manual Proxmox re-IP work; it is not a measured service-outage duration.')
f.save('05-reip-workflow')

f=Figure('06','Follow one cross-host pod packet','Same Kubernetes VNet, two physical hosts. Proxmox supplies the VXLAN crossing.',1030)
f.panel(52,201,610,514,'Source: worker1 on pve1')
f.panel(738,201,610,514,'Destination: worker2 on pve2')
f.box(76,270,562,112,'Source pod',['Pod range on worker1: 10.244.3.0/24'])
f.box(762,270,562,112,'Destination pod',['Pod range on worker2: 10.244.2.0/24'])
f.box(76,433,562,112,'Cilium native routing',['Node 10.50.10.12 → peer 10.50.10.13'])
f.box(762,433,562,112,'Cilium / Linux routing',['Node 10.50.10.13 → local destination pod'])
f.box(76,596,562,89,'Proxmox VNet: evpntest',[],BLUE)
f.box(762,596,562,89,'Proxmox VNet: evpntest',[],BLUE)
f.arrow([(357,382),(357,433)]);f.arrow([(357,545),(357,596)])
f.arrow([(1043,596),(1043,545)]);f.arrow([(1043,433),(1043,382)])
f.box(253,775,894,112,'VXLAN VNI 10002 over the direct cable',['Outer IP: 10.0.0.1 → 10.0.0.2  ·  Underlay MTU 9000'],BLUE)
f.arrow([(357,685),(357,775)]);f.arrow([(1043,775),(1043,685)])
f.footer('Guest / pod MTU 1500. Cilium adds no second VXLAN tunnel in the deployed native-routing mode.','The BGP EVPN session distributes reachability; the application’s data crosses the cable in VXLAN packets.')
f.save('06-packet-path')

# Cover uses the author's original RougarouOS terminal wolf, supplied as text.
cover_bg, cover_ink, cover_green = '#0b2025', '#edf5ed', '#96cba7'
f=Figure('SERIES 02','Proxmox lab series, Part 2','EVPN and Kubernetes with Codex and GPT on RougarouOS',790)
f.p=[f'<svg xmlns="http://www.w3.org/2000/svg" width="1400" height="790" viewBox="0 0 1400 790" role="img"><title>My two-node Proxmox lab, Part 2</title><desc>The original RougarouOS terminal wolf beside the article title. EVPN and Kubernetes, built with Codex and GPT.</desc><rect width="1400" height="790" fill="{cover_bg}"/>']
f.text(70,76,'THE PROXMOX LAB SERIES',22,cover_green,'700')
f.text(1330,76,'PART 02',22,cover_green,'700','end')
f.text(70,193,'A new chapter for',46,cover_ink,'400')
f.text(70,271,'my two-node lab.',64,cover_ink,'700')
f.text(70,365,'EVPN + Kubernetes',42,cover_green,'700')
f.text(70,445,'Built with Codex and GPT',30,cover_ink)
f.text(70,492,'on RougarouOS',30,cover_ink)
f.text(70,571,'About a week of building, testing and documenting.',22,'#aac0bb')
f.p.append('<path d="M817 159V597" stroke="#30524f" stroke-width="2"/>')
for i,row in enumerate((Path(__file__).parent/'assets/wolf.txt').read_text().splitlines()):
    f.p.append(f'<text xml:space="preserve" x="839" y="{173+i*21}" font-family="DejaVu Sans Mono,monospace" font-size="18" fill="{cover_green}">{escape(row)}</text>')
f.p.append('<path d="M70 653H1330" stroke="#30524f" stroke-width="2"/>')
f.text(70,704,'PART 1  Ceph, Podman and Pi quorum  →  PART 2  EVPN and Kubernetes',22,cover_ink)
f.text(70,748,'NEXT  Boot-drive replacement + Keepalived / VRRP + routing through pve2',22,cover_green)
f.save('00-series-cover')
print('Rendered branded cover and six diagrams as SVG and 2100px PNG.')
