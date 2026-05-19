# README demo video (GitHub)

GitHub **does not** show inline video when you use:

- `<video src="https://raw.githubusercontent.com/...">` — the tag is **removed**
- A poster image that links to the site — that is only a link, not a player

What works (see [Stack Overflow #4279611](https://stackoverflow.com/questions/4279611/how-to-embed-a-video-into-github-readme-md)):

1. Open the README in the **GitHub web editor** (not a local editor only).
2. Put the cursor on its **own paragraph** (blank line above and below).
3. **Drag and drop** `docs/demo.mp4` onto the editor (or use “Attach files…”).
4. Wait for upload; GitHub inserts a bare URL, for example:
   - `https://user-images.githubusercontent.com/.../....mp4`, or
   - `https://github.com/user-attachments/assets/...`
5. **Leave that URL alone** — no `<video>` wrapper, no markdown link syntax.
6. Commit from the web UI (or copy the URL into your local README and push).

The file stays on GitHub’s CDN; it is **not** required to keep a second copy only for README (the repo still has `docs/demo.mp4` for the website).

## Refresh after replacing `docs/demo.mp4`

```bash
bash scripts/publish_readme_demo_video.sh   # updates demo-asset release (fallback link)
gh browse README.md                         # then drag-and-drop the new MP4 in the browser
```

## Site vs README

| Where | File | Works |
|-------|------|--------|
| [GitHub Pages](https://omarelkhal.github.io/aftertone/) hero | `docs/demo.mp4` in repo | `<video>` in HTML |
| github.com README | user-images / user-attachments URL | bare URL line only |
