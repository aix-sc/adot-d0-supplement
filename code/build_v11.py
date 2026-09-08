# -*- coding: utf-8 -*-
import re, subprocess, sys, pandas as pd, numpy as np
sys.path.insert(0, '.')
import build_v10 as b10
TIME = b10.TIME
def to_min(t):
    p=[int(x) for x in str(t).split(':')]
    if len(p)==2: p=[0]+p
    return p[0]*60+p[1]+p[2]/60
SPLIT_COLS=['k5','k10','k15','k20','half','k25','k30','k35','k40']
FILES = [
 ('results_別府大分2022_1621-7.pdf','Betsudai',2022,'M'),
 ('results_別府大分2023_1697-7.pdf','Betsudai',2023,'M'),
 ('results_別府大分2024_1807-7.pdf','Betsudai',2024,'M'),
 ('results_別府大分2025_1907-7.pdf','Betsudai',2025,'M'),
 ('results_別府大分2026_2001-7.pdf','Betsudai',2026,'M'),
 ('results_福岡国際2021_1585-7.pdf','Fukuoka',2021,'M'),
 ('results_福岡国際2022_1720-7.pdf','Fukuoka',2022,'M'),
 ('results_福岡国際2023_1790-7.pdf','Fukuoka',2023,'M'),
 ('results_福岡国際2024_1895-7.pdf','Fukuoka',2024,'M'),
 ('results_福岡国際2025_1987-7.pdf','Fukuoka',2025,'M'),
 ('results_大阪2022_1633-7.pdf','OsakaMarathon',2022,'M'),
 ('results_大阪2023_1721-7.pdf','OsakaMarathon',2023,'M'),
 ('results_大阪2024_1812-7.pdf','OsakaMarathon',2024,'M'),
 ('results_大阪2025_1915-7.pdf','OsakaMarathon',2025,'M'),
 ('results_大阪2026_website.pdf','OsakaMarathon',2026,'M'),
 ('results_大阪国際女子2022_1595-7.pdf','OsakaWomen',2022,'F'),
 ('results_大阪国際女子2023_1689-7.pdf','OsakaWomen',2023,'F'),
 ('results_大阪国際女子2024_1799-7.pdf','OsakaWomen',2024,'F'),
 ('results_大阪国際女子2025_1904-7.pdf','OsakaWomen',2025,'F'),
 ('results_大阪国際女子2026_1997-7.pdf','OsakaWomen',2026,'F'),
 ('results_名古屋ウィメンズ2022_result.pdf','NagoyaWomen',2022,'F'),
 ('名古屋ウェイメンズ2023_result.pdf','NagoyaWomen',2023,'F'),
 ('results_名古屋ウィメンズ2024_result.pdf','NagoyaWomen',2024,'F'),
 ('results_名古屋ウィメンズ2025_result.pdf','NagoyaWomen',2025,'F'),
 ('results_名古屋ウィメンズ2026_result.pdf','NagoyaWomen',2026,'F'),
]
def pick_run(ts):
    """return 10 tokens (5k..40k+half, finish) forming a strictly increasing plausible run, or None"""
    m=[to_min(t) for t in ts]
    best=None
    for i in range(0,len(m)-9):
        run=m[i:i+10]
        if all(run[j]<run[j+1] for j in range(9)) and 13<=run[0]<=50 and 100<=run[9]<=480 \
           and run[3]<run[4]<run[5] and 0.40<=run[4]/run[9]<=0.60:
            best=ts[i:i+10]; break
    return best
def parse(path,race,year,sex0):
    lines=subprocess.run(['pdftotext','-layout',path,'-'],capture_output=True,text=True).stdout.split('\n')
    cur,keep,rows=sex0,True,[]
    for i,ln in enumerate(lines):
        cur,keep=b10._sections(ln,cur,keep)
        if not keep or re.search(r'\sT1[12]\b',ln): continue
        ts=TIME.findall(re.sub(r'\([^)]*\)','',ln))
        if len(ts)<10: continue
        run=pick_run(ts)
        if run is None: continue
        nxt=lines[i+1] if i+1<len(lines) else ''
        nat=b10.natof(ln,nxt)
        if nat=='JPN' and '・' in ln[:46]: nat='FOR'
        row=dict(race=race,year=year,sex=cur,nat=nat,finish=run[9]); row.update(zip(SPLIT_COLS,run[:9]))
        rows.append(row)
    return pd.DataFrame(rows)
out=pd.concat([parse(*f) for f in FILES],ignore_index=True)
out=out[['race','year','sex','nat']+SPLIT_COLS+['finish']]
out.to_csv('extract_v11.csv',index=False)
print(out.groupby(['race','year','sex']).size().to_string())
print('total',len(out),'JPN',(out.nat=='JPN').sum())
