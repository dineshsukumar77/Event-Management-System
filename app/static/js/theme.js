(function() {
  const STORAGE_KEY = 'ems-theme';
  function apply(theme) {
    const root = document.documentElement;
    if (theme === 'dark') {
      root.classList.add('theme-dark');
    } else {
      root.classList.remove('theme-dark');
    }
  }
  function getSystemPref() {
    return window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
  }
  function getInitial() {
    return localStorage.getItem(STORAGE_KEY) || getSystemPref();
  }
  window.__emsTheme = {
    toggle: function() {
      const current = document.documentElement.classList.contains('theme-dark') ? 'dark' : 'light';
      const next = current === 'dark' ? 'light' : 'dark';
      localStorage.setItem(STORAGE_KEY, next);
      apply(next);
    }
  };
  apply(getInitial());
})();

