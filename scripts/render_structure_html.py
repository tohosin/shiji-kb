#!/usr/bin/env python3
"""
生成章节结构语义关系HTML页面

使用提取的段落关系数据生成可视化页面
"""

import json
from pathlib import Path


def generate_html():
    """生成HTML"""
    project_root = Path(__file__).parent.parent
    data_file = project_root / 'kg' / 'structure' / 'data' / 'paragraph_relations_001.json'
    output_file = project_root / 'docs' / 'special' / 'structure.html'

    # 读取数据
    with open(data_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    paragraphs = data['paragraphs']
    relations = data['relations']

    # 按section分组
    sections = {}
    for para in paragraphs:
        section = para['section']
        if section not in sections:
            sections[section] = []
        sections[section].append(para)

    # 生成section节点HTML
    section_nodes_html = ''
    section_order = ['黄帝', '帝颛顼', '帝喾', '帝尧', '帝舜', '举贤任能', '五帝', '太史公']

    for section_name in section_order:
        if section_name not in sections:
            continue

        paras = sections[section_name]

        # 生成段落列表（显示所有段落）
        para_list_html = ''
        for para in paras:
            para_list_html += f'''
                    <div style="margin: 0.5em 0; padding: 0.5em; background: #fff; border-radius: 3px;">
                        <span style="color: #8B4513; font-weight: bold;">[{para["anchor"]}]</span>
                        {para["subsection"] if para["subsection"] else ""}
                        <br>
                        <span style="color: #666; font-size: 0.9em;">{para["summary"][:60]}...</span>
                    </div>'''

        # 节点HTML
        section_nodes_html += f'''
                <div class="node">
                    <div class="node-header">
                        <span class="node-title">{section_name}</span>
                        <span class="node-id">{len(paras)}段</span>
                    </div>
                    <div class="node-content">
                        {para_list_html}
                    </div>
                </div>'''

        # 添加关系箭头（简化版）
        if section_name != '太史公':
            next_section = section_order[section_order.index(section_name) + 1] if section_order.index(section_name) < len(section_order) - 1 else None
            if next_section and next_section in sections:
                label = '时序继承' if '帝' in section_name and '帝' in next_section else '时序'
                section_nodes_html += f'''
                <div class="relation-arrow">
                    ↓
                    <span class="relation-label">{label}</span>
                </div>'''

    html_content = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>章节结构语义关系 - 史记知识库</title>
    <link rel="stylesheet" href="../css/shiji-styles.css">
    <link rel="stylesheet" href="../css/entity-index.css">
    <style>
        .intro-section {{
            background: #fffef8;
            border-left: 4px solid #d4af37;
            padding: 1.5em;
            margin: 2em 0;
            line-height: 2;
            color: #555;
        }}

        .intro-section strong {{
            color: #8B4513;
        }}

        .wip-notice {{
            background: #fff8e1;
            border: 2px solid #ffc107;
            border-radius: 8px;
            padding: 1.5em;
            margin: 2em 0;
        }}

        .wip-notice h3 {{
            color: #f57c00;
            margin-top: 0;
            display: flex;
            align-items: center;
            gap: 0.5em;
        }}

        .wip-notice .icon {{
            font-size: 1.5em;
        }}

        .demo-section {{
            background: white;
            border: 1px solid #e6e0c0;
            border-radius: 8px;
            padding: 2em;
            margin: 2em 0;
        }}

        .demo-section h3 {{
            color: #8B4513;
            margin-top: 0;
            border-bottom: 2px solid #d4af37;
            padding-bottom: 0.5em;
        }}

        .relation-graph {{
            margin: 2em 0;
            padding: 1.5em;
            background: #fdfaf6;
            border-radius: 6px;
        }}

        .node {{
            background: white;
            border: 2px solid #8B4513;
            border-radius: 8px;
            padding: 1em 1.5em;
            margin: 1em 0;
            position: relative;
        }}

        .node-header {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 0.8em;
            border-bottom: 1px solid #e6e0c0;
            padding-bottom: 0.5em;
        }}

        .node-id {{
            background: #8B4513;
            color: white;
            padding: 0.3em 0.6em;
            border-radius: 4px;
            font-weight: bold;
            font-size: 0.85em;
        }}

        .node-title {{
            font-size: 1.3em;
            color: #8B4513;
            font-weight: bold;
        }}

        .node-content {{
            color: #666;
            line-height: 1.6;
        }}

        .relation-arrow {{
            text-align: center;
            color: #999;
            margin: 0.5em 0;
            font-size: 1.5em;
        }}

        .relation-label {{
            display: inline-block;
            background: #e3f2fd;
            color: #1976d2;
            padding: 0.3em 0.8em;
            border-radius: 4px;
            font-size: 0.85em;
            margin: 0 0.5em;
        }}

        .relation-types {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1em;
            margin: 2em 0;
        }}

        .relation-type {{
            background: white;
            border: 1px solid #e0e0e0;
            border-radius: 6px;
            padding: 1em;
        }}

        .relation-type-name {{
            font-weight: bold;
            color: #1976d2;
            margin-bottom: 0.5em;
        }}

        .relation-type-desc {{
            font-size: 0.9em;
            color: #666;
            line-height: 1.6;
        }}

        .skill-info {{
            background: #f3e5f5;
            border-left: 4px solid #9c27b0;
            padding: 1.5em;
            margin: 2em 0;
            border-radius: 4px;
        }}

        .skill-info h4 {{
            color: #6a1b9a;
            margin-top: 0;
        }}

        .skill-info code {{
            background: #ede7f6;
            padding: 0.2em 0.5em;
            border-radius: 3px;
            font-family: monospace;
        }}

        .stats-box {{
            background: #f0f7ff;
            border: 1px solid #b8d4f1;
            border-radius: 6px;
            padding: 1.2em;
            margin: 1.5em 0;
        }}

        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
            gap: 1em;
            margin-top: 1em;
        }}

        .stat-item {{
            text-align: center;
        }}

        .stat-number {{
            font-size: 1.8em;
            color: #2c5aa0;
            font-weight: bold;
        }}

        .stat-label {{
            color: #666;
            font-size: 0.9em;
        }}

        @media (max-width: 768px) {{
            .relation-types {{
                grid-template-columns: 1fr;
            }}
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>章节结构语义关系</h1>
        <p class="subtitle">五帝本纪段落语义关系建模（示例）</p>
    </div>

    <nav class="breadcrumb">
        <a href="../index.html">首页</a> &gt;
        <a href="special_index.html">专项索引</a> &gt;
        <span>结构语义关系</span>
    </nav>

    <div class="content">
        <!-- 工作进度说明 -->
        <div class="wip-notice">
            <h3><span class="icon">🚧</span> 正在开发中 - SKILL-02d</h3>
            <p>本页面展示的是<strong>段落语义关系建模</strong>的初步成果。目前已完成《五帝本纪》的{data['total_paragraphs']}个段落提取和{len(relations)}个关系推断。</p>
            <p><strong>计划</strong>：完成SKILL-02d（段落语义关系提取）后，将逐步完成全部130篇的语义关系标注。</p>
        </div>

        <!-- 数据统计 -->
        <div class="stats-box">
            <h3 style="margin-top: 0; color: #2c5aa0;">五帝本纪数据统计</h3>
            <div class="stats-grid">
                <div class="stat-item">
                    <div class="stat-number">{data['total_paragraphs']}</div>
                    <div class="stat-label">总段落数</div>
                </div>
                <div class="stat-item">
                    <div class="stat-number">{len([s for s in sections if s])}</div>
                    <div class="stat-label">大节数</div>
                </div>
                <div class="stat-item">
                    <div class="stat-number">{len(relations)}</div>
                    <div class="stat-label">语义关系数</div>
                </div>
                <div class="stat-item">
                    <div class="stat-number">1/130</div>
                    <div class="stat-label">完成进度</div>
                </div>
            </div>
        </div>

        <!-- 简介 -->
        <div class="intro-section">
            <h3 style="margin-top: 0;">为什么需要语义关系？</h3>
            <p>《史记》的章节结构不仅仅是物理上的小节划分，更重要的是<strong>段落之间的语义关系</strong>：</p>
            <ul style="margin-top: 1em; line-height: 2;">
                <li><strong>时序关系</strong>：事件的先后顺序（如"黄帝 → 颛顼 → 帝喾"）</li>
                <li><strong>因果关系</strong>：原因与结果的联系（如"炎帝侵陵诸侯 → 轩辕修德振兵"）</li>
                <li><strong>并列关系</strong>：同级别的平行描述（如列举五帝各自的功绩）</li>
                <li><strong>总分关系</strong>：概述与详述（如"太史公曰"对全篇的总结）</li>
                <li><strong>引用关系</strong>：对其他文献的引证（如引用《尚书》《诗经》）</li>
            </ul>
            <p style="margin-top: 1em;">这些语义关系对于<strong>知识图谱构建、事件推理、历史脉络理解</strong>至关重要。</p>
        </div>

        <!-- 语义关系类型 -->
        <div class="demo-section">
            <h3>段落语义关系类型</h3>
            <div class="relation-types">
                <div class="relation-type">
                    <div class="relation-type-name">⏱️ 时序关系 (temporal)</div>
                    <div class="relation-type-desc">描述事件发生的先后顺序，如继承关系、编年顺序</div>
                </div>
                <div class="relation-type">
                    <div class="relation-type-name">🔗 因果关系 (causal)</div>
                    <div class="relation-type-desc">原因导致结果，如战争缘起、政策后果</div>
                </div>
                <div class="relation-type">
                    <div class="relation-type-name">⚖️ 并列关系 (parallel)</div>
                    <div class="relation-type-desc">同级别的平行描述，如列举、对比</div>
                </div>
                <div class="relation-type">
                    <div class="relation-type-name">📊 总分关系 (hierarchy)</div>
                    <div class="relation-type-desc">总述与分述，如"太史公曰"总结全篇</div>
                </div>
                <div class="relation-type">
                    <div class="relation-type-name">📖 引用关系 (reference)</div>
                    <div class="relation-type-desc">引用其他文献、史料的证据支持</div>
                </div>
                <div class="relation-type">
                    <div class="relation-type-name">🔄 补充关系 (elaboration)</div>
                    <div class="relation-type-desc">对前文的进一步解释、细化</div>
                </div>
            </div>
        </div>

        <!-- 示例：五帝本纪段落结构 -->
        <div class="demo-section">
            <h3>五帝本纪段落结构与语义关系</h3>
            <p style="color: #666; margin-bottom: 2em;">基于chapter_md/001_五帝本纪.tagged.md提取的精确段落结构：</p>

            <div class="relation-graph">
                {section_nodes_html}
            </div>
        </div>

        <!-- SKILL任务说明 -->
        <div class="skill-info">
            <h4>📋 关联SKILL任务</h4>
            <p><strong>SKILL-02d</strong>: 段落语义关系提取</p>
            <p style="margin-top: 0.5em;">该SKILL将自动化提取《史记》130篇中所有段落之间的语义关系，包括：</p>
            <ul style="margin: 1em 0; line-height: 2;">
                <li>识别段落边界和主题</li>
                <li>分析段落之间的语义关系类型</li>
                <li>标注关系的置信度和证据</li>
                <li>生成结构化的关系图谱数据</li>
            </ul>
            <p>数据已存储在: <code>kg/structure/data/paragraph_relations_001.json</code></p>
        </div>

        <!-- 返回链接 -->
        <div class="intro-section">
            <h3 style="margin-top: 0;">相关资源</h3>
            <ul style="line-height: 2;">
                <li><a href="special_index.html" style="color: #8B4513;">返回专项索引</a></li>
                <li><a href="../chapters/001_五帝本纪.html" style="color: #8B4513;">查看《五帝本纪》全文</a></li>
                <li><a href="https://github.com/baojie/shiji-kb" style="color: #8B4513;" target="_blank">查看JSON数据</a></li>
            </ul>
        </div>
    </div>
</body>
</html>'''

    # 写入文件
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)

    print(f"✅ HTML已生成: {output_file}")
    print(f"   段落数: {data['total_paragraphs']}")
    print(f"   关系数: {len(relations)}")
    print(f"   大节数: {len([s for s in sections if s])}")


if __name__ == '__main__':
    generate_html()
