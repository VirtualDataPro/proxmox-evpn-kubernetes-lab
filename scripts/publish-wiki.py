#!/usr/bin/env python3
"""Build a nonsecret Kubernetes manifest from an already-built MkDocs site.

Usage: publish-wiki.py SITE HOSTNAME IMAGE > wiki-resources.json
Requires an existing lab-wiki/wiki-tls Secret. Does not generate/upload secrets.
"""
import base64,hashlib,io,json,pathlib,sys,tarfile
site=pathlib.Path(sys.argv[1]);hostname=sys.argv[2];image=sys.argv[3]
assert (site/'index.html').is_file()
assert '@sha256:' in image, 'Pin the Nginx image digest'
assert all(c.isalnum() or c in '.-' for c in hostname)
buf=io.BytesIO()
with tarfile.open(fileobj=buf,mode='w:gz') as archive:
 for path in sorted(site.rglob('*')):
  if path.is_file():
   content=path.read_bytes()
   assert b'PRIVATE KEY-----' not in content, 'Private key found in site'
   archive.add(path,arcname=str(path.relative_to(site)),recursive=False)
content=buf.getvalue();revision=hashlib.sha256(content).hexdigest()[:12]
ns='lab-wiki';labels={'app':'lab-wiki'}
def meta(name):return {'name':name,'namespace':ns,'labels':labels}
items=[{'apiVersion':'v1','kind':'Namespace','metadata':{'name':ns}}];sources=[]
for i,start in enumerate(range(0,len(content),600000)):
 name=f'wiki-content-{revision}-{i}';key=f'part-{i:03d}'
 items.append({'apiVersion':'v1','kind':'ConfigMap','metadata':meta(name),'immutable':True,'binaryData':{key:base64.b64encode(content[start:start+600000]).decode()}})
 sources.append({'configMap':{'name':name}})
nginx=f'''pid /tmp/nginx.pid;
error_log /dev/stderr warn;
events {{ worker_connections 1024; }}
http {{
 include /etc/nginx/mime.types;
 default_type application/octet-stream;
 access_log /dev/stdout;
 client_body_temp_path /tmp/client_temp;
 proxy_temp_path /tmp/proxy_temp;
 fastcgi_temp_path /tmp/fastcgi_temp;
 uwsgi_temp_path /tmp/uwsgi_temp;
 scgi_temp_path /tmp/scgi_temp;
 server {{
  listen 8443 ssl;
  server_name {hostname};
  absolute_redirect off;
  ssl_certificate /tls/tls.crt;
  ssl_certificate_key /tls/tls.key;
  ssl_protocols TLSv1.2 TLSv1.3;
  root /site;
  index index.html;
  location / {{ try_files $uri $uri/ =404; }}
 }}
}}
'''
items.append({'apiVersion':'v1','kind':'ConfigMap','metadata':meta('wiki-nginx'),'data':{'nginx.conf':nginx}})
security={'allowPrivilegeEscalation':False,'readOnlyRootFilesystem':True,'capabilities':{'drop':['ALL']}}
resources={'requests':{'cpu':'25m','memory':'32Mi'},'limits':{'cpu':'250m','memory':'128Mi'}}
pod={'automountServiceAccountToken':False,'securityContext':{'runAsUser':101,'runAsGroup':101,'runAsNonRoot':True,'fsGroup':101,'seccompProfile':{'type':'RuntimeDefault'}},
 'affinity':{'podAntiAffinity':{'requiredDuringSchedulingIgnoredDuringExecution':[{'labelSelector':{'matchLabels':labels},'topologyKey':'topology.kubernetes.io/zone'}]}},
 'topologySpreadConstraints':[{'maxSkew':1,'topologyKey':'topology.kubernetes.io/zone','whenUnsatisfiable':'DoNotSchedule','labelSelector':{'matchLabels':labels}}],
 'initContainers':[{'name':'unpack-site','image':image,'command':['/bin/sh','-c','cat /archive/part-* | tar xzf - -C /site'],'securityContext':security,'resources':resources,'volumeMounts':[{'name':'archive','mountPath':'/archive','readOnly':True},{'name':'site','mountPath':'/site'}]}],
 'containers':[{'name':'nginx','image':image,'command':['nginx','-g','daemon off;'],'securityContext':security,'resources':resources,'ports':[{'name':'https','containerPort':8443}],'readinessProbe':{'httpGet':{'path':'/','port':'https','scheme':'HTTPS'},'periodSeconds':5},'volumeMounts':[{'name':'site','mountPath':'/site','readOnly':True},{'name':'config','mountPath':'/etc/nginx/nginx.conf','subPath':'nginx.conf','readOnly':True},{'name':'tls','mountPath':'/tls','readOnly':True},{'name':'tmp','mountPath':'/tmp'}]}],
 'volumes':[{'name':'archive','projected':{'sources':sources}},{'name':'site','emptyDir':{}},{'name':'tmp','emptyDir':{}},{'name':'config','configMap':{'name':'wiki-nginx'}},{'name':'tls','secret':{'secretName':'wiki-tls','defaultMode':288}}]}
items.extend([{'apiVersion':'apps/v1','kind':'Deployment','metadata':meta('lab-wiki'),'spec':{'replicas':2,'strategy':{'type':'RollingUpdate','rollingUpdate':{'maxSurge':0,'maxUnavailable':1}},'selector':{'matchLabels':labels},'template':{'metadata':{'labels':labels,'annotations':{'wiki-content-revision':revision,'nginx-config-hash':hashlib.sha256(nginx.encode()).hexdigest()}},'spec':pod}}},
 {'apiVersion':'v1','kind':'Service','metadata':meta('lab-wiki'),'spec':{'selector':labels,'ports':[{'name':'https','port':443,'targetPort':'https'}]}},
 {'apiVersion':'policy/v1','kind':'PodDisruptionBudget','metadata':meta('lab-wiki'),'spec':{'minAvailable':1,'selector':{'matchLabels':labels}}}])
print(json.dumps({'apiVersion':'v1','kind':'List','items':items},indent=2))
