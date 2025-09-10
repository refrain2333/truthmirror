// 真相之镜 - 通用导航栏组件

// 导航栏配置
const NAV_CONFIG = {
    logo: '真相之镜',
    links: [
        { text: '首页', href: './index.html', id: 'nav-home' },
        { text: '提交事件', href: './submit-event.html', id: 'nav-submit' },
        { text: '关于', href: './about.html', id: 'nav-about' }
    ]
};

// 创建导航栏HTML
function createNavHTML(currentPage = '') {
    const currentUser = getCurrentUser();
    
    const linksHTML = NAV_CONFIG.links.map(link => {
        const activeClass = (currentPage && link.href.includes(currentPage)) ? 'active' : '';
        return `<a href="${link.href}" class="${activeClass}" id="${link.id}">${link.text}</a>`;
    }).join('');
    
    const authHTML = currentUser
        ? `<div class="user-info">
            <span class="user-name">欢迎，${currentUser.username || currentUser.nickname || '用户'}</span>
            <a href="./profile.html" class="btn">我的</a>
            <a href="#" class="btn" onclick="logout()">退出登录</a>
           </div>`
        : `<div class="auth-buttons">
            <a href="./auth.html" class="btn">登录</a>
            <a href="./auth.html?mode=register" class="btn btn-primary">注册</a>
           </div>`;
    
    return `
        <header id="main-header">
            <div class="container">
                <div class="header-content">
                    <div class="logo">
                        <h1 onclick="window.location.href='./index.html'">${NAV_CONFIG.logo}</h1>
                    </div>
                    <nav class="nav-links">
                        ${linksHTML}
                    </nav>
                    ${authHTML}
                </div>
            </div>
        </header>
    `;
}

// 创建导航栏CSS
function createNavCSS() {
    return `
        /* 通用导航栏样式 */
        #main-header {
            background: white;
            border-bottom: 1px solid #ddd;
            padding: 10px 0;
            position: sticky;
            top: 0;
            z-index: 1000;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }

        #main-header .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 20px;
        }

        #main-header .header-content {
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-wrap: wrap;
            gap: 20px;
        }

        #main-header .logo h1 {
            font-size: 24px;
            color: #2c5aa0;
            cursor: pointer;
            margin: 0;
        }

        #main-header .nav-links {
            display: flex;
            gap: 30px;
            align-items: center;
        }

        #main-header .nav-links a {
            text-decoration: none;
            color: #666;
            font-weight: 500;
            padding: 8px 0;
            border-bottom: 2px solid transparent;
            transition: all 0.2s;
        }

        #main-header .nav-links a:hover,
        #main-header .nav-links a.active {
            color: #2c5aa0;
            border-bottom-color: #2c5aa0;
        }

        #main-header .auth-buttons {
            display: flex;
            gap: 10px;
            align-items: center;
        }

        #main-header .user-info {
            display: flex;
            align-items: center;
            gap: 15px;
        }

        #main-header .user-name {
            color: #333;
            font-weight: 500;
            font-size: 14px;
        }

        #main-header .btn {
            padding: 8px 16px;
            border: 1px solid #ddd;
            background: white;
            color: #666;
            text-decoration: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 14px;
            display: inline-block;
            transition: all 0.2s;
        }

        #main-header .btn:hover {
            background: #f8f9fa;
        }

        #main-header .btn-primary {
            background: #2c5aa0;
            color: white;
            border-color: #2c5aa0;
        }

        #main-header .btn-primary:hover {
            background: #1e3d72;
        }

        /* 响应式设计 */
        @media (max-width: 768px) {
            #main-header .header-content {
                flex-direction: column;
                gap: 15px;
                text-align: center;
            }
            
            #main-header .nav-links {
                gap: 20px;
            }
            
            #main-header .logo h1 {
                font-size: 20px;
            }
        }

        @media (max-width: 480px) {
            #main-header .nav-links {
                gap: 15px;
                flex-wrap: wrap;
                justify-content: center;
            }
            
            #main-header .nav-links a {
                font-size: 14px;
            }
        }
    `;
}

// 初始化导航栏
function initNavigation(currentPage = '') {
    // 插入CSS
    const existingStyle = document.getElementById('nav-styles');
    if (!existingStyle) {
        const style = document.createElement('style');
        style.id = 'nav-styles';
        style.textContent = createNavCSS();
        document.head.appendChild(style);
    }
    
    // 插入HTML
    const navHTML = createNavHTML(currentPage);
    
    // 查找插入位置
    const existingHeader = document.getElementById('main-header');
    if (existingHeader) {
        existingHeader.outerHTML = navHTML;
    } else {
        // 在body开头插入
        document.body.insertAdjacentHTML('afterbegin', navHTML);
    }
    
    // 更新页面内容的上边距
    updatePageMargin();
}

// 更新页面边距以适应固定导航栏
function updatePageMargin() {
    const header = document.getElementById('main-header');
    if (header) {
        const headerHeight = header.offsetHeight;
        document.body.style.paddingTop = '0px'; // 重置
        
        // 为页面主内容添加上边距
        const main = document.querySelector('main');
        if (main && !main.style.marginTop) {
            main.style.marginTop = '0px';
        }
    }
}

// 获取当前用户信息
function getCurrentUser() {
    try {
        const userStr = localStorage.getItem('currentUser');
        return userStr ? JSON.parse(userStr) : null;
    } catch (error) {
        console.error('解析用户信息失败:', error);
        return null;
    }
}

// 退出登录
function logout() {
    if (confirm('确定要退出登录吗？')) {
        localStorage.removeItem('currentUser');
        window.location.href = './index.html';
    }
}

// 更新导航栏用户状态
function updateNavUserStatus() {
    const currentUser = getCurrentUser();
    const authContainer = document.querySelector('#main-header .auth-buttons, #main-header .user-info');
    
    if (authContainer) {
        if (currentUser) {
            authContainer.className = 'user-info';
            authContainer.innerHTML = `
                <span class="user-name">欢迎，${currentUser.username || currentUser.nickname || '用户'}</span>
                <a href="./profile.html" class="btn">我的</a>
                <a href="#" class="btn" onclick="logout()">退出登录</a>
            `;
        } else {
            authContainer.className = 'auth-buttons';
            authContainer.innerHTML = `
                <a href="./auth.html" class="btn">登录</a>
                <a href="./auth.html?mode=register" class="btn btn-primary">注册</a>
            `;
        }
    }
}

// 高亮当前页面导航项
function highlightCurrentNav(currentPage) {
    // 移除所有active类
    document.querySelectorAll('#main-header .nav-links a').forEach(link => {
        link.classList.remove('active');
    });
    
    // 添加当前页面的active类
    if (currentPage) {
        const currentLink = document.querySelector(`#main-header .nav-links a[href*="${currentPage}"]`);
        if (currentLink) {
            currentLink.classList.add('active');
        }
    }
}

// 页面加载完成后自动初始化导航栏
document.addEventListener('DOMContentLoaded', function() {
    // 从URL获取当前页面
    const currentPage = window.location.pathname.split('/').pop() || 'index.html';

    // 检查是否是登录注册页面，如果是则不显示导航栏
    const noNavPages = ['auth.html'];
    const shouldShowNav = !noNavPages.includes(currentPage);

    if (shouldShowNav) {
        initNavigation(currentPage);

        // 监听用户登录状态变化
        window.addEventListener('storage', function(e) {
            if (e.key === 'currentUser') {
                updateNavUserStatus();
            }
        });

        // 监听窗口大小变化，调整导航栏
        window.addEventListener('resize', function() {
            updatePageMargin();
        });
    }
});

// 导出函数供其他脚本使用
window.NavigationBar = {
    init: initNavigation,
    update: updateNavUserStatus,
    highlight: highlightCurrentNav,
    getCurrentUser: getCurrentUser,
    logout: logout
};