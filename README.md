# ADOT D0 — Supplementary material

Supplementary material for:

> Fujiwara A, Takahashi Y. **Every distance-conversion table has a range of validity: how the half-to-full marathon relationship changes with finish time, sex and race context in 34,139 finishes at Japanese marathons.** Submitted to *Translational Exercise Biomedicine* (De Gruyter), 2026.

論文「どの距離換算表にも妥当な範囲がある」（Translational Exercise Biomedicine 投稿中）の Supplementary Material です。

This repository contains **derived summaries, figures and analysis code only**. It does **not** contain the race results on which the analysis is based, nor any individual finisher records. See *Data sources* below.

## Contents

| Path | Item | Description |
|---|---|---|
| `supplementary/TableS1_ADOT_table.xlsx` | Table S1 | The complete ADOT table, with construction notes from its author |
| `supplementary/TableS2_S4_S5_derived_summaries.xlsx` | Tables S2, S4, S5 | Descriptive statistics by race, edition and sex; marginal slopes with bootstrap CIs and df sensitivity; race-by-time interaction and sensitivity excluding 2021–2022 (S2); race-day temperature and humidity by edition, from the result sheets (S4); median multiplier by 10-min finish-time bin and range of validity (S5) |
| `supplementary/TableS3_segment_profiles.csv` | Table S3 | Median relative pace by 5 km segment, race and finish-time band |
| `supplementary/FigureS1_segment_profiles_{EN,JA}.png` | Figure S1 | Segment profiles: men finishing 2:32–2:42 at the three men's races; women at Nagoya 2022 by finish time |
| `code/build_v10.py` | Code S1 | Extraction of half-way split and finish time from the result sheets |
| `code/analyze_v10.py` | Code S1 | Main analysis (spline fits, race-by-time interaction, sex differences) |
| `code/build_v11.py` | Code S1 | Extraction of all 5 km splits |
| `code/analyze_v11_splits.py` | Code S1 | Segment-profile analysis |
| `code/bootstrap_slopes.py` | Code S1 | Bootstrap confidence intervals and degrees-of-freedom sensitivity for marginal slopes |

Text S1 (summary of the structured questionnaire answered by the table's author) will be added once the author has approved the text.

## Data sources

All results are official results published by the race organisers. They are **not redistributed here**; the scripts in `code/` reproduce every figure and table in the paper when run against the PDFs downloaded from the sources below (see *Reproducing the analysis*).

| Race | Editions used | Source |
|---|---|---|
| Beppu–Oita Mainichi Marathon | 2022–2026 | Japan Association of Athletics Federations (JAAF), competition IDs 1621, 1697, 1807, 1907, 2001 — `https://www.jaaf.or.jp/competition/detail/{ID}/` |
| Fukuoka International Marathon | 2021–2025 | JAAF, IDs 1585, 1720, 1790, 1895, 1987 |
| Osaka Marathon (registered division) | 2022–2025 | JAAF, IDs 1633, 1721, 1812, 1915 |
| Osaka Marathon (registered division) | 2026 | Osaka Marathon Organizing Committee — https://www.osaka-lakebiwa-marathon.com/pdf/result_2026.pdf |
| Osaka International Women's Marathon | 2022–2026 | JAAF, IDs 1595, 1689, 1799, 1904, 1997 |
| Nagoya Women's Marathon | 2022, 2024, 2025, 2026 | Nagoya Women's Marathon Organizing Committee — `https://womens-marathon.nagoya/assets/womens/pdf/result/{year}_result.pdf` |

All pages accessed 7 September 2026. Race-day weather (Table S4) is taken from the course-conditions tables printed in the same result sheets.

**Terms of use.** The results remain the property of the respective organisers. This repository publishes only aggregated, derived values, in accordance with the analysis-only use of published records. Users who download the source PDFs must comply with the organisers' terms.

データ出典：上表のとおり。レース記録そのものおよび個票はこのリポジトリに含めていません。記録の権利は各大会主催者にあり、ここで公開するのは集計・導出値のみです。

## Reproducing the analysis

1. Download the 24 result PDFs from the sources above into `pdfs/` (this directory is git-ignored).
2. `pip install -r code/requirements.txt`
3. `python code/build_v10.py` → `extract_v10.csv` (half-way split and finish time). Note: 383 records (Beppu–Oita women, 2023 and 2024) cannot be regenerated because the archived JAAF sheets contain only the men's section; see the paper's Discussion.
4. `python code/analyze_v10.py` → all numbers in the Results, Table 1 and Table S2.
5. `python code/build_v11.py` → `extract_v11.csv` (all 5 km splits); `python code/analyze_v11_splits.py` → Table S3 and Figure S1.
6. `python code/bootstrap_slopes.py` → Table S2d.

Extracted CSVs are git-ignored and must not be committed or redistributed.

## Licence

- **Code** (`code/`): MIT License — see `LICENSE`.
- **Tables, figures and text** (`supplementary/`): Creative Commons Attribution 4.0 International (CC BY 4.0) — see `LICENSE-CC-BY-4.0.md`. This matches the licence under which *Translational Exercise Biomedicine* publishes articles and their supplementary material. Table S1 (the ADOT table) is the work of Arata Fujiwara and is released under CC BY 4.0 with his consent; please cite the paper when reusing it.

## Citing

See `CITATION.cff`. Until the article is published, cite the preprint (SportRxiv, DOI to be added) or this repository's tagged release.

## Versions

Tagged releases correspond to manuscript versions (e.g. `d0-v12`). The version submitted to the journal will be tagged `d0-submitted`; a Zenodo DOI will be minted for that tag.
