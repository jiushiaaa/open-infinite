import { useState } from "react";
import type { BranchDetail, InterventionCompilation } from "../api/types";
import { CharacterStatePanel } from "./CharacterStatePanel";
import { RetrievalPanel } from "./RetrievalPanel";
import { AgentTracePanel } from "./AgentTracePanel";
import { CompilationPanel } from "./CompilationPanel";
import "./rightPanel.css";

type Tab = "state" | "retrieval" | "trace" | "compilation";

export function RightPanel({
  branch,
  compilation,
  compilationLoading,
}: {
  branch: BranchDetail;
  compilation: InterventionCompilation | null;
  compilationLoading: boolean;
}) {
  const [tab, setTab] = useState<Tab>("compilation");

  const tabs: { id: Tab; label: string; dot?: boolean }[] = [
    { id: "compilation", label: "干预编译", dot: !!compilation },
    { id: "state", label: "状态", dot: !!branch.state_snapshot },
    { id: "retrieval", label: "检索记忆", dot: !!branch.retrieval },
    { id: "trace", label: "Agent 轨迹", dot: !!branch.multi_agent_trace },
  ];

  return (
    <div className="rpanel">
      <div className="rpanel__tabs" role="tablist">
        {tabs.map((t) => (
          <button
            key={t.id}
            role="tab"
            aria-selected={tab === t.id}
            className={`rpanel__tab ${tab === t.id ? "is-active" : ""}`}
            onClick={() => setTab(t.id)}
          >
            {t.label}
            {t.dot && <span className="rpanel__tab-dot" aria-hidden />}
          </button>
        ))}
      </div>
      <div className="rpanel__body">
        {tab === "compilation" && (
          <CompilationPanel compilation={compilation} loading={compilationLoading} />
        )}
        {tab === "state" && <CharacterStatePanel snapshot={branch.state_snapshot} />}
        {tab === "retrieval" && <RetrievalPanel retrieval={branch.retrieval} />}
        {tab === "trace" && <AgentTracePanel trace={branch.multi_agent_trace} />}
      </div>
    </div>
  );
}
