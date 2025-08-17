#!/usr/bin/env python3
"""
ArXiv论文转发工具 - 运行脚本
提供简单的命令行界面来运行工具
"""

import sys
import os
import subprocess
import argparse
from datetime import datetime

def check_dependencies():
    """检查依赖是否安装"""
    try:
        import requests
        import feedparser
        import fitz
        import PIL
        import google.generativeai
        import schedule
        from dotenv import load_dotenv
        print("✅ 所有依赖已安装")
        return True
    except ImportError as e:
        print(f"❌ 缺少依赖: {e}")
        print("请运行: pip install -r requirements.txt")
        return False

def test_wechat():
    """测试微信发送功能"""
    print("🔧 测试微信发送功能...")
    try:
        result = subprocess.run([sys.executable, 'test_wechat.py'], 
                              capture_output=True, text=True, encoding='utf-8')
        
        print(result.stdout)
        
        if result.stderr:
            print("⚠️  错误信息:")
            print(result.stderr)
        
        if result.returncode != 0:
            print(f"❌ 测试失败 (返回码: {result.returncode})")
            
    except Exception as e:
        print(f"❌ 测试出错: {str(e)}")

def check_config():
    """检查配置文件"""
    if not os.path.exists('.env'):
        print("❌ 找不到.env配置文件")
        print("请复制.env.example为.env并填写配置信息")
        return False
    
    from dotenv import load_dotenv
    load_dotenv()
    
    required_vars = ['GEMINI_API_KEY', 'SENDER_EMAIL', 'SENDER_PASSWORD', 'RECIPIENT_EMAIL']
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ 缺少必要的环境变量: {', '.join(missing_vars)}")
        print("请在.env文件中配置这些变量")
        return False
    
    print("✅ 配置检查通过")
    return True

def run_once():
    """运行一次"""
    print(f"🚀 开始单次运行... ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')})")
    
    try:
        result = subprocess.run([sys.executable, 'main.py', 'once'], 
                              capture_output=True, text=True, encoding='utf-8')
        
        print("📝 运行输出:")
        print(result.stdout)
        
        if result.stderr:
            print("⚠️  错误信息:")
            print(result.stderr)
        
        if result.returncode == 0:
            print("✅ 运行完成")
        else:
            print(f"❌ 运行失败 (返回码: {result.returncode})")
            
    except Exception as e:
        print(f"❌ 运行出错: {str(e)}")

def run_scheduled():
    """定时运行"""
    print("⏰ 启动定时任务...")
    print("按 Ctrl+C 停止")
    
    try:
        subprocess.run([sys.executable, 'main.py'])
    except KeyboardInterrupt:
        print("\n👋 定时任务已停止")
    except Exception as e:
        print(f"❌ 定时任务出错: {str(e)}")

def show_status():
    """显示状态信息"""
    print("📊 ArXiv论文转发工具状态")
    print("=" * 40)
    
    # 检查依赖
    print("📦 依赖检查:")
    check_dependencies()
    
    # 检查配置
    print("\n⚙️  配置检查:")
    check_config()
    
    # 检查文件
    print(f"\n📁 项目文件:")
    required_files = [
        'main.py', 'config.py', 'arxiv_search.py', 
        'pdf_processor.py', 'gemini_analyzer.py', 'email_sender.py'
    ]
    
    for file in required_files:
        if os.path.exists(file):
            print(f"   ✅ {file}")
        else:
            print(f"   ❌ {file} (缺失)")
    
    # 检查日志
    if os.path.exists('arxiv_to_mail.log'):
        try:
            with open('arxiv_to_mail.log', 'r', encoding='utf-8') as f:
                lines = f.readlines()
                if lines:
                    print(f"\n📋 最近日志 (最后5行):")
                    for line in lines[-5:]:
                        print(f"   {line.strip()}")
        except:
            pass

def install_deps():
    """安装依赖"""
    print("📦 安装依赖包...")
    try:
        subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'], 
                      check=True)
        print("✅ 依赖安装完成")
    except subprocess.CalledProcessError:
        print("❌ 依赖安装失败")

def setup():
    """初始化设置"""
    print("🛠️  ArXiv论文转发工具 - 初始化设置")
    print("=" * 50)
    
    # 安装依赖
    print("1. 安装依赖包...")
    install_deps()
    
    # 复制配置文件
    print("\n2. 创建配置文件...")
    if not os.path.exists('.env') and os.path.exists('.env.example'):
        import shutil
        shutil.copy('.env.example', '.env')
        print("✅ 已创建.env配置文件")
        print("请编辑.env文件，填入你的API密钥和邮箱信息")
    elif os.path.exists('.env'):
        print("✅ .env配置文件已存在")
    else:
        print("❌ .env.example文件不存在")
    
    # 创建目录
    print("\n3. 创建下载目录...")
    os.makedirs('./downloads', exist_ok=True)
    os.makedirs('./downloads/screenshots', exist_ok=True)
    print("✅ 目录创建完成")
    
    print("\n🎉 初始化完成！")
    print("\n接下来请：")
    print("1. 编辑.env文件，填入你的配置信息")
    print("2. 运行 'python run.py test' 进行测试")

def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="ArXiv论文转发工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  python run.py setup          # 初始化设置
  python run.py test           # 测试运行一次
  python run.py start          # 启动定时任务
  python run.py status         # 查看状态
  python run.py test-wechat    # 测试微信发送功能
        """
    )
    
    parser.add_argument('command', 
                       choices=['setup', 'test', 'start', 'status', 'install', 'test-wechat'],
                       help='要执行的命令')
    
    if len(sys.argv) == 1:
        parser.print_help()
        return
    
    args = parser.parse_args()
    
    if args.command == 'setup':
        setup()
    elif args.command == 'test':
        if check_dependencies() and check_config():
            run_once()
    elif args.command == 'start':
        if check_dependencies() and check_config():
            run_scheduled()
    elif args.command == 'status':
        show_status()
    elif args.command == 'install':
        install_deps()
    elif args.command == 'test-wechat':
        if check_dependencies():
            test_wechat()

if __name__ == "__main__":
    main()