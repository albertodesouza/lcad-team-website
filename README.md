# Prof. Dr. Alberto Ferreira De Souza - Academic Website

Modern academic website for Professor Emeritus Alberto Ferreira De Souza from UFES (Universidade Federal do Espírito Santo).

**Live Website:** http://www.lcad.inf.ufes.br/alberto/

## Features

- Modern, responsive design using Tailwind CSS
- Automatic Google Scholar metrics updates (top 10 publications with links)
- Embedded YouTube videos from LCAD channel
- Professional academic profile with publications, projects, and awards

## Project Structure

```
├── src/
│   └── alberto/
│       ├── index.html                # Main page
│       ├── publications.html         # Complete publications list (from Lattes)
│       └── projects.html             # Research projects list (from Lattes)
│   ├── assets/
│   │   ├── css/style.css             # Custom styles
│   │   ├── js/main.js                # JavaScript functionality
│   │   ├── images/                   # Photos and images
│   │   └── videos/                   # Local video files
│   └── data/
│       ├── scholar_metrics.json      # Google Scholar data (auto-updated)
│       └── lattes_data.json          # Parsed Lattes data
├── scripts/
│   ├── fetch_scholar.py              # Script to fetch Scholar metrics
│   ├── generate_html.py              # Script to update HTML with Scholar data
│   ├── parse_lattes.py               # Script to parse Lattes XML
│   ├── generate_lattes_pages.py      # Script to generate publications/projects pages
│   └── requirements.txt              # Python dependencies
├── .github/
│   └── workflows/
│       └── update_metrics.yml        # GitHub Action for weekly updates
├── dist/                             # Build output for deployment
├── team/                             # Backup of original MediaWiki site
├── preview.sh                        # Local preview with Python HTTP server
├── preview_alberto.sh                # Quick preview in default browser
└── deploy.sh                         # Deployment script (requires VPN)
```

## Local Preview

Before deploying changes, you can preview the website locally using one of these methods:

### Quick Preview (opens in default browser)

```bash
./preview_alberto.sh
```

This opens the page directly in your default browser. Best for quick checks after edits.

### HTTP Server Preview

```bash
./preview.sh [port]
```

This starts a local HTTP server (default port 8000). Access at http://localhost:8000

You can specify a custom port:
```bash
./preview.sh 3000
```

Press `Ctrl+C` to stop the server.

**Note:** The HTTP server is recommended when testing features that require a proper HTTP context (e.g., video loading, CORS-dependent resources).

## Deployment

### Prerequisites

- Connected to **UFES departmental VPN**
- `lftp` installed (`sudo apt install lftp`)
- SFTP credentials for `lcad@sftp.inf.ufes.br`

### Basic Deploy

```bash
./deploy.sh
```

Uploads the website to http://www.lcad.inf.ufes.br/alberto/

### Deploy with Updated Metrics

```bash
./deploy.sh --update-metrics
```

This option:
1. Fetches the latest Google Scholar data (citations, h-index, i10-index)
2. Retrieves top 10 most cited publications with links
3. Updates the HTML page with new data
4. Deploys everything to the server

### Dry Run (preview without uploading)

```bash
./deploy.sh --dry-run
```

Shows what files would be transferred without actually uploading anything.

### Combined Options

```bash
./deploy.sh --update-metrics --dry-run
```

Fetches metrics and shows what would be deployed, without uploading.

## Updating Google Scholar Metrics

### Manual Update (local)

```bash
cd scripts
pip install -r requirements.txt
python fetch_scholar.py
python generate_html.py
```

### Automatic Update via GitHub Actions

The workflow runs weekly. To trigger manually:

1. Go to GitHub repository
2. Navigate to Actions > Update Scholar Metrics
3. Click "Run workflow"

## Editing the Website

The main page is located at `src/alberto/index.html`. Edit this file to:

- Update personal information in the About section
- Add/remove publications (or use `--update-metrics` to auto-update)
- Modify projects, awards, or media gallery
- Change photos (place new images in `src/assets/images/`)
- Add videos (place in `src/assets/videos/` and reference in HTML)

After editing, use `./preview_alberto.sh` to verify changes locally, then `./deploy.sh` to publish.

## Updating Publications and Projects from Lattes

The `publications.html` and `projects.html` pages contain the complete list of publications and research projects extracted from the Currículo Lattes XML file.

### How to Update

1. **Export your Lattes XML:**
   - Access http://lattes.cnpq.br
   - Login and go to your curriculum
   - Click "Export" → "Export to XML"
   - Save the file (e.g., `7573837292080522.xml`)

2. **Parse the XML:**
   ```bash
   python scripts/parse_lattes.py src/data/lattes.xml
   ```
   This extracts publications and projects to `src/data/lattes_data.json`

3. **Generate HTML pages:**
   ```bash
   python scripts/generate_lattes_pages.py
   ```
   This generates complete `publications.html` and `projects.html` pages from the JSON data.

4. **Deploy:**
   ```bash
   ./deploy.sh
   ```

### Data Extracted from Lattes

The `parse_lattes.py` script extracts:
- **Journal Articles:** Title, authors, journal, volume, year, DOI
- **Conference Papers:** Title, authors, event name, location, year, DOI
- **Books:** Title, authors, publisher, year, ISBN
- **Book Chapters:** Title, book title, authors, publisher, year
- **Research Projects:** Name, period, status, description, funding agencies, team members

### Project Description Translations

The `generate_lattes_pages.py` script contains English translations for all project names and descriptions. When updating with new projects, you may need to add translations using the AI assistant (Cursor) with the following prompt:

```
I have added new projects to my Lattes. Please:

1. Read src/data/lattes_data.json and identify any projects without English translations
   in scripts/generate_lattes_pages.py (PROJECT_TRANSLATIONS dictionary)

2. Add English translations for:
   - Project name (name field)
   - Project description (description field)

3. Regenerate the HTML pages by running: python scripts/generate_lattes_pages.py
```

### Features of Generated Pages

**publications.html:**
- Complete list of all 55 journal articles, 136 conference papers, 10 books, and 4 book chapters
- DOI links for publications that have them
- Filter by publication type
- Sorted by year (most recent first)

**projects.html:**
- Complete list of all 38 research projects
- Expandable descriptions (click on project title to toggle)
- English translations for all project names and descriptions
- Original Portuguese names preserved
- Filter by status (ongoing/completed)
- Funding agency information

## Author

Prof. Dr. Alberto Ferreira De Souza
- Professor Emeritus, UFES
- Director, I2CA (Institute of Applied Computational Intelligence)
- CTO & Co-founder, Lume Robotics S.A.
- CSO & Co-founder, AUMO S.A.
- Google Scholar: https://scholar.google.com.br/citations?user=gvb7W0IAAAAJ
- ORCID: https://orcid.org/0000-0003-1561-8447

## License

Content © Alberto Ferreira De Souza. All rights reserved.
