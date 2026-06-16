#!/usr/bin/env python3
"""
验证所有章节 HTML 文件是否正确添加了配置面板
"""

import os
from pathlib import Path


def verify_file(filepath):
    """验证单个 HTML 文件"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    checks = {
        'settings-toggle': 'settings-toggle' in content,
        'settings-panel': 'settings-panel' in content,
        'syntax-highlight': 'syntax-highlight' in content,
        'settings-panel.js': 'settings-panel.js' in content,
    }

    return all(checks.values()), checks


def main():
    # 获取项目根目录
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    chapters_dir = project_root / 'docs' / 'chapters'

    if not chapters_dir.exists():
        print(f"错误：目录不存在 {chapters_dir}")
        return

    # 获取所有 HTML 文件
    html_files = sorted(chapters_dir.glob('*.html'))

    if not html_files:
        print("未找到 HTML 文件")
        return

    print(f"验证 {len(html_files)} 个 HTML 文件...\n")

    # 验证每个文件
    all_valid = True
    invalid_files = []

    for filepath in html_files:
        valid, checks = verify_file(filepath)
        if not valid:
            all_valid = False
            invalid_files.append((filepath.name, checks))
            print(f"✗ {filepath.name}")
            for key, value in checks.items():
                if not value:
                    print(f"  缺失: {key}")
        else:
            print(f"✓ {filepath.name}")

    print("\n" + "=" * 60)
    if all_valid:
        print(f"✓ 验证通过！所有 {len(html_files)} 个文件都已正确添加配置面板")
    else:
        print(f"✗ 发现问题！{len(invalid_files)} 个文件未正确添加配置面板")
        print("\n有问题的文件：")
        for filename, checks in invalid_files:
            print(f"  - {filename}")


if __name__ == '__main__':
    main()
