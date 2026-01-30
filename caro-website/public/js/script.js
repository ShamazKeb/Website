
const primaryNavbar = document.querySelector('.primary-navbar');
const secondaryNavbar = document.getElementById('secondaryNavbar');
const mobileMenuIcon = document.querySelector('.mobile-menu-icon');
const navLinks = document.querySelector('.nav-links');

// Handle scroll effect for desktop
window.addEventListener('scroll', function () {
  if (window.innerWidth > 768) { // Only apply scroll effect on desktop
    if (window.scrollY > 70) {
      if (primaryNavbar) primaryNavbar.classList.add('hidden');
      if (secondaryNavbar) secondaryNavbar.classList.add('visible');
    } else {
      if (primaryNavbar) primaryNavbar.classList.remove('hidden');
      if (secondaryNavbar) secondaryNavbar.classList.remove('visible');
    }
  }
});

// Handle mobile menu toggle
if (mobileMenuIcon) {
  mobileMenuIcon.addEventListener('click', () => {
    if (navLinks) navLinks.classList.toggle('active');
  });
}
