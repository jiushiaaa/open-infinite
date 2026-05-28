# Living Novel Engine — Phase 0

Phase 0 交付一个 **CLI 编排引擎**：内置原创样例世界，用户施加一次干预，系统生成 2-3 条世界线（JSON + Markdown），验证「角色 Agent 推演 → 干预变量 → 故事合约审计 → 世界线分支」核心链路。

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
```

### 真实 LLM 验收（demo，非 pytest）

配置 `.env` 后去掉 `--mock`，检查：

- 三条世界线主题固定为：**相信干预** / **半信半疑调查** / **拒绝干预/反弹**
- `state_snapshot.json` 含角色位置/情绪、关系变化、伏笔状态、`next_chapter_hook`
- `chapter.md` 约 1500–2500 字（mock 仅 300–600 字演示）

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

仅验证数据结构、状态机与三分支差异；**不要求** mock 模式下章节达到 1500 字。

## Phase 1+ 衔接

| 阶段 | 接入 |
|------|------|
| v0.2 | 文本导入；`CHAPTER_COMMIT` 投影（参考 webnovel-writer） |
| v0.3 | MiroFish OASIS 多 Agent 推演 |
| v0.4 | 阅读/干预/世界线 Web UI |
