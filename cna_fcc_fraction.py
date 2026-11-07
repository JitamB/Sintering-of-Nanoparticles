"""Adaptive common-neighbour analysis (same algorithm as OVITO default CNA), pure Python.
Usage: python3 cna_fcc_fraction.py 700 0 10 50 500     (T, then frame numbers = ps)
fcc: 12 neighbours within the local adaptive cutoff and all 12 bonds 421; hcp: 6x421 + 6x422; else other."""
import math,sys
from collections import defaultdict
K=(1+math.sqrt(2))/2
WANT=set(int(x) for x in sys.argv[2:])
def frames(path):
    with open(path) as f:
        k=0
        while True:
            l=f.readline()
            if not l:return
            f.readline();f.readline();n=int(f.readline());f.readline()
            for _ in range(3):f.readline()
            f.readline()
            if k in WANT:
                pos=[tuple(map(float,f.readline().split()[2:5])) for _ in range(n)]
                yield k,pos
                if k>=max(WANT):return
            else:
                for _ in range(n):f.readline()
            k+=1
def classify(pos):
    cell=5.0;g=defaultdict(list)
    for i,p in enumerate(pos):g[(int(p[0]//cell),int(p[1]//cell),int(p[2]//cell))].append(i)
    res=[]
    def nn(i):
        x,y,z=pos[i];cx,cy,cz=int(x//cell),int(y//cell),int(z//cell);c=[]
        for dx in(-1,0,1):
         for dy in(-1,0,1):
          for dz in(-1,0,1):
           for j in g.get((cx+dx,cy+dy,cz+dz),()):
            if j!=i:
              d=math.dist(pos[i],pos[j])
              if d<5.0:c.append((d,j))
        c.sort();return c[:14]
    for i in range(len(pos)):
        c=nn(i)
        if len(c)<12: res.append('other');continue
        scale=sum(d for d,_ in c[:12])/12*K
        nb=[j for d,j in c if d<=scale]
        if len(nb)!=12: res.append('other');continue
        nbset=set(nb);sig=[]
        ok=True
        for j in nb:
            cj=[k for k in nb if k!=j and math.dist(pos[j],pos[k])<=scale]
            if len(cj)!=4: ok=False;break
            bonds=[(a,b) for ai,a in enumerate(cj) for b in cj[ai+1:] if math.dist(pos[a],pos[b])<=scale]
            if len(bonds)!=2: ok=False;break
            chain=2 if len(set(bonds[0])&set(bonds[1]))>0 else 1
            sig.append(chain)
        if not ok:res.append('other');continue
        n1=sig.count(1);n2=sig.count(2)
        res.append('fcc' if n1==12 else 'hcp' if (n1==6 and n2==6) else 'other')
    return res
T=sys.argv[1]
for k,pos in frames(f"output/{T}K/traj_{T}.lammpstrj"):
    r=classify(pos);n=len(r)
    print(T,'t=%d ps'%k,'fcc %.3f hcp %.3f other %.3f'%(r.count('fcc')/n,r.count('hcp')/n,r.count('other')/n),flush=True)
