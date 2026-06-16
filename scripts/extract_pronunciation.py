#!/usr/bin/env python3
"""
从史记正义和集解中提取特殊读音注释
"""
import re
import json
from collections import Counter, defaultdict
from pathlib import Path

# 定义读音模式
PRONUNCIATION_PATTERNS = [
    # X音Y - 最常见的读音注释
    (r'(\S{1,3})音(\S{1,4})', 'X音Y'),
    # X读Y - 读作某音
    (r'(\S{1,3})读([如曰])(\S{1,4})', 'X读Y'),
    # X反 - 反切注音
    (r'(\S)(\S)反', '反切'),
    # 又音Y - 多音字
    (r'又音(\S{1,3})', '又音'),
]

def extract_pronunciations(file_path):
    """从文件中提取读音注释"""
    results = defaultdict(list)

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
        lines = content.split('\n')

    for line_no, line in enumerate(lines, 1):
        # 跳过注释说明段落
        if '论音例' in line or '音字例' in line:
            continue

        for pattern, pattern_name in PRONUNCIATION_PATTERNS:
            matches = re.finditer(pattern, line)
            for match in matches:
                # 提取上下文
                start = max(0, match.start() - 20)
                end = min(len(line), match.end() + 20)
                context = line[start:end]

                results[pattern_name].append({
                    'match': match.group(0),
                    'groups': match.groups(),
                    'context': context,
                    'line_no': line_no,
                    'line': line[:200]  # 限制长度
                })

    return results

def analyze_word_frequency(pronunciation_data):
    """分析词汇出现频率"""
    word_counter = Counter()

    for pattern_name, matches in pronunciation_data.items():
        if pattern_name == 'X音Y':
            for match_info in matches:
                word = match_info['groups'][0]
                # 过滤掉一些常见字
                if word and len(word) <= 3:
                    word_counter[word] += 1

    return word_counter

def main():
    base_dir = Path('/home/baojie/work/knowledge/shiji-kb')
    zhengyi_file = base_dir / 'archive' / '史记正义.txt'
    jijie_file = base_dir / 'archive' / '史记集解.txt'

    print("=" * 60)
    print("提取史记正义中的读音注释")
    print("=" * 60)
    zhengyi_data = extract_pronunciations(zhengyi_file)

    print("\n【史记正义】读音注释统计：")
    for pattern_name, matches in zhengyi_data.items():
        print(f"  {pattern_name}: {len(matches)} 条")

    print("\n" + "=" * 60)
    print("提取史记集解中的读音注释")
    print("=" * 60)
    jijie_data = extract_pronunciations(jijie_file)

    print("\n【史记集解】读音注释统计：")
    for pattern_name, matches in jijie_data.items():
        print(f"  {pattern_name}: {len(matches)} 条")

    # 分析X音Y模式中的高频词
    print("\n" + "=" * 60)
    print("史记正义 - 高频特殊读音词汇 (Top 50)")
    print("=" * 60)
    zhengyi_freq = analyze_word_frequency(zhengyi_data)
    for word, count in zhengyi_freq.most_common(50):
        print(f"  {word}: {count} 次")

    print("\n" + "=" * 60)
    print("史记集解 - 高频特殊读音词汇 (Top 30)")
    print("=" * 60)
    jijie_freq = analyze_word_frequency(jijie_data)
    for word, count in jijie_freq.most_common(30):
        print(f"  {word}: {count} 次")

    # 保存详细数据
    output_file = base_dir / 'temp_pronunciation_extraction.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            'zhengyi': {k: v[:100] for k, v in zhengyi_data.items()},  # 只保存前100条
            'jijie': {k: v[:100] for k, v in jijie_data.items()},
            'zhengyi_freq': dict(zhengyi_freq.most_common(100)),
            'jijie_freq': dict(jijie_freq.most_common(100))
        }, f, ensure_ascii=False, indent=2)

    print(f"\n详细数据已保存到: {output_file}")

if __name__ == '__main__':
    main()
