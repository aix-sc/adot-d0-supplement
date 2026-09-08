import numpy as np, pandas as pd
COLS=['k5','k10','k15','k20','k25','k30','k35','k40','finish']; DIST=np.array([5,5,5,5,5,5,5,5,2.195])
def to_min(t):
    p=[int(x) for x in str(t).split(':')]
    if len(p)==2: p=[0]+p
    return p[0]*60+p[1]+p[2]/60
d=pd.read_csv('extract_v11.csv'); d=d[d.nat=='JPN'].copy()
for c in COLS+['half']: d[c+'_m']=d[c].map(to_min)
d['fin_m']=d.finish_m; d['r']=(d.fin_m-d.half_m)/d.half_m
d=d[(d.half_m>50)&(d.fin_m>110)&(d.fin_m<480)&(d.r>0.8)&(d.r<2.5)]
cum=d[[c+'_m' for c in COLS]].values
seg=np.diff(np.concatenate([np.zeros((len(d),1)),cum],axis=1),axis=1); pace=seg/DIST; q=pace/pace[:,1:4].mean(axis=1,keepdims=True)
for i in range(9): d[f'q{i+1}']=q[:,i]
d.to_csv('derived_v11.csv',index=False)
print('n',len(d),' by sex',d.sex.value_counts().to_dict())
bands=[(128,160,'2:08-2:40'),(160,180,'2:40-3:00'),(180,210,'3:00-3:30'),(210,240,'3:30-4:00'),(240,300,'4:00-5:00'),(300,420,'5:00-7:00')]
d['band']=d.fin_m.map(lambda x: next((l for lo,hi,l in bands if lo<=x<hi),None))
pd.set_option('display.width',220)
QC=[f'q{i}' for i in range(1,10)]
print('\n[1] median relative pace q_s by race x band (normalised to mean pace of 5-20 km; q1 = start segment incl. gun-to-line delay)')
for sex in ['M','F']:
    print(f'\n== {sex} ==')
    g=d[d.sex==sex].groupby(['race','band'])
    t=g[QC].median().round(3); t['n']=g.size(); t=t[t.n>=30]
    print(t.to_string())
print('\n[2] Nagoya 2022 women by finish band (peak-and-decline)')
n22=d[(d.race=='NagoyaWomen')&(d.year==2022)]
fb=[(180,240,'3:00-4:00'),(240,270,'4:00-4:30'),(270,300,'4:30-5:00'),(300,330,'5:00-5:30'),(330,360,'5:30-6:00'),(360,420,'6:00-7:00')]
n22=n22.assign(fb=n22.fin_m.map(lambda x: next((l for lo,hi,l in fb if lo<=x<hi),None)))
g=n22.groupby('fb'); t=g[QC].median().round(3); t['n']=g.size(); print(t.to_string())
print('\n[3] Osaka men by finish band (steady slope beyond 4 h)')
om=d[(d.race=='OsakaMarathon')&(d.sex=='M')]
om=om.assign(fb=om.fin_m.map(lambda x: next((l for lo,hi,l in fb if lo<=x<hi),None)))
g=om.groupby('fb'); t=g[QC].median().round(3); t['n']=g.size(); print(t.to_string())
print('\n[4] Entry-standard fields: where does the fade start? median q_s, runners within 10 min inside the cutoff vs same band elsewhere')
for lab,race,sex,lo,hi in [('Fukuoka M 2:32-2:42',"Fukuoka",'M',152,162),('Betsudai M 2:32-2:42','Betsudai','M',152,162),('Osaka M 2:32-2:42','OsakaMarathon','M',152,162),
                           ('OsakaWomen F 3:00-3:10','OsakaWomen','F',180,190),('Nagoya F 3:00-3:10','NagoyaWomen','F',180,190),('Osaka F 3:00-3:10','OsakaMarathon','F',180,190)]:
    g=d[(d.race==race)&(d.sex==sex)&(d.fin_m>=lo)&(d.fin_m<hi)]
    print(f'{lab:24s} n={len(g):4d} ', ' '.join(f'{v:.3f}' for v in g[QC].median().values))
print('\n[5] first segment where q_s > 1.05 (median s*, 10 = never)')
qm=d[QC].values; d['sstar']=np.where((qm>1.05).any(axis=1),(qm>1.05).argmax(axis=1)+1,10)
print(d.groupby(['sex','race','band'])['sstar'].median().unstack('band').to_string())
