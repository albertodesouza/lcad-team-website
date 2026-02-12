#!/usr/bin/env python3
"""
Generate complete HTML pages for publications and projects from Lattes data.

This script reads the lattes_data.json file and generates:
- publications.html: Complete list of all publications
- projects.html: Complete list of all projects with descriptions

Usage:
    python generate_lattes_pages.py
"""

import json
import sys
from pathlib import Path
from html import escape
from datetime import datetime


# Configuration
DATA_FILE = Path(__file__).parent.parent / "src" / "data" / "lattes_data.json"
PUBLICATIONS_FILE = Path(__file__).parent.parent / "src" / "alberto" / "publications.html"
PROJECTS_FILE = Path(__file__).parent.parent / "src" / "alberto" / "projects.html"


def load_data() -> dict:
    """Load Lattes data from JSON file."""
    if not DATA_FILE.exists():
        print(f"Error: Data file not found: {DATA_FILE}")
        sys.exit(1)
    
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)


def format_authors(authors: list, max_authors: int = 10) -> str:
    """Format author list for display."""
    if not authors:
        return ""
    
    # Shorten author names
    formatted = []
    for author in authors[:max_authors]:
        # Try to format as "First Initial. Last Name"
        parts = author.replace(',', '').split()
        if len(parts) >= 2:
            # Keep last name and initials
            formatted.append(author)
        else:
            formatted.append(author)
    
    result = ", ".join(formatted)
    if len(authors) > max_authors:
        result += " et al."
    
    return result


def generate_publication_card(pub: dict, pub_type: str, color: str) -> str:
    """Generate HTML for a single publication card."""
    title = escape(pub.get('title', '') or pub.get('title_en', 'Unknown Title'))
    title_en = pub.get('title_en', '')
    authors = format_authors(pub.get('authors', []))
    year = pub.get('year', '')
    doi = pub.get('doi', '')
    
    # Build venue string based on publication type
    if pub_type == 'article':
        journal = escape(pub.get('journal', ''))
        volume = pub.get('volume', '')
        pages = pub.get('pages', '').strip('-')
        venue = journal
        if volume:
            venue += f", Vol. {volume}"
        if pages:
            venue += f", pp. {pages}"
    elif pub_type == 'conference':
        event = escape(pub.get('event', '') or pub.get('event_en', ''))
        city = pub.get('city', '')
        country = pub.get('country', '')
        venue = event
        if city:
            venue += f", {city}"
        if country and country != city:
            venue += f", {country}"
    elif pub_type == 'book':
        publisher = escape(pub.get('publisher', ''))
        venue = f"Publisher: {publisher}" if publisher else ""
    elif pub_type == 'chapter':
        book_title = escape(pub.get('book_title', ''))
        publisher = escape(pub.get('publisher', ''))
        venue = f"In: {book_title}"
        if publisher:
            venue += f" ({publisher})"
    else:
        venue = ""
    
    # Create link if DOI available
    if doi:
        if not doi.startswith('http'):
            doi_url = f"https://doi.org/{doi}"
        else:
            doi_url = doi
        title_html = f'<a href="{doi_url}" target="_blank" rel="noopener" class="hover:text-blue-600">{title}</a>'
    else:
        title_html = title
    
    return f'''        <div class="publication-card bg-white p-5 rounded-xl border hover:shadow-md transition-shadow">
          <div class="flex items-start gap-4">
            <span class="year-badge bg-{color}-100 text-{color}-800 px-3 py-1 rounded-full text-sm font-semibold flex-shrink-0">{year}</span>
            <div class="flex-1 min-w-0">
              <h3 class="font-semibold text-gray-900 mb-1">
                {title_html}
              </h3>
              <p class="text-sm text-gray-600 mb-1">{escape(authors)}</p>
              <p class="text-sm text-gray-500">{venue}</p>
            </div>
          </div>
        </div>'''


def generate_publications_html(data: dict) -> str:
    """Generate complete publications HTML page."""
    
    articles = data.get('articles', [])
    conference_papers = data.get('conference_papers', [])
    books = data.get('books', [])
    book_chapters = data.get('book_chapters', [])
    
    # Generate article cards
    articles_html = "\n\n".join(generate_publication_card(a, 'article', 'blue') for a in articles)
    
    # Generate conference paper cards
    conferences_html = "\n\n".join(generate_publication_card(p, 'conference', 'green') for p in conference_papers)
    
    # Generate book cards
    books_html = "\n\n".join(generate_publication_card(b, 'book', 'purple') for b in books)
    
    # Generate book chapter cards
    chapters_html = "\n\n".join(generate_publication_card(c, 'chapter', 'orange') for c in book_chapters)
    
    update_date = datetime.now().strftime('%B %Y')
    
    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta name="description" content="Complete list of publications by Prof. Dr. Alberto Ferreira De Souza">
  <title>Publications - Prof. Dr. Alberto Ferreira De Souza</title>
  
  <!-- Tailwind CSS CDN -->
  <script src="https://cdn.tailwindcss.com"></script>
  
  <!-- Custom Tailwind Config -->
  <script>
    tailwind.config = {{
      theme: {{
        extend: {{
          colors: {{
            'ufes-blue': '#003366',
            'ufes-gold': '#FFD700',
          }}
        }}
      }}
    }}
  </script>
  
  <!-- Custom Styles -->
  <link rel="stylesheet" href="assets/css/style.css">
  
  <style>
    .publication-card {{
      transition: all 0.2s ease;
    }}
    .publication-card:hover {{
      transform: translateY(-2px);
    }}
    .year-badge {{
      min-width: 50px;
      text-align: center;
    }}
    .filter-btn.active {{
      background-color: #2563eb;
      color: white;
    }}
  </style>
</head>
<body class="bg-gray-50 min-h-screen">
  <!-- Navigation -->
  <nav class="bg-ufes-blue text-white py-4 sticky top-0 z-50 shadow-lg">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="flex items-center justify-between">
        <a href="index.html" class="text-xl font-bold hover:text-ufes-gold transition-colors">
          ← Back to Home
        </a>
        <h1 class="text-lg font-semibold hidden sm:block">Prof. Dr. Alberto Ferreira De Souza</h1>
      </div>
    </div>
  </nav>

  <!-- Header -->
  <header class="bg-gradient-to-r from-ufes-blue to-blue-800 text-white py-12">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <h1 class="text-4xl font-bold mb-4">Complete List of Publications</h1>
      <p class="text-blue-200 text-lg">
        {len(articles)} journal articles, {len(conference_papers)} conference papers, {len(books)} books, and {len(book_chapters)} book chapters
      </p>
    </div>
  </header>

  <!-- Filter Buttons -->
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
    <div class="flex flex-wrap gap-3">
      <button onclick="filterPublications('all')" class="filter-btn active px-4 py-2 rounded-lg border border-gray-300 hover:bg-blue-600 hover:text-white transition-colors">
        All Publications
      </button>
      <button onclick="filterPublications('articles')" class="filter-btn px-4 py-2 rounded-lg border border-gray-300 hover:bg-blue-600 hover:text-white transition-colors">
        Journal Articles ({len(articles)})
      </button>
      <button onclick="filterPublications('conference')" class="filter-btn px-4 py-2 rounded-lg border border-gray-300 hover:bg-blue-600 hover:text-white transition-colors">
        Conference Papers ({len(conference_papers)})
      </button>
      <button onclick="filterPublications('books')" class="filter-btn px-4 py-2 rounded-lg border border-gray-300 hover:bg-blue-600 hover:text-white transition-colors">
        Books ({len(books)})
      </button>
      <button onclick="filterPublications('chapters')" class="filter-btn px-4 py-2 rounded-lg border border-gray-300 hover:bg-blue-600 hover:text-white transition-colors">
        Book Chapters ({len(book_chapters)})
      </button>
    </div>
  </div>

  <!-- Main Content -->
  <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pb-16">
    
    <!-- Journal Articles -->
    <section id="articles" class="publication-section mb-12">
      <h2 class="text-2xl font-bold text-gray-900 mb-6 flex items-center">
        <span class="bg-blue-600 text-white px-3 py-1 rounded-lg mr-3 text-sm">{len(articles)}</span>
        Journal Articles
      </h2>
      <div class="space-y-3">
{articles_html}
      </div>
    </section>

    <!-- Conference Papers -->
    <section id="conference" class="publication-section mb-12">
      <h2 class="text-2xl font-bold text-gray-900 mb-6 flex items-center">
        <span class="bg-green-600 text-white px-3 py-1 rounded-lg mr-3 text-sm">{len(conference_papers)}</span>
        Conference Papers
      </h2>
      <div class="space-y-3">
{conferences_html}
      </div>
    </section>

    <!-- Books -->
    <section id="books" class="publication-section mb-12">
      <h2 class="text-2xl font-bold text-gray-900 mb-6 flex items-center">
        <span class="bg-purple-600 text-white px-3 py-1 rounded-lg mr-3 text-sm">{len(books)}</span>
        Books Published or Organized
      </h2>
      <div class="space-y-3">
{books_html}
      </div>
    </section>

    <!-- Book Chapters -->
    <section id="chapters" class="publication-section mb-12">
      <h2 class="text-2xl font-bold text-gray-900 mb-6 flex items-center">
        <span class="bg-orange-600 text-white px-3 py-1 rounded-lg mr-3 text-sm">{len(book_chapters)}</span>
        Book Chapters
      </h2>
      <div class="space-y-3">
{chapters_html}
      </div>
    </section>

    <!-- Links Section -->
    <section class="mt-12 bg-white rounded-xl p-8 shadow-sm border">
      <h2 class="text-xl font-bold text-gray-900 mb-6">Publication Profiles</h2>
      <div class="flex flex-wrap gap-4">
        <a href="https://scholar.google.com.br/citations?user=gvb7W0IAAAAJ" target="_blank" rel="noopener" 
           class="inline-flex items-center px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">
          <svg class="w-5 h-5 mr-2" viewBox="0 0 24 24" fill="currentColor">
            <path d="M12 24a7 7 0 110-14 7 7 0 010 14zm0-24L0 9.5l4.838 3.94A8 8 0 0112 9a8 8 0 017.162 4.44L24 9.5z"/>
          </svg>
          Google Scholar
        </a>
        <a href="http://lattes.cnpq.br/7573837292080522" target="_blank" rel="noopener"
           class="inline-flex items-center px-6 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors">
          Currículo Lattes
        </a>
        <a href="https://www.scopus.com/authid/detail.uri?authorId=55425796800" target="_blank" rel="noopener"
           class="inline-flex items-center px-6 py-3 bg-orange-500 text-white rounded-lg hover:bg-orange-600 transition-colors">
          Scopus Profile
        </a>
        <a href="https://www.webofscience.com/wos/author/record/C-4546-2013" target="_blank" rel="noopener"
           class="inline-flex items-center px-6 py-3 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors">
          Web of Science
        </a>
        <a href="https://dblp.org/pid/s/AlbertoFdeSouza.html" target="_blank" rel="noopener"
           class="inline-flex items-center px-6 py-3 bg-gray-700 text-white rounded-lg hover:bg-gray-800 transition-colors">
          DBLP
        </a>
        <a href="https://orcid.org/0000-0003-1561-8447" target="_blank" rel="noopener"
           class="inline-flex items-center px-6 py-3 bg-green-700 text-white rounded-lg hover:bg-green-800 transition-colors">
          ORCID
        </a>
      </div>
    </section>

  </main>

  <!-- Footer -->
  <footer class="bg-ufes-blue text-white py-8">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
      <p class="text-blue-200">
        Data extracted from Currículo Lattes (CNPq) • Last updated: {update_date}
      </p>
      <p class="mt-2">
        <a href="index.html" class="text-white hover:text-ufes-gold">← Back to Home</a>
      </p>
    </div>
  </footer>

  <!-- Filter Script -->
  <script>
    function filterPublications(type) {{
      // Update button states
      document.querySelectorAll('.filter-btn').forEach(btn => {{
        btn.classList.remove('active', 'bg-blue-600', 'text-white');
      }});
      event.target.classList.add('active', 'bg-blue-600', 'text-white');

      // Show/hide sections
      const sections = document.querySelectorAll('.publication-section');
      sections.forEach(section => {{
        if (type === 'all') {{
          section.style.display = 'block';
        }} else if (type === 'articles' && section.id === 'articles') {{
          section.style.display = 'block';
        }} else if (type === 'conference' && section.id === 'conference') {{
          section.style.display = 'block';
        }} else if (type === 'books' && section.id === 'books') {{
          section.style.display = 'block';
        }} else if (type === 'chapters' && section.id === 'chapters') {{
          section.style.display = 'block';
        }} else if (type !== 'all') {{
          section.style.display = 'none';
        }}
      }});
    }}
  </script>
</body>
</html>'''
    
    return html


def generate_project_card(proj: dict, index: int, translations: dict) -> str:
    """Generate HTML for a single project card with description."""
    name = proj.get('name', '')
    name_en = proj.get('name_en', '') or translations.get(name, {}).get('name', name)
    year_start = proj.get('year_start', '')
    year_end = proj.get('year_end', '') or 'present'
    status = proj.get('status', '')
    description = proj.get('description', '')
    description_en = proj.get('description_en', '') or translations.get(name, {}).get('description', '')
    
    # Get funding agencies
    funding = proj.get('funding', [])
    funding_str = ", ".join([f.get('agency', '') for f in funding if f.get('agency')])
    # Simplify funding names
    funding_str = funding_str.replace('FUNDAÇÃO ESPÍRITO-SANTENSE DE TECNOLOGIA', 'FEST')
    funding_str = funding_str.replace('(FAPES) Fundação de Amparo à Pesquisa do Espírito Santo', 'FAPES')
    funding_str = funding_str.replace('Fundação de Amparo à Pesquisa do Espírito Santo', 'FAPES')
    funding_str = funding_str.replace('CONSELHO NACIONAL DE DESENVOLVIMENTO CIENTIFICO E TECNOLOGICO-CNPQ', 'CNPq')
    funding_str = funding_str.replace('Conselho Nacional de Desenvolvimento Científico e Tecnológico', 'CNPq')
    funding_str = funding_str.replace('Financiadora de Estudos e Projetos', 'FINEP')
    funding_str = funding_str.replace('Petrobrás Transporte - Matriz', 'Petrobras')
    funding_str = funding_str.replace('ArcelorMittal Brasil - Matriz', 'ArcelorMittal')
    
    status_class = 'status-ongoing' if status == 'EM_ANDAMENTO' else 'status-completed'
    status_text = 'Ongoing' if status == 'EM_ANDAMENTO' else 'Completed'
    border_color = 'green' if status == 'EM_ANDAMENTO' else 'indigo'
    project_class = 'ongoing' if status == 'EM_ANDAMENTO' else 'completed'
    
    # Escape HTML
    name_escaped = escape(name)
    name_en_escaped = escape(name_en) if name_en != name else ""
    description_escaped = escape(description_en) if description_en else escape(description)
    
    # Build description section
    desc_html = ""
    if description_escaped:
        desc_html = f'''
            <div id="desc-{index}" class="mt-3 text-sm text-gray-600 hidden">
              <p class="bg-gray-50 p-4 rounded-lg">{description_escaped}</p>
            </div>'''
    
    # Title with toggle if description exists
    if description:
        title_html = f'''<h3 class="text-lg font-semibold text-gray-900 mb-2">
              <button onclick="toggleDescription({index})" class="text-left hover:text-blue-600 flex items-center gap-2">
                <span>{name_en_escaped if name_en_escaped else name_escaped}</span>
                <svg id="icon-{index}" class="w-4 h-4 transform transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/>
                </svg>
              </button>
            </h3>'''
    else:
        title_html = f'''<h3 class="text-lg font-semibold text-gray-900 mb-2">
              {name_en_escaped if name_en_escaped else name_escaped}
            </h3>'''
    
    # Original Portuguese name if different
    original_html = ""
    if name_en_escaped and name_en != name:
        original_html = f'''<p class="text-sm text-gray-500 mb-2">
              <span class="font-medium">Original:</span> {name_escaped}
            </p>'''
    
    return f'''        <div class="project-card {project_class} bg-white p-6 rounded-xl border-l-4 border-{border_color}-500 shadow-sm hover:shadow-md transition-shadow">
            <div class="flex items-start justify-between mb-3">
              <span class="{status_class} px-3 py-1 rounded-full text-sm font-medium">{status_text}</span>
              <span class="text-gray-500 font-medium">{year_start} - {year_end}</span>
            </div>
            {title_html}
            {original_html}
            <div class="flex flex-wrap gap-2">
              <span class="bg-gray-100 text-gray-700 px-2 py-1 rounded text-xs">Funding: {funding_str if funding_str else 'N/A'}</span>
            </div>{desc_html}
          </div>'''


# Project name and description translations (Portuguese to English)
PROJECT_TRANSLATIONS = {
    "Investigação e Experimentação de Técnicas de Ajuste Fino de Grandes Modelos de Linguagem para Processo de Gestão da Inovação": {
        "name": "Investigation and Experimentation of Fine-Tuning Techniques for Large Language Models in Innovation Management Processes",
        "description": "This research project aims to investigate and experiment with fine-tuning techniques for Large Language Models (LLMs) focused on improving innovation management processes. The goal is to develop and validate methodologies that enable the customization of LLMs to specific organizational contexts, enhancing decision-making and knowledge management in innovation ecosystems."
    },
    "Desenvolvimento de Algoritmos de Percepção para Veículos Autônomos em Ambientes Industriais e de Mineração": {
        "name": "Development of Perception Algorithms for Autonomous Vehicles in Industrial and Mining Environments",
        "description": "The general objective of this project is to advance the development of Autonomous Computational Intelligences (ACIs), integrating it into a strategic set of I2CA macro-projects. These macro-projects aim to consolidate applied research in computational intelligence for industry, with emphasis on autonomous vehicles and intelligent robotic systems for industrial and mining environments."
    },
    "Inteligências Computacionais Autônomas Baseadas em Generative Pre-trained Transformers (ICAGPT)": {
        "name": "Autonomous Computational Intelligences Based on Generative Pre-trained Transformers (ICAGPT)",
        "description": "In this project, we propose the development of science and technology necessary for implementing powerful Autonomous Computational Intelligences (ACIs). ACIs are software and hardware systems that can autonomously perform complex tasks that currently require high-level human skills, such as driving vehicles, operating industrial equipment, and making complex decisions based on multimodal data."
    },
    "Movimentação de Pilhas de Blocos não Identificados por meio de Robôs Autônomos": {
        "name": "Movement of Unidentified Block Piles by Autonomous Robots",
        "description": "This project focuses on developing autonomous robotic systems capable of manipulating and organizing unidentified block piles in industrial environments. The research combines computer vision, deep learning, and robotic manipulation techniques to enable robots to work efficiently with objects that have not been previously catalogued or identified."
    },
    "Infraestrutura para Projetos interdisciplinares de Informática Aplicada à Saúde": {
        "name": "Infrastructure for Interdisciplinary Projects in Health Informatics",
        "description": "This project aims to establish computational infrastructure to support interdisciplinary research projects in health informatics, enabling the development and application of artificial intelligence techniques for medical diagnosis, health data analysis, and clinical decision support systems."
    },
    "Diagnóstico de Falhas em Motores Elétricos Baseado em Inteligência Artificial - DIME": {
        "name": "Fault Diagnosis in Electric Motors Based on Artificial Intelligence - DIME",
        "description": "The DIME project develops artificial intelligence-based systems for predictive maintenance and fault diagnosis in electric motors used in the oil and gas industry. Using machine learning and signal processing techniques, the system can identify incipient failures before they cause equipment breakdown."
    },
    "Desenvolvimento de novas tecnologias de Inteligência Artificial para veículos autônomos": {
        "name": "Development of New Artificial Intelligence Technologies for Autonomous Vehicles",
        "description": "This project aims to advance the state-of-the-art in artificial intelligence for autonomous vehicles, developing new deep learning architectures, perception algorithms, and decision-making systems that enable fully autonomous navigation in complex real-world environments."
    },
    "Inteligências Computacionais Autônomas": {
        "name": "Autonomous Computational Intelligences",
        "description": "This project focuses on fundamental research in autonomous computational intelligences, systems that can perceive their environment, reason about it, and take actions to achieve goals without continuous human supervision. The research encompasses perception, learning, planning, and control."
    },
    "Instituto de Inteligência Computacional Aplicada - I2CA": {
        "name": "Institute of Applied Computational Intelligence - I2CA",
        "description": "The Institute of Applied Computational Intelligence (I2CA) was established to conduct cutting-edge research in applied computational intelligence for industry, focusing on autonomous vehicles and other intelligent autonomous systems, training specialized personnel and strengthening the ecosystem of companies that employ and develop Artificial Intelligence."
    },
    "Carros Autônomos SAE Nível 5": {
        "name": "SAE Level 5 Autonomous Cars",
        "description": "This project aimed to develop fully autonomous vehicles (SAE Level 5) capable of operating without any human intervention in any driving condition. The research included perception systems, path planning, vehicle control, and integration with the IARA autonomous vehicle platform."
    },
    "Redes Neurais Profundas no Apoio à Fiscalização": {
        "name": "Deep Neural Networks for Regulatory Enforcement Support",
        "description": "This project developed deep neural network systems to support regulatory and enforcement activities, using computer vision and natural language processing to automate document analysis and pattern detection in large datasets."
    },
    "Desenvolvimento e Testes de um Demonstrador Tecnológico para Aeronaves baseado em Robótica Autônoma": {
        "name": "Development and Testing of a Technology Demonstrator for Aircraft Based on Autonomous Robotics",
        "description": "In partnership with Embraer, this project developed the world's first autonomous taxiing system for commercial aircraft. The system uses computer vision, sensor fusion, and artificial intelligence to enable aircraft to taxi autonomously on airport surfaces."
    },
    "Visão Artificial e Robótica Autônoma Aplicadas à Mineração": {
        "name": "Artificial Vision and Autonomous Robotics Applied to Mining",
        "description": "This project applied computer vision and autonomous robotics technologies to the mining industry, developing systems for autonomous vehicle operation, ore pile measurement, and environmental monitoring in mining operations."
    },
    "Cognição Espacial Artificial e sua Implementação Eficiente por meio de Computação de Alto Desempenho": {
        "name": "Artificial Spatial Cognition and its Efficient Implementation through High-Performance Computing",
        "description": "This long-term research project investigates artificial spatial cognition, developing computational models that enable machines to understand and navigate complex spatial environments, with efficient implementations using high-performance computing techniques including GPU acceleration."
    },
    "Sistema Inteligente para Negociação Automática de Ativos": {
        "name": "Intelligent System for Automatic Asset Trading",
        "description": "This project developed intelligent systems for automatic trading in financial markets, using machine learning and technical analysis to identify trading opportunities and execute transactions automatically."
    },
    "PhotoPography - Sistema de Topografia de Pilhas de Minério via Internet": {
        "name": "PhotoPography - Ore Pile Topography System via Internet",
        "description": "PhotoPography was an innovative system that used photogrammetry and stereo vision to measure the volume of ore piles remotely via the Internet, providing real-time inventory management for mining operations."
    },
    "HammerHead 2 - Projeto industrial de Equipamento Inovador para Captura de Imagens Estéreo": {
        "name": "HammerHead 2 - Industrial Design of Innovative Equipment for Stereo Image Capture",
        "description": "This project developed specialized industrial equipment for stereo image capture, designed for harsh industrial environments and optimized for computer vision applications in mining and manufacturing."
    },
    "Consolidação das Linhas de Pesquisa em Computação de Alto Desempenho, Otimização e Inteligência Computacional do PPGI-UFES": {
        "name": "Consolidation of Research Lines in High-Performance Computing, Optimization and Computational Intelligence at PPGI-UFES",
        "description": "This project aimed to consolidate and strengthen the research groups in high-performance computing, optimization, and computational intelligence at the Graduate Program in Informatics (PPGI) at UFES."
    },
    "Arquitetura e Programação de Sistemas Computacionais com Muitos Núcleos de Processamento": {
        "name": "Architecture and Programming of Many-Core Computing Systems",
        "description": "This project researched architectures and programming paradigms for computing systems with many processing cores, investigating parallel programming models and optimization techniques for multi-core and GPU systems."
    },
    "Modelos Matemático-Computacionais de Exploração e Busca Visual Aplicados ao Problema de Mapeamento e Localização Simultâneos de Robôs": {
        "name": "Mathematical-Computational Models of Visual Exploration and Search Applied to Simultaneous Localization and Mapping for Robots",
        "description": "This project developed mathematical and computational models for visual exploration and search, applying them to the Simultaneous Localization and Mapping (SLAM) problem in mobile robotics."
    },
    "PRONEX: Núcleo de Excelência em Computação de Alto Desempenho e sua Aplicação em Computação Científica e Inteligência Computacional": {
        "name": "PRONEX: Center of Excellence in High-Performance Computing and its Application in Scientific Computing and Computational Intelligence",
        "description": "This PRONEX project established a center of excellence in high-performance computing at UFES, fostering research in scientific computing and computational intelligence applications."
    },
    "Fortalecimento das Áreas de Computação de Alto Desempenho, Otimização e Inteligência Computacional do Programa de Pós-Graduação em Informática da UFES": {
        "name": "Strengthening High-Performance Computing, Optimization and Computational Intelligence Areas of the Graduate Program in Informatics at UFES",
        "description": "This project provided infrastructure and resources to strengthen the research areas of high-performance computing, optimization, and computational intelligence within UFES's Graduate Program in Informatics."
    },
    "Sistema de Medição baseado em Visão Artificial": {
        "name": "Measurement System Based on Artificial Vision",
        "description": "This project developed computer vision-based measurement systems for industrial applications, enabling accurate non-contact measurement of dimensions, areas, and volumes."
    },
    "Desenvolvimento de um Sistema de Localização e Mapeamento 3D por Visão Artificial para Navegação de Robôs e Veículos Aéreos ou Submarinos Não Tripulados": {
        "name": "Development of a 3D Localization and Mapping System by Artificial Vision for Navigation of Robots and Unmanned Aerial or Submarine Vehicles",
        "description": "This project developed 3D localization and mapping systems using computer vision for navigation of mobile robots, UAVs, and underwater vehicles, advancing the state-of-the-art in visual SLAM."
    },
    "Visita Técnico-Científica ao Department of Computing da City University London": {
        "name": "Technical-Scientific Visit to the Department of Computing at City University London",
        "description": "This project supported a technical-scientific visit to City University London's Department of Computing to strengthen international collaboration and exchange research experiences."
    },
    "Arquitetura de Sistemas Computacionais com Muitos Núcleos de Processamento em um Único CI": {
        "name": "Architecture of Computing Systems with Many Processing Cores on a Single Chip",
        "description": "This project researched many-core processor architectures on a single chip, investigating design principles and programming models for efficient utilization of massively parallel computing resources."
    },
    "Modernização da Infra-Estrutura de Pesquisa da Área de Computação de Alto Desempenho da UFES": {
        "name": "Modernization of Research Infrastructure in High-Performance Computing at UFES",
        "description": "This project modernized the high-performance computing research infrastructure at UFES, acquiring computational equipment and establishing facilities for advanced research."
    },
    "Classificação Automática em CNAE-Subclasse": {
        "name": "Automatic Classification in CNAE-Subclass",
        "description": "This project, in partnership with the Federal Revenue Service, developed automatic text classification systems to categorize economic activities according to the Brazilian National Classification of Economic Activities (CNAE) subclasses."
    },
    "Fortalecimento das Áreas de Computação de Alto Desempenho e Inteligência Computacional do Programa de Pós-Graduação em Informática da UFES": {
        "name": "Strengthening High-Performance Computing and Computational Intelligence Areas of the Graduate Program in Informatics at UFES",
        "description": "This project strengthened the research infrastructure and human resources in high-performance computing and computational intelligence at UFES's Graduate Program in Informatics."
    },
    "Automatizando a Medição de Dimensões, Áreas e Volumes": {
        "name": "Automating the Measurement of Dimensions, Areas, and Volumes",
        "description": "This project developed automated measurement systems using computer vision and image processing to accurately measure dimensions, areas, and volumes in industrial applications."
    },
    "Novas Arquiteturas de Alto Desempenho Baseadas no Escalonamento Dinâmico de Instruções": {
        "name": "New High-Performance Architectures Based on Dynamic Instruction Scheduling",
        "description": "This project researched new high-performance processor architectures based on dynamic instruction scheduling, continuing the work initiated during the DTSVLIW research."
    },
    "Arquiteturas de Computadores e Hierarquias de Memória Avançadas": {
        "name": "Advanced Computer Architectures and Memory Hierarchies",
        "description": "This project investigated advanced computer architectures and memory hierarchy designs to improve processor performance and energy efficiency."
    },
    "Rede Metropolitana de Alta Velocidade de Vitória - Metrovix": {
        "name": "Vitória Metropolitan High-Speed Network - Metrovix",
        "description": "The Metrovix project established a metropolitan high-speed optical network connecting research and education institutions in the Vitória metropolitan area, enabling advanced network applications and research."
    },
    "Rede GIGA: Implantação e utilização de um GRID de 1TFLOP/s": {
        "name": "GIGA Network: Implementation and Utilization of a 1TFLOP/s GRID",
        "description": "This project implemented and utilized a computational grid with 1 TFLOP/s capacity as part of the GIGA network infrastructure, enabling distributed high-performance computing research."
    },
    "Sistema Automático de Medição de Volumes Baseado em Visão Artificial": {
        "name": "Automatic Volume Measurement System Based on Artificial Vision",
        "description": "This project developed an automatic volume measurement system using stereo vision and photogrammetry for industrial applications, particularly in inventory management."
    },
    "Melhorias de Infra-Estrutura para o Funcionamento do LCAD": {
        "name": "Infrastructure Improvements for LCAD Operations",
        "description": "This project provided infrastructure improvements for the High-Performance Computing Laboratory (LCAD) at UFES, enhancing research capabilities and facilities."
    },
    "Plataforma de Acesso Seguro a Vídeo Sob Demanda para Dispositivos Móveis Sem Fio com Garantia de Qualidade de Serviço - TRAVIS-QDS": {
        "name": "Secure Video-on-Demand Access Platform for Wireless Mobile Devices with Quality of Service Guarantee - TRAVIS-QDS",
        "description": "The TRAVIS-QDS project developed a platform for secure video-on-demand access on wireless mobile devices, with quality of service guarantees for multimedia streaming."
    },
    "Arquiteturas Avançadas de Processador": {
        "name": "Advanced Processor Architectures",
        "description": "This foundational project researched advanced processor architectures, continuing the investigation of dynamic instruction scheduling and high-performance computing techniques."
    }
}


def generate_projects_html(data: dict) -> str:
    """Generate complete projects HTML page."""
    
    projects = data.get('projects', [])
    
    # Separate ongoing and completed projects
    ongoing = [p for p in projects if p.get('status') == 'EM_ANDAMENTO']
    completed = [p for p in projects if p.get('status') != 'EM_ANDAMENTO']
    
    # Generate project cards
    ongoing_html = "\n\n".join(generate_project_card(p, i, PROJECT_TRANSLATIONS) for i, p in enumerate(ongoing))
    completed_html = "\n\n".join(generate_project_card(p, i + len(ongoing), PROJECT_TRANSLATIONS) for i, p in enumerate(completed))
    
    update_date = datetime.now().strftime('%B %Y')
    
    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta name="description" content="Research projects by Prof. Dr. Alberto Ferreira De Souza">
  <title>Research Projects - Prof. Dr. Alberto Ferreira De Souza</title>
  
  <!-- Tailwind CSS CDN -->
  <script src="https://cdn.tailwindcss.com"></script>
  
  <!-- Custom Tailwind Config -->
  <script>
    tailwind.config = {{
      theme: {{
        extend: {{
          colors: {{
            'ufes-blue': '#003366',
            'ufes-gold': '#FFD700',
          }}
        }}
      }}
    }}
  </script>
  
  <!-- Custom Styles -->
  <link rel="stylesheet" href="assets/css/style.css">
  
  <style>
    .project-card {{
      transition: all 0.2s ease;
    }}
    .project-card:hover {{
      transform: translateY(-2px);
    }}
    .status-ongoing {{
      background-color: #dcfce7;
      color: #166534;
    }}
    .status-completed {{
      background-color: #e0e7ff;
      color: #3730a3;
    }}
    .filter-btn.active {{
      background-color: #2563eb;
      color: white;
    }}
  </style>
</head>
<body class="bg-gray-50 min-h-screen">
  <!-- Navigation -->
  <nav class="bg-ufes-blue text-white py-4 sticky top-0 z-50 shadow-lg">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="flex items-center justify-between">
        <a href="index.html" class="text-xl font-bold hover:text-ufes-gold transition-colors">
          ← Back to Home
        </a>
        <h1 class="text-lg font-semibold hidden sm:block">Prof. Dr. Alberto Ferreira De Souza</h1>
      </div>
    </div>
  </nav>

  <!-- Header -->
  <header class="bg-gradient-to-r from-ufes-blue to-blue-800 text-white py-12">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <h1 class="text-4xl font-bold mb-4">Research Projects</h1>
      <p class="text-blue-200 text-lg">
        {len(projects)} research projects ({len(ongoing)} ongoing, {len(completed)} completed) from 2003 to 2025
      </p>
      <p class="text-blue-300 text-sm mt-2">
        Click on project titles to expand descriptions
      </p>
    </div>
  </header>

  <!-- Filter Buttons -->
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
    <div class="flex flex-wrap gap-3">
      <button onclick="filterProjects('all')" class="filter-btn active px-4 py-2 rounded-lg border border-gray-300 hover:bg-blue-600 hover:text-white transition-colors">
        All Projects ({len(projects)})
      </button>
      <button onclick="filterProjects('ongoing')" class="filter-btn px-4 py-2 rounded-lg border border-gray-300 hover:bg-blue-600 hover:text-white transition-colors">
        Ongoing ({len(ongoing)})
      </button>
      <button onclick="filterProjects('completed')" class="filter-btn px-4 py-2 rounded-lg border border-gray-300 hover:bg-blue-600 hover:text-white transition-colors">
        Completed ({len(completed)})
      </button>
    </div>
  </div>

  <!-- Main Content -->
  <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pb-16">
    
    <!-- Ongoing Projects Section -->
    <section id="ongoing-section" class="mb-12">
      <h2 class="text-2xl font-bold text-gray-900 mb-6 flex items-center">
        <span class="w-3 h-3 bg-green-500 rounded-full mr-3"></span>
        Ongoing Projects ({len(ongoing)})
      </h2>
      
      <div class="space-y-4">
{ongoing_html}
      </div>
    </section>

    <!-- Completed Projects Section -->
    <section id="completed-section" class="mb-12">
      <h2 class="text-2xl font-bold text-gray-900 mb-6 flex items-center">
        <span class="w-3 h-3 bg-indigo-500 rounded-full mr-3"></span>
        Completed Projects ({len(completed)})
      </h2>
      
      <div class="space-y-4">
{completed_html}
      </div>
    </section>

    <!-- Funding Agencies -->
    <section class="mt-12 bg-white rounded-xl p-8 shadow-sm border">
      <h2 class="text-xl font-bold text-gray-900 mb-6">Main Funding Agencies</h2>
      <div class="grid grid-cols-2 md:grid-cols-4 gap-6 text-center">
        <div class="p-4">
          <div class="text-3xl font-bold text-blue-600">CNPq</div>
          <p class="text-sm text-gray-500 mt-1">National Council for Scientific and Technological Development</p>
        </div>
        <div class="p-4">
          <div class="text-3xl font-bold text-green-600">FAPES</div>
          <p class="text-sm text-gray-500 mt-1">Espírito Santo Research Foundation</p>
        </div>
        <div class="p-4">
          <div class="text-3xl font-bold text-orange-600">FINEP</div>
          <p class="text-sm text-gray-500 mt-1">Funding Authority for Studies and Projects</p>
        </div>
        <div class="p-4">
          <div class="text-3xl font-bold text-purple-600">Industry</div>
          <p class="text-sm text-gray-500 mt-1">Embraer, Petrobras, ArcelorMittal</p>
        </div>
      </div>
    </section>

  </main>

  <!-- Footer -->
  <footer class="bg-ufes-blue text-white py-8">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
      <p class="text-blue-200">
        Data extracted from Currículo Lattes (CNPq) • Last updated: {update_date}
      </p>
      <p class="mt-2">
        <a href="index.html" class="text-white hover:text-ufes-gold">← Back to Home</a>
      </p>
    </div>
  </footer>

  <!-- Scripts -->
  <script>
    function toggleDescription(index) {{
      const desc = document.getElementById('desc-' + index);
      const icon = document.getElementById('icon-' + index);
      
      if (desc.classList.contains('hidden')) {{
        desc.classList.remove('hidden');
        icon.classList.add('rotate-180');
      }} else {{
        desc.classList.add('hidden');
        icon.classList.remove('rotate-180');
      }}
    }}

    function filterProjects(type) {{
      // Update button states
      document.querySelectorAll('.filter-btn').forEach(btn => {{
        btn.classList.remove('active', 'bg-blue-600', 'text-white');
      }});
      event.target.classList.add('active', 'bg-blue-600', 'text-white');

      const ongoingSection = document.getElementById('ongoing-section');
      const completedSection = document.getElementById('completed-section');

      if (type === 'all') {{
        ongoingSection.style.display = 'block';
        completedSection.style.display = 'block';
      }} else if (type === 'ongoing') {{
        ongoingSection.style.display = 'block';
        completedSection.style.display = 'none';
      }} else if (type === 'completed') {{
        ongoingSection.style.display = 'none';
        completedSection.style.display = 'block';
      }}
    }}
  </script>
</body>
</html>'''
    
    return html


def main():
    """Main function to generate HTML pages."""
    print("=" * 60)
    print("Generating Lattes HTML Pages")
    print("=" * 60)
    print()
    
    # Load data
    print(f"Loading data from: {DATA_FILE}")
    data = load_data()
    
    print(f"Data loaded:")
    print(f"  - Journal articles: {len(data.get('articles', []))}")
    print(f"  - Conference papers: {len(data.get('conference_papers', []))}")
    print(f"  - Books: {len(data.get('books', []))}")
    print(f"  - Book chapters: {len(data.get('book_chapters', []))}")
    print(f"  - Research projects: {len(data.get('projects', []))}")
    print()
    
    # Generate publications page
    print(f"Generating publications page...")
    publications_html = generate_publications_html(data)
    with open(PUBLICATIONS_FILE, 'w', encoding='utf-8') as f:
        f.write(publications_html)
    print(f"  Saved to: {PUBLICATIONS_FILE}")
    
    # Generate projects page
    print(f"Generating projects page...")
    projects_html = generate_projects_html(data)
    with open(PROJECTS_FILE, 'w', encoding='utf-8') as f:
        f.write(projects_html)
    print(f"  Saved to: {PROJECTS_FILE}")
    
    print()
    print("=" * 60)
    print("SUCCESS: HTML pages generated!")
    print("=" * 60)
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
