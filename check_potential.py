"""Independent check of Al99.eam.alloy (pure Python): a0, E_coh, bulk modulus, unrelaxed (111)/(100)/(110) surface energies.
Usage: python3 check_potential.py Al99.eam.alloy
Surface energy = sum over depth of (E_atom(depth, half-space neighbours) - E_bulk) per surface area."""
import math, itertools, sys
f=open(sys.argv[1]).read().split('\n')
nrho,drho,nr,dr,rc=f[4].split()[:5]; nrho=int(nrho);nr=int(nr);drho=float(drho);dr=float(dr);rc=float(rc)
vals=[]
for l in f[6:]: vals+= [float(x) for x in l.split()]
F=vals[:nrho]; rho=vals[nrho:nrho+nr]; z2r=vals[nrho+nr:nrho+2*nr]
print('nrho,drho,nr,dr,rc',nrho,drho,nr,dr,rc,'len',len(vals))
def interp(tab,x,h):
    p=x/h; i=int(p)
    if i<0: i=0
    if i>=len(tab)-2: return tab[-1] if i>=len(tab)-1 else tab[i]
    t=p-i
    # cubic Lagrange (4-pt)
    if i<1: i=1
    t=p-i
    y0,y1,y2,y3=tab[i-1],tab[i],tab[i+1],tab[i+2]
    return (y1+0.5*t*(y2-y0+t*(2*y0-5*y1+4*y2-y3+t*(3*(y1-y2)+y3-y0))))
def fr(r): return interp(rho,r,dr)
def phi(r): return interp(z2r,r,dr)/r
def Fe(x): return interp(F,x,drho)
def energy(dists):   # list of neighbour distances
    rh=sum(fr(r) for r in dists if r<rc); ph=sum(phi(r) for r in dists if r<rc)
    return Fe(rh)+0.5*ph
def lattice_pts(a,R):
    n=int(R/a)+2;pts=[]
    for i in range(-n,n+1):
      for j in range(-n,n+1):
        for k in range(-n,n+1):
          for b in ((0,0,0),(.5,.5,0),(.5,0,.5),(0,.5,.5)):
            p=((i+b[0])*a,(j+b[1])*a,(k+b[2])*a)
            if 0<math.dist(p,(0,0,0))<rc: pts.append(p)
    return pts
def Ebulk(a): return energy([math.hypot(*p) for p in lattice_pts(a,rc)])
best=min(((Ebulk(4.0+0.0025*i),4.0+0.0025*i) for i in range(0,41)))
print('min E (eV/atom) %.4f at a=%.4f'%best)
a0=best[1];E0=Ebulk(a0)
# refine
lo=a0-0.003;hi=a0+0.003
for _ in range(40):
    m1=lo+(hi-lo)/3;m2=hi-(hi-lo)/3
    if Ebulk(m1)<Ebulk(m2): hi=m2
    else: lo=m1
a0=(lo+hi)/2;E0=Ebulk(a0);print('a0=%.4f  Ecoh=%.4f eV'%(a0,-E0))
# bulk modulus: B = V d2E/dV2 ; V per atom=a^3/4
h=0.01
d2=(Ebulk(a0+h)-2*E0+Ebulk(a0-h))/h**2   # d2E/da2
# E(V), V=a^3/4: d2E/dV2 = (d2E/da2 - (dE/da)^2... at min dE/da=0) / (dV/da)^2
dVda=3*a0**2/4; V=a0**3/4
B=V*d2/dVda**2*160.2177   # GPa
print('bulk modulus B=%.1f GPa'%B)
# unrelaxed surface energies via semi-infinite crystal, per-atom energies by depth
def surf(hkl):
    n=math.sqrt(sum(x*x for x in hkl));nz=tuple(x/n for x in hkl)
    n_=int(rc/a0)+3
    allp=[]
    for i in range(-n_*2,n_*2+1):
      for j in range(-n_*2,n_*2+1):
        for k in range(-n_*2,n_*2+1):
          for b in ((0,0,0),(.5,.5,0),(.5,0,.5),(0,.5,.5)):
            p=((i+b[0])*a0,(j+b[1])*a0,(k+b[2])*a0)
            if math.dist(p,(0,0,0))<rc+1e-9: allp.append(p)
    zs=lambda p: p[0]*nz[0]+p[1]*nz[1]+p[2]*nz[2]
    levels=sorted(set(round(zs(p),6) for p in allp),reverse=True)
    # layer depths: distinct z-values below 0 spaced by d
    zset=sorted(set(round(zs(p),6) for p in allp if abs(zs(p))<rc))
    d=min(b-a for a,b in zip(zset,zset[1:]) if b-a>1e-3)
    A_atom=(a0**3/4)/d    # area per atom in a layer
    tot=0.0
    for depth in range(0,int(rc/d)+2):
        # atom at depth*d below surface; neighbours exist only with z_rel <= depth*d (i.e. below surface plane)
        ds=[math.hypot(*p) for p in allp if 0<math.hypot(*p)<rc and zs(p)<=depth*d+1e-3]
        tot+=energy(ds)-E0
    return tot/A_atom*16.0218, d
for hkl in ((1,1,1),(1,0,0),(1,1,0)):
    g,d=surf(hkl);print('unrelaxed gamma',hkl,'= %.3f J/m2  (layer spacing %.3f A)'%(g,d))
