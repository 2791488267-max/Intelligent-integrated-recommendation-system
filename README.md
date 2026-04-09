# 智慧融合推荐系统 (Lightweight RAG System)

本项目为全国大学生计算机设计大赛参赛作品。
本系统是一个基于轻量级 RAG（检索增强生成）架构的非遗文化（彝绣）电商推荐 Web 平台。

## 技术栈
- **后端**：Python + Flask
- **数据与检索层**：Pandas + 自研轻量级多维字符串滑动匹配算法
- **AI 引擎**：接入国产智谱 GLM 大语言模型 API
- **前端**：HTML5/CSS3/Vanilla JS + 毛玻璃 (Glassmorphism) UI 设计

## 核心创新点
摒弃了沉重的图数据库（Neo4j）与本地向量模型，针对云原生环境资源受限的痛点进行了极简架构重构，实现了在单核 2G 服务器上的高可用运行。

## 如何运行
1. 安装依赖：`pip install Flask pandas requests openpyxl`
2. 在 `rag_with_qwen.py` 中配置你自己的智谱 API Key。
3. 运行 `python app.py`。
4. 访问 `http://localhost:5000`。
