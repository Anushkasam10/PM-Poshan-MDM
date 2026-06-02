document.addEventListener('DOMContentLoaded', () => {
    // Theme Management
    const getSavedTheme = () => localStorage.getItem('mdm-theme') || 'light';
    
    const applyTheme = (theme) => {
        document.documentElement.setAttribute('data-theme', theme);
        localStorage.setItem('mdm-theme', theme);
        
        const themeToggleBtns = document.querySelectorAll('.btn-theme-toggle');
        themeToggleBtns.forEach(btn => {
            const icon = btn.querySelector('i');
            if (icon) {
                if (theme === 'dark') {
                    icon.className = 'fas fa-sun';
                } else {
                    icon.className = 'fas fa-moon';
                }
            }
        });
        
        // Dispatch event so charts can re-render
        window.dispatchEvent(new CustomEvent('themechanged', { detail: { theme } }));
    };

    // Initialize theme
    applyTheme(getSavedTheme());

    // Theme Toggle Click Listener
    document.addEventListener('click', (e) => {
        const btn = e.target.closest('.btn-theme-toggle');
        if (btn) {
            const currentTheme = document.documentElement.getAttribute('data-theme');
            const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
            applyTheme(newTheme);
        }
    });

    // Tab Swapping Controller
    const tabs = document.querySelectorAll('.nav-tab');
    const panels = document.querySelectorAll('.tab-panel');

    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            const targetPanelId = tab.getAttribute('data-target');

            // Set active tab
            tabs.forEach(t => t.classList.remove('active'));
            tab.classList.add('active');

            // Set active panel
            panels.forEach(panel => {
                if (panel.id === targetPanelId) {
                    panel.classList.add('active');
                } else {
                    panel.classList.remove('active');
                }
            });

            // Trigger window resize so ApexCharts updates its dimensions inside the newly shown tab
            window.dispatchEvent(new Event('resize'));
        });
    });
});
