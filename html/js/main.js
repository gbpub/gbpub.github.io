// GB 插件市场 - 主脚本文件

// 复制到剪贴板功能
window.copyToClipboard = function(elementId) {
    const element = document.getElementById(elementId);
    if (!element) {
        console.error('元素不存在:', elementId);
        return;
    }
    
    const text = element.textContent;
    navigator.clipboard.writeText(text).then(() => {
        // 显示复制成功消息
        const pluginId = elementId.replace('command-', '');
        const messageElement = document.getElementById(`copy-message-${pluginId}`);
        if (messageElement) {
            messageElement.classList.add('show');
            setTimeout(() => {
                messageElement.classList.remove('show');
            }, 2000);
        }
    }).catch(err => {
        console.error('复制失败:', err);
    });
};

// 页面加载完成后执行
window.addEventListener('DOMContentLoaded', async () => {
    // 确保插件加载器已加载
    if (!window.pluginLoader) {
        console.error('插件加载器未加载，请检查pluginsLoader.js是否正确引入');
    }
    
    initSearch();
    initCategoryButtons();
    await loadFeaturedPlugins();
    await loadLatestPlugins();
    initSmoothScroll();
});

// 初始化搜索功能
function initSearch() {
    const searchInput = document.getElementById('search-input');
    const searchButton = document.getElementById('search-button');
    
    searchButton.addEventListener('click', () => {
        const query = searchInput.value.trim();
        if (query) {
            searchPlugins(query);
        }
    });
    
    searchInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            const query = searchInput.value.trim();
            if (query) {
                searchPlugins(query);
            }
        }
    });
}

// 初始化分类按钮
function initCategoryButtons() {
    const categoryButtons = document.querySelectorAll('.category-btn');
    
    categoryButtons.forEach(button => {
        button.addEventListener('click', () => {
            // 移除所有按钮的active类
            categoryButtons.forEach(btn => btn.classList.remove('active'));
            // 添加当前按钮的active类
            button.classList.add('active');
            
            const category = button.getAttribute('data-category');
            loadPluginsByCategory(category);
        });
    });
}

// 加载精选插件
async function loadFeaturedPlugins() {
    const container = document.getElementById('featured-plugins');
    container.innerHTML = '<div class="loading">加载中...</div>';
    
    try {
        // 使用新的插件加载器API
        const response = await window.getFeaturedPlugins();
        if (response.success) {
            const featuredPlugins = response.data;
            container.innerHTML = '';
            
            featuredPlugins.forEach(plugin => {
                container.appendChild(createPluginCard(plugin));
            });
        } else {
            console.error('加载精选插件失败:', response.message);
            container.innerHTML = '<div class="error">加载失败，请稍后重试</div>';
        }
    } catch (error) {
        console.error('加载精选插件时出错:', error);
        container.innerHTML = '<div class="error">加载失败，请稍后重试</div>';
    }
}

// 加载最新插件
async function loadLatestPlugins() {
    const container = document.getElementById('latest-plugins');
    container.innerHTML = '<div class="loading">加载中...</div>';
    
    try {
        // 使用新的插件加载器API
        const response = await window.getLatestPlugins();
        if (response.success) {
            const latestPlugins = response.data;
            container.innerHTML = '';
            
            latestPlugins.forEach(plugin => {
                container.appendChild(createPluginCard(plugin));
            });
        } else {
            console.error('加载最新插件失败:', response.message);
            container.innerHTML = '<div class="error">加载失败，请稍后重试</div>';
        }
    } catch (error) {
        console.error('加载最新插件时出错:', error);
        container.innerHTML = '<div class="error">加载失败，请稍后重试</div>';
    }
}

// 按分类加载插件
async function loadPluginsByCategory(category) {
    const container = document.getElementById('category-plugins');
    container.innerHTML = '<div class="loading">加载中...</div>';
    
    try {
        // 使用新的插件加载器API
        const response = await window.getPluginsByCategory(category);
        if (response.success) {
            const plugins = response.data;
            container.innerHTML = '';
            
            if (plugins.length === 0) {
                container.innerHTML = '<div class="no-results">该分类暂无插件</div>';
            } else {
                plugins.forEach(plugin => {
                    container.appendChild(createPluginCard(plugin));
                });
            }
        } else {
            console.error('加载分类插件失败:', response.message);
            container.innerHTML = '<div class="error">加载失败，请稍后重试</div>';
        }
    } catch (error) {
        console.error('加载分类插件时出错:', error);
        container.innerHTML = '<div class="error">加载失败，请稍后重试</div>';
    }
}

// 搜索插件
async function searchPlugins(query) {
    // 使用新的插件加载器API
    try {
        const container = document.getElementById('category-plugins');
        container.innerHTML = '<div class="loading">搜索中...</div>';
        
        const response = await window.searchPlugins(query);
        if (response.success) {
            const results = response.data;
            
            container.innerHTML = '';
            if (results.length > 0) {
                results.forEach(plugin => {
                    container.appendChild(createPluginCard(plugin));
                });
            } else {
                container.innerHTML = '<div class="no-results">没有找到匹配的插件</div>';
            }
        } else {
            alert('搜索失败: ' + (response.message || '未知错误'));
            container.innerHTML = '<div class="no-results">搜索失败，请稍后重试</div>';
        }
    } catch (error) {
        console.error('搜索插件时出错:', error);
        alert('搜索失败，请稍后再试');
    }
}

// 创建插件卡片
function createPluginCard(plugin) {
    const card = document.createElement('div');
    card.className = 'plugin-card';
    
    card.innerHTML = `
        <img src="${plugin.image}" alt="${plugin.name}">
        <div class="plugin-content">
            <h4 class="plugin-title">${plugin.name}</h4>
            <p class="plugin-description">${plugin.description}</p>
            <div class="plugin-meta">
                <span>${plugin.author}</span>
                <span>v${plugin.version}</span>
                <span>${plugin.downloads} 下载</span>
            </div>
            <button class="install-btn" data-plugin="${plugin.name}">安装插件</button>
        </div>
    `;
    
    // 添加安装按钮事件
    const installBtn = card.querySelector('.install-btn');
    installBtn.addEventListener('click', (e) => {
        const pluginName = e.target.getAttribute('data-plugin');
        installPlugin(pluginName);
    });
    
    // 添加可复制的安装命令代码框
    const infoContainer = card.querySelector('.plugin-content');
    infoContainer.appendChild(createInstallCommandCodeBlock(plugin.name));
    
    return card;
}

// 安装插件
async function installPlugin(pluginName) {
    try {
        // 使用新的插件加载器API
        const response = await window.installPlugin(pluginName);
        if (response.success) {
            alert(`插件 "${pluginName}" 安装成功！`);
        } else {
            alert(`插件 "${pluginName}" 安装失败: ${response.message || '未知错误'}`);
        }
    } catch (error) {
        console.error('安装插件时出错:', error);
        alert(`插件 "${pluginName}" 安装失败，请稍后再试`);
    }
}

// 初始化平滑滚动
function initSmoothScroll() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            
            const targetId = this.getAttribute('href');
            const targetElement = document.querySelector(targetId);
            
            if (targetElement) {
                window.scrollTo({
                    top: targetElement.offsetTop - 80,
                    behavior: 'smooth'
                });
            }
        });
    });
}

// 错误处理函数
function handleError(error, message = '操作失败') {
    console.error('错误:', error);
    alert(`${message}: ${error.message || '未知错误'}`);
}

// 创建可复制的安装命令代码框
function createInstallCommandCodeBlock(pluginName) {
    const codeContainer = document.createElement('div');
    codeContainer.className = 'mt-3 bg-gray-100 rounded-md p-3 relative';
    
    const commandText = `gb install ${pluginName}`;
    const codeBlock = document.createElement('code');
    codeBlock.className = 'text-sm text-gray-800 font-mono';
    codeBlock.textContent = commandText;
    
    const copyBtn = document.createElement('button');
    copyBtn.className = 'absolute top-2 right-2 bg-blue-500 text-white px-2 py-1 rounded text-xs hover:bg-blue-600 transition-colors';
    copyBtn.textContent = '复制';
    copyBtn.setAttribute('aria-label', '复制安装命令');
    
    copyBtn.addEventListener('click', () => {
        navigator.clipboard.writeText(commandText).then(() => {
            // 显示复制成功提示
            copyBtn.textContent = '已复制!';
            copyBtn.classList.remove('bg-blue-500');
            copyBtn.classList.add('bg-green-500');
            setTimeout(() => {
                copyBtn.textContent = '复制';
                copyBtn.classList.remove('bg-green-500');
                copyBtn.classList.add('bg-blue-500');
            }, 2000);
        }).catch(err => {
            console.error('复制失败:', err);
            // 降级方案：选择文本
            const range = document.createRange();
            range.selectNode(codeBlock);
            window.getSelection().removeAllRanges();
            window.getSelection().addRange(range);
        });
    });
    
    codeContainer.appendChild(codeBlock);
    codeContainer.appendChild(copyBtn);
    return codeContainer;
}