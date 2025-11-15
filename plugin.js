// GB 插件市场 - 插件管理模块

// 插件管理类
class PluginManager {
    constructor() {
        this.plugins = [];
        this.pluginDirectory = '/Plugin';
    }
    
    // 初始化插件管理器
    async initialize() {
        try {
            // 加载插件列表
            const response = await PluginAPI.getPluginList();
            if (response.success) {
                this.plugins = response.data;
                return true;
            }
            return false;
        } catch (error) {
            console.error('初始化插件管理器失败:', error);
            return false;
        }
    }
    
    // 搜索插件
    async search(query, filters = {}) {
        try {
            const results = await PluginAPI.searchPlugins(query, filters);
            return results.data || [];
        } catch (error) {
            console.error('搜索插件失败:', error);
            return [];
        }
    }
    
    // 安装插件
    async install(pluginName) {
        try {
            // 显示安装中提示
            this.showInstallationStatus(pluginName, 'installing');
            
            // 调用API下载插件
            const response = await PluginAPI.downloadPlugin(pluginName);
            
            if (response.success) {
                // 模拟安装过程
                await this.simulateInstallation(pluginName);
                
                // 显示安装成功提示
                this.showInstallationStatus(pluginName, 'success');
                return {
                    success: true,
                    message: `插件 ${pluginName} 安装成功`
                };
            } else {
                throw new Error(response.message || '下载失败');
            }
        } catch (error) {
            console.error(`安装插件 ${pluginName} 失败:`, error);
            this.showInstallationStatus(pluginName, 'error', error.message);
            return {
                success: false,
                message: error.message || '安装失败'
            };
        }
    }
    
    // 模拟安装过程
    simulateInstallation(pluginName) {
        return new Promise(resolve => {
            setTimeout(() => {
                console.log(`模拟安装插件 ${pluginName}`);
                resolve();
            }, 1500);
        });
    }
    
    // 显示安装状态
    showInstallationStatus(pluginName, status, message = '') {
        // 在实际应用中，这里会显示一个模态框或通知
        console.log(`[${status.toUpperCase()}] 插件 ${pluginName}:`, message);
        
        // 创建临时通知元素
        const notification = document.createElement('div');
        notification.className = `plugin-notification notification-${status}`;
        
        let statusText = '';
        let statusColor = '#007aff';
        
        switch (status) {
            case 'installing':
                statusText = '安装中...';
                statusColor = '#007aff';
                break;
            case 'success':
                statusText = '安装成功';
                statusColor = '#34c759';
                break;
            case 'error':
                statusText = '安装失败';
                statusColor = '#ff3b30';
                break;
        }
        
        notification.innerHTML = `
            <div class="notification-content">
                <span class="notification-status" style="color: ${statusColor}">${statusText}</span>
                <span class="notification-plugin">${pluginName}</span>
                ${message ? `<span class="notification-message">${message}</span>` : ''}
            </div>
        `;
        
        // 设置通知样式
        Object.assign(notification.style, {
            position: 'fixed',
            bottom: '20px',
            right: '20px',
            backgroundColor: 'white',
            padding: '15px 20px',
            borderRadius: '8px',
            boxShadow: '0 4px 15px rgba(0, 0, 0, 0.1)',
            zIndex: '9999',
            minWidth: '250px',
            maxWidth: '400px',
            animation: 'slideInRight 0.3s ease-out'
        });
        
        // 添加通知样式到页面
        const style = document.createElement('style');
        style.textContent = `
            @keyframes slideInRight {
                from { transform: translateX(100%); opacity: 0; }
                to { transform: translateX(0); opacity: 1; }
            }
            .notification-content {
                display: flex;
                flex-direction: column;
                gap: 5px;
            }
            .notification-status {
                font-weight: 600;
                font-size: 16px;
            }
            .notification-plugin {
                color: #666;
                font-size: 14px;
            }
            .notification-message {
                color: #888;
                font-size: 13px;
                margin-top: 5px;
            }
        `;
        document.head.appendChild(style);
        
        // 添加通知到页面
        document.body.appendChild(notification);
        
        // 自动关闭通知
        setTimeout(() => {
            notification.style.animation = 'slideOutRight 0.3s ease-in';
            setTimeout(() => {
                notification.remove();
            }, 300);
        }, status === 'error' ? 5000 : 3000);
    }
    
    // 获取插件详情
    async getDetails(pluginName) {
        try {
            const response = await PluginAPI.getPluginDetails(pluginName);
            return response.data || null;
        } catch (error) {
            console.error(`获取插件 ${pluginName} 详情失败:`, error);
            return null;
        }
    }
    
    // 获取推荐插件
    async getRecommended() {
        try {
            // 这里可以根据用户历史或热门程度推荐插件
            const response = await StatsAPI.getPopularPlugins();
            return response.data || [];
        } catch (error) {
            console.error('获取推荐插件失败:', error);
            return [];
        }
    }
    
    // 生成安装命令
    getInstallCommand(pluginName) {
        return `gb install ${pluginName}`;
    }
    
    // 复制安装命令到剪贴板
    async copyInstallCommand(pluginName) {
        const command = this.getInstallCommand(pluginName);
        try {
            await navigator.clipboard.writeText(command);
            return true;
        } catch (error) {
            console.error('复制命令失败:', error);
            // 降级方案
            try {
                const textArea = document.createElement('textarea');
                textArea.value = command;
                document.body.appendChild(textArea);
                textArea.select();
                document.execCommand('copy');
                document.body.removeChild(textArea);
                return true;
            } catch (fallbackError) {
                console.error('降级复制方案也失败:', fallbackError);
                return false;
            }
        }
    }
    
    // 验证插件名称
    validatePluginName(name) {
        // 插件名称应该只包含字母、数字、下划线和连字符
        const regex = /^[a-zA-Z0-9_-]+$/;
        return regex.test(name) && name.length > 0 && name.length <= 50;
    }
    
    // 格式化下载数量
    formatDownloads(count) {
        if (typeof count === 'string') {
            return count;
        }
        
        if (count >= 1000000) {
            return (count / 1000000).toFixed(1) + 'M';
        } else if (count >= 1000) {
            return (count / 1000).toFixed(1) + 'K';
        }
        return count.toString();
    }
    
    // 排序插件
    sortPlugins(plugins, sortBy = 'latest', order = 'desc') {
        const sorted = [...plugins].sort((a, b) => {
            let aValue, bValue;
            
            switch (sortBy) {
                case 'name':
                    aValue = a.name.toLowerCase();
                    bValue = b.name.toLowerCase();
                    break;
                case 'downloads':
                    aValue = parseInt(a.downloads.replace(/[^0-9]/g, ''));
                    bValue = parseInt(b.downloads.replace(/[^0-9]/g, ''));
                    break;
                case 'version':
                    aValue = a.version;
                    bValue = b.version;
                    break;
                case 'latest':
                default:
                    // 如果没有时间字段，按ID排序
                    aValue = a.id || 0;
                    bValue = b.id || 0;
                    break;
            }
            
            if (aValue < bValue) return order === 'asc' ? -1 : 1;
            if (aValue > bValue) return order === 'asc' ? 1 : -1;
            return 0;
        });
        
        return sorted;
    }
}

// 创建全局插件管理器实例
const pluginManager = new PluginManager();

// 初始化插件管理器
pluginManager.initialize().then(success => {
    console.log('插件管理器初始化:', success ? '成功' : '失败');
});

// 注册全局函数，方便在HTML中调用
window.installPluginFromUI = async function(pluginName) {
    const result = await pluginManager.install(pluginName);
    return result;
};

window.copyPluginInstallCommand = async function(pluginName) {
    const success = await pluginManager.copyInstallCommand(pluginName);
    if (success) {
        // 显示复制成功提示
        alert(`安装命令已复制到剪贴板:\ngb install ${pluginName}`);
    } else {
        alert('复制失败，请手动复制命令');
    }
    return success;
};

window.searchPlugins = async function(query) {
    const results = await pluginManager.search(query);
    return results;
};

// 插件安装命令解析器
function parseInstallCommand(command) {
    // 解析形如 "gb install plugin-name" 的命令
    const match = command.match(/^gb\s+install\s+([a-zA-Z0-9_-]+)$/i);
    if (match) {
        return match[1];
    }
    return null;
}

// 导出插件管理器
export default pluginManager;
export { PluginManager, parseInstallCommand };

// 注册到全局window对象
window.pluginManager = pluginManager;
window.PluginManager = PluginManager;
window.parseInstallCommand = parseInstallCommand;

// 添加一些常用的辅助函数
window.createPluginCard = function(plugin) {
    const card = document.createElement('div');
    card.className = 'plugin-card';
    
    const formattedDownloads = pluginManager.formatDownloads(plugin.downloads);
    
    card.innerHTML = `
        <img src="${plugin.image || 'https://via.placeholder.com/300x160?text=Plugin'}" alt="${plugin.name}">
        <div class="plugin-content">
            <h4 class="plugin-title">${plugin.name}</h4>
            <p class="plugin-description">${plugin.description || '暂无描述'}</p>
            <div class="plugin-meta">
                <span>${plugin.author || '未知作者'}</span>
                <span>v${plugin.version || '1.0.0'}</span>
                <span>${formattedDownloads} 下载</span>
            </div>
            <div class="plugin-actions">
                <button class="install-btn" onclick="installPluginFromUI('${plugin.name}')">安装插件</button>
                <button class="copy-btn" onclick="copyPluginInstallCommand('${plugin.name}')">复制命令</button>
            </div>
        </div>
    `;
    
    return card;
};

// 为插件操作按钮添加样式
const pluginStyles = document.createElement('style');
pluginStyles.textContent = `
    .plugin-actions {
        display: flex;
        gap: 10px;
        margin-top: 15px;
    }
    
    .install-btn {
        flex: 1;
        background-color: #007aff;
        color: white;
        border: none;
        padding: 10px;
        border-radius: 8px;
        cursor: pointer;
        font-weight: 500;
        transition: background-color 0.3s;
    }
    
    .install-btn:hover {
        background-color: #0066cc;
    }
    
    .copy-btn {
        background-color: #f0f0f0;
        color: #333;
        border: none;
        padding: 10px 15px;
        border-radius: 8px;
        cursor: pointer;
        font-size: 14px;
        transition: background-color 0.3s;
    }
    
    .copy-btn:hover {
        background-color: #e0e0e0;
    }
    
    .plugin-notification {
        position: fixed;
        bottom: 20px;
        right: 20px;
        z-index: 9999;
    }
`;
document.head.appendChild(pluginStyles);