# Clean Python example

This dependency-free project is intentionally small. It already has a task
artifact and working tests, but no Warmboot files. Copy it to a disposable
directory to try `bin/warmboot init` without touching a real project.

Run its native check with:

```sh
python3 -m unittest discover -s tests -v
```
