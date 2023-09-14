option trader

# package development
cd option_trader/src
pip install e .
py -m build
py -m twine upload --repository pypi dist/*
docker run --restart always -p 8000:8000 docker.io/jihuang/optiontrader

#tests
https://docs.pytest.org/en/latest/explanation/goodpractices.html