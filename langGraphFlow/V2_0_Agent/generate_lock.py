#!/usr/bin/env python3
"""
生成依赖锁定文件脚本
用于生成 requirements.lock 文件，包含所有直接和间接依赖的精确版本

使用方法：
    python generate_lock.py

说明：
    - 此脚本会先安装 requirements.txt 中的依赖
    - 然后使用 pip freeze 生成精确版本锁定文件
    - 生成的 requirements.lock 文件用于生产环境部署，确保版本一致性
"""
import subprocess
import sys
import os
from pathlib import Path


def run_command(cmd: list, description: str) -> bool:
    """执行命令并返回是否成功"""
    print(f"\n{'='*60}")
    print(f"执行: {description}")
    print(f"命令: {' '.join(cmd)}")
    print(f"{'='*60}\n")
    
    try:
        result = subprocess.run(
            cmd,
            check=True,
            capture_output=True,
            text=True
        )
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"错误: {e}")
        if e.stdout:
            print(f"标准输出: {e.stdout}")
        if e.stderr:
            print(f"错误输出: {e.stderr}")
        return False


def main():
    """主函数"""
    script_dir = Path(__file__).parent
    requirements_txt = script_dir / "requirements.txt"
    requirements_lock = script_dir / "requirements.lock"
    
    # 检查 requirements.txt 是否存在
    if not requirements_txt.exists():
        print(f"错误: 找不到 {requirements_txt}")
        sys.exit(1)
    
    print("="*60)
    print("生成依赖锁定文件")
    print("="*60)
    print(f"工作目录: {script_dir}")
    print(f"requirements.txt: {requirements_txt}")
    print(f"输出文件: {requirements_lock}")
    
    # 步骤1: 安装/更新依赖
    print("\n步骤1: 安装 requirements.txt 中的依赖")
    if not run_command(
        [sys.executable, "-m", "pip", "install", "-r", str(requirements_txt), "--upgrade"],
        "安装/更新依赖包"
    ):
        print("警告: 依赖安装过程中出现错误，但继续执行...")
    
    # 步骤2: 生成锁定文件
    print("\n步骤2: 生成 requirements.lock 文件")
    try:
        # 获取 pip freeze 输出
        result = subprocess.run(
            [sys.executable, "-m", "pip", "freeze"],
            check=True,
            capture_output=True,
            text=True
        )
        
        # 读取 requirements.txt 以获取项目依赖列表
        with open(requirements_txt, 'r', encoding='utf-8') as f:
            req_lines = f.readlines()
        
        # 提取项目依赖包名（去除版本号、注释等）
        project_packages = set()
        for line in req_lines:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            # 提取包名（去除版本约束、特殊字符等）
            package_name = line.split('>=')[0].split('==')[0].split('<')[0].split('~=')[0].split('[')[0].strip()
            if package_name:
                project_packages.add(package_name.lower())
        
        # 过滤冻结的输出，只保留项目相关的依赖
        lock_lines = []
        lock_lines.append("# V2.0 多智能体路由系统 - 依赖锁定文件\n")
        lock_lines.append("# 此文件包含所有直接和间接依赖的精确版本\n")
        lock_lines.append("# 生成时间: 请手动更新此时间戳\n")
        lock_lines.append("# 注意: 此文件用于生产环境部署，确保版本一致性\n")
        lock_lines.append("# 生成方法: python generate_lock.py\n\n")
        
        # 按字母顺序排序
        frozen_packages = sorted(result.stdout.strip().split('\n'))
        
        # 添加项目直接依赖（从 requirements.txt 中提取的包）
        added_packages = set()
        
        for line in frozen_packages:
            if '==' in line:
                package_name = line.split('==')[0].split('[')[0].strip().lower()
                # 检查是否是项目依赖或其子依赖
                is_project_dep = any(
                    package_name.startswith(pkg) or pkg in package_name
                    for pkg in project_packages
                )
                
                if is_project_dep and package_name not in added_packages:
                    lock_lines.append(line + '\n')
                    added_packages.add(package_name)
        
        # 写入锁定文件
        with open(requirements_lock, 'w', encoding='utf-8') as f:
            f.writelines(lock_lines)
        
        print(f"\n✅ 成功生成锁定文件: {requirements_lock}")
        print(f"📦 共包含 {len(added_packages)} 个依赖包")
        
        # 显示一些统计信息
        print("\n锁定文件预览（前10行）:")
        print("-" * 60)
        preview_lines = lock_lines[:15]
        for line in preview_lines:
            print(line.rstrip())
        if len(lock_lines) > 15:
            print(f"... （共 {len(lock_lines)} 行）")
        
    except subprocess.CalledProcessError as e:
        print(f"错误: 无法获取 pip freeze 输出")
        print(f"错误信息: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"错误: 生成锁定文件时出错: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    print("\n" + "="*60)
    print("✅ 完成！")
    print("="*60)
    print("\n如何使用锁定文件:")
    print("  1. 开发环境: pip install -r requirements.txt")
    print("  2. 生产环境: pip install -r requirements.lock")
    print("\n建议:")
    print("  - 将 requirements.lock 提交到版本控制")
    print("  - 定期更新依赖: python generate_lock.py")
    print("  - 在 CI/CD 中使用锁定文件确保一致性")


if __name__ == "__main__":
    main()

