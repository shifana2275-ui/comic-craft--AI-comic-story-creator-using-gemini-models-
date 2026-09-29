# ComicCraft — AI Comic Story Creator (Gemini-only build)

ComicCraft turns a story prompt into a fully illustrated, downloadable comic.
This build runs entirely on a single **Gemini API key** — no Hugging Face /
Stable Diffusion setup needed:

- **Gemini 2.5 Flash** — generates the structured, panel-by-panel outline
- **Gemini 2.5 Pro** — expands each panel into narration and dialogue
- **Gemini 2.5 Flash Image** — generates the comic-style illustration for
  each panel
- **FastAPI + Jinja2** — web UI and API
- **fpdf2** — exports the finished comic as a PDF

## 1. Get a Gemini API key

Create one for free at <https://aistudio.google.com/apikey>.

## 2. Set up the project

```bash
python -m venv comiccraft-env
# Windows
comiccraft-env\Scripts\activate
# macOS/Linux
source comiccraft-env/bin/activate

pip install -r requirements.txt
```

## 3. Add your API key

```bash
cp .env.example .env
```

Then edit `.env` and set:

```
GEMINI_API_KEY=your_actual_key_here
```

## 4. Run the app

```bash
uvicorn app.main:app --reload
```

- App: <http://127.0.0.1:8000>
- Interactive API docs: <http://127.0.0.1:8000/docs>

## Project structure

```
comiccraft/
├── app/
│   ├── main.py             # FastAPI app + static file mounting
│   ├── routes.py           # All routes (/, /generate, /generate-comic/json, ...)
│   ├── gemini_client.py    # Shared Gemini client (reads GEMINI_API_KEY)
│   ├── gemini_flash.py     # generate_outline() — panel outline
│   ├── gemini_pro.py       # generate_story() — narration & dialogue
│   ├── image_generator.py  # generate_image() — Gemini image generation
│   ├── layout_builder.py   # build_comic_layout() — combine text + images
│   └── exporters.py        # save_pdf() — compile the final PDF
├── templates/
│   ├── index.html          # Story prompt form
│   ├── comic_preview.html  # Generated comic, panel by panel
│   └── export_success.html # Confirmation after download
├── static/
│   ├── style.css
│   ├── panels/              # generated panel images land here
│   └── exports/             # generated PDFs land here
├── requirements.txt
└── .env.example
```

## Routes

| Route | Method | Purpose |
|---|---|---|
| `/` | GET | Homepage with the comic creation form |
| `/generate` | POST (form) | Runs the full pipeline, renders the comic preview |
| `/generate-comic/json` | POST (JSON) | Same pipeline, returns JSON (`layout`, `pdf_path`) |
| `/export-success` | GET | Confirmation page after downloading the PDF |
| `/test-image` | GET | Dev utility — generate one image from `?prompt=...` |

## Notes

- Generating a comic makes several Gemini calls (1 outline + 1 story + 1
  image per panel), so a 5-panel comic takes a bit of time and uses your
  API quota accordingly.
- If image generation fails for a panel (rate limit, safety filter, etc.),
  that panel is still shown with its text — the pipeline doesn't stop.
- `gemini-2.5-flash-image` availability depends on your API key's access
  tier; if it's not available for your key, swap `IMAGE_MODEL` in
  `app/image_generator.py` for another Gemini image-capable model.
