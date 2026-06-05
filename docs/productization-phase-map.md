# 未终章产品化阶段归类

> 用途：解释“技术 MVP / 产品化 MVP / 世界沙盘第一版 / 商业化后置”的口径，避免把已完成底座误读成完整商业产品，或把支撑层当作当前下一刀。当前事实以 `../memory.md` 为准；文档分层见 `index.md`。

## 1. 当前结论

未终章已经完成多层底座，但当前默认主线只有一个：**World Sandbox Loop / 小说世界沙盘体验深化**。

| 层级 | 当前状态 | 现在怎么用 |
| --- | --- | --- |
| 技术 MVP | v0.1-v0.6，证明导入、检索、分支、续章、runner 和 trace 能跑 | 作为引擎底座保留 |
| 短中篇产品化 MVP | v0.7-v0.7.5，Web App 与基础用户流程成立 | 作为前端体验和 UI 风格底座 |
| 长篇产品化 alpha | v0.8-v0.9.0-alpha，长篇导入、审计、续写、世界线选择、导出和 closeout 跑通 | 作为长篇世界资料底座 |
| 本地优先加固 | v0.9.1-v1.0-local，模型配置、本地启动、provider/cost、设定工作台、商业化边界等收口 | 作为支撑层，不默认扩张 |
| 支撑层后续增强 | 运行前体检、投影健康、读者评审、检索样本、Graph/长期记忆 mock 复核链、真实 retrieval provider、opt-in Vector Retrieval Pipeline 均已收口 | 只在用户明确点名或主线真实瓶颈需要时进入 |
| 世界沙盘第一版 | S1-S9、卷宗阅读、自演可读入口、Reviewer 局部重写采纳、编辑后定稿和确认入卷反哺下一轮入口已形成产品链路 | 当前继续深化的主线 |

本阶段的产品化判断不是“有多少面板”，而是用户是否能感到：

```text
世界在运行。
角色在自主行动。
干预有后果。
角色会记得和误会。
世界会代偿。
章节来自世界演化。
作者能把涌现剧情采纳成可写材料。
```

## 2. MVP 口径

不同阶段的 MVP 不等价：

| 口径 | 含义 |
| --- | --- |
| 技术 MVP | service/API/artifact/tests 能跑通，主要证明机制可行 |
| 产品化 MVP | 普通用户能通过 Web UI 完成一条可理解流程 |
| 世界沙盘第一版 | 世界、角色、干预、记忆、代偿、正文和作者采纳能串成一条可继续运行的链 |
| 完整产品能力 | 用户真实觉得角色活、世界会变、章节好读、审稿意见能转成作品材料 |

因此，`有 API / 有页面 / 有测试 / 有 artifact` 是底线，不是完整产品能力。

## 3. 当前已闭环但不是默认主线

以下能力已经有证据链或本地边界，归为支撑层：

- provider / cost / route matrix / model configuration。
- MasterSetting / Cards Workspace / 设定资产。
- Runtime Preflight / Projection Health / Reader Panel / Prompt Budget Pack。
- OpenAPI / typed client / packaging readiness。
- BM25、canon ledger、aliases、retrieval samples、真实 embedding、Zilliz、reranker、hybrid vector opt-in。
- GraphRAG / Zep / Temporal Memory 的触发证据、shadow、case matrix、provider boundary、offline replay、manual mock adapter review。
- 商业化边界、权限、审计、对象存储、认证、配额、计费和发行准备。

这些能力保留为工具箱；只有直接服务世界沙盘主线时才被重新启用。

## 4. 当前仍需产品化深化

| 方向 | 为什么还要做 |
| --- | --- |
| 真实 LLM 多 Agent 策略 | 让角色行动少一点 deterministic 模板感，形成真正的信任、欺骗、试探、反抗和妥协 |
| 长正文/连续阅读 | 让章节像小说连续读下去，而不是卷宗素材或说明文 |
| 正文内证据锚点/误会图谱 | 让读者不离开阅读流也能理解谁知道什么、谁误会什么 |
| 更强语义 Reviewer | 像编辑一样审人物动机、冲突张力、视角、世界状态入文和章节好读度 |
| 整章风格润色 | 从片段级改写继续走向整章定稿质量 |
| 角色/势力独立卷 | 把 tab 里的第一版阅读推进为长期个人卷和势力卷 |
| 世界自演醒来报告 | 让无人值守结果像一夜世界真的发生过事情，而不是任务摘要 |

## 5. 后置排期原则

1. 先世界体验，再工程支撑。
2. 先本地产品稳定，再发行安装包和服务器在线体验。
3. 先触发式评估，再接重依赖。
4. 先 Web UI + API，再 CLI 外壳。
5. 先 additive，不破坏 `chapter.md`、`events.json`、`state_snapshot.json`、`multi_agent_trace.json`、`causal_diff.json`。
6. 商业化、认证、对象存储、队列、计费、硬配额和云端多租户继续后置。
