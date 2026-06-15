# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

GitHub 个人主页项目，通过 GitHub Actions 每日自动更新 README.md，展示：
- 随机句子（每日一句）
- 豆瓣动态（最近观影/读书）
- 博客文章更新

## 常用命令

### 本地运行

```bash
# 安装依赖
pip install -r src/requirements.txt

# 运行构建脚本（需要设置 GH_TOKEN 环境变量）
GH_TOKEN=your_token python src/build.py

# 查看生成的 README
cat README.md
```

### 测试单个功能

```python
# 测试豆瓣 RSS 抓取
python -c "import feedparser; print(feedparser.parse('https://www.douban.com/feed/people/heyitao/interests')['entries'][0])"

# 测试博客 RSS 抓取
python -c "import feedparser; print(feedparser.parse('https://heyitao.com/feed')['entries'][0])"

# 测试随机句子
python -c "import random; lines = open('src/juzi.txt', 'r', encoding='utf-8').readlines(); print(random.choice([l.strip() for l in lines if l.strip()]))"
```

## 架构说明

### 文件结构

```
.
├── README.md              # 自动生成的输出文件
├── .github/workflows/
│   └── build.yml         # GitHub Actions 配置
└── src/
    ├── build.py          # 主构建脚本
    ├── requirements.txt  # Python 依赖
    ├── juzi.txt         # 句子库（每行一句）
    └── release-projects.md  # 发布项目列表
```

### 核心流程

1. **构建脚本** (`src/build.py`)：
   - 从豆瓣 RSS 和博客 RSS 抓取最新数据
   - 从 `juzi.txt` 随机选择一句
   - 使用正则表达式替换 README.md 中的标记区块

2. **标记区块**：
   - `<!-- juzi starts -->...<!-- juzi ends -->` - 每日一句
   - `<!-- douban starts -->...<!-- douban ends -->` - 豆瓣动态
   - `<!-- blog starts -->...<!-- blog ends -->` - 博客文章

3. **自动化触发**：
   - 每日定时运行（cron: `0 0 * * *`）
   - 手动触发（workflow_dispatch）
   - Push 时触发

### 依赖说明

- `python-graphql-client`：GitHub GraphQL API 客户端
- `feedparser`：RSS/Atom 解析器
- `httpx`：HTTP 客户端
- `datetime`：日期处理

## 开发注意事项

### 修改内容区块

所有区块使用 `replace_chunk()` 函数更新，保持标记格式：
```html
<!-- marker starts -->
内容
<!-- marker ends -->
```

### 添加新的数据源

1. 在 `build.py` 中添加 `fetch_*()` 函数
2. 在 README.md 中添加对应标记区块
3. 在 `__main__` 中调用并更新

### 本地测试注意事项

- 需要设置 `GH_TOKEN` 环境变量（用于 GitHub GraphQL API）
- 豆瓣 RSS 可能需要 SSL 验证绕过（`make_ssl_unverify()`）
- 时区处理：豆瓣时间戳 +8 小时转为北京时间

### 容错机制

每个数据源独立处理，单个失败不影响其他源更新：
- 豆瓣 RSS 获取失败 → 跳过豆瓣更新，保留原数据
- 博客 RSS 获取失败 → 跳过博客更新，保留原数据
- 每日一句获取失败 → 跳过句子更新，保留原数据

## README 组成

### 动态更新部分
- 每日一句：从 `src/juzi.txt` 随机选择
- 豆瓣动态：最近 10 条观影/读书记录
- 博客文章：最近 10 篇文章

### 静态部分
- 访问计数：使用 [visitor-badge.laobi.icu](https://visitor-badge.laobi.icu) 服务
  - 2026-06 从 badges.toozhao.com 迁移（原服务已停止运营）
  - 2026-06 从 hits.dwyl.com 迁移（国内访问不稳定）
