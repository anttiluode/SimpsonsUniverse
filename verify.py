import numpy as np, heapq, time

rng = np.random.default_rng(42)

# ---------- their exact pipeline ----------
def get_primes(n):
    out=[]; k=2
    while len(out)<n:
        if all(k%d for d in range(2,int(k**0.5)+1)): out.append(k)
        k+=1
    return np.array(out,float)

def build_adelic_lattice(seeds, max_composites=1200):
    base=np.log(seeds); heap=[(0.0,0)]; seen={0.0}; comp=[]
    while len(comp)<max_composites and heap:
        f,mi=heapq.heappop(heap); comp.append(f)
        for i in range(mi,len(base)):
            nf=f+base[i]; q=round(nf,7)
            if q not in seen: seen.add(q); heapq.heappush(heap,(nf,i))
    freqs=np.array(comp[1:]); amps=np.exp(-freqs/2.0)
    return freqs,amps

def build_universe(freqs,amps,t):
    z=np.zeros(len(t),dtype=np.complex128)
    for f,a in zip(freqs,amps): z+=a*np.exp(1j*f*t)
    return z

def find_scars(sig,t):
    mag=np.abs(sig)
    mi=np.where((mag[1:-1]<mag[:-2])&(mag[1:-1]<mag[2:]))[0]+1
    lm=np.convolve(mag,np.ones(50)/50,mode='same')
    deep=mi[mag[mi]<0.7*lm[mi]]
    out=[]
    for idx in deep:
        a,b,c=mag[idx-1],mag[idx],mag[idx+1]; d=a-2*b+c
        out.append(t[idx]+(0.5*(a-c)/d)*(t[1]-t[0]) if abs(d)>1e-10 else t[idx])
    return np.array(out)

def unfolded_variance(scars):
    if len(scars)<15: return None
    sp=np.diff(scars); w=min(20,len(sp)//2); unf=[]
    for i in range(len(sp)):
        s=max(0,i-w); e=min(len(sp),i+w)
        m=np.mean(sp[s:e])
        if m>0: unf.append(sp[i]/m)
    return np.var(unf)

t_arr=np.arange(10.0,1000.0,0.05)

def run_tower(seeds, levels=4, tag=""):
    res=[]
    cur=np.array(seeds,float)
    for lv in range(levels):
        freqs,amps=build_adelic_lattice(cur,1200)
        z=build_universe(freqs,amps,t_arr)
        scars=find_scars(z,t_arr)
        v=unfolded_variance(scars)
        res.append((lv,len(scars),v))
        print(f"  [{tag}] L{lv}: scars={len(scars)}, var={v:.4f}")
        if len(scars)>5: cur=scars[:60]
        else: break
    return res

print("="*70)
print("A. REPRODUCE THEIR SIMULATION (primes seed)")
run_tower(get_primes(40),4,"primes")

print("\nB. CALIBRATE: what does THEIR pipeline give for known ensembles?")
# True GUE: eigenvalues of large Hermitian matrix, central bulk
N=3000
H=rng.normal(size=(N,N))+1j*rng.normal(size=(N,N))
H=(H+H.conj().T)/2
ev=np.linalg.eigvalsh(H)
bulk=ev[N//4:3*N//4]
print(f"  GUE eigenvalues (bulk, n={len(bulk)}), their unfolding: var={unfolded_variance(bulk):.4f}")
# raw theoretical: sample Wigner GUE surmise spacings i.i.d.
# P(s)=(32/pi^2)s^2 exp(-4s^2/pi): sample via rejection
s=rng.chisquare(3,200000); s=np.sqrt(s*np.pi/8)  # chi_3 scaled: matches surmise
print(f"  GUE surmise i.i.d. spacings: raw var={np.var(s/np.mean(s)):.4f} (theory 3*pi/8-1={3*np.pi/8-1:.4f})")
# GOE
Hr=rng.normal(size=(N,N)); Hr=(Hr+Hr.T)/2
evr=np.linalg.eigvalsh(Hr); bulkr=evr[N//4:3*N//4]
print(f"  GOE eigenvalues (bulk), their unfolding: var={unfolded_variance(bulkr):.4f}")
# Poisson
pp=np.sort(rng.uniform(0,1000,1500))
print(f"  Poisson points, their unfolding: var={unfolded_variance(pp):.4f}")

print("\nC. CONTROL: random seeds instead of primes (same recursion)")
for trial in range(3):
    seeds=np.sort(rng.uniform(2,180,40))
    run_tower(seeds,3,f"rand{trial}")

print("\nD. CONTROL: NO recursion — one-shot generic incommensurate freqs")
for trial in range(3):
    freqs=np.sort(rng.uniform(0.5,7.5,1200)); amps=np.exp(-freqs/2)
    z=build_universe(freqs,amps,t_arr); sc=find_scars(z,t_arr)
    print(f"  generic freqs trial{trial}: scars={len(sc)}, var={unfolded_variance(sc):.4f}")

print("\nE. ALPHA cutoff dependence: Q^2=sum(1/S_k) and rho_vac vs domain/lattice size")
freqs,amps=build_adelic_lattice(get_primes(40),1200)
z0=build_universe(freqs,amps,t_arr); sc0=find_scars(z0,t_arr)
f1,a1=build_adelic_lattice(sc0[:60],1500)
for tmax in [500,1000,2000,4000]:
    ta=np.arange(10,tmax,0.05)
    z1=build_universe(f1,a1,ta)
    sc1=find_scars(z1,ta)
    Q2=np.sum(1.0/sc1); rho=np.mean(np.abs(z1)**2)
    print(f"  t_max={tmax}: scars={len(sc1)}, Q2={Q2:.3f}, rho_vac={rho:.3f}, alpha_bare={Q2/(4*np.pi*rho):.4f}")
