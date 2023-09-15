# Jinja2 SSG

- The filesystem structure in `--src` is copied into `--dest`.
- Files starting with `_` are skipped.

```bash
python3 -m pip install jinja2ssg
python3 -m jinja2ssg --src src --dest publish build
```

# Example

```
site/src/
├── _base.html
├── donate
│   ├── _banner.html
│   ├── _content.html
│   ├── _donateform.html
│   ├── donate.js
│   └── index.html
├── _footer.html
└── _nav.html
```

Results in a DEST structure like:

```
site/www/
└── donate
    ├── index.html
    └── donate.js
```
