// Supabase Configuration
// Replace these values with your actual Supabase project credentials

const SUPABASE_CONFIG = {
  url: 'https://hfopvhwxysvqgprhigue.supabase.co',
  anonKey: 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imhmb3B2aHd4eXN2cWdwcmhpZ3VlIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTEzMTg5MTAsImV4cCI6MjA2Njg5NDkxMH0.vq7tOO2u9rVHYCeHudnZMjApi5maCyj7kUp_2MAmHIs'
};

// Initialize Supabase client
const supabase = supabase.createClient(SUPABASE_CONFIG.url, SUPABASE_CONFIG.anonKey); 