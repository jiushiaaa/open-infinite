# Living Novel Engine — Phase 0

Phase 0 交付一个 **CLI 编排引擎**：内置原创样例世界，用户施加干预，系统生成 2-3 条世界线（JSON + Markdown），并支持沿选定世界线续章与再干预。

## 版本表

| 版本 | 能力 | 状态 |
|------|------|------|
| Phase 0 Alpha | `intervene` / `compare` / 内置样例《天荒城残夜》/ mock + LLM | 已收口 |
| Phase 0 Beta | 状态渲染、三分支钳制、玉简锁、章节兜底 | 已收口 |
| v0.1.1 | 快照 location、正史锁、墨青烟称谓、退魂铃来源 | 已收口 |
| v0.1.2 | `resume continue` → `linear/` 续章 | 已收口 |
| v0.1.3 | `resume intervene` → 续章上再三分叉 | 已收口 |
| v0.2 | `import-novel` 文本导入 | 设计中，见 [v0.2-import-novel-mvp.md](../docs/v0.2-import-novel-mvp.md) |

**测试基线**：`pytest -q` → 46 passed（2026-05-28）。

**验收参考 run**

| 版本 | run_id |
|------|--------|
| v0.1.2 | `run_20260528_155153_c3275c_continue_branch_a` |
| v0.1.3 | `run_20260528_171207_94a6b9_resume_intervene_linear` |

**完整能力链**

```text
lne intervene <sample>  →  branch_a | branch_b | branch_c
lne resume continue <run_id> --branch branch_a  →  linear/
lne resume intervene <continue_run_id> --branch linear  →  branch_a | branch_b | branch_c
```

`MiroFish/` 与 `webnovel-writer/` **保持不动**。Phase 0 **不强依赖** 外部项目；仅当设置 `WEBNOVEL_GENRE_TEMPLATE` 时才可选读取外部题材文件，否则使用 `src/living_novel_engine/resources/style_fallback_xianxia.md`。

## 安装

```bash
cd engine
python -m venv .venv
.venv\Scripts\activate
pip install -e ".[dev]"
```

## 配置

```bash
copy .env.example .env
```

| 变量 | 说明 |
|------|------|
| `LLM_API_KEY` | OpenAI 兼容 API（与 MiroFish 相同） |
| `LLM_BASE_URL` / `LLM_MODEL_NAME` | 模型端点 |
| `WEBNOVEL_GENRE_TEMPLATE` | **可选**，外部风格参考；缺失或读失败则用内置 fallback |
| `LNE_MOCK=1` | 强制 mock |

**未配置 `LLM_API_KEY` 时，CLI 会自动启用 mock**，无需加 `--mock` 即可跑通端到端 demo。

## 快速演示

```bash
lne list-samples
# slug: tianhuang-night  display_name: 天荒城残夜

lne show-sample tianhuang-night

# 无 API Key 也可运行（自动 mock）
lne intervene tianhuang-night ^
  --target lin_wan_zhou ^
  --type whisper ^
  --content "今晚不要去城外竹林，那是墨青烟设的局" ^
  --branches 3 ^
  --rounds 4

# 或显式 mock
lne intervene tianhuang-night --target lin_wan_zhou --content "..." --mock

lne compare outputs/run_YYYYMMDD_HHMMSS

# v0.1.2：沿分支续写一章（无新干预）
lne intervene tianhuang-night --target lin_wan_zhou --content "今晚不要去城外竹林" --mock
lne resume continue run_YYYYMMDD_HHMMSS --branch branch_a --mock
# 新 run 目录：run_*_continue_branch_a/ 含 meta.json、parent_chapter.md、linear/chapter.md

# v0.1.3：在续章 linear 上再干预三分叉
lne resume intervene run_YYYYMMDD_continue_branch_a ^
  --branch linear ^
  --target lin_fan ^
  --content "告诉林晚舟，她身后的影子来自乱葬岗" ^
  --mock
```

### 真实 LLM 验收（demo，非 pytest）

配置 `.env` 后去掉 `--mock`，检查：

- 三条世界线主题固定为：**相信干预** / **半信半疑调查** / **拒绝干预/反弹**
- `state_snapshot.json` 含角色位置/情绪、关系变化、伏笔状态、`next_chapter_hook`
- `chapter.md` 约 1500–2500 字（mock 含前情提要 + 第一章节选 + 第十二章节点 + 第十三章演示续写）

## 合约审计输出

`intervention.json` 内 `contract_audit` 字段：

- `allowed` — 是否允许注入
- `risk` — low / medium / high
- `violations` — 违反世界规则或合约项
- `repair_suggestions` — 修改建议
- `expected_character_resistance` — 预期角色抗拒程度

## 输出结构

```text
outputs/run_<timestamp>/
├── intervention.json      # 含 contract_audit
├── compare.md
├── branch_a/              # 相信干预
├── branch_b/              # 半信半疑调查
├── branch_c/              # 拒绝干预/反弹
│   ├── events.json
│   ├── summary.md
│   ├── chapter.md
│   └── state_snapshot.json  # 完整状态快照
```

## 测试

```bash
pytest -q
```

仅验证数据结构、状态机与三分支差异；**不要求** mock 模式下第十三章达到 1500 字。

样例 `samples/tianhuang-night/` 阅读顺序：`prologue.md`（前情）→ `canon_opening.md`（第一章）→ `canon_chapter.md`（第十二章·干预节点）。

### v0.1.2 续章 run 结构

```text
outputs/run_<ts>_continue_branch_a/
├── meta.json              # parent_run_id, parent_branch, lineage
├── parent_snapshot.json
├── parent_chapter.md
└── linear/
    ├── events.json
    ├── state_snapshot.json
    ├── chapter.md         # 第十四章
    └── summary.md
```

### v0.1.3 续章干预 run 结构

```text
outputs/run_<ts>_resume_intervene_linear/
├── meta.json              # kind=resume_intervene, lineage, branch_seed_lineage
├── parent_snapshot.json
├── parent_chapter.md
├── intervention.json
├── compare.md
├── branch_a/              # 第十五章 · 相信新干预
├── branch_b/
└── branch_c/
```

## Phase 1+ 衔接

| 阶段 | 接入 |
|------|------|
| v0.1.3 | 续章上再次干预（`resume intervene`）✓ |
| v0.2 | 文本导入（[设计稿](../docs/v0.2-import-novel-mvp.md)） |
| v0.3 | MiroFish OASIS 多 Agent 推演 |
| v0.4 | 阅读/干预/世界线 Web UI |
