# 语义标签处理模块使用说明

## 概述

`semantic_tags.py` 提供了史记知识库中语义标签的统一处理功能，确保所有HTML生成脚本使用相同的标签标准。

## 语义标签标准（2024版）

| 标签 | 类型 | 说明 | 示例 |
|------|------|------|------|
| `@` | 人名 | 人物名称 | `〖@武王〗` |
| `%` | 时间 | 时间表达 | `〖%十一年〗` |
| `#` | 地名 | 地理位置 | `〖#洛邑〗` |
| `$` | 官职 | 官职职位 | `〖$太史公〗` |
| `&` | 战争 | 战争/事件名 | `〖&牧野之战〗` |
| `;` | 上文提及 | 上文已提及的人名 | `〖;武王〗` |

### 消歧格式

当显示名与规范名不同时使用：
```
〖@姬发|周武王〗  → 显示"姬发"
```

## 主要功能

### 1. 移除标签（用于纯文本显示）

```python
from semantic_tags import remove_semantic_tags, clean_text

# 基本用法
text = "〖@武王〗伐〖#纣〗"
result = remove_semantic_tags(text)
# 结果: "武王伐纣"

# 快捷方式（自动处理旧版标签）
result = clean_text(text)
```

### 2. 转换为HTML（用于带高亮显示）

```python
from semantic_tags import render_tags_to_html, html_with_highlights

# 基本用法
text = "〖@武王〗伐〖#纣〗"
html = render_tags_to_html(text, normalize_legacy=True)
# 结果: '<span class="entity person" title="人名">武王</span>伐<span class="entity place" title="地名">纣</span>'

# 快捷方式
html = html_with_highlights(text)
```

### 3. 提取实体

```python
from semantic_tags import extract_entities

text = "〖@武王〗伐〖#朝歌〗"
entities = extract_entities(text)
# 结果: {'person': ['武王'], 'place': ['朝歌']}
```

### 4. 获取CSS样式

```python
from semantic_tags import get_entity_css_styles

# 在HTML模板中使用
css = get_entity_css_styles()
```

## 旧版标签自动转换

模块会自动将旧版标签符号转换为新标准：

| 旧版 | 新版 | 说明 |
|------|------|------|
| `=` | `#` | 地名 |
| `^` | `$` | 官职 |
| 其他非标准符号 | `~` | 归类为"其他" |

## 在渲染脚本中使用

### 示例：render_xxx_html.py

```python
#!/usr/bin/env python3
import json
from pathlib import Path
import sys

# 导入统一模块
sys.path.insert(0, str(Path(__file__).parent))
from semantic_tags import render_tags_to_html, remove_semantic_tags

def render_entity_tags(text):
    """将实体标注转换为HTML（保留高亮）"""
    return render_tags_to_html(text, normalize_legacy=True)

def clean_text_for_display(text):
    """移除标签（纯文本显示）"""
    return remove_semantic_tags(text, normalize_legacy=True)
```

### CSS样式（在HTML模板中）

```css
/* 使用统一的实体标注样式 */
.entity {
    font-weight: 500;
    border-bottom: 1px dotted;
    cursor: help;
}

.entity.person { color: #c00; border-bottom-color: #c00; }
.entity.time { color: #06c; border-bottom-color: #06c; }
.entity.place { color: #080; border-bottom-color: #080; }
.entity.office { color: #660; border-bottom-color: #660; }
.entity.war { color: #690; border-bottom-color: #690; }
.entity.ref { color: #999; border-bottom-color: #999; }
.entity.other { color: #999; border-bottom-color: #999; }
```

## 已更新的脚本

以下脚本已更新使用统一的语义标签处理：

1. ✅ `scripts/render_wars_html.py`
2. ✅ `scripts/render_taishigongyue_html.py`
3. ✅ `scripts/render_yunwen_html.py`
4. ✅ `scripts/render_chengyu_html.py`

## 注意事项

1. **标签标准**: 所有新代码应使用2024版标签标准
2. **旧数据兼容**: 模块会自动转换旧版标签，但建议逐步更新源数据
3. **不完整标签**: 源数据中的不完整标签（如`〖#`）会被自动清理
4. **嵌套标签**: 支持最多3层嵌套标签的处理

## 未来改进

- [ ] 完善扩展标签类型的定义（器物、典籍等）
- [ ] 提供标签验证工具
- [ ] 批量更新旧数据脚本
- [ ] 添加单元测试
