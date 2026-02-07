// Main JavaScript for Prof. Alberto's academic website

document.addEventListener('DOMContentLoaded', function() {
  // Initialize components
  initSmoothScroll();
  initNavHighlight();
  initMetricsAnimation();
  loadScholarMetrics();
});

/**
 * Smooth scroll for anchor links
 */
function initSmoothScroll() {
  document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function(e) {
      e.preventDefault();
      const target = document.querySelector(this.getAttribute('href'));
      if (target) {
        target.scrollIntoView({
          behavior: 'smooth',
          block: 'start'
        });
      }
    });
  });
}

/**
 * Highlight current section in navigation
 */
function initNavHighlight() {
  const sections = document.querySelectorAll('section[id]');
  const navLinks = document.querySelectorAll('.nav-link');

  if (sections.length === 0 || navLinks.length === 0) return;

  window.addEventListener('scroll', () => {
    let current = '';
    
    sections.forEach(section => {
      const sectionTop = section.offsetTop;
      const sectionHeight = section.clientHeight;
      if (scrollY >= sectionTop - 100) {
        current = section.getAttribute('id');
      }
    });

    navLinks.forEach(link => {
      link.classList.remove('active');
      if (link.getAttribute('href') === `#${current}`) {
        link.classList.add('active');
      }
    });
  });
}

/**
 * Animate metrics when they come into view
 */
function initMetricsAnimation() {
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        const element = entry.target;
        const finalValue = parseInt(element.dataset.value);
        animateCounter(element, finalValue);
        observer.unobserve(element);
      }
    });
  }, { threshold: 0.5 });

  document.querySelectorAll('.metric-value').forEach(el => {
    observer.observe(el);
  });
}

/**
 * Animate a counter from 0 to target value
 */
function animateCounter(element, target) {
  const duration = 2000;
  const steps = 60;
  const stepDuration = duration / steps;
  let current = 0;
  const increment = target / steps;

  const timer = setInterval(() => {
    current += increment;
    if (current >= target) {
      element.textContent = formatNumber(target);
      clearInterval(timer);
    } else {
      element.textContent = formatNumber(Math.floor(current));
    }
  }, stepDuration);
}

/**
 * Format number with thousands separator
 */
function formatNumber(num) {
  return num.toLocaleString('en-US');
}

/**
 * Load and display Google Scholar metrics from JSON
 */
async function loadScholarMetrics() {
  try {
    const response = await fetch('../data/scholar_metrics.json');
    if (!response.ok) {
      console.log('Scholar metrics file not found, using default values');
      return;
    }
    
    const data = await response.json();
    
    // Update metrics display
    updateMetricDisplay('citations-count', data.metrics.citations);
    updateMetricDisplay('h-index', data.metrics.h_index);
    updateMetricDisplay('i10-index', data.metrics.i10_index);
    
    // Update last updated date
    const lastUpdated = document.getElementById('last-updated');
    if (lastUpdated && data.last_updated) {
      const date = new Date(data.last_updated);
      lastUpdated.textContent = `Last updated: ${date.toLocaleDateString('en-US', { 
        year: 'numeric', 
        month: 'long', 
        day: 'numeric' 
      })}`;
    }
    
    // Update publications if container exists
    const pubContainer = document.getElementById('publications-list');
    if (pubContainer && data.top_publications) {
      updatePublications(pubContainer, data.top_publications);
    }
    
  } catch (error) {
    console.error('Error loading scholar metrics:', error);
  }
}

/**
 * Update a metric display element
 */
function updateMetricDisplay(id, value) {
  const element = document.getElementById(id);
  if (element) {
    element.dataset.value = value;
    element.textContent = formatNumber(value);
  }
}

/**
 * Update publications list
 */
function updatePublications(container, publications) {
  // Only update if we have dynamic content
  if (!container.dataset.dynamic) return;
  
  container.innerHTML = publications.map((pub, index) => `
    <div class="publication-item p-4 rounded-lg border border-gray-200 animate-fade-in-up stagger-${index + 1}" style="opacity: 0;">
      <h4 class="font-semibold text-gray-900 mb-2">
        <a href="${pub.url}" target="_blank" rel="noopener" class="hover:text-blue-600 transition-colors">
          ${pub.title}
        </a>
      </h4>
      <p class="text-sm text-gray-600 mb-1">${pub.authors}</p>
      <p class="text-sm text-gray-500">${pub.venue}, ${pub.year}</p>
      <p class="text-sm font-medium text-blue-600 mt-2">
        <svg class="inline-block w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6"></path>
        </svg>
        ${pub.citations.toLocaleString()} citations
      </p>
    </div>
  `).join('');
}

/**
 * Toggle mobile menu
 */
function toggleMobileMenu() {
  const menu = document.getElementById('mobile-menu');
  if (menu) {
    menu.classList.toggle('hidden');
  }
}

// Expose toggle function globally
window.toggleMobileMenu = toggleMobileMenu;
