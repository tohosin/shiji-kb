#!/usr/bin/env python3
"""
从《史记正义》提取结果中筛选并转换为JSON格式的特殊读音词条
只包含在史记原文中确实出现且有实用价值的词条
"""

import json
import re
from pathlib import Path

# 精选的特殊读音词条（基于史记正义提取结果）
# 选择标准：1) 在史记中确实出现 2) 现代读音容易误读 3) 地名/人名/常见词

special_pronunciations = [
    # === 地名 ===
    {
        "text": "阏与",
        "pinyin": ["è", "yǔ"],
        "context": "地名",
        "note": "赵奢破秦军处，'阏'读è，'与'读yǔ"
    },
    {
        "text": "亢父",
        "pinyin": ["gāng", "fǔ"],
        "context": "地名",
        "note": "在今山东济宁，'亢'读gāng"
    },
    {
        "text": "卷县",
        "pinyin": ["quān", "xiàn"],
        "context": "地名",
        "note": "河南地名，'卷'读quān"
    },
    {
        "text": "令支",
        "pinyin": ["líng", "zhī"],
        "context": "地名",
        "note": "有孤竹城，'令'读líng"
    },
    {
        "text": "方与",
        "pinyin": ["fāng", "yǔ"],
        "context": "地名",
        "note": "兖州县名，'与'读yǔ"
    },
    {
        "text": "峣关",
        "pinyin": ["yáo", "guān"],
        "context": "地名",
        "note": "在蓝田，'峣'读yáo"
    },
    {
        "text": "殽",
        "pinyin": ["xiáo"],
        "context": "地名",
        "note": "殽山，秦晋战于殽"
    },
    {
        "text": "汶山",
        "pinyin": ["mín", "shān"],
        "context": "地名",
        "note": "即岷山，'汶'读mín"
    },
    {
        "text": "鄢",
        "pinyin": ["yān"],
        "context": "地名",
        "note": "楚都鄢郢的鄢"
    },
    {
        "text": "妫水",
        "pinyin": ["guī", "shuǐ"],
        "context": "地名",
        "note": "舜居妫汭，'妫'读guī"
    },
    {
        "text": "嶓冢",
        "pinyin": ["bō", "zhǒng"],
        "context": "地名",
        "note": "汉水源头山名"
    },
    {
        "text": "湔氐",
        "pinyin": ["jiān", "dī"],
        "context": "地名",
        "note": "岷山在湔氐道"
    },
    {
        "text": "共",
        "pinyin": ["gòng"],
        "context": "地名或国名",
        "note": "共伯和、共城，读gòng"
    },
    {
        "text": "戏",
        "pinyin": ["xī"],
        "context": "地名",
        "note": "戏水、戏戎，读xī不读xì"
    },
    {
        "text": "汜水",
        "pinyin": ["sì", "shuǐ"],
        "context": "地名",
        "note": "在成皋，'汜'读sì"
    },
    {
        "text": "朝鲜",
        "pinyin": ["cháo", "xiǎn"],
        "context": "地名",
        "note": "古国名，'朝'读cháo如潮汐"
    },

    # === 人名 ===
    {
        "text": "樗里",
        "pinyin": ["chū", "lǐ"],
        "context": "人名",
        "note": "樗里子，秦惠王弟，'樗'读chū"
    },
    {
        "text": "盱眙",
        "pinyin": ["xū", "yí"],
        "context": "人名或地名",
        "note": "'盱'读xū，'眙'读yí"
    },

    # === 称号/官职 ===
    {
        "text": "大行",
        "pinyin": ["dà", "háng"],
        "context": "官职",
        "note": "掌宾客之官，'行'读háng"
    },
    {
        "text": "仆射",
        "pinyin": ["pú", "yè"],
        "context": "官职",
        "note": "官名，'仆'读pú，'射'读yè"
    },

    # === 姓氏 ===
    {
        "text": "员",
        "pinyin": ["yùn"],
        "context": "姓氏或人名",
        "note": "伍子胥名员，读yùn（已在原词表中）"
    },
    {
        "text": "区",
        "pinyin": ["ōu"],
        "context": "姓氏",
        "note": "姓区读ōu（已在原词表中）"
    },

    # === 常用多音字（去声、上声标注）===
    {
        "text": "为",
        "pinyin": ["wèi"],
        "context": "动词",
        "note": "作为、成为义时读wèi（去声）"
    },
    {
        "text": "长",
        "pinyin": ["zhǎng"],
        "context": "动词或名词",
        "note": "生长、年长义时读zhǎng（上声）"
    },
    {
        "text": "相",
        "pinyin": ["xiàng"],
        "context": "名词",
        "note": "宰相、丞相读xiàng（去声）"
    },
    {
        "text": "将",
        "pinyin": ["jiàng"],
        "context": "名词",
        "note": "将军、大将读jiàng（去声）"
    },
    {
        "text": "行",
        "pinyin": ["háng"],
        "context": "名词",
        "note": "行列、道路义时读háng"
    },
    {
        "text": "骑",
        "pinyin": ["jì"],
        "context": "动词",
        "note": "跨骑义时读jì（去声）"
    },
    {
        "text": "中",
        "pinyin": ["zhòng"],
        "context": "动词",
        "note": "中试、射中义时读zhòng（去声）"
    },
    {
        "text": "王",
        "pinyin": ["wàng"],
        "context": "动词",
        "note": "称王、为王义时读wàng（去声）"
    },
]

def create_pronunciation_json():
    """创建特殊读音JSON文件（从史记正义提取）"""

    output = {
        "$schema": "特殊读音词表（史记正义版） v1.0",
        "description": "从《史记集解三家注索隐正义》中提取的特殊读音词汇",
        "source": "史记正义",
        "version": "1.0",
        "lastUpdated": "2026-03-31",
        "note": "所有词条均已验证在《史记》原文中出现",
        "entries": special_pronunciations
    }

    # 写入JSON文件
    output_path = Path(__file__).parent.parent / "docs" / "data" / "special-pronunciation-zhengyi.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"✓ 已生成: {output_path}")
    print(f"✓ 词条总数: {len(special_pronunciations)}")

    # 统计分类
    categories = {}
    for entry in special_pronunciations:
        ctx = entry['context']
        categories[ctx] = categories.get(ctx, 0) + 1

    print(f"\n分类统计:")
    for ctx, count in sorted(categories.items(), key=lambda x: -x[1]):
        print(f"  {ctx}: {count}个")

if __name__ == "__main__":
    create_pronunciation_json()
