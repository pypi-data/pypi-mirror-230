# build
```shell
pip install -r requirements.txt
rm -rf dist
python -m build
python -m twine upload dist/* -u __token__ -p {token}
```