export const theme = {
    // 初始化主题
    init() {
        const themeToggle = document.getElementById('themeToggle');
        const icon = themeToggle.querySelector('i');
        
        // 检查系统主题
        if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
            this.setTheme('dark');
            icon.textContent = '🌙';
        }
        
        let clickCount = 2;
        // 主题切换事件
        themeToggle.addEventListener('click', () => {
            clickCount++;
            console.log('Step 1: Theme change initiated');
            const currentTheme = document.documentElement.getAttribute('data-theme');
            let newTheme;
            
            if (clickCount % 2 === 1) {
                newTheme = 'dark';
                icon.textContent = '🌙'; 
            } else {
                newTheme = 'light';
                icon.textContent = '☀️'; 
            }
            
            console.log(`Step 1.5: Changing theme from ${currentTheme} to ${newTheme}`);
            this.setTheme(newTheme);
            console.log('Step 2: Theme change completed');
            console.log('Step 3: Toggling theme icons');
            
            // 添加动画效果
            document.documentElement.style.transition = 'background-color 0.5s ease';
            
            // 显示提示信息
            this.showToast(`已切换至${newTheme === 'dark' ? '深色' : '浅色'}主题`);
        });
        
        // 监听系统主题变化
        window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', e => {
            const newTheme = e.matches ? 'dark' : 'light';
            this.setTheme(newTheme);
            icon.textContent = e.matches ? '🌙' : '☀️';
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
    },

    // 显示提示信息
    showToast(message) {
        const toast = document.createElement('div');
        toast.textContent = message;
        toast.style.position = 'fixed';
        toast.style.bottom = '20px';
        toast.style.left = '50%';
        toast.style.transform = 'translateX(-50%)';
        toast.style.backgroundColor = 'rgba(0, 0, 0, 0.7)';
        toast.style.color = '#fff';
        toast.style.padding = '10px 20px';
        toast.style.borderRadius = '5px';
        toast.style.zIndex = '1000';
        toast.style.transition = 'opacity 0.5s ease';
        document.body.appendChild(toast);
        
        // 1.5秒后淡出
        setTimeout(() => {
            toast.style.opacity = '0';
            setTimeout(() => {
                document.body.removeChild(toast);
            }, 500);
        }, 1500);
    }
};