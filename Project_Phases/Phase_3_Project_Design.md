# Phase 3: Project Design

## System Architecture
- **Client Tier:** Dynamic HTML5/CSS3 templates served via Jinja2.
- **Server Tier:** Asynchronous FastAPI backend running on Uvicorn.
- **AI Processing Tier:** Google Generative AI API (Gemini 1.5 Flash) for multimodal parsing.
- **Infrastructure:** Containerized web service running on Render cloud.

## Data Flow
1. User uploads a receipt image via the web client.
2. FastAPI processes the payload and forwards the image to the Gemini multimodal endpoint.
3. Gemini extracts itemized details and spending insights.
4. Jinja2 renders and returns the structured results view to the user.





- *Date:* 29 September 2026
- *Team ID:* 08
- *Project Name:* ComicCraft - Al Comic Story Creator using Gemini Models
- *Maximum Marks:* 3 Marks

---

## Step 3: Project Design Phase Phase 

| S.No | Team Member | Idea / Suggestion | Category | Group No. |
|------|-------------|-------------------|----------|-----------|
| 1 | Lokesh | Multimodal receipt image parsing using Google Gemini 1.5 Flash API | AI Architecture & Vision | Group 08 |
| 2 | Dharan kumar| Automated line-item expense categorization and tax breakdown | Data Processing & Logic | Group 08 |
| 3 | Munniyapan | Dynamic Jinja2 web interface for intuitive mobile and desktop uploads | Frontend & UI/UX | Group 08 |
| 4 | Muthukumar | Budget threshold alerting and smart savings recommendations engine | Business Logic & Rules | Group 08 |

