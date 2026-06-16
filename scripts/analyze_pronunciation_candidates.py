#!/usr/bin/env python3
"""
分析特殊读音候选词的综合脚本
- 读取提取结果
- 在史记原文中验证出现频率
- 与现有词典比对
- 分类并生成最终报告
"""
import re
import json
from pathlib import Path
from collections import defaultdict, Counter

def load_existing_dict(dict_path):
    """加载现有特殊读音词典"""
    with open(dict_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    existing_words = set()
    existing_data = {}

    for entry in data.get('entries', []):
        text = entry['text']
        existing_words.add(text)
        existing_data[text] = entry

    return existing_words, existing_data

def load_extraction_results(json_path):
    """加载提取结果"""
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data

def count_occurrences_in_text(word, text_files):
    """统计词汇在所有史记原文中的出现次数"""
    total_count = 0
    occurrences = []

    for text_file in text_files:
        if not text_file.exists():
            continue

        with open(text_file, 'r', encoding='utf-8') as f:
            content = f.read()

        count = content.count(word)
        if count > 0:
            total_count += count
            occurrences.append({
                'file': text_file.name,
                'count': count
            })

    return total_count, occurrences

def categorize_word(word, sound, context):
    """根据词汇特征分类"""
    # 匈奴相关
    if any(x in context for x in ['匈奴', '单于', '冒顿', '头曼']):
        return '人名_匈奴'

    # 西域国名
    if any(x in context for x in ['西域', '国名', '月氏', '大宛']):
        return '地名_西域'

    # 其他人名特征
    if '音' in context and len(word) >= 2:
        # 检查是否是人名模式
        if any(x in word for x in ['曼', '顿', '氏', '其']):
            return '人名'

    # 地名特征
    if any(x in word for x in ['山', '水', '县', '郡', '关', '阳', '阴']):
        return '地名'

    # 官职特征
    if any(x in word for x in ['射', '行', '尉']):
        return '官职名'

    # 单字可能是姓氏
    if len(word) == 1:
        return '姓氏'

    return '其他'

def analyze_special_patterns(special_patterns):
    """分析特殊模式提取的结果"""
    results = []

    for item in special_patterns:
        if 'word' in item:
            results.append({
                'word': item['word'],
                'sound': item['sound'],
                'pattern': item['pattern'],
                'context': item['context'],
                'source': item['source']
            })

    return results

def main():
    base_dir = Path('/home/baojie/work/knowledge/shiji-kb')

    # 文件路径
    extraction_file = base_dir / 'temp_pronunciation_v2.json'
    dict_file = base_dir / 'docs' / 'data' / 'special-pronunciation.json'
    archive_dir = base_dir / 'archive'

    # 获取所有史记原文文件
    shiji_files = list(archive_dir.glob('史记*.txt'))
    # 排除注释文件
    shiji_files = [f for f in shiji_files if '正义' not in f.name and '集解' not in f.name and '索隐' not in f.name]

    print("=" * 80)
    print("史记特殊读音候选词综合分析")
    print("=" * 80)

    # 1. 加载现有词典
    print("\n【步骤1】加载现有词典...")
    existing_words, existing_data = load_existing_dict(dict_file)
    print(f"现有词典包含: {len(existing_words)} 个词条")

    # 2. 加载提取结果
    print("\n【步骤2】加载提取结果...")
    extraction_data = load_extraction_results(extraction_file)
    all_sounds = extraction_data.get('all_sounds', {})
    special_patterns = extraction_data.get('special_patterns', [])

    print(f"提取到 {len(all_sounds)} 个基本读音词条")
    print(f"提取到 {len(special_patterns)} 个特殊模式")

    # 3. 分析特殊模式（优先级更高）
    print("\n【步骤3】分析特殊模式提取的词汇...")
    pattern_results = analyze_special_patterns(special_patterns)

    # 去重并统计
    pattern_words = {}
    for item in pattern_results:
        word = item['word']
        if word not in pattern_words:
            pattern_words[word] = {
                'sound': item['sound'],
                'pattern': item['pattern'],
                'contexts': [item['context']],
                'sources': [item['source']],
                'count': 1
            }
        else:
            pattern_words[word]['count'] += 1
            if item['context'] not in pattern_words[word]['contexts']:
                pattern_words[word]['contexts'].append(item['context'])

    print(f"特殊模式去重后: {len(pattern_words)} 个词汇")

    # 4. 在史记原文中验证出现频率
    print("\n【步骤4】在史记原文中验证候选词频率...")
    print(f"将扫描 {len(shiji_files)} 个史记原文文件")

    candidates = []
    verified_count = 0

    # 合并所有候选词
    all_candidates = {}

    # 先处理特殊模式提取的（优先级高）
    for word, info in pattern_words.items():
        all_candidates[word] = {
            'sound': info['sound'],
            'source': ', '.join(info['sources']),
            'contexts': info['contexts'],
            'extraction_count': info['count'],
            'is_pattern': True
        }

    # 再处理基本音注提取的
    for word, info in all_sounds.items():
        if word not in all_candidates:
            all_candidates[word] = {
                'sound': info['sound'],
                'source': info['source'],
                'contexts': [],
                'extraction_count': info['count'],
                'is_pattern': False
            }

    print(f"合并后共 {len(all_candidates)} 个候选词")
    print("开始频率验证（这可能需要几分钟）...")

    for i, (word, info) in enumerate(all_candidates.items()):
        if (i + 1) % 100 == 0:
            print(f"  已处理 {i + 1}/{len(all_candidates)} 个词...")

        # 在原文中计数
        total_count, occurrences = count_occurrences_in_text(word, shiji_files)

        # 只保留出现3次及以上的
        if total_count >= 3:
            verified_count += 1

            # 判断是否已在词典中
            in_existing = word in existing_words

            candidate = {
                'word': word,
                'sound': info['sound'],
                'source': info['source'],
                'occurrences': total_count,
                'extraction_count': info['extraction_count'],
                'is_pattern': info['is_pattern'],
                'in_existing': in_existing,
                'contexts': info['contexts'][:3] if info['contexts'] else [],  # 最多保留3个上下文
                'category': categorize_word(word, info['sound'], ' '.join(info['contexts'][:3]) if info['contexts'] else '')
            }

            candidates.append(candidate)

    print(f"验证完成: {verified_count} 个词汇出现≥3次")

    # 5. 分类统计
    print("\n【步骤5】分类统计...")
    by_category = defaultdict(list)
    new_candidates = []
    existing_candidates = []

    for candidate in candidates:
        by_category[candidate['category']].append(candidate)

        if candidate['in_existing']:
            existing_candidates.append(candidate)
        else:
            new_candidates.append(candidate)

    print(f"新候选词: {len(new_candidates)} 个")
    print(f"已在词典: {len(existing_candidates)} 个")

    # 6. 生成报告
    print("\n【步骤6】生成综合报告...")

    # 按出现频率排序
    candidates.sort(key=lambda x: (x['occurrences'], x['extraction_count']), reverse=True)

    # 输出报告
    output_file = base_dir / 'temp_pronunciation_analysis_report.json'
    report = {
        'metadata': {
            'total_candidates': len(candidates),
            'new_candidates': len(new_candidates),
            'existing_in_dict': len(existing_candidates),
            'categories': {cat: len(words) for cat, words in by_category.items()},
            'extraction_sources': {
                'pattern_based': len([c for c in candidates if c['is_pattern']]),
                'basic_annotation': len([c for c in candidates if not c['is_pattern']])
            }
        },
        'new_candidates_by_category': {},
        'existing_in_dict': existing_candidates,
        'all_candidates_ranked': candidates[:200]  # 前200个
    }

    # 按类别整理新候选词
    for category, words in by_category.items():
        new_in_category = [w for w in words if not w['in_existing']]
        if new_in_category:
            # 按频率排序
            new_in_category.sort(key=lambda x: x['occurrences'], reverse=True)
            report['new_candidates_by_category'][category] = new_in_category

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print(f"完整报告已保存: {output_file}")

    # 7. 打印摘要
    print("\n" + "=" * 80)
    print("【分析摘要】")
    print("=" * 80)

    print(f"\n总候选词数: {len(candidates)} 个（出现≥3次）")
    print(f"新候选词: {len(new_candidates)} 个")
    print(f"已在词典: {len(existing_candidates)} 个")

    print("\n按类别分布:")
    for category in sorted(by_category.keys()):
        words = by_category[category]
        new_count = len([w for w in words if not w['in_existing']])
        print(f"  {category}: {len(words)} 个（新: {new_count}）")

    print("\n" + "=" * 80)
    print("【高优先级新候选词 Top 20】")
    print("=" * 80)

    new_candidates_sorted = sorted(new_candidates, key=lambda x: x['occurrences'], reverse=True)
    for i, candidate in enumerate(new_candidates_sorted[:20], 1):
        print(f"{i:2d}. {candidate['word']} → 音{candidate['sound']} "
              f"(出现{candidate['occurrences']}次, 提取{candidate['extraction_count']}次) "
              f"[{candidate['category']}] "
              f"{'[特殊模式]' if candidate['is_pattern'] else ''}")
        if candidate['contexts']:
            print(f"    上下文: {candidate['contexts'][0][:60]}...")

    print("\n" + "=" * 80)
    print("【已在词典中的高频词 Top 10】")
    print("=" * 80)

    existing_sorted = sorted(existing_candidates, key=lambda x: x['occurrences'], reverse=True)
    for i, candidate in enumerate(existing_sorted[:10], 1):
        print(f"{i:2d}. {candidate['word']} → 音{candidate['sound']} "
              f"(出现{candidate['occurrences']}次) "
              f"[已收录]")

    print("\n" + "=" * 80)
    print(f"详细数据请查看: {output_file}")
    print("=" * 80)

if __name__ == '__main__':
    main()
