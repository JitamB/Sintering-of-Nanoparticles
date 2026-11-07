"""Misorientation between the two particles about z, from the trajectory.

Usage: python3 misorientation.py 700      (pure Python, ~2-3 min per temperature)

Particle 1 = atom ids 1..3997, particle 2 = ids 3998..7994 (Atomsk merge order).
For each particle, take the nearest-neighbour bonds that lie in the xy-plane
(|dz| < 0.7 A, 2.3 < length < 3.4 A). In an fcc crystal with [001] along z these
bonds point along [110]-type directions, which repeat every 90 deg, so the
particle's orientation is the circular mean of 4*angle, divided by 4.
Misorientation = angle(P2) - angle(P1), wrapped to (-45, 45] deg.
Prints: T, time(ps), angle P1, angle P2, misorientation, bonds used (P1, P2).
Only rotation about z is measured; tilts about x or y are not.
"""
from collections import defaultdict
WANT=set(list(range(0,30,2))+list(range(30,100,5))+list(range(100,501,25))+[1,3,5,8,13,15])
N1=3997
def frames(path):
    with open(path) as f:
        while True:
            l=f.readline()
            if not l: return
            step=int(f.readline()); f.readline(); n=int(f.readline()); f.readline()
            box=[tuple(map(float,f.readline().split())) for _ in range(3)]
            f.readline()
            pos={}
            for _ in range(n):
                w=f.readline().split(); pos[int(w[0])]=(float(w[2]),float(w[3]),float(w[4]))
            yield step,pos
def angle(pos,ids):
    cell=3.4; g=defaultdict(list)
    for i in ids:
        x,y,z=pos[i]; g[(int(x//cell),int(y//cell),int(z//cell))].append(i)
    sx=sy=0.0;nb=0
    for i in ids:
        x,y,z=pos[i];cx,cy,cz=int(x//cell),int(y//cell),int(z//cell)
        for dx in(-1,0,1):
          for dy in(-1,0,1):
            for dz in(-1,0,1):
              for j in g.get((cx+dx,cy+dy,cz+dz),()):
                if j<=i: continue
                u=pos[j][0]-x;v=pos[j][1]-y;w=pos[j][2]-z
                if abs(w)<0.7 and 2.3<math.hypot(u,v)<3.4:
                    t=4*math.atan2(v,u);sx+=math.cos(t);sy+=math.sin(t);nb+=1
    return math.degrees(math.atan2(sy,sx))/4,nb   # in-plane NN bonds repeat every 90 deg
T=sys.argv[1]
ids1=range(1,N1+1);ids2=range(N1+1,2*N1+1)
for k,(step,pos) in enumerate(frames(f"output/{T}K/traj_{T}.lammpstrj")):
    t=k  # 1 ps per frame
    if t not in WANT: continue
    a1,n1=angle(pos,ids1);a2,n2=angle(pos,ids2)
    d=(a2-a1+45)%90-45
    print(T,t,round(a1,1),round(a2,1),round(d,1),n1,n2,flush=True)
