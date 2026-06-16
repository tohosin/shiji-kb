#!/usr/bin/env python3
"""
从史记正义和集解中提取特殊读音注释（改进版）
重点提取明确的 "X音Y" 形式，过滤噪音
"""
import re
import json
from collections import Counter, defaultdict
from pathlib import Path

def extract_sound_annotations(file_path, source_name):
    """提取X音Y格式的读音注释"""
    pronunciation_dict = {}

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 改进的模式：更精确地匹配 "X音Y" 格式
    # 要求：汉字+音+汉字，前后有合理边界
    pattern = r'([一-龥]{1,3})音([一-龥]{1,3})'

    matches = re.findall(pattern, content)

    for word, sound in matches:
        # 过滤明显的噪音
        if word in ['音', '又', '并', '上', '下', '如', '曰'] or sound in ['音', '又', '并']:
            continue

        if word not in pronunciation_dict:
            pronunciation_dict[word] = {
                'sound': sound,
                'source': source_name,
                'count': 1
            }
        else:
            pronunciation_dict[word]['count'] += 1

    return pronunciation_dict

def extract_special_patterns(file_path, source_name):
    """提取特殊读音模式"""
    results = []

    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    for i, line in enumerate(lines):
        # 模式1: 氏音支（月氏）
        if '氏音支' in line:
            results.append({'pattern': '氏音支', 'context': line.strip()[:100], 'line': i+1})

        # 模式2: X音瞒（头曼音瞒）
        matches = re.finditer(r'([一-龥]{2,3})音([瞒滑掸]{1})', line)
        for m in matches:
            results.append({
                'word': m.group(1),
                'sound': m.group(2),
                'pattern': f'{m.group(1)}音{m.group(2)}',
                'context': line[max(0, m.start()-20):min(len(line), m.end()+20)].strip(),
                'line': i+1,
                'source': source_name
            })

        # 模式3: 读如X
        matches = re.finditer(r'([一-龥]{1,3})读如([一-龥]{1,3})', line)
        for m in matches:
            results.append({
                'word': m.group(1),
                'sound': m.group(2),
                'pattern': f'{m.group(1)}读如{m.group(2)}',
                'context': line[max(0, m.start()-20):min(len(line), m.end()+20)].strip(),
                'line': i+1,
                'source': source_name
            })

        # 模式4: X读曰Y
        matches = re.finditer(r'([一-龥]{1,3})读曰([一-龥]{1,3})', line)
        for m in matches:
            results.append({
                'word': m.group(1),
                'sound': m.group(2),
                'pattern': f'{m.group(1)}读曰{m.group(2)}',
                'context': line[max(0, m.start()-20):min(len(line), m.end()+20)].strip(),
                'line': i+1,
                'source': source_name
            })

    return results

def main():
    base_dir = Path('/home/baojie/work/knowledge/shiji-kb')
    zhengyi_file = base_dir / 'archive' / '史记正义.txt'
    jijie_file = base_dir / 'archive' / '史记集解.txt'

    print("=" * 70)
    print("提取史记注释中的特殊读音（改进版）")
    print("=" * 70)

    # 提取基本读音
    zhengyi_sounds = extract_sound_annotations(zhengyi_file, '史记正义')
    jijie_sounds = extract_sound_annotations(jijie_file, '史记集解')

    # 合并两个来源
    all_sounds = {}
    for word, info in zhengyi_sounds.items():
        all_sounds[word] = info

    for word, info in jijie_sounds.items():
        if word in all_sounds:
            all_sounds[word]['count'] += info['count']
            all_sounds[word]['source'] += ', 史记集解'
        else:
            all_sounds[word] = info

    # 提取特殊模式
    zhengyi_special = extract_special_patterns(zhengyi_file, '史记正义')
    jijie_special = extract_special_patterns(jijie_file, '史记集解')

    print(f"\n史记正义提取: {len(zhengyi_sounds)} 个词汇")
    print(f"史记集解提取: {len(jijie_sounds)} 个词汇")
    print(f"合并后总计: {len(all_sounds)} 个词汇")
    print(f"特殊模式: {len(zhengyi_special + jijie_special)} 条")

    # 按出现频率排序
    sorted_sounds = sorted(all_sounds.items(), key=lambda x: x[1]['count'], reverse=True)

    print("\n" + "=" * 70)
    print("高频特殊读音词汇 (出现2次及以上)")
    print("=" * 70)
    for word, info in sorted_sounds:
        if info['count'] >= 2:
            print(f"  {word} → 音{info['sound']} ({info['count']}次) [{info['source']}]")

    print("\n" + "=" * 70)
    print("特殊读音模式示例")
    print("=" * 70)
    for item in (zhengyi_special + jijie_special)[:20]:
        if 'word' in item:
            print(f"  {item['word']}音{item['sound']} - {item['context'][:50]}...")
        else:
            print(f"  {item['pattern']} - {item['context'][:50]}...")

    # 保存结果
    output_file = base_dir / 'temp_pronunciation_v2.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            'all_sounds': {k: v for k, v in sorted_sounds[:200]},  # 前200个
            'special_patterns': zhengyi_special + jijie_special
        }, f, ensure_ascii=False, indent=2)

    print(f"\n详细数据已保存到: {output_file}")

if __name__ == '__main__':
    main()
