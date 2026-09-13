import re

text = open('app.py', encoding='utf-8').read()
routes = re.findall(r'@app\.route\([\'"]([^\'"]+)[\'"]', text)
for r in routes:
    if any(k in r for k in ['sector', 'corridor', 'predict', 'inference', 'pahad', 'snapshot']):
        print(r)
