import numpy as np, pandas as pd, statsmodels.formula.api as smf, warnings; warnings.filterwarnings('ignore')
def to_min(t):
    p=[int(x) for x in str(t).split(':')]
    if len(p)==2: p=[0]+p
    return p[0]*60+p[1]+p[2]/60
d=pd.read_csv('extract_v10.csv'); d=d[d.nat=='JPN'].copy()
d['half_m']=d.half.map(to_min); d['fin_m']=d.finish.map(to_min)
d=d[(d.half_m>50)&(d.fin_m>110)&(d.fin_m<480)]
d['r']=(d.fin_m-d.half_m)/d.half_m; d=d[(d.r>0.8)&(d.r<2.5)]; d['edition']=d.race+d.year.astype(str)
def hm(m): return f'{int(m)//60}:{int(m)%60:02d}'
def slopes(g, pts, df=4):
    res=smf.ols(f"r ~ cr(fin_m, df={df}) + C(edition)",g).fit(); base=g.edition.iloc[0]
    out=[]
    for x in pts:
        y=res.predict(pd.DataFrame({'fin_m':[x-1,x+1],'edition':[base,base]})); out.append((y.iloc[1]-y.iloc[0])/2)
    return np.array(out)
rng=np.random.default_rng(20260908); B=300
targets=[('M','OsakaMarathon',[220,240,270,300,330,360]),('F','NagoyaWomen',[180,220,240,270,300,330,360,400]),
         ('M','Fukuoka',[130,145,160]),('F','OsakaWomen',[145,160,180]),('M','Betsudai',[145,180,200]),('F','OsakaMarathon',[240,300,360])]
rows=[]
for sex,race,pts in targets:
    g=d[(d.sex==sex)&(d.race==race)].copy(); lo,hi=g.fin_m.quantile(.01),g.fin_m.quantile(.99)
    pts=[p for p in pts if lo<=p<=hi]
    est=slopes(g,pts); e3=slopes(g,pts,3); e5=slopes(g,pts,5)
    boots=[]
    groups=[gg for _,gg in g.groupby('edition')]
    for b in range(B):
        samp=pd.concat([gg.sample(len(gg),replace=True,random_state=int(rng.integers(1e9))) for gg in groups])
        boots.append(slopes(samp,pts))
    boots=np.array(boots); lo_ci=np.percentile(boots,2.5,axis=0); hi_ci=np.percentile(boots,97.5,axis=0)
    for i,p in enumerate(pts):
        rows.append(dict(sex=sex,race=race,finish=hm(p),slope_df4=round(est[i],5),ci_lo=round(lo_ci[i],5),ci_hi=round(hi_ci[i],5),slope_df3=round(e3[i],5),slope_df5=round(e5[i],5)))
        print(f"{sex} {race:14s} {hm(p)}  {est[i]:+.5f} [{lo_ci[i]:+.5f},{hi_ci[i]:+.5f}]  df3 {e3[i]:+.5f} df5 {e5[i]:+.5f}")
pd.DataFrame(rows).to_csv('slopes_boot.csv',index=False)
