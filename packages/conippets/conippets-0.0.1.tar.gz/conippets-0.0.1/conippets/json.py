import json

def read(file, mode, encoding='utf-8', **kwargs):
    with open(file, mode=mode, encoding=encoding, **kwargs) as f:
        data = json.load(f)
    return data

def write(data, file, mode, encoding='utf-8', indent=4, **kwargs):
    with open(file, mode=mode, encoding=encoding) as f:
        json.dump(data, f, ensure_ascii=False, indent=indent, **kwargs)