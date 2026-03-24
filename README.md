# FakeWiki

FakeWiki is a small Flask app for the dead-internet idea: search a term, get a polished AI-generated page, then keep clicking into more generated pages until the whole web feels fake.

## What changed

This refactor replaces the old single-page HTML write-to-disk flow with a cleaner graph-style app:

- pages are generated in memory and persisted to `internet.json`
- every page has related fake links
- clicking a link expands the generated web
- Flask renders templates directly instead of writing `output.html`
- the app falls back to deterministic filler content if the model returns bad JSON

## Run it

Install dependencies:

```bash
pip install -r requirements.txt
```

Start Ollama or another OpenAI-compatible server, then run:

```bash
python main.py
```

Default model endpoint in `Engine.py`:

- base URL: `http://localhost:11434/v1/`
- model: `llama3`

Open the Flask URL in your browser and start clicking.

## File layout

- `main.py` — Flask routes
- `Engine.py` — page generation, fake-web graph, persistence
- `templates/index.html` — homepage
- `templates/page.html` — generated page view

## Notes

`internet.json` is created automatically after the first generated page.
