# Alpha Net website

Static site styled after bcg.com, with Alpha Net's navigation (from the Word sitemap and rename spreadsheet) and copy taken verbatim from anetcorp.com plus the new Word-document content.

## Publish on GitHub Pages
1. Create a GitHub repository and push this folder's contents to the `main` branch.
2. In the repository: **Settings → Pages → Build and deployment → Deploy from a branch → `main` / root**.
3. The site appears at `https://<user>.github.io/<repo>/`. All links are relative, so it works from a sub-path or a custom domain.

There are no forms; every call to action links to the Contact page or to `mailto:info@anetcorp.com`.

## Editing
Pages are generated. Change copy in `_src/newcontent.py` (new copy) or `_src/data/old-site-pages.json` (old-site copy), or layout in `_src/build.py`, then run:

```
python3 _src/build.py
```

Styles: `assets/css/site.css`. Scripts: `assets/js/site.js`. `_src/` is ignored by GitHub Pages.
`python3 _src/check_copy.py` lists any old-site text that doesn't appear on its new page.
