import re
import json
import pandas as pd
from pathlib import Path


commands = {'EK': 'EK_DBLP.json'}

for c_key, file in commands.items():
    file = Path(file)
    output = file.parent / (c_key + '.csv')

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
    result.to_csv(output, index=False, header=True)
