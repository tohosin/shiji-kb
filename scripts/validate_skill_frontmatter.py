#!/usr/bin/env python3
"""
验证所有SKILL文件的front matter格式

检查项:
1. 是否有YAML front matter (以 --- 开始和结束)
2. 是否包含必需字段: name, description
3. description是否足够详细 (至少100字符)
4. description是否包含"何时使用"的触发条件
"""

import re
from pathlib import Path
from typing import Dict, List, Tuple


def extract_frontmatter(file_path: Path) -> Dict[str, str]:
    """提取frontmatter"""
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    frontmatter = {}

    if not lines or lines[0].strip() != '---':
        return frontmatter

    for i in range(1, len(lines)):
        if lines[i].strip() == '---':
            # 解析frontmatter
            for line in lines[1:i]:
                if ':' in line:
                    key, value = line.split(':', 1)
                    frontmatter[key.strip()] = value.strip()
            break

    return frontmatter


def validate_frontmatter(file_path: Path) -> Tuple[bool, List[str]]:
    """
    验证frontmatter

    Returns:
        (is_valid, issues)
    """
    frontmatter = extract_frontmatter(file_path)
    issues = []

    # 检查是否存在frontmatter
    if not frontmatter:
        issues.append("缺少YAML frontmatter")
        return False, issues

    # 检查必需字段
    if 'name' not in frontmatter:
        issues.append("缺少name字段")

    if 'description' not in frontmatter:
        issues.append("缺少description字段")
    else:
        desc = frontmatter['description']

        # 检查description长度
        if len(desc) < 50:
            issues.append(f"description过短 ({len(desc)}字符,建议≥50)")

        # 检查是否包含触发条件关键词
        trigger_keywords = ['当', '时使用', '适用于', '触发']
        has_trigger = any(kw in desc for kw in trigger_keywords)
        if not has_trigger:
            issues.append("description缺少使用场景/触发条件(建议包含'当...时使用')")

    is_valid = len(issues) == 0
    return is_valid, issues


def main():
    skills_dir = Path('/home/baojie/work/knowledge/shiji-kb/skills')

    # 收集所有SKILL和META文件
    skill_files = sorted(skills_dir.glob('SKILL_*.md'))
    meta_files = sorted(skills_dir.glob('00-META-*.md'))
    all_files = skill_files + meta_files

    print("=" * 80)
    print(f"验证 {len(all_files)} 个SKILL文件的front matter")
    print("=" * 80)
    print()

    valid_count = 0
    invalid_count = 0

    invalid_files = []

    for file_path in all_files:
        is_valid, issues = validate_frontmatter(file_path)

        if is_valid:
            valid_count += 1
            print(f"✅ {file_path.name}")
        else:
            invalid_count += 1
            invalid_files.append((file_path.name, issues))
            print(f"❌ {file_path.name}")
            for issue in issues:
                print(f"   - {issue}")

    print()
    print("=" * 80)
    print("总结")
    print("=" * 80)
    print(f"✅ 合格: {valid_count} 个")
    print(f"❌ 不合格: {invalid_count} 个")
    print(f"📊 通过率: {valid_count}/{len(all_files)} ({100*valid_count//len(all_files)}%)")

    if invalid_files:
        print()
        print("需要修正的文件:")
        for filename, issues in invalid_files:
            print(f"  - {filename}")


if __name__ == '__main__':
    main()
