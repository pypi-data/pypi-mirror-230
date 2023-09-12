from snbtlib import dumps, loads
from json import dumps as jdumps
from pathlib import Path


text = Path('ars_noveau.snbt').read_text(encoding='utf-8')
Path('test.snbt').write_text(dumps(loads(text)), encoding='utf-8')