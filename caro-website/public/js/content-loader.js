// Content Loader for Dynamic Website Content
// This file loads content from Supabase and updates the website

// Supabase configuration
const SUPABASE_URL = 'https://hfopvhwxysvqgprhigue.supabase.co';
const SUPABASE_ANON_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imhmb3B2aHd4eXN2cWdwcmhpZ3VlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTEzMTg5MTAsImV4cCI6MjA2Njg5NDkxMH0.vq7tOO2u9rVHYCeHudnZMjApi5maCyj7kUp_2MAmHIs';

const supabaseClient = supabase.createClient(SUPABASE_URL, SUPABASE_ANON_KEY);

// Content mapping for different elements
const contentMapping = {
  'hero_title': {
    selector: '.container h1',
    attribute: 'textContent',
    fallback: 'Guiding into higher Frequencies'
  },
  'hero_subtitle': {
    selector: '.container h2',
    attribute: 'textContent',
    fallback: '& Cranio-Sacrale Balance'
  },
  'about_text': {
    selector: '.textblock:first-of-type p',
    attribute: 'innerHTML',
    fallback: 'Ich möchte gar nicht viel über mich sprechen...'
  },
  'cranio_text': {
    selector: '.textblock:last-of-type p',
    attribute: 'innerHTML',
    fallback: 'Cranio ist eine sanfte Methode...'
  }
};

// Load and apply content
async function loadAndApplyContent() {
  try {
    console.log('Loading content from Supabase...');
    
    const { data: content, error } = await supabaseClient
      .from('website_content')
      .select('*');
    
    if (error) {
      console.error('Error loading content:', error);
      return;
    }
    
    console.log('Content loaded:', content);
    
    // Apply content to elements
    content.forEach(item => {
      const mapping = contentMapping[item.content_key];
      if (mapping) {
        const element = document.querySelector(mapping.selector);
        console.log(`Looking for element with selector: ${mapping.selector}`);
        console.log(`Found element:`, element);
        
        if (element) {
          if (mapping.attribute === 'textContent') {
            console.log(`Updating ${item.content_key} to:`, item.content_value);
            element.textContent = item.content_value;
          } else if (mapping.attribute === 'innerHTML') {
            console.log(`Updating ${item.content_key} to:`, item.content_value);
            element.innerHTML = item.content_value;
          }
        } else {
          console.warn(`Element not found for ${item.content_key} with selector: ${mapping.selector}`);
        }
      }
    });
    
    console.log('Content application completed');
    
  } catch (error) {
    console.error('Error in loadAndApplyContent:', error);
  }
}

// Load content when page loads
document.addEventListener('DOMContentLoaded', loadAndApplyContent);

// Export for use in other scripts
window.contentLoader = {
  loadAndApplyContent,
  supabaseClient
}; 