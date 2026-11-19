"""Pilot: toy semantic network + RAT-like items + simulated responses.
Breadth kernel: a(theta) = (1-theta) * sum_t theta^t (P^T)^t a0 = (1-theta) (I - theta P^T)^{-1} a0,
a geometric mixture over spreading steps (theta = spread breadth). Uniform decay drops out of the
relative pattern, so it is not a parameter here.
Response: choose among K candidate words or 'no answer' with softmax(gamma * log a_k(theta_i)), no-answer utility kappa.
"""
import numpy as np, scipy.sparse as sp, scipy.sparse.linalg as spl, json, sys, os
rng=np.random.default_rng(int(sys.argv[1]) if len(sys.argv)>1 else 7)
out=os.path.dirname(os.path.abspath(__file__))
n, k_ring, p_rewire = 3000, 8, 0.1
# Watts-Strogatz small world with random weights
rows,cols=[],[]
for i in range(n):
    for d in range(1,k_ring//2+1):
        j=(i+d)%n
        if rng.random()<p_rewire: j=int(rng.integers(n))
        if j!=i: rows+= [i,j]; cols+=[j,i]
W=sp.coo_matrix((rng.uniform(.1,1,len(rows)),(rows,cols)),shape=(n,n)).tocsr(); W.sum_duplicates()
deg=np.asarray(W.sum(1)).ravel(); P=sp.diags(1/deg)@W            # row-stochastic
PT=P.T.tocsc()
J,K=40,20
grid=np.linspace(-4,4,33); thetas=1/(1+np.exp(-grid))
I=sp.identity(n,format='csc')
items=[]; L=np.zeros((J,K,len(grid)))
# first pick all items (answer + 3 cues), then solve all right-hand sides per grid point with one factorization
specs=[]
for j in range(J):
    ans=int(rng.integers(n))
    frontier={ans}; seen={ans}; layers=[]
    for _ in range(3):
        nxt=set()
        for u in frontier: nxt|=set(W[u].indices.tolist())
        nxt-=seen; seen|=nxt; layers.append(list(nxt)); frontier=nxt
    cues=[]
    for c in range(3):
        lay=layers[0] if (rng.random()<0.7 or len(layers[1])==0) else layers[1]
        cand_c=[x for x in lay if x not in cues]
        cues.append(int(rng.choice(cand_c)))
    specs.append((ans,cues))
# RAT answers are strong associates of each cue: strengthen answer-cue edges, then rebuild P
W=W.tolil()
for ans,cues in specs:
    for c in cues: W[ans,c]=W[c,ans]=float(rng.uniform(1.5,3.0))
W=W.tocsr(); deg=np.asarray(W.sum(1)).ravel(); P=sp.diags(1/deg)@W; PT=P.T.tocsc()
B=np.zeros((n,J))
for j,(ans,cues) in enumerate(specs): B[cues,j]=1/3
A=np.zeros((len(grid),n,J))
for g,th in enumerate(thetas):
    lu=spl.splu((I-th*PT).tocsc())
    A[g]=(1-th)*lu.solve(B)
for j,(ans,cues) in enumerate(specs):
    mid=A[len(grid)//2,:,j].copy(); mid[cues]=-1; mid[ans]=-1
    cand=[ans]+np.argsort(-mid)[:K-1].tolist()
    L[j]=np.log(np.maximum(A[:,cand,j].T,1e-300))
    items.append({'answer':ans,'cues':cues,'cand':cand})
# simulate people
N=int(sys.argv[2]) if len(sys.argv)>2 else 60
mu,sigma,gamma,kappa=0.0,1.0,2.0,None
lt=rng.normal(mu,sigma,N); 
def interp(Ljk,x): return np.interp(x,grid,Ljk)
# set kappa so that average no-answer rate ~ .3 at theta=mid
Lmid=L[:,:,len(grid)//2]; kappa=float(np.quantile(gamma*Lmid[:,0],0.4))
Y=np.zeros((N,J),int); corr=np.zeros((N,J),int)
for i in range(N):
    for j in range(J):
        u=np.array([kappa]+[gamma*interp(L[j,k],lt[i]) for k in range(K)])
        p=np.exp(u-u.max()); p/=p.sum(); y=rng.choice(K+1,p=p); Y[i,j]=y; corr[i,j]=int(y==1)
json.dump({'N':N,'J':J,'K':K,'G':len(grid),'grid':grid.tolist(),'L':L.tolist(),'y':(Y+1).tolist()},open(os.path.join(out,'pilot_data.json'),'w'))
json.dump({'logit_theta':lt.tolist(),'mu':mu,'sigma':sigma,'gamma':gamma,'kappa':kappa},open(os.path.join(out,'pilot_truth.json'),'w'))
print('accuracy %.2f | no-answer %.2f | wrong %.2f | kappa %.2f'%(corr.mean(),(Y==0).mean(),((Y>1)).mean(),kappa))
print('corr(true breadth, accuracy) = %.2f'%np.corrcoef(lt,corr.mean(1))[0,1])
