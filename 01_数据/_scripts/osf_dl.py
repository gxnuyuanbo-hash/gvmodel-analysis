import sys,json,os,urllib.request
root=sys.argv[1]; out=sys.argv[2]
def j(u): return json.load(urllib.request.urlopen(u))
def walk(u,dest):
    os.makedirs(dest,exist_ok=True)
    while u:
        d=j(u)
        for x in d['data']:
            a=x['attributes']; p=os.path.join(dest,os.path.basename(a['name']))
            if a['kind']=='folder': walk(x['relationships']['files']['links']['related']['href'],p)
            else:
                urllib.request.urlretrieve(x['links']['download'],p); print(p,os.path.getsize(p))
        u=d['links'].get('next')
walk(j(root)['data'][0]['relationships']['files']['links']['related']['href'],out)
