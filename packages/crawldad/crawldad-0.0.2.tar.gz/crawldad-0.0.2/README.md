# crawldad

## Deploy

```
python3 -m venv deploy
source deploy/bin/activate
python3 -m pip install -r deploy.txt
python3 -m build
python3 -m twine upload dist/*
```
