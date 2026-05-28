const $ = (sel) => document.querySelector(sel);
const sidebar = $("#sidebar");
const readerBody = $("#reader-body");
const statePanel = $("#state-panel");
const storyFilter = $("#story-filter");
const readerTitle = $("#reader-title");

let currentStory = null;
let currentRun = null;
let currentBranch = null;
let viewMode = "chapter";

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
      html += `
        <div class="tree-item branch" data-run="${esc(node.run_id)}" data-branch="${esc(b.branch_id)}" style="padding-left:${1.75 + depth * 0.75}rem">
          <div>${esc(b.branch_id)} — ${esc(b.theme || "(无主题)")}</div>
          <div class="meta">${b.chapter_chars || 0} 字</div>
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
    viewMode = "chapter";
    renderBranchView(data);
    renderStatePanel(data.state_snapshot);
    renderCliHints(data.cli_hints || []);
  } catch (err) {
    showError(readerBody, err);
    statePanel.innerHTML = '<div class="empty">无法加载状态</div>';
    renderCliHints([]);
  }
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
  if (data.child_runs?.length) {
    html += `<hr style="border-color:var(--border);margin:1.5rem 0"><h3 style="color:var(--muted)">沿此分支续写的 run</h3><ul>${data.child_runs.map((id) => `<li>${esc(id)}</li>`).join("")}</ul>`;
  }
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
      const data = await api(`/api/runs/${encodeURIComponent(currentRun)}`);
      readerBody.innerHTML = data.compare_md
        ? `<pre>${esc(data.compare_md)}</pre>`
        : '<div class="empty">无 compare.md</div>';
      return;
    }
    if (viewMode === "summary" && currentBranch) {
      const data = await api(
        `/api/runs/${encodeURIComponent(currentRun)}/branches/${encodeURIComponent(currentBranch)}`
      );
      readerBody.innerHTML = `<pre>${esc(data.summary_md || "")}</pre>`;
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
