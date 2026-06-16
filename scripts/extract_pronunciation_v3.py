#!/usr/bin/env python3
"""
从史记正义和集解中提取特殊读音注释（第三版）
改进策略：
1. 排除学者引用格式（如"徐广曰音"、"韦昭曰音"）
2. 只保留多字词的读音注释
3. 重点提取"X音Y"中X是地名、人名、官职等实体的情况
"""
import re
import json
from pathlib import Path
from collections import defaultdict

def extract_clean_pronunciations(file_path, source_name):
    """提取干净的读音注释，排除学者引用"""
    pronunciation_dict = {}

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 关键改进：寻找学者注释中的音注
    # 格式：【学者曰...音...】或 学者曰音...
    scholar_pattern = r'【([^】]{0,20})曰([^】]{0,50})音([一-龥]{1,3})([^】]{0,20})】'

    results = []
    for match in re.finditer(scholar_pattern, content):
        scholar = match.group(1)
        before = match.group(2)
        sound = match.group(3)
        after = match.group(4)

        # 查找被注音的词
        # 通常在"音"字之前
        word_match = re.search(r'([一-龥]{2,6})$', before)
        if word_match:
            word = word_match.group(1)

            # 过滤常见虚词和格式词
            if word in ['也音', '曰音', '一作', '或作', '徐广曰', '韦昭曰', '服防曰']:
                continue

            context = before[-20:] + '音' + sound + after[:20]

            if word not in pronunciation_dict:
                pronunciation_dict[word] = {
                    'word': word,
                    'sound': sound,
                    'scholar': scholar,
                    'context': context,
                    'source': source_name,
                    'count': 1
                }
            else:
                pronunciation_dict[word]['count'] += 1

    return pronunciation_dict

def extract_special_name_pronunciations(file_path, source_name):
    """提取特定格式的专名读音
    如：头曼【韦昭曰音瞒】
    """
    results = []

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 模式：专名后跟注释
    # 如：头曼【韦昭曰音瞒】
    pattern = r'([一-龥]{2,4})【([^】]{0,15})曰音([一-龥]{1,3})】'

    for match in re.finditer(pattern, content):
        word = match.group(1)
        scholar = match.group(2)
        sound = match.group(3)

        # 获取上下文
        start = max(0, match.start() - 30)
        end = min(len(content), match.end() + 30)
        context = content[start:end]

        results.append({
            'word': word,
            'sound': sound,
            'scholar': scholar,
            'pattern': f'{word}【{scholar}曰音{sound}】',
            'context': context,
            'source': source_name
        })

    return results

def main():
    base_dir = Path('/home/baojie/work/knowledge/shiji-kb')
    zhengyi_file = base_dir / 'archive' / '史记正义.txt'
    jijie_file = base_dir / 'archive' / '史记集解.txt'

    print("=" * 70)
    print("史记特殊读音提取（第三版 - 清洗版）")
    print("=" * 70)

    # 方法1：从学者注释中提取
    print("\n【方法1】从学者注释格式中提取...")
    zhengyi_dict = extract_clean_pronunciations(zhengyi_file, '史记正义')
    jijie_dict = extract_clean_pronunciations(jijie_file, '史记集解')

    print(f"史记正义: {len(zhengyi_dict)} 个词")
    print(f"史记集解: {len(jijie_dict)} 个词")

    # 合并
    all_pronunciations = {}
    for word, info in zhengyi_dict.items():
        all_pronunciations[word] = info

    for word, info in jijie_dict.items():
        if word in all_pronunciations:
            all_pronunciations[word]['count'] += info['count']
            all_pronunciations[word]['source'] += ', 史记集解'
        else:
            all_pronunciations[word] = info

    print(f"合并后: {len(all_pronunciations)} 个词")

    # 方法2：特殊格式提取
    print("\n【方法2】提取特殊专名格式...")
    zhengyi_special = extract_special_name_pronunciations(zhengyi_file, '史记正义')
    jijie_special = extract_special_name_pronunciations(jijie_file, '史记集解')

    print(f"史记正义: {len(zhengyi_special)} 条")
    print(f"史记集解: {len(jijie_special)} 条")

    # 按出现频率排序
    sorted_items = sorted(all_pronunciations.items(),
                         key=lambda x: x[1]['count'],
                         reverse=True)

    print("\n" + "=" * 70)
    print("清洗后的读音词汇 Top 50")
    print("=" * 70)
    for i, (word, info) in enumerate(sorted_items[:50], 1):
        print(f"{i:2d}. {word} → 音{info['sound']} ({info['count']}次) "
              f"[{info['scholar']}] [{info['source']}]")
        print(f"    {info['context'][:60]}...")

    print("\n" + "=" * 70)
    print("特殊专名格式 示例")
    print("=" * 70)
    all_special = zhengyi_special + jijie_special
    for i, item in enumerate(all_special[:20], 1):
        print(f"{i:2d}. {item['word']} 音{item['sound']} - {item['scholar']}")
        print(f"    {item['context'][:60]}...")

    # 保存
    output_file = base_dir / 'temp_pronunciation_v3.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            'pronunciation_dict': {k: v for k, v in sorted_items[:100]},
            'special_names': all_special
        }, f, ensure_ascii=False, indent=2)

    print(f"\n数据已保存: {output_file}")

if __name__ == '__main__':
    main()
