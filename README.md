# Prof. Dr. Alberto Ferreira De Souza - Academic Website

Modern academic website for Professor Emeritus Alberto Ferreira De Souza from UFES (Universidade Federal do Espírito Santo).

## Features

- Modern, responsive design using Tailwind CSS
- Automatic Google Scholar metrics updates via GitHub Actions
- Embedded YouTube videos from LCAD channel
- Professional academic profile with publications, projects, and awards

## Project Structure

```
├── src/
│   ├── index.php/                    # Directory structure for MediaWiki URL compatibility
│   │   └── Prof._Dr._Alberto_Ferreira_De_Souza/
│   │       └── index.html            # Main page
│   ├── assets/
│   │   ├── css/style.css             # Custom styles
│   │   ├── js/main.js                # JavaScript functionality
│   │   └── images/                   # Photos and images
│   └── data/
│       └── scholar_metrics.json      # Google Scholar data (auto-updated)
├── scripts/
│   ├── fetch_scholar.py              # Script to fetch Scholar metrics
│   ├── generate_html.py              # Script to regenerate HTML with new data
│   └── requirements.txt              # Python dependencies
├── .github/
│   └── workflows/
│       └── update_metrics.yml        # GitHub Action for weekly updates
├── dist/                             # Build output for deployment
└── deploy.sh                         # Manual deployment script (requires VPN)
```

## Usage

### Update Scholar Metrics Locally

```bash
cd scripts
pip install -r requirements.txt
python fetch_scholar.py
```

### Deploy to Server (requires VPN connection)

```bash
./deploy.sh
```

### Force Update via GitHub Actions

1. Go to GitHub repository
2. Navigate to Actions > Update Scholar Metrics
3. Click "Run workflow"

## URL Compatibility

This site maintains compatibility with the original MediaWiki URL:
`http://www.lcad.inf.ufes.br/team/index.php/Prof._Dr._Alberto_Ferreira_De_Souza`

## Author

Prof. Dr. Alberto Ferreira De Souza
- Professor Emeritus, UFES
- Director, I2CA (Institute of Applied Computational Intelligence)
- Google Scholar: https://scholar.google.com.br/citations?user=gvb7W0IAAAAJ
- ORCID: https://orcid.org/0000-0003-1561-8447

## License

Content © Alberto Ferreira De Souza. All rights reserved.
