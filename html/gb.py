#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GB 插件安装工具
用法: gb install [插件名称]
功能: 从GitHub Pages托管的网站API获取插件
support开机自启动，监听编辑器内置终端的gb命令
"""

import sys
import os
import json
import shutil
import time
import subprocess
import winreg
import logging
import threading
import requests
import tempfile
import zipfile
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import tkinter as tk
from tkinter import messagebox

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename=os.path.join(os.path.expanduser("~"), ".gb", "gb_tool.log"),
    filemode='a'
)

# GitHub Pages API 配置
GITHUB_PAGES_URL = "https://your-username.github.io/gb-plugin-market"
API_ENDPOINT = f"{GITHUB_PAGES_URL}/data"

# 插件目录配置
GB_EDIT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PLUGIN_TARGET_DIR = os.path.join(GB_EDIT_DIR, "GbPlugin")
LOCAL_PLUGIN_DIR = os.path.join(os.path.expanduser("~"), ".gb", "plugins")

# 确保必要的目录存在
for directory in [PLUGIN_TARGET_DIR, LOCAL_PLUGIN_DIR, os.path.join(os.path.expanduser("~"), ".gb")]:
    os.makedirs(directory, exist_ok=True)

# 终端命令历史文件路径
TERMINAL_HISTORY_PATH = os.path.join(os.path.expanduser("~"), ".gb", "terminal_history.txt")

def install_plugin(plugin_name):
    """从GitHub Pages获取并安装插件"""
    print(f"正在安装插件: {plugin_name}")
    logging.info(f"开始安装插件: {plugin_name}")
    
    temp_file_path = None
    try:
        # 获取插件列表
        print("正在从GitHub Pages获取插件信息...")
        logging.info(f"请求插件数据: {API_ENDPOINT}/plugins.json")
        
        response = requests.get(f"{API_ENDPOINT}/plugins.json", timeout=10)
        response.raise_for_status()
        
        plugins_data = response.json()
        
        # 查找指定插件
        plugin_info = None
        for plugin in plugins_data.get('data', []):
            if plugin.get('id') == plugin_name or plugin.get('name') == plugin_name:
                plugin_info = plugin
                break
        
        if not plugin_info:
            error_msg = f"未找到插件: {plugin_name}"
            print(f"错误: {error_msg}")
            logging.error(error_msg)
            return False
        
        print(f"找到插件: {plugin_info['name']} v{plugin_info['version']} by {plugin_info['author']}")
        
        # 准备下载URL
        plugin_id = plugin_info.get('id')
        download_url = f"{API_ENDPOINT}/plugins/{plugin_id}.zip"
        print(f"正在下载插件: {download_url}")
        logging.info(f"下载插件文件: {download_url}")
        
        # 创建临时文件
        with tempfile.NamedTemporaryFile(delete=False, suffix='.zip') as temp_file:
            temp_file_path = temp_file.name
            
            # 下载文件
            with requests.get(download_url, stream=True, timeout=30) as r:
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
        
        # 创建目标目录
        plugin_target_dir = os.path.join(PLUGIN_TARGET_DIR, plugin_id)
        os.makedirs(plugin_target_dir, exist_ok=True)
        
        # 解压插件
        with zipfile.ZipFile(temp_file_path, 'r') as zip_ref:
            zip_ref.extractall(plugin_target_dir)
        
        # 创建插件元数据文件
        with open(os.path.join(plugin_target_dir, 'plugin.json'), 'w', encoding='utf-8') as f:
            json.dump(plugin_info, f, ensure_ascii=False, indent=2)
        
        # 检查是否需要安装Python依赖
        requirements_file = os.path.join(plugin_target_dir, 'requirements.txt')
        if os.path.exists(requirements_file):
            print("检测到依赖文件，正在安装Python依赖...")
            logging.info(f"安装插件依赖: {requirements_file}")
            try:
                subprocess.run(
                    [sys.executable, '-m', 'pip', 'install', '-r', requirements_file],
                    check=True,
                    capture_output=True,
                    text=True
                )
                print("依赖安装成功")
            except subprocess.CalledProcessError as e:
                print(f"警告: 依赖安装失败: {e.stderr}")
                logging.warning(f"依赖安装失败: {e.stderr}")
        
        # 清理临时文件
        try:
            if temp_file_path and os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
                temp_file_path = None
        except:
            logging.warning(f"无法删除临时文件: {temp_file_path}")
        
        print(f"\n插件 {plugin_info['name']} 安装成功！")
        print(f"插件路径: {plugin_target_dir}")
        logging.info(f"插件 {plugin_info['name']} 安装成功，路径: {plugin_target_dir}")
        
        # 同时复制到用户本地插件目录
        local_plugin_dir = os.path.join(LOCAL_PLUGIN_DIR, plugin_id)
        if os.path.exists(local_plugin_dir):
            shutil.rmtree(local_plugin_dir)
        shutil.copytree(plugin_target_dir, local_plugin_dir)
        print(f"插件已同步到本地目录: {local_plugin_dir}")
        
        return True
        
    except requests.exceptions.RequestException as e:
        error_msg = f"网络错误: {e}"
        print(error_msg)
        print("请检查网络连接或GitHub Pages是否正常访问")
        logging.error(error_msg)
    except zipfile.BadZipFile:
        error_msg = "错误: 下载的文件不是有效的ZIP文件"
        print(error_msg)
        logging.error(error_msg)
    except Exception as e:
        print(f"安装过程中发生错误: {e}")
        logging.error(f"安装错误: {e}")
    finally:
        # 确保临时文件被清理
        if temp_file_path and os.path.exists(temp_file_path):
            try:
                os.unlink(temp_file_path)
            except:
                pass
    
    return False

def list_plugins():
    print("已安装的插件:")
    if not os.path.exists(PLUGIN_TARGET_DIR):
        print("  暂无安装的插件")
        return
    
    plugin_dirs = [d for d in os.listdir(PLUGIN_TARGET_DIR) if os.path.isdir(os.path.join(PLUGIN_TARGET_DIR, d))]
    
    if not plugin_dirs:
        print("  暂无安装的插件")
        return
    
    for plugin_id in plugin_dirs:
        plugin_path = os.path.join(PLUGIN_TARGET_DIR, plugin_id)
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
        # 从GitHub Pages获取插件列表
        print("正在从GitHub Pages搜索插件...")
        response = requests.get(f"{API_ENDPOINT}/plugins.json", timeout=10)
        response.raise_for_status()
        
        plugins_data = response.json()
        results = []
        
        # 本地过滤搜索
        query_lower = query.lower()
        for plugin in plugins_data.get('data', []):
            if (query_lower in plugin.get('name', '').lower() or 
                query_lower in plugin.get('description', '').lower() or 
                query_lower in plugin.get('category', '').lower() or
                query_lower in plugin.get('author', '').lower()):
                results.append(plugin)
        
        print(f"找到 {len(results)} 个插件:")
        
        for plugin in results:
            print(f"\n  - {plugin['name']} v{plugin['version']}")
            print(f"    作者: {plugin['author']}")
            print(f"    分类: {plugin['category']}")
            print(f"    描述: {plugin['description']}")
            print(f"    安装命令: gb install {plugin['id']}")
            
    except requests.exceptions.RequestException as e:
        print(f"网络错误: {e}")
        print("请检查网络连接或GitHub Pages是否正常访问")
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
