#!/usr/bin/env python3
"""
Generate teaching.html from teaching.csv

This script reads the teaching.csv file containing course information
and generates a formatted HTML page for the academic website.

Usage:
    python scripts/generate_teaching.py
"""

import csv
import os
from collections import defaultdict

# Paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
CSV_FILE = os.path.join(PROJECT_ROOT, 'teaching.csv')
OUTPUT_FILE = os.path.join(PROJECT_ROOT, 'src', 'alberto', 'teaching.html')


def read_teaching_csv(csv_path):
    """Read and parse the teaching CSV file."""
    courses = []
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            courses.append({
                'year': int(row['year']),
                'semester': int(row['semester']),
                'code': row['course_code'].strip(),
                'section': row['section'].strip(),
                'name': row['course_name'].strip(),
                'details': row['details'].strip()
            })
    return courses


def categorize_course(course):
    """Categorize a course based on its details."""
    details_lower = course['details'].lower()
    name_lower = course['name'].lower()
    
    if 'gpt' in details_lower or 'generative' in details_lower or 'transformer' in details_lower:
        return 'generative-ai'
    elif 'deep learning' in details_lower or 'neural' in details_lower or 'cnn' in details_lower:
        return 'deep-learning'
    elif 'visual cognition' in details_lower or 'visual cognition' in name_lower:
        return 'visual-cognition'
    elif 'autonomous' in details_lower or 'robotic' in details_lower or 'vehicle' in details_lower or 'robot' in details_lower:
        return 'autonomous-robots'
    elif 'directed study' in name_lower:
        return 'directed-study'
    else:
        return 'other'


def get_course_type(course):
    """Determine if course is Master's or PhD level."""
    code = course['code']
    if code.startswith('PINF-6'):
        return "Master's"
    elif code.startswith('PINF-7'):
        return "PhD"
    else:
        return "Graduate"


def generate_html(courses):
    """Generate the teaching.html content."""
    
    # Group courses by year
    courses_by_year = defaultdict(list)
    for course in courses:
        courses_by_year[course['year']].append(course)
    
    # Sort years descending
    years = sorted(courses_by_year.keys(), reverse=True)
    
    # Count statistics
    total_courses = len(courses)
    years_span = f"{min(years)}-{max(years)}"
    years_count = max(years) - min(years) + 1  # Total years in the period
    
    # Generate course cards HTML
    course_cards_html = ""
    for year in years:
        year_courses = sorted(courses_by_year[year], key=lambda x: (-x['semester'], x['code']))
        
        course_cards_html += f'''
        <!-- Year {year} -->
        <div class="year-section mb-8" data-year="{year}">
          <h3 class="text-xl font-semibold text-gray-900 mb-4 border-b pb-2">{year}</h3>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
'''
        
        for course in year_courses:
            category = categorize_course(course)
            course_type = get_course_type(course)
            semester_label = f"{course['year']}/{course['semester']}"
            
            # Color based on category
            category_colors = {
                'generative-ai': 'purple',
                'deep-learning': 'blue',
                'visual-cognition': 'green',
                'autonomous-robots': 'orange',
                'directed-study': 'gray',
                'other': 'slate'
            }
            color = category_colors.get(category, 'gray')
            
            course_cards_html += f'''
            <div class="course-card bg-white rounded-lg shadow-sm border p-4 hover:shadow-md transition-shadow" 
                 data-category="{category}" data-year="{course['year']}">
              <div class="flex items-start justify-between mb-2">
                <span class="bg-{color}-100 text-{color}-800 text-xs font-medium px-2.5 py-0.5 rounded">{course_type}</span>
                <span class="text-sm text-gray-500">{semester_label}</span>
              </div>
              <h4 class="font-semibold text-gray-900 mb-1">{course['name']}</h4>
              <p class="text-sm text-gray-600 mb-2">{course['details']}</p>
              <p class="text-xs text-gray-400">Code: {course['code']} | Section: {course['section']}</p>
            </div>
'''
        
        course_cards_html += '''
          </div>
        </div>
'''
    
    # Full HTML template
    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Teaching - Prof. Alberto Ferreira De Souza</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <link rel="stylesheet" href="assets/css/style.css">
  <script>
    tailwind.config = {{
      theme: {{
        extend: {{
          colors: {{
            'ufes-blue': '#003366',
          }}
        }}
      }}
    }}
  </script>
</head>
<body class="bg-gray-100 min-h-screen">
  <!-- Navigation -->
  <nav class="bg-white shadow-sm sticky top-0 z-50">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="flex justify-between items-center h-16">
        <a href="index.html" class="text-xl font-bold text-ufes-blue">Alberto F. De Souza</a>
        <a href="index.html#teaching" class="inline-flex items-center text-blue-600 hover:text-blue-800 font-medium">
          <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"/>
          </svg>
          Back to Home
        </a>
      </div>
    </div>
  </nav>

  <!-- Header -->
  <header class="bg-gradient-to-r from-ufes-blue to-blue-800 text-white py-12">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <h1 class="text-4xl font-bold mb-4">Teaching</h1>
      <p class="text-blue-200 text-lg">Courses and Directed Studies ({years_span})</p>
      <div class="mt-4 flex flex-wrap gap-4 text-sm">
        <span class="bg-white/20 px-3 py-1 rounded-full">{total_courses} courses</span>
        <span class="bg-white/20 px-3 py-1 rounded-full">{years_count} years</span>
      </div>
    </div>
  </header>

  <!-- Filter Buttons -->
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
    <div class="flex flex-wrap gap-2 mb-6">
      <button onclick="filterCourses('all')" class="filter-btn active px-4 py-2 rounded-lg bg-ufes-blue text-white font-medium transition-colors" data-filter="all">
        All
      </button>
      <button onclick="filterCourses('generative-ai')" class="filter-btn px-4 py-2 rounded-lg bg-gray-200 text-gray-700 font-medium hover:bg-purple-100 transition-colors" data-filter="generative-ai">
        Generative AI
      </button>
      <button onclick="filterCourses('deep-learning')" class="filter-btn px-4 py-2 rounded-lg bg-gray-200 text-gray-700 font-medium hover:bg-blue-100 transition-colors" data-filter="deep-learning">
        Deep Learning
      </button>
      <button onclick="filterCourses('visual-cognition')" class="filter-btn px-4 py-2 rounded-lg bg-gray-200 text-gray-700 font-medium hover:bg-green-100 transition-colors" data-filter="visual-cognition">
        Visual Cognition
      </button>
      <button onclick="filterCourses('autonomous-robots')" class="filter-btn px-4 py-2 rounded-lg bg-gray-200 text-gray-700 font-medium hover:bg-orange-100 transition-colors" data-filter="autonomous-robots">
        Autonomous Robots
      </button>
      <button onclick="filterCourses('directed-study')" class="filter-btn px-4 py-2 rounded-lg bg-gray-200 text-gray-700 font-medium hover:bg-gray-300 transition-colors" data-filter="directed-study">
        Directed Studies
      </button>
    </div>

    <!-- Course List -->
    <div id="courses-container">
      {course_cards_html}
    </div>
  </div>

  <!-- Footer -->
  <footer class="py-8 bg-gray-900 text-gray-400 mt-12">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="flex flex-col md:flex-row justify-between items-center">
        <p class="text-sm">
          &copy; 2026 Alberto Ferreira De Souza. All rights reserved.
        </p>
        <p class="text-sm mt-2 md:mt-0">
          Department of Informatics, UFES - Vitória, ES, Brazil
        </p>
      </div>
    </div>
  </footer>

  <script>
    function filterCourses(category) {{
      const cards = document.querySelectorAll('.course-card');
      const yearSections = document.querySelectorAll('.year-section');
      const buttons = document.querySelectorAll('.filter-btn');
      
      // Update button styles
      buttons.forEach(btn => {{
        btn.classList.remove('active', 'bg-ufes-blue', 'text-white');
        btn.classList.add('bg-gray-200', 'text-gray-700');
      }});
      
      const activeBtn = document.querySelector(`[data-filter="${{category}}"]`);
      if (activeBtn) {{
        activeBtn.classList.remove('bg-gray-200', 'text-gray-700');
        activeBtn.classList.add('active', 'bg-ufes-blue', 'text-white');
      }}
      
      // Filter cards
      cards.forEach(card => {{
        if (category === 'all' || card.dataset.category === category) {{
          card.style.display = 'block';
        }} else {{
          card.style.display = 'none';
        }}
      }});
      
      // Hide empty year sections
      yearSections.forEach(section => {{
        const visibleCards = section.querySelectorAll('.course-card[style="display: block"], .course-card:not([style])');
        let hasVisible = false;
        visibleCards.forEach(card => {{
          if (card.style.display !== 'none') hasVisible = true;
        }});
        
        const sectionCards = section.querySelectorAll('.course-card');
        let anyVisible = false;
        sectionCards.forEach(card => {{
          if (category === 'all' || card.dataset.category === category) {{
            anyVisible = true;
          }}
        }});
        
        section.style.display = anyVisible ? 'block' : 'none';
      }});
    }}
  </script>
</body>
</html>
'''
    
    return html


def main():
    """Main function to generate teaching.html."""
    print(f"Reading courses from: {CSV_FILE}")
    courses = read_teaching_csv(CSV_FILE)
    print(f"Found {len(courses)} courses")
    
    print(f"Generating HTML...")
    html = generate_html(courses)
    
    print(f"Writing to: {OUTPUT_FILE}")
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print("Done! teaching.html has been generated.")


if __name__ == '__main__':
    main()
