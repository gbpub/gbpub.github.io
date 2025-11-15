#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成静态插件数据文件
用于GitHub Pages托管
"""

import os
import json
import glob

# 配置
PLUGIN_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'Plugin')
OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')

# 确保输出目录存在
os.makedirs(OUTPUT_DIR, exist_ok=True)

# 获取Plugin目录中的实际文件
real_plugins = []
for filename in os.listdir(PLUGIN_DIR):
    file_path = os.path.join(PLUGIN_DIR, filename)
    if os.path.isfile(file_path):
        # 生成插件信息
        plugin_id = os.path.splitext(filename)[0].lower().replace(' ', '-')
        plugin = {
            'id': plugin_id,
            'name': os.path.splitext(filename)[0],
            'description': f'这是一个GB编辑器插件: {filename}',
            'author': 'GB Team',
            'version': '1.0.0',
            'downloads': 0,
            'category': 'tool',
            'image': 'https://via.placeholder.com/300x160?text=Plugin',
            'filename': filename,
            'url': f'/Plugin/{filename}'
        }
        real_plugins.append(plugin)

# 如果没有实际插件，添加一些示例插件
if not real_plugins:
    real_plugins = [
        {
            'id': 'gb-parser',
            'name': 'gb_parser',
            'description': 'GB语言解析器插件',
            'author': 'GB Team',
            'version': '1.0.0',
            'downloads': 100,
            'category': 'core',
            'image': 'https://via.placeholder.com/300x160?text=GB+Parser',
            'filename': 'gb_parser.py',
            'url': '/Plugin/gb_parser.py'
        }
    ]

# 生成插件列表数据
plugins_data = {
    'success': True,
    'data': real_plugins,
    'pagination': {
        'page': 1,
        'limit': 20,
        'total': len(real_plugins),
        'totalPages': 1
    }
}

# 保存插件列表数据
with open(os.path.join(OUTPUT_DIR, 'plugins.json'), 'w', encoding='utf-8') as f:
    json.dump(plugins_data, f, ensure_ascii=False, indent=2)

# 为每个插件生成单独的数据文件
for plugin in real_plugins:
    plugin_detail_data = {
        'success': True,
        'data': plugin
    }
    with open(os.path.join(OUTPUT_DIR, f'plugin_{plugin["id"]}.json'), 'w', encoding='utf-8') as f:
        json.dump(plugin_detail_data, f, ensure_ascii=False, indent=2)

# 生成搜索数据示例
search_data = {
    'success': True,
    'data': real_plugins,
    'total': len(real_plugins)
}
with open(os.path.join(OUTPUT_DIR, 'search_example.json'), 'w', encoding='utf-8') as f:
    json.dump(search_data, f, ensure_ascii=False, indent=2)

# 生成统计数据
stats_data = {
    'success': True,
    'data': {
        'totalDownloads': sum(p['downloads'] for p in real_plugins),
        'totalPlugins': len(real_plugins),
        'popularPlugins': sorted(real_plugins, key=lambda x: x['downloads'], reverse=True)[:3],
        'categoryCounts': {}
    }
}

# 统计各分类插件数量
for plugin in real_plugins:
    stats_data['data']['categoryCounts'][plugin['category']] = \
        stats_data['data']['categoryCounts'].get(plugin['category'], 0) + 1

with open(os.path.join(OUTPUT_DIR, 'stats.json'), 'w', encoding='utf-8') as f:
    json.dump(stats_data, f, ensure_ascii=False, indent=2)

print(f"已生成静态数据文件到 {OUTPUT_DIR}")
print(f"生成了 {len(real_plugins)} 个插件的数据")
print("文件列表:")
for filename in os.listdir(OUTPUT_DIR):
    print(f"  - {filename}")

print("\n请确保在前端代码中修改API调用路径，使用这些静态JSON文件")