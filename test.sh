python3 -m doctest README.md &&\
    python3 -m doctest docs/classes.md &&\
    python3 -m doctest docs/upgrading.md &&\
    python3 -m doctest docs/creating_schema.md &&\
    python3 -m unittest discover &&\
    mypy pydbml --ignore-missing-imports
