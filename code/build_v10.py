# -*- coding: utf-8 -*-
"""extract_v10.csv の構築
  既存 extract_v9.csv（監査済み13エディション）
+ extract_2026.csv のうち別大2026・大阪国際女子2026
+ 新規抽出（別大2022 / 福岡2021・2022 / 大阪マラソン2022・2026 /
            大阪国際女子2022 / 名古屋2022・2024・2026）
名古屋2026 は陸連登録者649名版ではなく大会公式サイトの上位300名版を使う。
名古屋2023 は公式サイト版PDFが未入手のため保留。
"""
import re, subprocess, pandas as pd

TIME = re.compile(r'(?<![\d:(])(\d{1,2}:\d{2}(?::\d{2})?)(?![\d:)])')
FW = 'ＡＢＣＤＥＦＧＨＩＪＫＬＭＮＯＰＱＲＳＴＵＶＷＸＹＺ'
def ascii_(s): return ''.join(chr(ord(c) - 0xFEE0) if c in FW else c for c in s)
ISO = set('''JPN KEN ETH USA AUS CHN KOR TPE HKG MAS THA GBR GER FRA ITA NZL CAN BRN ISR
UGA MGL ROU IRL UZB ARG MEX CHI PER SUI ESP POL SWE NOR DEN NED BEL AUT RSA ERI DJI TAN
MAR ALG TUR IND VIE INA PHI SIN NEP SRI PAK BAN MYA BRA POR FIN CZE HUN UKR RUS MDA SVK
LTU LAT EST GRE CRO SLO SRB SGP PUR BER GRC'''.split())
CODE = re.compile(r'(?<![A-Za-z])([A-Z]{3})(?![A-Za-z])|([' + FW + r']{3})')
FOREIGN_WORDS = ['ケニア','エチオピア','ケ ニ ア','中国','韓国','タイ','香港','アメリカ','米国',
                 'オースト','ニュージ','モンゴル','台湾','ブラジル','イタリア','フランス','ドイツ',
                 'イギリス','英国','ウガンダ','バーレーン','イスラエル','ジブチ','モロッコ','チリ',
                 'メキシコ','シンガポール','マレーシア','南アフリカ','スペイン','スウェーデン',
                 'ルーマニア','アイルランド','ギリシャ','ロシア','プエルトリコ','バミューダ']

def natof(*lines):
    for ln in lines:
        for m in CODE.finditer(ascii_(ln)):
            c = m.group(1) or m.group(2)
            if c in ISO:
                return ascii_(c)
    for ln in lines:
        if any(w in ln for w in FOREIGN_WORDS):
            return 'FOR'
    return 'JPN'

def _sections(ln, cur, keep):
    """節見出しから性別と採否を更新する。視覚障がい者の部は除外。"""
    if '視覚' in ln and '*' in ln:
        return cur, False
    if '*' in ln and 'マラソン' in ln:
        if '女子' in ln:
            return 'F', True
        if '男子' in ln:
            return 'M', True
    if re.match(r'\s*女子\s*マラソン', ln):
        return 'F', True
    if re.match(r'\s*男子\s*マラソン', ln):
        return 'M', True
    if 'WOMEN 登録' in ln:
        return 'F', True
    if 'MEN 登録' in ln:
        return 'M', True
    if '女子登録' in ln and 'マラソン' in ln:
        return 'F', True
    if '男子登録' in ln and 'マラソン' in ln:
        return 'M', True
    return cur, keep

def parse(path, race, year, sex_default, one_line=False):
    lines = subprocess.run(['pdftotext', '-layout', path, '-'],
                           capture_output=True, text=True).stdout.split('\n')
    cur, keep, rows = sex_default, True, []
    for i, ln in enumerate(lines):
        cur, keep = _sections(ln, cur, keep)
        if not keep or re.search(r'\sT1[12]\b', ln):
            continue
        ts = TIME.findall(re.sub(r'\([^)]*\)', '', ln))
        if len(ts) < 10:
            continue
        nxt = lines[i + 1] if i + 1 < len(lines) else ''
        nat = natof(ln, nxt)
        if one_line:
            if not re.match(r'\s*\d{1,5}\s', ln):
                continue
            if nat == 'JPN' and '・' in ln[:46]:
                nat = 'FOR'      # 福岡2021 は外国籍をカタカナ中黒で表記
            finish = ts[9]
        else:
            finish = ts[-1]
        rows.append(dict(race=race, year=year, sex=cur, nat=nat,
                         half=ts[4], finish=finish))
    return pd.DataFrame(rows)

P = './pdfs/pdfs/'
U = '/mnt/user-data/uploads/'

NEW = [
    (P + 'results_別府大分2022_1621-7.pdf',        'Betsudai',      2022, 'M', True),
    (P + 'results_福岡国際2021_1585-7.pdf',        'Fukuoka',       2021, 'M', True),
    (P + 'results_福岡国際2022_1720-7.pdf',        'Fukuoka',       2022, 'M', False),
    (P + 'results_大阪2022_1633-7.pdf',            'OsakaMarathon', 2022, 'M', False),
    (P + 'results_大阪2026_website.pdf',           'OsakaMarathon', 2026, 'M', False),
    (P + 'results_大阪国際女子2022_1595-7.pdf',     'OsakaWomen',    2022, 'F', False),
    (U + 'results_名古屋ウィメンス_2022_result.pdf', 'NagoyaWomen',   2022, 'F', True),
    (P + 'results_名古屋ウィメンズ2024_result.pdf',  'NagoyaWomen',   2024, 'F', False),
    (P + 'results_名古屋ウィメンズ2026_result.pdf',  'NagoyaWomen',   2026, 'F', False),
]

def year_of(race):
    return int(re.search(r'(\d{4})$', race).group(1))

def main():
    v9 = pd.read_csv('./pdfs/extract_v9.csv')
    v9['year'] = v9['race'].map(year_of)
    v9['race'] = v9['race'].str.replace(r'\d{4}$', '', regex=True)
    v9 = v9[v9['race'] != 'NagoyaWomen'].copy()          # 名古屋は公式サイト版に統一
    nagoya25 = pd.read_csv('./pdfs/extract_v9.csv')
    nagoya25 = nagoya25[nagoya25['race'] == 'NagoyaWomen2025'].copy()
    nagoya25['year'] = 2025
    nagoya25['race'] = 'NagoyaWomen'

    e26 = pd.read_csv('./pdfs/extract_2026.csv')
    e26['year'] = e26['race'].map(year_of)
    e26['race'] = e26['race'].str.replace(r'\d{4}$', '', regex=True)
    e26 = e26[e26['race'].isin(['Betsudai', 'OsakaWomen'])].copy()

    frames = [v9, nagoya25, e26]
    for path, race, year, sex, one in NEW:
        d = parse(path, race, year, sex, one_line=one)
        print(f'  {race}{year}: {len(d)}')
        frames.append(d)

    cols = ['race', 'year', 'sex', 'nat', 'half', 'finish']
    d = pd.concat([f[cols] for f in frames], ignore_index=True)
    d.to_csv('extract_v10.csv', index=False)
    print(d.groupby(['race', 'year', 'sex']).size().to_string())
    print('合計', len(d), '/ 日本人', (d.nat == 'JPN').sum())

if __name__ == '__main__':
    main()
