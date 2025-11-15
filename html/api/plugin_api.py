#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GB 插件市场 - API 服务
用于处理插件搜索、下载等功能
"""

import os
import json
import glob
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import mimetypes

# API 配置
class Config:
    PLUGIN_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'Plugin')
    PORT = 8000
    HOST = 'localhost'
    DEBUG = True

# 确保插件目录存在
os.makedirs(Config.PLUGIN_DIR, exist_ok=True)

# 模拟插件数据库
PLUGINS_DB = [
    {
        'id': 'dark-theme-pro',
        'name': 'Dark Theme Pro',
        'description': '专业级暗黑主题，保护您的眼睛，提供舒适的编码体验。',
        'author': 'GB Team',
        'version': '1.2.0',
        'downloads': 12456,
        'category': 'theme',
        'image': 'https://via.placeholder.com/300x160?text=Dark+Theme',
        'filename': 'dark-theme-pro.zip',
        'url': '/Plugin/dark-theme-pro.zip'
    },
    {
        'id': 'code-snippets',
        'name': 'Code Snippets',
        'description': '常用代码片段库，快速插入各种模板代码，提高开发效率。',
        'author': 'DeveloperX',
        'version': '2.1.0',
        'downloads': 8732,
        'category': 'tool',
        'image': 'https://via.placeholder.com/300x160?text=Code+Snippets',
        'filename': 'code-snippets.zip',
        'url': '/Plugin/code-snippets.zip'
    },
    {
        'id': 'debug-helper',
        'name': 'Debug Helper',
        'description': '高级调试工具，帮助您快速定位和解决代码中的问题。',
        'author': 'BugHunter',
        'version': '1.5.3',
        'downloads': 5689,
        'category': 'debug',
        'image': 'https://via.placeholder.com/300x160?text=Debug+Helper',
        'filename': 'debug-helper.zip',
        'url': '/Plugin/debug-helper.zip'
    },
    {
        'id': 'python-support',
        'name': 'Python Support',
        'description': '为GB编辑器添加Python语言支持，包括语法高亮和代码补全。',
        'author': 'PyExpert',
        'version': '1.0.0',
        'downloads': 2345,
        'category': 'language',
        'image': 'https://via.placeholder.com/300x160?text=Python+Support',
        'filename': 'python-support.zip',
        'url': '/Plugin/python-support.zip'
    }
]

# HTTP 请求处理器
class PluginAPIHandler(BaseHTTPRequestHandler):
    # 设置响应头
    def _set_headers(self, status=200, content_type='application/json'):
        self.send_response(status)
        self.send_header('Content-type', content_type)
        self.send_header('Access-Control-Allow-Origin', '*')  # 允许跨域请求
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    # 处理 OPTIONS 请求（CORS 预检）
    def do_OPTIONS(self):
        self._set_headers(204)
    
    # 处理 GET 请求
    def do_GET(self):
        parsed_url = urlparse(self.path)
        path = parsed_url.path
        query_params = parse_qs(parsed_url.query)
        
        # API 路由处理
        if path.startswith('/api/plugins/search'):
            self.handle_search_plugins(query_params)
        elif path.startswith('/api/plugins/') and '/download' in path:
            self.handle_download_plugin(path)
        elif path.startswith('/api/plugins/'):
            self.handle_get_plugin(path)
        elif path.startswith('/api/plugins'):
            self.handle_get_plugins(query_params)
        elif path.startswith('/api/stats'):
            self.handle_stats()
        elif path.startswith('/Plugin/'):
            self.serve_plugin_file(path)
        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({
                'success': False,
                'error': 'Not Found'
            }).encode())
    
    # 处理 POST 请求
    def do_POST(self):
        parsed_url = urlparse(self.path)
        path = parsed_url.path
        
        if path.startswith('/api/plugins/upload'):
            self.handle_upload_plugin()
        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({
                'success': False,
                'error': 'Not Found'
            }).encode())
    
    # 搜索插件
    def handle_search_plugins(self, query_params):
        query = query_params.get('query', [''])[0].lower()
        category = query_params.get('category', [''])[0]
        
        results = []
        for plugin in PLUGINS_DB:
            # 按名称或描述搜索
            if query in plugin['name'].lower() or query in plugin['description'].lower():
                # 如果指定了分类，只返回该分类的插件
                if not category or plugin['category'] == category:
                    results.append(plugin)
        
        self._set_headers()
        self.wfile.write(json.dumps({
            'success': True,
            'data': results,
            'total': len(results)
        }).encode())
    
    # 获取插件列表
    def handle_get_plugins(self, query_params):
        category = query_params.get('category', [''])[0]
        sort = query_params.get('sort', ['latest'])[0]
        page = int(query_params.get('page', [1])[0])
        limit = int(query_params.get('limit', [20])[0])
        
        # 过滤插件
        filtered_plugins = PLUGINS_DB
        if category:
            filtered_plugins = [p for p in filtered_plugins if p['category'] == category]
        
        # 排序插件
        if sort == 'downloads':
            filtered_plugins.sort(key=lambda x: x['downloads'], reverse=True)
        elif sort == 'name':
            filtered_plugins.sort(key=lambda x: x['name'].lower())
        # 默认按最新排序（这里使用ID作为排序依据）
        else:
            filtered_plugins.sort(key=lambda x: x['id'], reverse=True)
        
        # 分页
        start = (page - 1) * limit
        end = start + limit
        paginated_plugins = filtered_plugins[start:end]
        
        self._set_headers()
        self.wfile.write(json.dumps({
            'success': True,
            'data': paginated_plugins,
            'pagination': {
                'page': page,
                'limit': limit,
                'total': len(filtered_plugins),
                'totalPages': (len(filtered_plugins) + limit - 1) // limit
            }
        }).encode())
    
    # 获取单个插件详情
    def handle_get_plugin(self, path):
        # 提取插件ID
        plugin_id = path.split('/')[-1]
        
        # 查找插件
        plugin = None
        for p in PLUGINS_DB:
            if p['id'] == plugin_id or p['name'].lower() == plugin_id.lower():
                plugin = p
                break
        
        if plugin:
            self._set_headers()
            self.wfile.write(json.dumps({
                'success': True,
                'data': plugin
            }).encode())
        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({
                'success': False,
                'error': 'Plugin not found'
            }).encode())
    
    # 下载插件
    def handle_download_plugin(self, path):
        # 提取插件ID
        plugin_id = path.split('/')[-2]
        
        # 查找插件
        plugin = None
        for p in PLUGINS_DB:
            if p['id'] == plugin_id or p['name'].lower() == plugin_id.lower():
                plugin = p
                break
        
        if plugin:
            # 增加下载计数
            plugin['downloads'] += 1
            
            # 返回下载链接
            self._set_headers()
            self.wfile.write(json.dumps({
                'success': True,
                'message': f'Plugin {plugin["name"]} download link generated',
                'downloadUrl': plugin['url'],
                'filename': plugin['filename']
            }).encode())
        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({
                'success': False,
                'error': 'Plugin not found'
            }).encode())
    
    # 提供插件文件下载
    def serve_plugin_file(self, path):
        # 获取文件路径
        file_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), path.lstrip('/'))
        
        if os.path.exists(file_path):
            # 检查是否是插件文件
            if not file_path.endswith('.zip') or not 'Plugin' in file_path:
                self._set_headers(403)
                self.wfile.write(json.dumps({
                    'success': False,
                    'error': 'Access denied'
                }).encode())
                return
            
            # 提供文件下载
            try:
                content_type, _ = mimetypes.guess_type(file_path)
                content_type = content_type or 'application/octet-stream'
                
                self.send_response(200)
                self.send_header('Content-Type', content_type)
                self.send_header('Content-Disposition', f'attachment; filename="{os.path.basename(file_path)}"')
                self.send_header('Content-Length', os.path.getsize(file_path))
                self.end_headers()
                
                with open(file_path, 'rb') as f:
                    self.wfile.write(f.read())
            except Exception as e:
                self._set_headers(500)
                self.wfile.write(json.dumps({
                    'success': False,
                    'error': str(e)
                }).encode())
        else:
            # 如果文件不存在，创建一个模拟的空ZIP文件
            zip_content = b'PK\x05\x06' + b'\x00' * 18  # 最小有效ZIP文件
            
            filename = os.path.basename(file_path)
            self.send_response(200)
            self.send_header('Content-Type', 'application/zip')
            self.send_header('Content-Disposition', f'attachment; filename="{filename}"')
            self.send_header('Content-Length', len(zip_content))
            self.end_headers()
            self.wfile.write(zip_content)
    
    # 处理上传插件
    def handle_upload_plugin(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        
        # 简化处理，实际应用中需要更复杂的表单数据解析
        # 这里只是返回一个成功的响应
        
        self._set_headers()
        self.wfile.write(json.dumps({
            'success': True,
            'message': 'Plugin upload is not fully implemented in this demo',
            'data': {'received_bytes': content_length}
        }).encode())
    
    # 获取统计信息
    def handle_stats(self):
        total_downloads = sum(plugin['downloads'] for plugin in PLUGINS_DB)
        popular_plugins = sorted(PLUGINS_DB, key=lambda x: x['downloads'], reverse=True)[:3]
        
        stats = {
            'totalDownloads': total_downloads,
            'totalPlugins': len(PLUGINS_DB),
            'popularPlugins': [
                {'name': p['name'], 'downloads': p['downloads']}
                for p in popular_plugins
            ],
            'categoryCounts': {}
        }
        
        # 统计各分类插件数量
        for plugin in PLUGINS_DB:
            stats['categoryCounts'][plugin['category']] = \
                stats['categoryCounts'].get(plugin['category'], 0) + 1
        
        self._set_headers()
        self.wfile.write(json.dumps({
            'success': True,
            'data': stats
        }).encode())
    
    # 自定义日志格式
    def log_message(self, format, *args):
        if Config.DEBUG:
            super().log_message(format, *args)

# 创建简单的插件安装命令脚本
def create_install_script():
    script_content = '''#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GB 插件安装工具
用法: gb install [插件名称]
"""

import sys
import os
import json
import requests
import zipfile
import tempfile

# API 配置
API_URL = "http://localhost:8000/api"
PLUGIN_DIR = os.path.join(os.path.expanduser("~"), ".gb", "plugins")

# 确保插件目录存在
os.makedirs(PLUGIN_DIR, exist_ok=True)

def install_plugin(plugin_name):
    print(f"正在安装插件: {plugin_name}")
    
    try:
        # 获取插件信息
        print("正在获取插件信息...")
        response = requests.get(f"{API_URL}/plugins/{plugin_name}")
        response.raise_for_status()
        
        plugin_data = response.json()
        
        if not plugin_data.get('success'):
            print(f"错误: {plugin_data.get('error', '获取插件信息失败')}")
            return False
        
        plugin_info = plugin_data['data']
        print(f"找到插件: {plugin_info['name']} v{plugin_info['version']} by {plugin_info['author']}")
        
        # 获取下载链接
        print("正在获取下载链接...")
        download_response = requests.get(f"{API_URL}/plugins/{plugin_name}/download")
        download_response.raise_for_status()
        
        download_data = download_response.json()
        
        if not download_data.get('success'):
            print(f"错误: {download_data.get('error', '获取下载链接失败')}")
            return False
        
        # 下载插件文件
        download_url = f"http://localhost:8000{download_data['downloadUrl']}"
        print(f"正在下载插件: {download_url}")
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.zip') as temp_file:
            temp_file_path = temp_file.name
            
            with requests.get(download_url, stream=True) as r:
                r.raise_for_status()
                total_size = int(r.headers.get('content-length', 0))
                downloaded_size = 0
                
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk:
                        temp_file.write(chunk)
                        downloaded_size += len(chunk)
                        
                        # 显示下载进度
                        if total_size > 0:
                            progress = (downloaded_size / total_size) * 100
                            print(f"下载进度: {progress:.1f}%", end='\r')
                
        print("\n下载完成，正在解压...")
        
        # 解压插件
        plugin_target_dir = os.path.join(PLUGIN_DIR, plugin_info['id'])
        os.makedirs(plugin_target_dir, exist_ok=True)
        
        with zipfile.ZipFile(temp_file_path, 'r') as zip_ref:
            zip_ref.extractall(plugin_target_dir)
        
        # 创建插件元数据文件
        with open(os.path.join(plugin_target_dir, 'plugin.json'), 'w', encoding='utf-8') as f:
            json.dump(plugin_info, f, ensure_ascii=False, indent=2)
        
        # 清理临时文件
        os.unlink(temp_file_path)
        
        print(f"\n插件 {plugin_info['name']} 安装成功！")
        print(f"插件路径: {plugin_target_dir}")
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"网络错误: {e}")
        print("请确保API服务正在运行 (python plugin_api.py)")
    except zipfile.BadZipFile:
        print("错误: 下载的文件不是有效的ZIP文件")
    except Exception as e:
        print(f"安装过程中发生错误: {e}")
    finally:
        # 确保临时文件被清理
        if 'temp_file_path' in locals() and os.path.exists(temp_file_path):
            try:
                os.unlink(temp_file_path)
            except:
                pass
    
    return False

def list_plugins():
    print("已安装的插件:")
    if not os.path.exists(PLUGIN_DIR):
        print("  暂无安装的插件")
        return
    
    plugin_dirs = [d for d in os.listdir(PLUGIN_DIR) if os.path.isdir(os.path.join(PLUGIN_DIR, d))]
    
    if not plugin_dirs:
        print("  暂无安装的插件")
        return
    
    for plugin_id in plugin_dirs:
        plugin_path = os.path.join(PLUGIN_DIR, plugin_id)
        meta_file = os.path.join(plugin_path, 'plugin.json')
        
        if os.path.exists(meta_file):
            try:
                with open(meta_file, 'r', encoding='utf-8') as f:
                    plugin_info = json.load(f)
                    print(f"  - {plugin_info.get('name', plugin_id)} v{plugin_info.get('version', '?')}")
                    print(f"    作者: {plugin_info.get('author', '未知')}")
                    print(f"    描述: {plugin_info.get('description', '无')}")
            except:
                print(f"  - {plugin_id} (元数据格式错误)")
        else:
            print(f"  - {plugin_id} (无元数据)")

def search_plugins(query):
    print(f"搜索插件: {query}")
    
    try:
        response = requests.get(f"{API_URL}/plugins/search?query={query}")
        response.raise_for_status()
        
        search_data = response.json()
        
        if not search_data.get('success'):
            print(f"错误: {search_data.get('error', '搜索失败')}")
            return
        
        results = search_data.get('data', [])
        print(f"找到 {len(results)} 个插件:")
        
        for plugin in results:
            print(f"\n  - {plugin['name']} v{plugin['version']}")
            print(f"    作者: {plugin['author']}")
            print(f"    下载: {plugin['downloads']}")
            print(f"    分类: {plugin['category']}")
            print(f"    描述: {plugin['description']}")
            print(f"    安装命令: gb install {plugin['id']}")
            
    except Exception as e:
        print(f"搜索失败: {e}")

def main():
    if len(sys.argv) < 2:
        print("用法:")
        print("  gb install [插件名称]   - 安装指定插件")
        print("  gb list                - 列出已安装的插件")
        print("  gb search [关键词]      - 搜索插件")
        print("  gb help                - 显示帮助信息")
        return
    
    command = sys.argv[1].lower()
    
    if command == 'install' and len(sys.argv) > 2:
        plugin_name = sys.argv[2]
        install_plugin(plugin_name)
    elif command == 'list':
        list_plugins()
    elif command == 'search' and len(sys.argv) > 2:
        query = sys.argv[2]
        search_plugins(query)
    elif command == 'help':
        print("GB 插件管理工具")
        print("用法:")
        print("  gb install [插件名称]   - 安装指定插件")
        print("  gb list                - 列出已安装的插件")
        print("  gb search [关键词]      - 搜索插件")
        print("  gb help                - 显示帮助信息")
    else:
        print(f"未知命令: {command}")
        print("使用 'gb help' 查看帮助信息")

if __name__ == "__main__":
    main()
'''
    
    # 保存脚本到 html 目录
    script_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'gb.py')
    with open(script_path, 'w', encoding='utf-8') as f:
        f.write(script_content)
    
    # 在 Windows 上创建批处理文件
    batch_content = '''@echo off
python "%~dp0\gb.py" %*'''
    batch_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'gb.bat')
    with open(batch_path, 'w') as f:
        f.write(batch_content)
    
    print(f"已创建插件安装工具: {script_path}")
    print(f"已创建批处理文件: {batch_path}")
    print("使用方法:")
    print("  在命令行中: gb install 插件名称")
    print("  或在编辑器终端中: !gb install 插件名称")

# 启动服务器
def run_server():
    # 创建API目录
    api_dir = os.path.dirname(os.path.abspath(__file__))
    os.makedirs(api_dir, exist_ok=True)
    
    # 创建插件安装脚本
    create_install_script()
    
    # 启动HTTP服务器
    server_address = (Config.HOST, Config.PORT)
    httpd = HTTPServer(server_address, PluginAPIHandler)
    
    print(f"GB 插件市场 API 服务启动在 http://{Config.HOST}:{Config.PORT}")
    print(f"API 文档: http://{Config.HOST}:{Config.PORT}/api")
    print("按 Ctrl+C 停止服务")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n服务已停止")
    finally:
        httpd.server_close()

if __name__ == "__main__":
    run_server()