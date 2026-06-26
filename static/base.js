const navbar = document.getElementById('main-navbar');
const navbarCollapse = document.getElementById('navbarSupportedContent');
const scrollThreshold = 50;

function changeNavBackground() {
    
    if (window.scrollY > scrollThreshold || navbarCollapse.classList.contains('show')) {
        navbar.classList.add('scrolled');
    } else {
        navbar.classList.remove('scrolled');
    }
}

// Listen for Scroll
window.addEventListener('scroll', changeNavBackground);

// Listen for Bootstrap Menu Toggling (Mobile)
navbarCollapse.addEventListener('shown.bs.collapse', changeNavBackground);
navbarCollapse.addEventListener('hidden.bs.collapse', changeNavBackground);





document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll('.toast').forEach(toastEl => {
    const t = new bootstrap.Toast(toastEl, { delay: 3500 });
    t.show();
  });
});


document.addEventListener("DOMContentLoaded", () => {
  const banner = document.getElementById("offlineBanner");
  if (!banner) return;

  
  const showBanner = () => {
    banner.style.display = "block";
    setTimeout(() => banner.style.transform = "translateY(0%)", 10);

    // Disable all form submit buttons
    document.querySelectorAll("form button[type='submit']").forEach(btn => btn.disabled = true);
  };

  // Hide the banner
  const hideBanner = () => {
    banner.style.transform = "translateY(-100%)";
    setTimeout(() => banner.style.display = "none", 300);

    // Enable all form submit buttons
    document.querySelectorAll("form button[type='submit']").forEach(btn => btn.disabled = false);
  };

  // Initial check
  if (!navigator.onLine) showBanner();

  // Listen to offline/online events
  window.addEventListener("offline", showBanner);
  window.addEventListener("online", hideBanner);
});


const toggleBtn = document.getElementById("themeToggle");

if (localStorage.getItem("theme") === "dark") {
  toggleBtn.textContent = "☀️ Light Mode";
}

toggleBtn.addEventListener("click", () => {
  const current = document.documentElement.getAttribute("data-theme");

  if (current === "dark") {
    document.documentElement.setAttribute("data-theme", "light");
    localStorage.setItem("theme", "light");
    toggleBtn.textContent = "🌙 Dark Mode";
  } else {
    document.documentElement.setAttribute("data-theme", "dark");
    localStorage.setItem("theme", "dark");
    toggleBtn.textContent = "☀️ Light Mode";
  }
});







