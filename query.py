import requests
from urllib.parse import quote

formula = input('Input formula: ')

data = {
    'formula': formula,
    'fsize': '50px',
    'fcolor': '000000',
    'bcolor': 'ffffff',
    'errors': '1',
    'preamble': '\\usepackage{amsmath}\n\\usepackage{amsfonts}\n\\usepackage{amssymb}',
}
data_text = '&'.join([key + '=' + value for key, value in data.items()])

response = requests.post('https://quicklatex.com/latex3.f', data=data_text)

lines = response.text.split('\r\n')
status = int(lines[0])
if status == 0:
    url = lines[1].split()[0]
    print(url)
else:
    print('\n'.join(lines[2:]))
