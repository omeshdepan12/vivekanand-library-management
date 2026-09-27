document.addEventListener('DOMContentLoaded', () => {
  const forms = document.querySelectorAll('form');

  forms.forEach((form) => {
    form.addEventListener('submit', () => {
      const submitBtn = form.querySelector('button[type="submit"]');
      if (submitBtn) {
        submitBtn.textContent = 'Processing...';
        submitBtn.disabled = true;
      }
    });
  });
});

const links = document.querySelectorAll('nav a');
links.forEach((link) => {
  if (link.textContent.trim() === 'Logout') {
    link.style.opacity = '0.9';
  }
});
