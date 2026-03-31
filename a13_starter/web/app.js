const state = {
  samples: [],
  currentSampleName: null,
  currentReport: "",
  currentAnalysisId: null,
  latestResult: null,
};

const resumeInput = document.getElementById("resume-input");
const loadSampleButton = document.getElementById("load-sample-btn");
const analyzeButton = document.getElementById("analyze-btn");
const uploadFileButton = document.getElementById("upload-file-btn");
const resumeFileInput = document.getElementById("resume-file-input");
const parserModeSelect = document.getElementById("parser-mode-select");
const statusPanel = document.getElementById("status-panel");
const statusText = document.getElementById("status-text");
const sampleGallery = document.getElementById("sample-gallery");
const systemCheckList = document.getElementById("system-check-list");
const historyList = document.getElementById("history-list");
const emptyState = document.getElementById("empty-state");
const resultsContent = document.getElementById("results-content");
const primaryRole = document.getElementById("primary-role");
const primaryScoreBadge = document.getElementById("primary-score-badge");
const backupRoles = document.getElementById("backup-roles");
const studentMeta = document.getElementById("student-meta");
const parserMeta = document.getElementById("parser-meta");
const completenessScore = document.getElementById("completeness-score");
const competitivenessScore = document.getElementById("competitiveness-score");
const skillsTags = document.getElementById("skills-tags");
const softSkillsTags = document.getElementById("soft-skills-tags");
const matchCards = document.getElementById("match-cards");
const jdSearchInput = document.getElementById("jd-search-input");
const jdSearchButton = document.getElementById("jd-search-btn");
const jdSearchResults = document.getElementById("jd-search-results");
const templateEvidence = document.getElementById("template-evidence");
const careerOverview = document.getElementById("career-overview");
const growthPath = document.getElementById("growth-path");
const transitionPaths = document.getElementById("transition-paths");
const reportPreview = document.getElementById("report-preview");
const plan30 = document.getElementById("plan-30");
const plan90 = document.getElementById("plan-90");
const plan180 = document.getElementById("plan-180");
const careerStrengths = document.getElementById("career-strengths");
const careerRisks = document.getElementById("career-risks");
const recommendedProjects = document.getElementById("recommended-projects");
const careerGraph = document.getElementById("career-graph");
const copyReportButton = document.getElementById("copy-report-btn");
const downloadReportButton = document.getElementById("download-report-btn");
const downloadHtmlButton = document.getElementById("download-html-btn");
const downloadDocxButton = document.getElementById("download-docx-btn");
const printPdfButton = document.getElementById("print-pdf-btn");

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}

function renderMarkdownPreview(markdownText) {
  if (!markdownText || !markdownText.trim()) {
    return '<div class="empty-inline">当前还没有生成报告内容。</div>';
  }

  const parts = [];
  let listItems = [];

  const flushList = () => {
    if (!listItems.length) {
      return;
    }
    parts.push(`<ul>${listItems.join("")}</ul>`);
    listItems = [];
  };

  markdownText.split(/\r?\n/).forEach((rawLine) => {
    const line = rawLine.trimEnd();
    const trimmed = line.trim();

    if (!trimmed) {
      flushList();
      return;
    }

    if (trimmed.startsWith("# ")) {
      flushList();
      parts.push(`<h1>${escapeHtml(trimmed.slice(2).trim())}</h1>`);
      return;
    }

    if (trimmed.startsWith("## ")) {
      flushList();
      parts.push(`<h2>${escapeHtml(trimmed.slice(3).trim())}</h2>`);
      return;
    }

    if (trimmed.startsWith("### ")) {
      flushList();
      parts.push(`<h3>${escapeHtml(trimmed.slice(4).trim())}</h3>`);
      return;
    }

    if (trimmed.startsWith("- ")) {
      listItems.push(`<li>${escapeHtml(trimmed.slice(2).trim())}</li>`);
      return;
    }

    flushList();
    parts.push(`<p>${escapeHtml(trimmed)}</p>`);
  });

  flushList();
  return parts.join("");
}

function setStatus(text, type = "idle") {
  statusText.textContent = text;
  statusPanel.classList.remove("is-loading", "is-success", "is-error");
  if (type === "loading") {
    statusPanel.classList.add("is-loading");
  } else if (type === "success") {
    statusPanel.classList.add("is-success");
  } else if (type === "error") {
    statusPanel.classList.add("is-error");
  }
}

function setBusy(isBusy) {
  analyzeButton.disabled = isBusy;
  loadSampleButton.disabled = isBusy;
  uploadFileButton.disabled = isBusy;
  resumeFileInput.disabled = isBusy;
  parserModeSelect.disabled = isBusy;
  sampleGallery.querySelectorAll(".sample-card").forEach((button) => {
    button.disabled = isBusy;
  });
  historyList.querySelectorAll(".history-card").forEach((button) => {
    button.disabled = isBusy;
  });
}

function renderSystemChecks(payload) {
  systemCheckList.innerHTML = "";
  (payload.checks || []).forEach((check) => {
    const div = document.createElement("div");
    div.className = `system-check-item ${check.status}`;
    div.innerHTML = `
      <strong>${check.name}</strong>
      <span>${check.detail}</span>
    `;
    systemCheckList.appendChild(div);
  });
}

function fillTagList(container, items, emptyLabel = "暂无") {
  container.innerHTML = "";
  if (!items || items.length === 0) {
    const span = document.createElement("span");
    span.className = "tag";
    span.textContent = emptyLabel;
    container.appendChild(span);
    return;
  }

  items.forEach((item) => {
    const span = document.createElement("span");
    span.className = "tag";
    span.textContent = item;
    container.appendChild(span);
  });
}

function fillList(container, items) {
  container.innerHTML = "";
  const source = items && items.length ? items : ["暂无"];
  source.forEach((item) => {
    const li = document.createElement("li");
    li.textContent = item;
    container.appendChild(li);
  });
}

function renderStudentProfile(student) {
  const rows = [
    ["姓名", student.name || "未填写"],
    ["学校", student.school_name || "未填写"],
    ["专业", student.major || "未填写"],
    ["学历", student.education_level || "未识别"],
    ["目标岗位", (student.target_roles || []).join("、") || "未填写"],
    ["意向城市", student.city_preference || "未填写"],
  ];

  studentMeta.innerHTML = "";
  rows.forEach(([label, value]) => {
    const div = document.createElement("div");
    div.className = "meta-row";
    div.innerHTML = `<span>${label}</span><strong>${value}</strong>`;
    studentMeta.appendChild(div);
  });

  completenessScore.textContent = student.profile_completeness ?? 0;
  competitivenessScore.textContent = student.competitiveness_score ?? 0;
  fillTagList(skillsTags, student.skills || []);
  fillTagList(softSkillsTags, student.soft_skills || []);
}

function renderParserMeta(parser) {
  parserMeta.innerHTML = "";
  if (!parser) {
    return;
  }

  const items = [
    `请求模式：${parser.requested_mode}`,
    `实际解析：${parser.used_mode.toUpperCase()}`,
    `LLM 已配置：${parser.llm_configured ? "是" : "否"}`,
    `是否回退：${parser.fallback_used ? "是" : "否"}`,
  ];

  items.forEach((item) => {
    const span = document.createElement("span");
    span.className = "parser-pill";
    span.textContent = item;
    parserMeta.appendChild(span);
  });

  if (parser.message) {
    const div = document.createElement("div");
    div.className = "parser-note";
    div.textContent = parser.message;
    parserMeta.appendChild(div);
  }
}

function createBreakdownLine(label, value) {
  const wrapper = document.createElement("div");
  wrapper.className = "breakdown-line";

  const labels = document.createElement("div");
  labels.className = "breakdown-labels";
  labels.innerHTML = `<span>${label}</span><strong>${value}</strong>`;

  const track = document.createElement("div");
  track.className = "breakdown-track";

  const fill = document.createElement("div");
  fill.className = "breakdown-fill";
  fill.style.width = `${Math.max(0, Math.min(100, Number(value) || 0))}%`;

  track.appendChild(fill);
  wrapper.appendChild(labels);
  wrapper.appendChild(track);
  return wrapper;
}

function renderMatches(matches) {
  matchCards.innerHTML = "";
  (matches || []).forEach((match, index) => {
    const card = document.createElement("article");
    card.className = "match-card";

    const topRow = document.createElement("div");
    topRow.className = "match-top";
    topRow.innerHTML = `
      <div>
        <span class="mini-label">Top ${index + 1}</span>
        <h4>${match.role_title}</h4>
      </div>
      <div class="score-badge">${match.score} 分 · ${match.confidence_label || "中"}</div>
    `;

    const meta = document.createElement("p");
    meta.className = "match-summary";
    meta.textContent = match.summary || "暂无岗位摘要";

    const explanation = document.createElement("p");
    explanation.className = "match-explanation";
    explanation.textContent = match.explanation || "暂无解释";

    const breakdown = document.createElement("div");
    breakdown.className = "breakdown-grid";
    breakdown.appendChild(createBreakdownLine("基础要求", match.breakdown?.basic_requirements ?? 0));
    breakdown.appendChild(createBreakdownLine("专业技能", match.breakdown?.professional_skills ?? 0));
    breakdown.appendChild(createBreakdownLine("职业素养", match.breakdown?.professional_literacy ?? 0));
    breakdown.appendChild(createBreakdownLine("成长潜力", match.breakdown?.growth_potential ?? 0));

    const strengths = document.createElement("div");
    strengths.className = "insight-block";
    strengths.innerHTML = `<span class="summary-label">优势亮点</span>`;
    const strengthsTags = document.createElement("div");
    strengthsTags.className = "tag-list compact";
    fillTagList(strengthsTags, (match.strengths || []).slice(0, 3), "暂无");
    strengths.appendChild(strengthsTags);

    const evidence = document.createElement("div");
    evidence.className = "insight-block";
    evidence.innerHTML = `<span class="summary-label">匹配证据</span>`;
    const evidenceTags = document.createElement("div");
    evidenceTags.className = "tag-list compact";
    fillTagList(evidenceTags, (match.shared_skills || []).slice(0, 5), "暂无直接证据");
    evidence.appendChild(evidenceTags);

    const gaps = document.createElement("div");
    gaps.className = "insight-block";
    gaps.innerHTML = `<span class="summary-label">核心差距</span>`;
    const gapsTags = document.createElement("div");
    gapsTags.className = "tag-list subtle compact";
    fillTagList(gapsTags, (match.gaps || []).slice(0, 3), "暂无");
    gaps.appendChild(gapsTags);

    const actions = document.createElement("div");
    actions.className = "match-actions";
    const evidenceButton = document.createElement("button");
    evidenceButton.type = "button";
    evidenceButton.className = "button tertiary";
    evidenceButton.textContent = "查看原始 JD";
    evidenceButton.addEventListener("click", () => {
      loadTemplateEvidence(match.role_title).catch((error) => {
        setStatus(`加载模板证据失败：${error.message}`, "error");
      });
    });
    actions.appendChild(evidenceButton);

    card.appendChild(topRow);
    card.appendChild(meta);
    card.appendChild(explanation);
    card.appendChild(breakdown);
    card.appendChild(evidence);
    card.appendChild(strengths);
    card.appendChild(gaps);
    card.appendChild(actions);
    matchCards.appendChild(card);
  });
}

function renderCareerPlan(plan, matches) {
  const topMatch = matches && matches.length ? matches[0] : null;
  primaryRole.textContent = plan.primary_role || topMatch?.role_title || "待生成";
  primaryScoreBadge.textContent = `${topMatch?.score ?? 0} 分`;
  careerOverview.textContent = plan.overview || "";
  fillTagList(backupRoles, plan.backup_roles || [], "暂无备选方向");
  fillTagList(transitionPaths, plan.transition_paths || [], "暂无转岗建议");
  fillTagList(careerStrengths, plan.strengths || [], "暂无明显优势");
  fillTagList(careerRisks, plan.risks || [], "暂无明显风险");

  growthPath.innerHTML = "";
  (plan.primary_growth_path || []).forEach((item, index) => {
    const div = document.createElement("div");
    div.className = "path-item";
    div.innerHTML = `<span class="path-index">0${index + 1}</span><strong>${item}</strong>`;
    growthPath.appendChild(div);
  });

  fillList(plan30, plan.action_plan_30_days || []);
  fillList(plan90, plan.action_plan_90_days || []);
  fillList(plan180, plan.action_plan_180_days || []);
  fillList(recommendedProjects, plan.recommended_projects || []);
}

function renderCareerGraph(student, plan, matches) {
  const primary = plan.primary_role || matches?.[0]?.role_title || "主岗位";
  const backups = plan.backup_roles || [];
  const path = plan.primary_growth_path || [];
  const width = 940;
  const height = 340;
  const nodeWidth = 150;
  const nodeHeight = 56;
  const centerY = 148;
  const upperY = 86;
  const lowerY = 228;

  const nodes = [
    { id: "student", label: student.name || "学生", x: 74, y: centerY, tone: "teal", meta: "当前画像" },
    { id: "primary", label: primary, x: 286, y: centerY, tone: "accent", meta: "主推荐岗位" },
  ];

  path.slice(1, 4).forEach((item, index) => {
    nodes.push({
      id: `path-${index}`,
      label: item,
      x: 510 + index * 160,
      y: upperY,
      tone: "teal",
      meta: "成长路径",
    });
  });

  backups.slice(0, 2).forEach((item, index) => {
    nodes.push({
      id: `backup-${index}`,
      label: item,
      x: 510 + index * 160,
      y: lowerY,
      tone: "muted",
      meta: "备选方向",
    });
  });

  const nodeMap = new Map(nodes.map((node) => [node.id, node]));
  const centerYOf = (node) => node.y + nodeHeight / 2;
  const rightEdge = (node) => node.x + nodeWidth;
  const leftEdge = (node) => node.x;

  const lines = [];
  const connect = (fromId, toId, tone, mode = "horizontal") => {
    const from = nodeMap.get(fromId);
    const to = nodeMap.get(toId);
    if (!from || !to) {
      return;
    }

    if (mode === "diagonal") {
      lines.push({
        x1: rightEdge(from) - 8,
        y1: centerYOf(from),
        x2: leftEdge(to) + 8,
        y2: centerYOf(to),
        tone,
      });
      return;
    }

    lines.push({
      x1: rightEdge(from),
      y1: centerYOf(from),
      x2: leftEdge(to),
      y2: centerYOf(to),
      tone,
    });
  };

  connect("student", "primary", "accent");

  if (nodeMap.has("path-0")) {
    connect("primary", "path-0", "teal", "diagonal");
    for (let index = 0; index < 2; index += 1) {
      if (nodeMap.has(`path-${index}`) && nodeMap.has(`path-${index + 1}`)) {
        connect(`path-${index}`, `path-${index + 1}`, "teal");
      }
    }
  }

  if (nodeMap.has("backup-0")) {
    connect("primary", "backup-0", "muted", "diagonal");
    if (nodeMap.has("backup-1")) {
      connect("backup-0", "backup-1", "muted");
    }
  }

  careerGraph.innerHTML = `
    <svg viewBox="0 0 ${width} ${height}" role="img" aria-label="职业图谱">
      ${lines
        .map(
          (line) => `
            <line class="graph-line ${line.tone}" x1="${line.x1}" y1="${line.y1}" x2="${line.x2}" y2="${line.y2}" />
          `
        )
        .join("")}
      ${nodes
        .map(
          (node) => `
            <g class="graph-node ${node.tone}" transform="translate(${node.x}, ${node.y})">
              <rect rx="22" ry="22" width="${nodeWidth}" height="${nodeHeight}"></rect>
              <text x="${nodeWidth / 2}" y="21" class="graph-meta">${node.meta}</text>
              <text x="${nodeWidth / 2}" y="38" class="graph-label">${node.label}</text>
            </g>
          `
        )
        .join("")}
    </svg>
  `;
}

function renderHistory(items) {
  historyList.innerHTML = "";
  if (!items || items.length === 0) {
    const div = document.createElement("div");
    div.className = "history-empty";
    div.textContent = "还没有历史记录。生成一次职业规划后会自动保存。";
    historyList.appendChild(div);
    return;
  }

  items.forEach((item) => {
    const button = document.createElement("button");
    button.type = "button";
    button.className = "history-card";
    button.innerHTML = `
      <span class="mini-label">#${item.id}</span>
      <strong>${item.student_name || "未命名学生"} → ${item.primary_role || "待生成"}</strong>
      <p>${item.created_at}｜${item.parser_used_mode?.toUpperCase() || "RULE"}｜${item.student_major || "专业未填写"}</p>
    `;
    button.addEventListener("click", () => {
      loadAnalysis(item.id).catch((error) => {
        setStatus(`载入历史失败：${error.message}`, "error");
      });
    });
    historyList.appendChild(button);
  });
}

function renderJdSearchResults(items) {
  jdSearchResults.innerHTML = "";
  if (!items || items.length === 0) {
    jdSearchResults.innerHTML = `<div class="empty-inline">没有搜索到匹配的原始 JD，请换一个岗位名或技能词试试。</div>`;
    return;
  }

  items.forEach((item) => {
    const card = document.createElement("article");
    card.className = "jd-card";
    card.innerHTML = `
      <div class="jd-card-top">
        <div>
          <span class="mini-label">原始 JD</span>
          <h4>${item.job_title || "未命名岗位"}</h4>
        </div>
        <div class="score-badge">${item.score}</div>
      </div>
      <p class="jd-meta">${item.company_name || "未知公司"}｜${item.city || "城市未知"}｜${item.salary_range || "薪资未知"}</p>
      <p class="jd-summary">${item.job_detail || "暂无岗位详情"}</p>
    `;
    jdSearchResults.appendChild(card);
  });
}

function renderTemplateEvidence(data) {
  if (!data) {
    templateEvidence.innerHTML = `<div class="empty-inline">没有找到对应模板证据。</div>`;
    return;
  }
  const jobs = (data.representative_jobs || [])
    .map(
      (item) => `
        <article class="jd-card compact">
          <div class="jd-card-top">
            <div>
              <span class="mini-label">代表样本</span>
              <h4>${item.company_name || "未知公司"}</h4>
            </div>
          </div>
          <p class="jd-meta">${item.job_title || ""}｜${item.city || "城市未知"}｜${item.salary_range || "薪资未知"}</p>
          <p class="jd-summary">${item.job_detail || "暂无岗位详情"}</p>
        </article>
      `
    )
    .join("");

  templateEvidence.innerHTML = `
    <div class="evidence-head">
      <h4>${data.role_title}</h4>
      <p>源岗位名：${data.source_title}｜模板覆盖样本数：${data.dataset_job_count}</p>
    </div>
    <div class="evidence-tags">
      ${(data.dataset_evidence?.top_skills || [])
        .slice(0, 8)
        .map((item) => `<span class="tag">${item[0]} · ${item[1]}</span>`)
        .join("")}
    </div>
    <div class="evidence-list">${jobs || '<div class="empty-inline">暂无代表样本。</div>'}</div>
  `;
}

function renderResults(data) {
  emptyState.classList.add("hidden");
  resultsContent.classList.remove("hidden");
  state.latestResult = data;
  state.currentAnalysisId = data.analysis_id || data.id || null;
  renderStudentProfile(data.student_profile);
  renderParserMeta(data.parser);
  renderMatches(data.matches || []);
  renderCareerPlan(data.career_plan || {}, data.matches || []);
  renderCareerGraph(data.student_profile || {}, data.career_plan || {}, data.matches || []);
  state.currentReport = data.report_markdown || "";
  reportPreview.innerHTML = renderMarkdownPreview(state.currentReport);

  const topRole = data.career_plan?.primary_role || data.matches?.[0]?.role_title || "";
  if (topRole) {
    jdSearchInput.value = topRole;
    templateEvidence.innerHTML = `<div class="empty-inline">正在加载 ${topRole} 的模板证据...</div>`;
    loadTemplateEvidence(topRole).catch((error) => {
      templateEvidence.innerHTML = `<div class="empty-inline">模板证据加载失败：${error.message}</div>`;
    });
  }

  resultsContent.scrollIntoView({ behavior: "smooth", block: "start" });
}

function renderSampleGallery(samples) {
  sampleGallery.innerHTML = "";
  samples.forEach((sample) => {
    const button = document.createElement("button");
    button.type = "button";
    button.className = "sample-card";
    button.dataset.sampleName = sample.name;
    button.innerHTML = `
      <span class="mini-label">演示样例</span>
      <strong>${sample.label}</strong>
      <p>${sample.description}</p>
    `;
    button.addEventListener("click", () => {
      loadSampleResume(sample.name).catch((error) => {
        setStatus(`载入样例失败：${error.message}`, "error");
      });
    });
    sampleGallery.appendChild(button);
  });
  syncActiveSample();
}

function syncActiveSample() {
  sampleGallery.querySelectorAll(".sample-card").forEach((button) => {
    button.classList.toggle("active", button.dataset.sampleName === state.currentSampleName);
  });
}

async function initSamples() {
  const response = await fetch("/api/demo-resumes");
  const data = await response.json();
  state.samples = data.samples || [];
  renderSampleGallery(state.samples);
}

async function refreshHistory() {
  const response = await fetch("/api/history");
  const data = await response.json();
  renderHistory(data.items || []);
}

async function refreshSystemChecks() {
  const response = await fetch("/api/system-check");
  const data = await response.json();
  renderSystemChecks(data);
}

async function loadSampleResume(sampleName = null) {
  setBusy(true);
  setStatus("正在载入演示样例...", "loading");
  const url = sampleName ? `/api/demo-resume?name=${encodeURIComponent(sampleName)}` : "/api/demo-resume";
  const response = await fetch(url);
  const data = await response.json();
  resumeInput.value = data.resume_text || "";
  state.currentSampleName = data.sample_name || sampleName;
  syncActiveSample();
  setStatus(`样例已载入：${state.currentSampleName || "默认样例"}`, "success");
  setBusy(false);
}

async function analyzeResume() {
  const resumeText = resumeInput.value.trim();
  if (!resumeText) {
    setStatus("请先输入简历文本，或点击上方样例卡片。", "error");
    return;
  }

  setBusy(true);
  setStatus("正在调用解析链路，生成学生画像、岗位匹配与职业规划...", "loading");
  try {
    const response = await fetch("/api/career-plan", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        resume_text: resumeText,
        top_k: 5,
        parser_mode: parserModeSelect.value,
        sample_name: state.currentSampleName,
      }),
    });
    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.error || "请求失败");
    }
    renderResults(data);
    await refreshHistory();
    const parserInfo = data.parser
      ? `分析完成，当前使用 ${data.parser.used_mode.toUpperCase()} 解析。`
      : "分析完成，结果已刷新。";
    setStatus(parserInfo, "success");
  } catch (error) {
    setStatus(`分析失败：${error.message}`, "error");
  } finally {
    setBusy(false);
  }
}

async function loadAnalysis(analysisId) {
  setBusy(true);
  setStatus(`正在载入历史记录 #${analysisId}...`, "loading");
  try {
    const response = await fetch(`/api/history/${analysisId}`);
    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.error || "载入失败");
    }
    resumeInput.value = data.resume_text || "";
    state.currentSampleName = data.sample_name || null;
    syncActiveSample();
    renderResults({
      analysis_id: data.id,
      student_profile: data.student_profile,
      matches: data.matches,
      career_plan: data.career_plan,
      report_markdown: data.report_markdown,
      parser: {
        requested_mode: data.parser_requested_mode || "unknown",
        used_mode: data.parser_used_mode || "unknown",
        llm_configured: (data.parser_used_mode || "").toLowerCase() === "llm",
        llm_attempted: true,
        fallback_used: false,
        message: `该结果生成于 ${data.created_at}`,
      },
    });
    setStatus(`已载入历史记录 #${analysisId}。`, "success");
  } catch (error) {
    setStatus(`载入历史失败：${error.message}`, "error");
  } finally {
    setBusy(false);
  }
}

async function searchJd() {
  const query = jdSearchInput.value.trim();
  if (!query) {
    setStatus("请先输入岗位名、技能或公司名。", "error");
    return;
  }
  setStatus(`正在检索原始 JD：${query}...`, "loading");
  try {
    const response = await fetch(`/api/jd-search?q=${encodeURIComponent(query)}&limit=8`);
    const data = await response.json();
    renderJdSearchResults(data.items || []);
    setStatus(`原始 JD 检索完成，共返回 ${(data.items || []).length} 条结果。`, "success");
  } catch (error) {
    setStatus(`JD 检索失败：${error.message}`, "error");
  }
}

async function loadTemplateEvidence(roleTitle) {
  setStatus(`正在加载 ${roleTitle} 的模板证据...`, "loading");
  const response = await fetch(`/api/template-evidence?role_title=${encodeURIComponent(roleTitle)}`);
  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.error || "模板证据加载失败");
  }
  renderTemplateEvidence(data);
  setStatus(`已加载 ${roleTitle} 的模板证据。`, "success");
}

async function uploadResumeFile() {
  const file = resumeFileInput.files && resumeFileInput.files[0];
  if (!file) {
    setStatus("请先选择一个简历文件。", "error");
    return;
  }

  const formData = new FormData();
  formData.append("resume_file", file);
  setBusy(true);
  setStatus(`正在解析文件：${file.name}...`, "loading");
  try {
    const response = await fetch("/api/upload-resume-file", {
      method: "POST",
      body: formData,
    });
    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.error || "文件解析失败");
    }
    resumeInput.value = data.resume_text || "";
    state.currentSampleName = null;
    syncActiveSample();
    setStatus(data.message || `文件已解析：${file.name}`, "success");
  } catch (error) {
    setStatus(`文件解析失败：${error.message}`, "error");
  } finally {
    setBusy(false);
  }
}

async function copyReport() {
  if (!state.currentReport) {
    setStatus("当前还没有可复制的报告内容。", "error");
    return;
  }
  await navigator.clipboard.writeText(state.currentReport);
  setStatus("报告内容已复制到剪贴板。", "success");
}

function downloadReport() {
  if (!state.currentReport) {
    setStatus("当前还没有可下载的报告内容。", "error");
    return;
  }
  const blob = new Blob([state.currentReport], { type: "text/markdown;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = "career_plan_report.md";
  link.click();
  URL.revokeObjectURL(url);
  setStatus("Markdown 报告已开始下载。", "success");
}

function downloadStoredExport(format) {
  if (!state.currentAnalysisId) {
    setStatus("请先生成一次分析结果，再导出正式文件。", "error");
    return;
  }
  const url = `/api/export/analysis/${state.currentAnalysisId}?format=${format}`;
  window.open(url, "_blank");
  const labels = {
    html: "HTML",
    docx: "Word",
    pdf: "PDF",
  };
  setStatus(`${labels[format] || format} 导出已开始。`, "success");
}

function printReportPdf() {
  if (!state.currentAnalysisId) {
    setStatus("请先生成一次分析结果，再导出 PDF。", "error");
    return;
  }
  const url = `/print-report/${state.currentAnalysisId}`;
  const printWindow = window.open(url, "_blank");
  if (!printWindow) {
    setStatus("浏览器拦截了打印窗口，请允许弹窗后重试。", "error");
    return;
  }
  setStatus("已打开打印页，请在浏览器中选择“另存为 PDF”。", "success");
}

loadSampleButton.addEventListener("click", () => {
  loadSampleResume().catch((error) => {
    setBusy(false);
    setStatus(`载入样例失败：${error.message}`, "error");
  });
});

analyzeButton.addEventListener("click", () => {
  analyzeResume();
});

uploadFileButton.addEventListener("click", () => {
  uploadResumeFile();
});

resumeFileInput.addEventListener("change", () => {
  if (resumeFileInput.files && resumeFileInput.files[0]) {
    setStatus(`已选择文件：${resumeFileInput.files[0].name}`, "success");
  }
});

copyReportButton.addEventListener("click", () => {
  copyReport().catch((error) => {
    setStatus(`复制失败：${error.message}`, "error");
  });
});

downloadReportButton.addEventListener("click", downloadReport);
downloadHtmlButton.addEventListener("click", () => downloadStoredExport("html"));
downloadDocxButton.addEventListener("click", () => downloadStoredExport("docx"));
printPdfButton.addEventListener("click", printReportPdf);
jdSearchButton.addEventListener("click", () => {
  searchJd().catch((error) => {
    setStatus(`JD 检索失败：${error.message}`, "error");
  });
});

window.addEventListener("load", () => {
  Promise.all([initSamples(), refreshHistory(), refreshSystemChecks()])
    .then(() => loadSampleResume("demo_resume_backend.txt"))
    .catch((error) => {
      setStatus(`初始化样例失败：${error.message}`, "error");
    });
});
