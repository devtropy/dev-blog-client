# viniciusarre.dev

Source for [viniciusarre.dev](https://viniciusarre.dev): a terminal-styled blog built from markdown into one self-contained Cloudflare Worker.

```bash
pip install -r requirements.txt
python3 build.py        # -> dist/worker.js (+ dist/preview/*.html for local viewing)
```

- `posts/*.md`: published posts. Front matter keys: `title`, `slug`, `date` (YYYY-MM-DD), `series`, `summary`, `draft` (true/false). Values are unquoted.
- `assets/`: CSS and JS, inlined into the Worker at build time.
- `archive/`: content mined from the previous Nuxt version of this blog that isn't published (an unfinished tutorial, the old about page). Not read by the build.

The two 2018 posts from the old blog are republished under the `Archive` series. The previous Vue 2 / Nuxt.js version of the blog is in this repo's git history.
