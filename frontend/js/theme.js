// 主题管理
export const theme = {
    // 初始化主题
    init() {
        const themeToggle = document.getElementById('themeToggle');
        const icon = themeToggle.querySelector('i');
        
        // 检查系统主题
        if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
            this.setTheme('dark');
            icon.classList.replace('fa-moon', 'fa-sun');
        }
        
        // 主题切换事件
        themeToggle.addEventListener('click', () => {
            const currentTheme = document.documentElement.getAttribute('data-theme');
            const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
            
            this.setTheme(newTheme);
            icon.classList.toggle('fa-moon');
            icon.classList.toggle('fa-sun');
        });
        
        // 监听系统主题变化
        window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', e => {
            const newTheme = e.matches ? 'dark' : 'light';
            this.setTheme(newTheme);
            icon.classList.toggle('fa-moon', !e.matches);
            icon.classList.toggle('fa-sun', e.matches);
        });
    },

    // 设置主题
    setTheme(theme) {
        document.documentElement.setAttribute('data-theme', theme);
        localStorage.setItem('theme', theme);
    },

    // 获取当前主题
    getTheme() {
        return document.documentElement.getAttribute('data-theme') || 'light';
    }
};
