import type { RuntimeMemoryContext } from "../api/types";
import { EmptyState } from "./common/States";

export function RuntimeMemoryPanel({
  memory,
}: {
  memory: RuntimeMemoryContext | null | undefined;
}) {
  if (!memory) {
    return (
      <EmptyState
        title="该分支没有运行记忆"
        hint="runtime_memory_context.json 缺失，通常表示内置样例或旧 run。"
      />
    );
  }

  const aliases = memory.entity_aliases;
  const resolved = memory.resolved_query_entities || [];
  const warnings = memory.warnings || [];
  const layers = memory.consumed_layers || [];

  return (
    <div>
      <section className="expl-section">
        <h3 className="expl-section__title">本章生成前读取了哪些记忆层</h3>
        <div className="kv">
          <span className="kv__k">查询</span>
          <span className="kv__v">{memory.query || "未记录"}</span>
        </div>
        <div className="kv">
          <span className="kv__k">章节</span>
          <span className="kv__v">第 {memory.current_chapter || 1} 章</span>
        </div>
        <div className="chip-row">
          {layers.length === 0 ? (
            <span className="muted tiny">没有消费到记忆层。</span>
          ) : (
            layers.map((layer) => (
              <span key={layer} className="memory-chip">
                {labelLayer(layer)}
              </span>
            ))
          )}
        </div>
      </section>

      <section className="expl-section">
        <h3 className="expl-section__title">实体别名归一化</h3>
        <div className="kv">
          <span className="kv__k">状态</span>
          <span className="kv__v">{labelAliasStatus(aliases?.status)}</span>
        </div>
        <div className="kv">
          <span className="kv__k">实体数</span>
          <span className="kv__v">{aliases?.count ?? 0}</span>
        </div>
        {resolved.length > 0 ? (
          <div className="chip-row">
            {resolved.map((entity) => (
              <span key={entity} className="memory-chip memory-chip--entity">
                {entity}
              </span>
            ))}
          </div>
        ) : (
          <p className="muted tiny">本次查询未命中可归一化实体。</p>
        )}
      </section>

      {warnings.length > 0 && (
        <section className="expl-section">
          <h3 className="expl-section__title">降级提示</h3>
          {warnings.map((warning, i) => (
            <div key={i} className="runtime-warning">
              {warning}
            </div>
          ))}
        </section>
      )}
    </div>
  );
}

function labelLayer(layer: string) {
  const labels: Record<string, string> = {
    entity_aliases: "实体别名",
    canon_ledger: "正史账本",
    chapter_brief: "章节摘要",
    volume_brief: "卷摘要",
    contract: "故事合约",
    fact: "正史事实",
  };
  return labels[layer] || layer;
}

function labelAliasStatus(status: string | undefined) {
  if (status === "ready") return "已就绪";
  if (status === "damaged") return "文件损坏，已降级";
  if (status === "missing") return "未生成";
  return status || "未知";
}
