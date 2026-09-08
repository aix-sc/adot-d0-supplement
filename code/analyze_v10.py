# -*- coding: utf-8 -*-
"""ADOT v10 解析（連続モデル版）

帯で切って傾きを比べる方式をやめ、完走タイムを連続変数のまま扱う。
  失速率 r = (finish - half) / half

(A) コースごとに自然3次スプラインを当て、そのコースの観測範囲内でだけ
    限界傾き dr/d(分) を出す。範囲外には外挿しない。
(B) 複数コースが重なる区間に限定して r ~ 完走タイム × コース の交互作用を検定する。
    「コースによって走力依存性の急峻さが違う」という主張の検定にあたる。
(C) 帯別平均は記述のためだけに残す。推論には使わない。
変量切片はエディション（大会×年）。
"""
import numpy as np, pandas as pd
from scipy import stats
import statsmodels.formula.api as smf

SRC = 'extract_v10.csv'

def to_min(t):
    p = [int(x) for x in str(t).split(':')]
    if len(p) == 2:
        p = [0] + p
    return p[0] * 60 + p[1] + p[2] / 60

def hm(m):
    return f'{int(m)//60}:{int(m)%60:02d}'

def load():
    d = pd.read_csv(SRC)
    d = d[d.nat == 'JPN'].copy()
    d['half_m'] = d['half'].map(to_min)
    d['fin_m'] = d['finish'].map(to_min)
    d = d[(d.half_m > 50) & (d.fin_m > 110) & (d.fin_m < 480)]
    d['r'] = (d.fin_m - d.half_m) / d.half_m
    d = d[(d.r > 0.8) & (d.r < 2.5)]
    d['edition'] = d.race + d.year.astype(str)
    return d

def per_course_spline(d, sex):
    print(f'\n【A】コース別スプライン（{"男子" if sex=="M" else "女子"}）')
    sd = d[d.sex == sex]
    for race, g in sd.groupby('race'):
        if len(g) < 150:
            print(f'  {race}: n={len(g)} 少数のため当てはめを行わない')
            continue
        lo, hi = g.fin_m.quantile(.01), g.fin_m.quantile(.99)
        try:
            res = smf.mixedlm("r ~ cr(fin_m, df=4)", g, groups=g['edition']).fit(
                method='lbfgs', maxiter=300)
        except Exception as e:
            print(f'  {race}: 当てはめ失敗 {e}')
            continue
        print(f'\n  ● {race}  n={len(g)}  範囲 {hm(g.fin_m.min())}-{hm(g.fin_m.max())}'
              f'  年数={g.year.nunique()}')
        print(f'    変量切片SD(エディション)={np.sqrt(res.cov_re.iloc[0,0]):.4f}'
              f'  残差SD={np.sqrt(res.scale):.4f}')
        pts = [p for p in (130, 145, 160, 180, 200, 220, 240, 270, 300, 330, 360, 400)
               if lo <= p <= hi]
        h = 1.0
        for x in pts:
            y = res.predict(pd.DataFrame({'fin_m': [x - h, x + h]}))
            print(f'      {hm(x):>6} 限界傾き {(y.iloc[1]-y.iloc[0])/(2*h):+.5f}')

def overlap_interaction(d, sex, races, lo, hi, note=''):
    sd = d[(d.sex == sex) & d.race.isin(races) &
           (d.fin_m >= lo) & (d.fin_m <= hi)].copy()
    if sd.race.nunique() < 2:
        print(f'  重なり区間にコースが揃わない: {races}')
        return
    sd['x'] = sd.fin_m - lo
    res = smf.mixedlm("r ~ x * C(race)", sd, groups=sd['edition']).fit(
        method='lbfgs', maxiter=300)
    print(f'\n  ● {"/".join(races)}  区間 {hm(lo)}-{hm(hi)}  n={len(sd)} {note}')
    for k in res.params.index:
        if k.startswith('x'):
            print(f'    {k:<40}{res.params[k]:+.6f}'
                  f'  SE={res.bse[k]:.6f}  p={res.pvalues[k]:.3g}')
    base = res.params.get('x', np.nan)
    print('    コース別の単純傾き:')
    for rc in sorted(sd.race.unique()):
        key = f'x:C(race)[T.{rc}]'
        print(f'      {rc:<16}{base + res.params.get(key, 0.0):+.6f}')

def band_table(d, sex):
    bins = [120, 150, 180, 210, 240, 270, 300, 330, 480]
    sd = d[d.sex == sex].copy()
    sd['bin'] = pd.cut(sd.fin_m, bins)
    t = sd.groupby(['race', 'bin'], observed=True)['r'].agg(['size', 'mean']).round(4)
    print(f'\n【C】帯別平均失速率（{"男子" if sex=="M" else "女子"}・記述のみ）')
    print(t.to_string())

def descriptives(d):
    g = d.groupby(['race', 'year', 'sex'])
    t = g.agg(n=('r', 'size'), fin_min=('fin_m', 'min'), fin_max=('fin_m', 'max'),
              fin_med=('fin_m', 'median'), r_mean=('r', 'mean'),
              r_sd=('r', 'std')).reset_index()
    for c in ['fin_min', 'fin_max', 'fin_med']:
        t[c] = t[c].map(hm)
    t['r_mean'] = t.r_mean.round(4)
    t['r_sd'] = t.r_sd.round(4)
    return t

def main():
    d = load()
    print('【0】総数', len(d), ' 男子', (d.sex == 'M').sum(), ' 女子', (d.sex == 'F').sum())
    print('   大会', d.race.nunique(), ' エディション', d.edition.nunique())

    print('\n【1】エディション別の記述統計（日本人のみ）')
    print(descriptives(d).to_string(index=False))

    for sex in ['M', 'F']:
        per_course_spline(d, sex)

    print('\n【B】重なり区間でのコース×完走タイム交互作用')
    print('  男子:')
    overlap_interaction(d, 'M', ['Betsudai', 'Fukuoka', 'OsakaMarathon'], 128, 160,
                        '(3コースが重なる範囲)')
    print('  女子:')
    overlap_interaction(d, 'F', ['OsakaWomen', 'NagoyaWomen', 'OsakaMarathon'], 145, 195,
                        '(3コースが重なる範囲)')

    for sex in ['M', 'F']:
        band_table(d, sex)

    print('\n【D】性差（同一エディション内）')
    both = d.groupby(['race', 'year']).filter(lambda g: g.sex.nunique() == 2)
    for (rc, yr), g in both.groupby(['race', 'year']):
        m, f = g[g.sex == 'M'].r, g[g.sex == 'F'].r
        if len(m) < 10 or len(f) < 10:
            continue
        t, p = stats.ttest_ind(m, f, equal_var=False)
        print(f'  {rc}{yr}  男{m.mean():.4f}(n={len(m)})  女{f.mean():.4f}(n={len(f)})'
              f'  差{m.mean()-f.mean():+.4f}  p={p:.3g}')

    print('\n【E】4時間以降を含むコースの形')
    for rc, sex in [('OsakaMarathon', 'M'), ('NagoyaWomen', 'F')]:
        g = d[(d.race == rc) & (d.sex == sex)]
        bins = [120, 180, 210, 240, 270, 300, 330, 360, 480]
        gg = g.copy(); gg['bin'] = pd.cut(gg.fin_m, bins)
        print(f'  {rc}({sex}) n={len(g)}')
        print(gg.groupby('bin', observed=True)['r'].agg(['size', 'mean']).round(4).to_string())

if __name__ == '__main__':
    main()
