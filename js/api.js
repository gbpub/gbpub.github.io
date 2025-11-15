// GB 插件市场 - API 交互模块

// 静态数据配置 - 用于GitHub Pages
const STATIC_DATA_PATH = '../data';

// 通用HTTP请求函数
async function fetchApi(endpoint, options = {}) {
    try {
        // 处理不同的端点，返回对应的静态文件路径
        let staticFilePath = STATIC_DATA_PATH;
        
        if (endpoint.includes('/plugins/search')) {
            // 搜索时返回示例数据
            staticFilePath += '/search_example.json';
        } else if (endpoint.startsWith('/plugins/') && endpoint.includes('/download')) {
            // 处理下载请求
            const pluginName = endpoint.split('/plugins/')[1].split('/download')[0];
            staticFilePath += `/plugin_${pluginName}.json`;
        } else if (endpoint.startsWith('/plugins/')) {
            // 获取单个插件详情
            const pluginId = endpoint.split('/plugins/')[1];
            staticFilePath += `/plugin_${pluginId}.json`;
        } else if (endpoint === '/plugins') {
            staticFilePath += '/plugins.json';
        } else if (endpoint.includes('/stats/downloads')) {
            staticFilePath += '/download_stats.json';
        } else if (endpoint.includes('/stats/popular')) {
            staticFilePath += '/popular_plugins.json';
        } else if (endpoint === '/user/login' || endpoint === '/user/info') {
            // 用户相关API返回模拟数据
            return { success: true, data: { username: 'demo', isLoggedIn: true } };
        } else {
            // 默认返回插件列表
            staticFilePath += '/plugins.json';
        }
        
        // 设置默认选项，适配原始代码中的默认值
        const defaultOptions = {
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }
        };
        
        const fetchOptions = {
            ...defaultOptions,
            ...options,
            headers: {
                ...defaultOptions.headers,
                ...options.headers
            }
        };
        
        const response = await fetch(staticFilePath, fetchOptions);
        
        if (!response.ok) {
            // 如果文件不存在，返回默认数据
            console.warn(`文件不存在: ${staticFilePath}`);
            
            // 根据不同的端点返回不同的默认数据结构
            if (endpoint.includes('/search')) {
                return { success: true, data: [], total: 0 };
            } else if (endpoint.startsWith('/plugins/')) {
                return {
                    success: true,
                    data: {
                        id: 'default',
                        name: '默认插件',
                        description: '这是一个默认插件描述',
                        author: '系统',
                        version: '1.0.0'
                    }
                };
            } else {
                return { success: true, data: [], total: 0 };
            }
        }
        
        // 检查响应是否为空
        const contentType = response.headers.get('content-type');
        if (contentType && contentType.includes('application/json')) {
            return await response.json();
        } else {
            return await response.text();
        }
    } catch (error) {
        console.error('数据加载失败:', error);
        // 返回默认数据而不是抛出异常，确保应用能够继续运行
        return { success: true, data: [], total: 0 };
    }
}

// 插件相关API
export const PluginAPI = {
    // 搜索插件
    async searchPlugins(query, filters = {}) {
        try {
            const searchParams = new URLSearchParams();
            searchParams.append('query', query);
            
            // 添加过滤器参数
            Object.keys(filters).forEach(key => {
                if (filters[key]) {
                    searchParams.append(key, filters[key]);
                }
            });
            
            return await fetchApi(`/plugins/search?${searchParams.toString()}`);
        } catch (error) {
            console.error('搜索插件失败:', error);
            // 返回模拟数据作为备用
            return {
                success: true,
                data: [
                    {
                        id: 'search-1',
                        name: `${query} Plugin`,
                        description: `这是一个与${query}相关的插件示例`,
                        author: 'Example Author',
                        version: '1.0.0',
                        downloads: '1,234',
                        category: 'tool',
                        image: 'https://via.placeholder.com/300x160?text=Search+Result'
                    }
                ],
                total: 1
            };
        }
    },
    
    // 获取插件详情
    async getPluginDetails(pluginName) {
        try {
            return await fetchApi(`/plugins/${encodeURIComponent(pluginName)}`);
        } catch (error) {
            console.error(`获取插件 ${pluginName} 详情失败:`, error);
            // 返回模拟数据
            return {
                success: true,
                data: {
                    id: pluginName,
                    name: pluginName,
                    description: `这是插件 ${pluginName} 的详细描述。该插件提供了强大的功能，可以帮助您更高效地进行开发。`,
                    author: 'Plugin Author',
                    version: '1.0.0',
                    downloads: '10,000+',
                    category: 'tool',
                    image: 'https://via.placeholder.com/600x320?text=Plugin+Details',
                    features: [
                        '功能一：提供强大的编辑功能',
                        '功能二：支持多种文件格式',
                        '功能三：自定义配置选项'
                    ],
                    requirements: 'GB Editor 1.0.0 或更高版本',
                    changelog: [
                        { version: '1.0.0', date: '2025-01-01', changes: ['初始版本发布'] }
                    ]
                }
            };
        }
    },
    
    // 下载插件
    async downloadPlugin(pluginName) {
        try {
            const response = await fetchApi(`/plugins/${encodeURIComponent(pluginName)}/download`, {
                method: 'GET',
                // 对于下载，我们不期望JSON响应
                headers: {
                    'Accept': '*/*'
                }
            });
            return response;
        } catch (error) {
            console.error(`下载插件 ${pluginName} 失败:`, error);
            // 模拟下载成功
            return {
                success: true,
                message: `插件 ${pluginName} 下载链接已生成`,
                downloadUrl: `/Plugin/${pluginName}.zip`
            };
        }
    },
    
    // 获取插件列表
    async getPluginList(options = {}) {
        try {
            const { category = '', sort = 'latest', page = 1, limit = 20 } = options;
            
            const searchParams = new URLSearchParams({
                category,
                sort,
                page,
                limit
            });
            
            return await fetchApi(`/plugins?${searchParams.toString()}`);
        } catch (error) {
            console.error('获取插件列表失败:', error);
            // 返回模拟数据
            return {
                success: true,
                data: [
                    {
                        id: 'list-1',
                        name: 'Example Plugin 1',
                        description: '示例插件1的描述',
                        author: 'Author 1',
                        version: '1.0.0',
                        downloads: '1,000',
                        category: category || 'tool',
                        image: 'https://via.placeholder.com/300x160?text=Example+1'
                    },
                    {
                        id: 'list-2',
                        name: 'Example Plugin 2',
                        description: '示例插件2的描述',
                        author: 'Author 2',
                        version: '1.1.0',
                        downloads: '2,000',
                        category: category || 'theme',
                        image: 'https://via.placeholder.com/300x160?text=Example+2'
                    }
                ],
                pagination: {
                    page: 1,
                    limit: 20,
                    total: 2,
                    totalPages: 1
                }
            };
        }
    },
    
    // 上传插件
    async uploadPlugin(formData) {
        try {
            return await fetchApi('/plugins/upload', {
                method: 'POST',
                headers: {
                    // 不设置Content-Type，让浏览器自动设置
                    // 'Content-Type': 'multipart/form-data'
                },
                body: formData
            });
        } catch (error) {
            console.error('上传插件失败:', error);
            throw error;
        }
    }
};

// 统计相关API
export const StatsAPI = {
    // 获取下载统计
    async getDownloadStats() {
        try {
            return await fetchApi('/stats/downloads');
        } catch (error) {
            console.error('获取下载统计失败:', error);
            return {
                success: true,
                data: {
                    totalDownloads: '100,000',
                    dailyDownloads: '1,234',
                    monthlyDownloads: '36,543'
                }
            };
        }
    },
    
    // 获取热门插件
    async getPopularPlugins() {
        try {
            return await fetchApi('/stats/popular');
        } catch (error) {
            console.error('获取热门插件失败:', error);
            return {
                success: true,
                data: [
                    { name: 'Popular Plugin 1', downloads: '50,000' },
                    { name: 'Popular Plugin 2', downloads: '45,000' },
                    { name: 'Popular Plugin 3', downloads: '40,000' }
                ]
            };
        }
    }
};

// 用户相关API（如果需要用户登录功能）
export const UserAPI = {
    // 用户登录
    async login(username, password) {
        try {
            return await fetchApi('/user/login', {
                method: 'POST',
                body: JSON.stringify({ username, password })
            });
        } catch (error) {
            console.error('登录失败:', error);
            throw error;
        }
    },
    
    // 获取用户信息
    async getUserInfo() {
        try {
            return await fetchApi('/user/info');
        } catch (error) {
            console.error('获取用户信息失败:', error);
            return null;
        }
    }
};

// 注册全局API对象，方便其他脚本使用
window.PluginAPI = PluginAPI;
window.StatsAPI = StatsAPI;
window.UserAPI = UserAPI;

// 错误处理
export function handleApiError(error, defaultMessage = 'API请求失败') {
    console.error('API错误:', error);
    
    // 根据错误类型提供不同的提示
    if (error.name === 'AbortError') {
        return '请求超时，请稍后重试';
    } else if (error.message.includes('network')) {
        return '网络连接失败，请检查您的网络';
    } else if (error.message.includes('401')) {
        return '请先登录';
    } else if (error.message.includes('404')) {
        return '请求的资源不存在';
    }
    
    return defaultMessage;
}

// 导出默认对象
export default {
    PluginAPI,
    StatsAPI,
    UserAPI,
    handleApiError
};