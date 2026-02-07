#!/usr/bin/env python3
"""
Parse Lattes XML curriculum and extract publications and projects.

This script reads a Lattes XML file and outputs structured JSON data
for publications and projects.

Usage:
    python parse_lattes.py <lattes.xml>
"""

import xml.etree.ElementTree as ET
import json
import sys
from pathlib import Path


def parse_lattes_xml(xml_path: str) -> dict:
    """Parse Lattes XML and extract publications and projects."""
    
    tree = ET.parse(xml_path)
    root = tree.getroot()
    
    data = {
        'articles': [],
        'conference_papers': [],
        'books': [],
        'book_chapters': [],
        'projects': []
    }
    
    # Extract journal articles
    for artigo in root.iter('ARTIGO-PUBLICADO'):
        dados = artigo.find('DADOS-BASICOS-DO-ARTIGO')
        detalhes = artigo.find('DETALHAMENTO-DO-ARTIGO')
        
        if dados is not None:
            authors = []
            for autor in artigo.iter('AUTORES'):
                name = autor.get('NOME-COMPLETO-DO-AUTOR', '')
                order = int(autor.get('ORDEM-DE-AUTORIA', 0))
                authors.append((order, name))
            
            authors.sort(key=lambda x: x[0])
            author_list = [a[1] for a in authors]
            
            article = {
                'title': dados.get('TITULO-DO-ARTIGO', ''),
                'title_en': dados.get('TITULO-DO-ARTIGO-INGLES', ''),
                'year': dados.get('ANO-DO-ARTIGO', ''),
                'doi': dados.get('DOI', ''),
                'language': dados.get('IDIOMA', ''),
                'authors': author_list,
                'journal': detalhes.get('TITULO-DO-PERIODICO-OU-REVISTA', '') if detalhes is not None else '',
                'volume': detalhes.get('VOLUME', '') if detalhes is not None else '',
                'issue': detalhes.get('FASCICULO', '') if detalhes is not None else '',
                'pages': f"{detalhes.get('PAGINA-INICIAL', '')}-{detalhes.get('PAGINA-FINAL', '')}" if detalhes is not None else '',
                'issn': detalhes.get('ISSN', '') if detalhes is not None else ''
            }
            data['articles'].append(article)
    
    # Extract conference papers
    for trabalho in root.iter('TRABALHO-EM-EVENTOS'):
        dados = trabalho.find('DADOS-BASICOS-DO-TRABALHO')
        detalhes = trabalho.find('DETALHAMENTO-DO-TRABALHO')
        
        if dados is not None:
            authors = []
            for autor in trabalho.iter('AUTORES'):
                name = autor.get('NOME-COMPLETO-DO-AUTOR', '')
                order = int(autor.get('ORDEM-DE-AUTORIA', 0))
                authors.append((order, name))
            
            authors.sort(key=lambda x: x[0])
            author_list = [a[1] for a in authors]
            
            paper = {
                'title': dados.get('TITULO-DO-TRABALHO', ''),
                'title_en': dados.get('TITULO-DO-TRABALHO-INGLES', ''),
                'year': dados.get('ANO-DO-TRABALHO', ''),
                'doi': dados.get('DOI', ''),
                'language': dados.get('IDIOMA', ''),
                'authors': author_list,
                'event': detalhes.get('NOME-DO-EVENTO', '') if detalhes is not None else '',
                'event_en': detalhes.get('NOME-DO-EVENTO-INGLES', '') if detalhes is not None else '',
                'proceedings': detalhes.get('TITULO-DOS-ANAIS-OU-PROCEEDINGS', '') if detalhes is not None else '',
                'pages': f"{detalhes.get('PAGINA-INICIAL', '')}-{detalhes.get('PAGINA-FINAL', '')}" if detalhes is not None else '',
                'city': detalhes.get('CIDADE-DO-EVENTO', '') if detalhes is not None else '',
                'country': detalhes.get('PAIS-DO-EVENTO', '') if detalhes is not None else ''
            }
            data['conference_papers'].append(paper)
    
    # Extract books
    for livro in root.iter('LIVRO-PUBLICADO-OU-ORGANIZADO'):
        dados = livro.find('DADOS-BASICOS-DO-LIVRO')
        detalhes = livro.find('DETALHAMENTO-DO-LIVRO')
        
        if dados is not None:
            authors = []
            for autor in livro.iter('AUTORES'):
                name = autor.get('NOME-COMPLETO-DO-AUTOR', '')
                order = int(autor.get('ORDEM-DE-AUTORIA', 0))
                authors.append((order, name))
            
            authors.sort(key=lambda x: x[0])
            author_list = [a[1] for a in authors]
            
            book = {
                'title': dados.get('TITULO-DO-LIVRO', ''),
                'title_en': dados.get('TITULO-DO-LIVRO-INGLES', ''),
                'year': dados.get('ANO', ''),
                'doi': dados.get('DOI', ''),
                'authors': author_list,
                'publisher': detalhes.get('NOME-DA-EDITORA', '') if detalhes is not None else '',
                'isbn': detalhes.get('ISBN', '') if detalhes is not None else '',
                'pages': detalhes.get('NUMERO-DE-PAGINAS', '') if detalhes is not None else ''
            }
            data['books'].append(book)
    
    # Extract book chapters
    for capitulo in root.iter('CAPITULO-DE-LIVRO-PUBLICADO'):
        dados = capitulo.find('DADOS-BASICOS-DO-CAPITULO')
        detalhes = capitulo.find('DETALHAMENTO-DO-CAPITULO')
        
        if dados is not None:
            authors = []
            for autor in capitulo.iter('AUTORES'):
                name = autor.get('NOME-COMPLETO-DO-AUTOR', '')
                order = int(autor.get('ORDEM-DE-AUTORIA', 0))
                authors.append((order, name))
            
            authors.sort(key=lambda x: x[0])
            author_list = [a[1] for a in authors]
            
            chapter = {
                'title': dados.get('TITULO-DO-CAPITULO-DO-LIVRO', ''),
                'title_en': dados.get('TITULO-DO-CAPITULO-DO-LIVRO-INGLES', ''),
                'year': dados.get('ANO', ''),
                'doi': dados.get('DOI', ''),
                'authors': author_list,
                'book_title': detalhes.get('TITULO-DO-LIVRO', '') if detalhes is not None else '',
                'publisher': detalhes.get('NOME-DA-EDITORA', '') if detalhes is not None else '',
                'isbn': detalhes.get('ISBN', '') if detalhes is not None else '',
                'pages': f"{detalhes.get('PAGINA-INICIAL', '')}-{detalhes.get('PAGINA-FINAL', '')}" if detalhes is not None else ''
            }
            data['book_chapters'].append(chapter)
    
    # Extract research projects
    for projeto in root.iter('PROJETO-DE-PESQUISA'):
        proj_data = {
            'name': projeto.get('NOME-DO-PROJETO', ''),
            'year_start': projeto.get('ANO-INICIO', ''),
            'year_end': projeto.get('ANO-FIM', ''),
            'status': projeto.get('SITUACAO', ''),
            'nature': projeto.get('NATUREZA', ''),
            'description': '',
            'description_en': '',
            'funding': [],
            'members': []
        }
        
        # Get project description
        for equipe in projeto.iter('EQUIPE-DO-PROJETO'):
            for integrante in equipe.iter('INTEGRANTES-DO-PROJETO'):
                member = {
                    'name': integrante.get('NOME-COMPLETO', ''),
                    'role': integrante.get('FLAG-RESPONSAVEL', '')
                }
                proj_data['members'].append(member)
        
        # Get funding agencies
        for financiador in projeto.iter('FINANCIADOR-DO-PROJETO'):
            funding = {
                'agency': financiador.get('NOME-INSTITUICAO', ''),
                'nature': financiador.get('NATUREZA', '')
            }
            proj_data['funding'].append(funding)
        
        data['projects'].append(proj_data)
    
    # Sort by year (most recent first)
    data['articles'].sort(key=lambda x: x.get('year', '0'), reverse=True)
    data['conference_papers'].sort(key=lambda x: x.get('year', '0'), reverse=True)
    data['books'].sort(key=lambda x: x.get('year', '0'), reverse=True)
    data['book_chapters'].sort(key=lambda x: x.get('year', '0'), reverse=True)
    data['projects'].sort(key=lambda x: x.get('year_start', '0'), reverse=True)
    
    return data


def main():
    if len(sys.argv) < 2:
        print("Usage: python parse_lattes.py <lattes.xml>")
        sys.exit(1)
    
    xml_path = sys.argv[1]
    
    if not Path(xml_path).exists():
        print(f"Error: File not found: {xml_path}")
        sys.exit(1)
    
    print(f"Parsing Lattes XML: {xml_path}")
    data = parse_lattes_xml(xml_path)
    
    print(f"\nExtracted:")
    print(f"  - Journal articles: {len(data['articles'])}")
    print(f"  - Conference papers: {len(data['conference_papers'])}")
    print(f"  - Books: {len(data['books'])}")
    print(f"  - Book chapters: {len(data['book_chapters'])}")
    print(f"  - Research projects: {len(data['projects'])}")
    
    # Output JSON
    output_path = Path(__file__).parent.parent / "src" / "data" / "lattes_data.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"\nData saved to: {output_path}")
    
    return data


if __name__ == '__main__':
    main()
