from pydbml import PyDBML
from pathlib import Path


if __name__ == '__main__':
    d = PyDBML(Path('test_schema.dbml'))
    print(d)
