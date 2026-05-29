const $ = (sel) => document.querySelector(sel);
const sidebar = $("#sidebar");
const readerBody = $("#reader-body");
const statePanel = $("#state-panel");
const storyFilter = $("#story-filter");
const readerTitle = $("#reader-title");

let currentStory = null;
let currentRun = null;
let currentBranch = null;
let currentBranchData = null;
let viewMode = "chapter";

const RETRIEVAL_SOURCE_LABELS = {
  fact: "正史事实",
  chapter_brief: "章节摘要",
  volume_brief: "卷摘要",
  contract: "合约约束",
};

async function api(path) {
  let res;
  try {
    res = await fetch(path);
  } catch (networkErr) {
    throw new Error(`网络错误：${networkErr.message || networkErr}`);
  }
  let data = null;
  const text = await res.text();
  if (text) {
    try {
      data = JSON.parse(text);
    } catch (_) {
      data = null;
    }
  }
  if (!res.ok) {
    const msg = (data && data.error) || `${res.status} ${res.statusText}`;
    throw new Error(msg);
  }
  return data || {};
}

function esc(s) {
  const d = document.createElement("div");
  d.textContent = s ?? "";
  return d.innerHTML;
}

function showError(target, err) {
  const msg = (err && err.message) || String(err);
  target.innerHTML = `<div class="empty" style="color:var(--warn)">加载失败：${esc(msg)}</div>`;
}

function showLoading(target, label = "加载中") {
  target.innerHTML = `<div class="empty">${esc(label)}…</div>`;
}

window.addEventListener("error", (e) => {
  console.error("[browser]", e.error || e.message);
});
window.addEventListener("unhandledrejection", (e) => {
  console.error("[browser] unhandled", e.reason);
  showError(readerBody, e.reason);
});

function renderStories(stories) {
  const html = stories
    .map(
      (s) => `
    <div class="story-item" data-slug="${esc(s.slug)}">
      <div>${esc(s.display_name)}</div>
      <div class="meta">${esc(s.slug)} · ${s.source_kind} · ${s.run_count} runs</div>
    </div>`
    )
    .join("");
  sidebar.innerHTML = `<h2>故事</h2>${html || '<div class="empty">暂无故事</div>'}`;
  sidebar.querySelectorAll(".story-item").forEach((el) => {
    el.addEventListener("click", () => selectStory(el.dataset.slug));
  });
}

function renderTree(nodes, depth = 0) {
  let html = "";
  for (const node of nodes) {
    const orphan = node.is_orphan
      ? '<span class="tag-mini" title="父 run 已不在当前索引中">孤儿</span> '
      : "";
    html += `
      <div class="tree-item run" data-run="${esc(node.run_id)}" style="padding-left:${1 + depth * 0.75}rem">
        <div>${orphan}${esc(node.run_id)}</div>
        <div class="meta">${esc(node.kind)} · ${esc(node.intervention_preview || node.story_slug)}</div>
      </div>`;
    for (const b of node.branches || []) {
      const rbadge = b.retrieval_count
        ? ` <span class="tag-retrieval" title="检索记忆命中数">检索 ${b.retrieval_count}</span>`
        : "";
      const tbadge = b.has_multi_agent_trace
        ? ` <span class="tag-trace" title="多 Agent 轨迹（角色计划数）">轨迹 ${b.multi_agent_trace_count || 0}</span>`
        : "";
      html += `
        <div class="tree-item branch" data-run="${esc(node.run_id)}" data-branch="${esc(b.branch_id)}" style="padding-left:${1.75 + depth * 0.75}rem">
          <div>${esc(b.branch_id)} — ${esc(b.theme || "(无主题)")}</div>
          <div class="meta">${b.chapter_chars || 0} 字${rbadge}${tbadge}</div>
        </div>`;
      for (const child of b.child_runs || []) {
        html += renderTree([child], depth + 1);
      }
    }
  }
  return html;
}

async function selectStory(slug) {
  currentStory = slug;
  storyFilter.textContent = slug;
  sidebar.querySelectorAll(".story-item").forEach((el) => {
    el.classList.toggle("active", el.dataset.slug === slug);
  });
  showLoading(sidebar, `加载世界线树 · ${slug}`);
  try {
    const { tree } = await api(
      `/api/tree?story_slug=${encodeURIComponent(slug)}`
    );
    const treeHtml = renderTree(tree || []);
    sidebar.innerHTML =
      `<h2>世界线树 · ${esc(slug)}</h2>` +
      (treeHtml || '<div class="empty">该故事尚无 run 输出</div>');
    bindTreeClicks();
  } catch (err) {
    showError(sidebar, err);
    return;
  }
  try {
    const story = await api(`/api/stories/${encodeURIComponent(slug)}`);
    renderStoryMeta(story);
  } catch (err) {
    $("#story-meta").innerHTML = "";
    console.warn("story meta load failed:", err);
  }
}

function bindTreeClicks() {
  sidebar.querySelectorAll(".tree-item.branch").forEach((el) => {
    el.addEventListener("click", (e) => {
      e.stopPropagation();
      selectBranch(el.dataset.run, el.dataset.branch);
    });
  });
  sidebar.querySelectorAll(".tree-item.run").forEach((el) => {
    el.addEventListener("click", () => selectRun(el.dataset.run));
  });
}

async function selectRun(runId) {
  currentRun = runId;
  currentBranch = null;
  currentBranchData = null;
  readerTitle.textContent = runId;
  showLoading(readerBody, `加载 ${runId}`);
  try {
    const data = await api(`/api/runs/${encodeURIComponent(runId)}`);
    viewMode = data.has_compare ? "compare" : "meta";
    renderRunView(data);
    renderCliHints(data.cli_hints || []);
  } catch (err) {
    showError(readerBody, err);
    renderCliHints([]);
  }
}

async function selectBranch(runId, branchId) {
  currentRun = runId;
  currentBranch = branchId;
  readerTitle.textContent = `${runId} / ${branchId}`;
  sidebar.querySelectorAll(".tree-item").forEach((el) => {
    el.classList.toggle(
      "active",
      el.dataset.run === runId && el.dataset.branch === branchId
    );
  });
  showLoading(readerBody, `加载 ${branchId}`);
  try {
    const data = await api(
      `/api/runs/${encodeURIComponent(runId)}/branches/${encodeURIComponent(branchId)}`
    );
    currentBranchData = data;
    viewMode = "chapter";
    syncToolbar("chapter");
    renderBranchView(data);
    renderStatePanel(data.state_snapshot);
    renderCliHints(data.cli_hints || []);
  } catch (err) {
    currentBranchData = null;
    showError(readerBody, err);
    statePanel.innerHTML = '<div class="empty">无法加载状态</div>';
    renderCliHints([]);
  }
}

function syncToolbar(mode) {
  document.querySelectorAll(".reader-toolbar button").forEach((b) => {
    b.classList.toggle("active", b.dataset.view === mode);
  });
}

function retrievalCount(data) {
  const items = data && data.retrieval && data.retrieval.items;
  return Array.isArray(items) ? items.length : 0;
}

function renderCliHints(hints) {
  const el = $("#cli-hints");
  if (!hints.length) {
    el.innerHTML = "";
    return;
  }
  el.innerHTML =
    "<strong>继续 CLI</strong>" +
    hints.map((h) => `<code title="点击复制">${esc(h)}</code>`).join("");
  el.querySelectorAll("code").forEach((c) => {
    c.addEventListener("click", () => {
      navigator.clipboard.writeText(c.textContent);
      c.style.color = "#fff";
      setTimeout(() => (c.style.color = ""), 400);
    });
  });
}

function renderBranchView(data) {
  const chapter = data.chapter_md
    ? `<pre>${esc(data.chapter_md)}</pre>`
    : '<div class="empty">该分支无 chapter.md（可能数据不完整或运行被中断）</div>';
  let html = chapter;
  if (data.summary_md) {
    html += `<hr style="border-color:var(--border);margin:1.5rem 0"><h3 style="color:var(--muted)">分支摘要</h3><pre>${esc(data.summary_md)}</pre>`;
  }
  const rcount = retrievalCount(data);
  if (rcount > 0) {
    html += `<hr style="border-color:var(--border);margin:1.5rem 0"><p style="color:var(--muted);font-size:0.82rem">本章生成引用了 <strong style="color:var(--accent)">${rcount}</strong> 条检索记忆，点上方「检索记忆」查看引擎引用了哪些事实/合约。</p>`;
  }
  if (data.multi_agent_trace) {
    const plans = Array.isArray(data.multi_agent_trace.turn_plans)
      ? data.multi_agent_trace.turn_plans.length
      : 0;
    html += `<hr style="border-color:var(--border);margin:1.5rem 0"><p style="color:var(--muted);font-size:0.82rem">本分支由多 Agent runner 推演，含 <strong style="color:var(--accent)">${plans}</strong> 份角色计划，点上方「Agent 轨迹」查看计划/私下信息/误解/延迟行动/关系信号。</p>`;
  }
  if (data.child_runs?.length) {
    html += `<hr style="border-color:var(--border);margin:1.5rem 0"><h3 style="color:var(--muted)">沿此分支续写的 run</h3><ul>${data.child_runs.map((id) => `<li>${esc(id)}</li>`).join("")}</ul>`;
  }
  readerBody.innerHTML = html;
}

function renderRetrieval(data) {
  const retrieval = data && data.retrieval;
  if (!retrieval) {
    readerBody.innerHTML =
      '<div class="empty">该分支无 retrieval_context.json（builtin 样例或 v0.3.1 之前的 run 不写检索记忆）</div>';
    return;
  }
  const items = Array.isArray(retrieval.items) ? retrieval.items : [];
  const query = retrieval.query || "";
  const chapter = retrieval.current_chapter;

  let html = `<div class="retrieval-head">`;
  if (query) html += `<div><span class="field">检索 query</span> ${esc(query)}</div>`;
  if (chapter != null)
    html += `<div><span class="field">当前章节</span> 第 ${esc(chapter)} 章</div>`;
  html += `<div><span class="field">命中</span> ${items.length} 条</div></div>`;

  if (items.length === 0) {
    html +=
      '<div class="empty" style="text-align:left">本次检索无命中（项目可能缺少 facts / summaries / contract，已优雅降级）。</div>';
    readerBody.innerHTML = html;
    return;
  }

  const grouped = {};
  for (const it of items) {
    const src = it.source || it.type || "unknown";
    (grouped[src] = grouped[src] || []).push(it);
  }
  const order = ["contract", "fact", "chapter_brief", "volume_brief"];
  const sources = Object.keys(grouped).sort(
    (a, b) => (order.indexOf(a) + 1 || 99) - (order.indexOf(b) + 1 || 99)
  );

  for (const src of sources) {
    const label = RETRIEVAL_SOURCE_LABELS[src] || src;
    html += `<div class="retrieval-group"><h3>${esc(label)} <span class="meta">(${grouped[src].length})</span></h3>`;
    for (const it of grouped[src]) {
      const score = typeof it.score === "number" ? it.score.toFixed(3) : "";
      const chap = it.chapter != null ? `第${esc(it.chapter)}章` : "";
      const evi = it.evidence ? ` · ${esc(it.evidence)}` : "";
      html += `
        <div class="retrieval-item">
          <div class="retrieval-text">${esc(it.text || "")}</div>
          <div class="meta">${chap}${evi}${score ? ` · score ${score}` : ""}</div>
        </div>`;
    }
    html += `</div>`;
  }
  readerBody.innerHTML = html;
}

function traceBadge(on, onLabel, offLabel) {
  const cls = on ? "trace-flag on" : "trace-flag off";
  return `<span class="${cls}">${esc(on ? onLabel : offLabel)}</span>`;
}

function renderTraceGroup(title, count, itemsHtml) {
  return `<div class="trace-group"><h3>${esc(title)} <span class="meta">(${count})</span></h3>${
    itemsHtml || '<div class="empty" style="text-align:left">（无）</div>'
  }</div>`;
}

function renderTrace(data) {
  const trace = data && data.multi_agent_trace;
  if (!trace) {
    readerBody.innerHTML =
      '<div class="empty">该分支无 multi_agent_trace.json（仅 multi_agent 系 runner 产出；默认 lightweight 不写）</div>';
    return;
  }
  const plans = Array.isArray(trace.turn_plans) ? trace.turn_plans : [];
  const intents = [];
  const delayed = [];
  const signals = [];
  for (const p of plans) {
    for (const it of p.intents || []) intents.push(it);
    for (const da of p.delayed_actions || []) delayed.push(da);
    for (const sg of p.relationship_signals || []) signals.push(sg);
  }
  const publicIntents = intents.filter((i) => i.visibility === "public");
  const privateIntents = intents.filter((i) => i.visibility !== "public");
  const knowledge = Array.isArray(trace.private_knowledge) ? trace.private_knowledge : [];
  const misund = Array.isArray(trace.misunderstandings) ? trace.misunderstandings : [];

  let html = `<div class="retrieval-head"><div><span class="field">世界线</span> ${esc(
    trace.worldline_id || data.branch_id || ""
  )}</div><div><span class="field">种子</span> ${esc(trace.branch_seed || "")}</div><div><span class="field">角色计划</span> ${plans.length} 份</div></div>`;

  const intentItem = (i) =>
    `<div class="trace-item"><div class="trace-text">${esc(i.actor_id)} · <em>${esc(
      i.intent_type || "plan"
    )}</em>${i.target ? ` → ${esc(i.target)}` : ""}</div><div>${esc(
      i.description || ""
    )}</div><div class="meta">${esc(i.motivation || "")}${
      i.confidence != null ? ` · 置信 ${esc(i.confidence)}` : ""
    }</div></div>`;
  html += renderTraceGroup(
    "公开意图 public",
    publicIntents.length,
    publicIntents.map(intentItem).join("")
  );
  html += renderTraceGroup(
    "私下意图 private/scene",
    privateIntents.length,
    privateIntents.map(intentItem).join("")
  );

  html += renderTraceGroup(
    "私下信息 private_knowledge",
    knowledge.length,
    knowledge
      .map(
        (k) =>
          `<div class="trace-item"><div class="trace-text">${esc(
            k.owner_id || ""
          )} ${traceBadge(!!k.revealed, "已揭露", "未揭露")}</div><div>${esc(
            k.content || ""
          )}</div><div class="meta">来源 ${esc(k.source || "?")}${
            (k.known_by || []).length ? ` · 知情 ${esc((k.known_by || []).join("、"))}` : ""
          }</div></div>`
      )
      .join("")
  );

  html += renderTraceGroup(
    "误解 misunderstandings",
    misund.length,
    misund
      .map(
        (m) =>
          `<div class="trace-item"><div class="trace-text">${esc(
            m.holder_id || ""
          )} · ${esc(m.about || "")} ${traceBadge(
            !!m.corrected,
            "已纠正",
            "未纠正"
          )}</div><div>相信：${esc(m.believed || "")}</div>${
            m.corrected ? `<div class="meta">真相：${esc(m.reality || "")}</div>` : ""
          }</div>`
      )
      .join("")
  );

  html += renderTraceGroup(
    "延迟行动 delayed_actions",
    delayed.length,
    delayed
      .map(
        (d) =>
          `<div class="trace-item"><div class="trace-text">${esc(
            d.actor_id || ""
          )} · <em>${esc(d.action_type || "act")}</em> ${traceBadge(
            !!d.executed,
            "已执行",
            "待触发"
          )}</div><div>${esc(d.description || "")}</div><div class="meta">due_round ${esc(
            d.due_round
          )} · created ${esc(d.created_round)}</div></div>`
      )
      .join("")
  );

  html += renderTraceGroup(
    "关系信号 relationship_signals",
    signals.length,
    signals
      .map(
        (s) =>
          `<div class="trace-item"><div class="trace-text">${esc(s.from_id || "")} → ${esc(
            s.to_id || ""
          )}</div><div>${esc(s.change || "")} · 强度 ${esc(s.magnitude)}</div>${
            s.propagated_from
              ? `<div class="meta">传播自 ${esc(s.propagated_from)}</div>`
              : ""
          }</div>`
      )
      .join("")
  );

  readerBody.innerHTML = html;
}

function renderRunView(data) {
  if (viewMode === "compare") {
    readerBody.innerHTML = data.compare_md
      ? `<pre>${esc(data.compare_md)}</pre>`
      : '<div class="empty">该 run 无 compare.md（resume continue 默认无对比）</div>';
    return;
  }
  const branches = (data.branches || [])
    .map((b) => `<li>${esc(b.id)} — ${esc(b.theme)} (${b.chapter_chars} 字)</li>`)
    .join("");
  readerBody.innerHTML = `
    <p><strong>类型</strong> ${esc(data.kind)} · <strong>故事</strong> ${esc(data.story_slug)} · <strong>来源</strong> ${esc(data.source_kind)}</p>
    ${data.intervention_preview ? `<p>${esc(data.intervention_preview)}</p>` : ""}
    ${data.parent_run_id ? `<p style="color:var(--muted)">父 run: ${esc(data.parent_run_id)} / ${esc(data.parent_branch || "")}</p>` : ""}
    <ul>${branches || '<li class="empty">无分支</li>'}</ul>
    <p style="color:var(--muted)">点击左侧分支阅读章节</p>`;
}

function renderStatePanel(snapshot) {
  if (!snapshot) {
    statePanel.innerHTML = '<div class="empty">该分支无 state_snapshot.json</div>';
    return;
  }
  const characters = snapshot.characters && typeof snapshot.characters === "object"
    ? snapshot.characters
    : {};
  let html = "<h2>角色状态</h2>";
  const charEntries = Object.entries(characters);
  if (charEntries.length === 0) {
    html += '<div class="empty" style="text-align:left;padding:0.5rem 1rem">快照中无角色字段</div>';
  } else {
    for (const [id, ch] of charEntries) {
      const safeCh = ch && typeof ch === "object" ? ch : {};
      const resources = Array.isArray(safeCh.resources) ? safeCh.resources : [];
      html += `
        <div class="state-card">
          <h3>${esc(safeCh.name || id)}</h3>
          <div class="field">位置 · 情绪</div>
          <div>${esc(safeCh.location || "?")} · ${esc(safeCh.emotion || "?")}</div>
          ${resources.length ? `<div class="field" style="margin-top:0.35rem">资源</div><div>${esc(resources.join("、"))}</div>` : ""}
        </div>`;
    }
  }
  const hook = snapshot.next_chapter_hook;
  if (hook) {
    html += `<div class="state-card"><h3>下一章钩子</h3><div>${esc(hook)}</div></div>`;
  }
  const threads = Array.isArray(snapshot.open_threads) ? snapshot.open_threads : [];
  if (threads.length) {
    html += `<div class="state-card"><h3>开放伏笔</h3><ul>${threads.map((t) => `<li>${esc(t.title || t.id || "?")} (${esc(t.status || "?")})</li>`).join("")}</ul></div>`;
  }
  statePanel.innerHTML = html;
}

function renderStoryMeta(story) {
  const el = $("#story-meta");
  const hasContract = !!story.story_contract;
  const hasFacts = !!story.facts?.length;
  const hasSummaries = !!story.summaries?.length;
  if (!hasContract && !hasFacts && !hasSummaries) {
    el.innerHTML =
      story.source_kind === "imported"
        ? '<h2>项目元数据</h2><div class="empty">该导入项目暂无 story_contract / facts / summaries（属于 v0.2.2 之前的旧项目）</div>'
        : "";
    return;
  }
  let html = "<h2>项目元数据</h2>";
  if (hasContract) {
    const rules = story.story_contract.world_rules || [];
    html += `<div class="contract-block"><strong>世界规则 (${rules.length})</strong><ul>${rules.slice(0, 5).map((r) => `<li>${esc(r)}</li>`).join("")}</ul></div>`;
  }
  if (hasFacts) {
    html += `<div class="contract-block"><strong>事实 (${story.facts.length})</strong><ul>${story.facts.slice(0, 4).map((f) => `<li>${esc(f.text)}</li>`).join("")}</ul></div>`;
  }
  if (hasSummaries) {
    html += `<div class="contract-block"><strong>章节摘要 (${story.summaries.length})</strong></div>`;
  }
  el.innerHTML = html;
}

$("#btn-refresh").addEventListener("click", async () => {
  try {
    const { stories } = await api("/api/stories");
    renderStories(stories || []);
    if (currentStory) await selectStory(currentStory);
  } catch (err) {
    showError(sidebar, err);
  }
});

$("#btn-all-stories").addEventListener("click", async () => {
  currentStory = null;
  storyFilter.textContent = "全部";
  showLoading(sidebar, "加载全部世界线");
  try {
    const [{ stories }, { tree }] = await Promise.all([
      api("/api/stories"),
      api("/api/tree"),
    ]);
    renderStories(stories || []);
    sidebar.innerHTML =
      `<h2>全部世界线</h2>` +
      (renderTree(tree || []) || '<div class="empty">暂无 run</div>');
    bindTreeClicks();
  } catch (err) {
    showError(sidebar, err);
  }
});

document.querySelectorAll(".reader-toolbar button").forEach((btn) => {
  btn.addEventListener("click", async () => {
    document.querySelectorAll(".reader-toolbar button").forEach((b) => b.classList.remove("active"));
    btn.classList.add("active");
    viewMode = btn.dataset.view;
    if (!currentRun) return;
    if (currentBranch && viewMode === "chapter") {
      return selectBranch(currentRun, currentBranch);
    }
    if (viewMode === "compare") {
      try {
        const data = await api(`/api/runs/${encodeURIComponent(currentRun)}`);
        readerBody.innerHTML = data.compare_md
          ? `<pre>${esc(data.compare_md)}</pre>`
          : '<div class="empty">无 compare.md</div>';
      } catch (err) {
        showError(readerBody, err);
      }
      return;
    }
    if (!currentBranch) {
      readerBody.innerHTML =
        '<div class="empty">请先在左侧选择一个分支</div>';
      return;
    }
    let data = currentBranchData;
    if (!data) {
      try {
        data = await api(
          `/api/runs/${encodeURIComponent(currentRun)}/branches/${encodeURIComponent(currentBranch)}`
        );
        currentBranchData = data;
      } catch (err) {
        showError(readerBody, err);
        return;
      }
    }
    if (viewMode === "summary") {
      readerBody.innerHTML = data.summary_md
        ? `<pre>${esc(data.summary_md)}</pre>`
        : '<div class="empty">该分支无 summary.md</div>';
    } else if (viewMode === "retrieval") {
      renderRetrieval(data);
    } else if (viewMode === "trace") {
      renderTrace(data);
    }
  });
});

(async function init() {
  showLoading(sidebar, "加载故事");
  try {
    const { stories } = await api("/api/stories");
    renderStories(stories || []);
  } catch (err) {
    showError(sidebar, err);
  }
})();
