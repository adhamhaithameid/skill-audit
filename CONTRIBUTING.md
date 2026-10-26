# Contributing

Run both commands before you commit. Both must pass.

```
python3 tools/check.py
python3 -m unittest discover -s tests
```

Enable the pre-commit hook once:

```
git config core.hooksPath .githooks
```