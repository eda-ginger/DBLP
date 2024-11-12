import re
import json
import pandas as pd
from pathlib import Path


top_tier = '''AAAI
CCS
CHI
MobiCom
MM
SIGCOMM
SIGIR
KDD
FSE
SOSP
STOC
ACL
ASPLOS
CVPR
NIPS
OOPSLA
INFOCOM
HPCA
RTSS
FOCS
S&P
VIS
MICRO
SIGGRAPH
ICCV
CAV
ICML
SIGMOD
ICSE
EUROCRYPT
VLDB/PVLDB
CRYPTO
IJCAI
ISCA
WWW
PLDI
POPL
NSDI
OSDI
CSCW
SenSys
CIKM
MobiSys
WSDM
UbiComp
MobiHoc
SIGMETRICS
PPoPP
SPAA
PODS
PODC
IPSN
SC
LICS
SODA
COLT
UAI
DAC
EMNLP
ICDE
ICDM
ICDCS
PerCom
ASE
ICCAD'''.split('\n')


top_tier_journals = [
    'Nature Computational Science',
    'Nature Machine Intelligence',
    'Journal of Chemical Information and Modeling',
    'Bioinformatics',
    'BMC Bioinformatics',
    'Briefings in Bioinformatics',
    'PLoS Computational Biology',
    'IEEE Transactions on Biomedical Engineering',
    'Journal of Biomedical Informatics',
    'Artificial Intelligence in Medicine',
    'IJCV', 'TIP', 'TPAMI'
]

top_tier_conferences = [
    'NeurIPS',
    'AAAI',
    'ECML/PKDD',
    'RECOMB',
    'IEEE Big Data',
    'BIBM',
    'ICDM',
    'ICASSP',
    'GECCO Companion',
    'CVPR',
    'ICLR',
    'ICCV',
    'ICML',
    'ECCV'
]

other_important_journals = [
    'IEEE Access',
    'Neural Networks',
    'Neurocomputing'
]

dti_journals = top_tier_journals + top_tier_conferences + other_important_journals

def filter_word(data, words):
    if len(words) == 1:
        pattern = re.compile(words[0], re.IGNORECASE)
    else:
        pattern = re.compile("|".join(words), re.IGNORECASE)

    title = data['title'].to_list()
    f_title = [t for t in title if not bool(pattern.search(t))]
    data = data[data['title'].isin(f_title)].reset_index(drop=True)
    return data


def filter_tier(data, tiers, capitalize=True):
    if len(tiers) == 1:
        if capitalize:
            pattern = re.compile(tiers[0], re.IGNORECASE)
        else:
            pattern = re.compile(tiers[0])
    else:
        if capitalize:
            pattern = re.compile("|".join(tiers), re.IGNORECASE)
        else:
            pattern = re.compile("|".join(tiers))

    venue = [v for v in data['venue'].to_list() if isinstance(v, str)]
    f_venue = [v for v in venue if bool(pattern.search(v))]
    data = data[data['venue'].isin(f_venue)].reset_index(drop=True)
    return data



commands = {'DDI': ('dblp_ddi.json', ['target', 'dti', 'protein', 'food']),
            'DTI': ('dblp_dti.json', ['ddi', 'drug-drug', 'food'])}

for c_key, command in commands.items():
    file, filter_words = command

    file = Path(file)
    output = file.parent / (file.stem + '.csv')

    with open(file, encoding='utf-8') as f:
        data = json.load(f)
    data = data['result']['hits']['hit']

    result = []
    for i in data:
        row = {
            'score': i['@score'],
            'id': i['@id'],
            'url_id': i['url']
        }

        infos = i['info']
        for k in infos.keys():
            if k == 'authors':
                authors = infos[k]['author']
                if isinstance(authors, list):
                    row[k] = ', '.join([str(a['text']) for a in authors])
                else:
                    row[k] = authors['text']
            else:
                row[k] = infos[k]
        result.append(row)
    result = pd.DataFrame(result)
    result.dropna(subset=['title'], inplace=True)

    result = result.sort_values(by=['year', 'score'], ascending=False)
    result = filter_word(result, filter_words)
    if c_key == 'DTI':
        result = filter_tier(result, dti_journals, capitalize=False)
    result.to_csv(output, index=False, header=True)

