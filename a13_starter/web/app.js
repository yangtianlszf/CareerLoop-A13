const state = {
  samples: [],
  currentSampleName: null,
  currentReport: "",
  currentAnalysisId: null,
  latestResult: null,
  schoolDashboard: null,
  benchmark: null,
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
const runBenchmarkButton = document.getElementById("run-benchmark-btn");
const benchmarkStatus = document.getElementById("benchmark-status");
const agentQuestionList = document.getElementById("agent-question-list");
const selfAssessmentForm = document.getElementById("self-assessment-form");
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
const learningSprints = document.getElementById("learning-sprints");
const reviewTargets = document.getElementById("review-targets");
const growthComparison = document.getElementById("growth-comparison");
const competencyRadar = document.getElementById("competency-radar");
const competencyDimensions = document.getElementById("competency-dimensions");
const serviceLoop = document.getElementById("service-loop");
const assessmentTasks = document.getElementById("assessment-tasks");
const resourceMap = document.getElementById("resource-map");
const selfAssessmentSummary = document.getElementById("self-assessment-summary");
const schoolSummaryCards = document.getElementById("school-summary-cards");
const schoolDistribution = document.getElementById("school-distribution");
const schoolFollowUp = document.getElementById("school-follow-up");
const stakeholderViews = document.getElementById("stakeholder-views");
const evaluationMetrics = document.getElementById("evaluation-metrics");
const benchmarkSummaryCards = document.getElementById("benchmark-summary-cards");
const benchmarkVerdict = document.getElementById("benchmark-verdict");
const benchmarkCases = document.getElementById("benchmark-cases");
const technicalModules = document.getElementById("technical-modules");
const careerStrengths = document.getElementById("career-strengths");
const careerRisks = document.getElementById("career-risks");
const recommendedProjects = document.getElementById("recommended-projects");
const productSignature = document.getElementById("product-signature");
const innovationHighlights = document.getElementById("innovation-highlights");
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
  runBenchmarkButton.disabled = isBusy;
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

function collectAgentAnswers() {
  const answers = {};
  agentQuestionList.querySelectorAll("[data-agent-id]").forEach((input) => {
    const value = input.value.trim();
    if (value) {
      answers[input.dataset.agentId] = value;
    }
  });
  return answers;
}

function collectSelfAssessmentAnswers() {
  const answers = {};
  selfAssessmentForm.querySelectorAll("[data-self-assessment-id]:checked").forEach((input) => {
    answers[input.dataset.selfAssessmentId] = Number(input.value);
  });
  return answers;
}

function renderAgentQuestions(questions, existingAnswers = {}) {
  agentQuestionList.innerHTML = "";
  if (!questions || questions.length === 0) {
    agentQuestionList.innerHTML = `<div class="empty-inline compact">当前没有需要补充的追问，可以直接继续分析。</div>`;
    return;
  }

  questions.forEach((question, index) => {
    const card = document.createElement("div");
    card.className = "agent-question-card";
    const inputId = `agent-question-${index}`;
    const preset = existingAnswers?.[question.id] || question.suggested_answer || "";
    card.innerHTML = `
      <label for="${inputId}" class="agent-question-label">${question.question}</label>
      <input
        id="${inputId}"
        class="agent-answer-input"
        type="text"
        data-agent-id="${question.id}"
        placeholder="${escapeHtml(question.placeholder || "请输入你的补充信息")}"
        value="${escapeHtml(preset)}"
      />
      <p class="agent-question-note">${question.rationale || ""}</p>
    `;
    agentQuestionList.appendChild(card);
  });
}

function renderSelfAssessmentForm(selfAssessment) {
  selfAssessmentForm.innerHTML = "";
  const items = selfAssessment?.items || [];
  if (!items.length) {
    selfAssessmentForm.innerHTML = `<div class="empty-inline compact">主推荐岗位生成后，这里会出现岗位自测题。</div>`;
    return;
  }

  items.forEach((item, index) => {
    const card = document.createElement("div");
    card.className = "assessment-card";
    const baseName = `assessment-${item.id}-${index}`;
    const currentValue = item.score === null || item.score === undefined ? null : Number(item.score);
    const options = [
      { label: "待补强", value: 0 },
      { label: "基础", value: 1 },
      { label: "熟练", value: 2 },
    ];
    card.innerHTML = `
      <strong>${item.prompt || "岗位自测题"}</strong>
      <p>${item.focus || ""}</p>
      <div class="assessment-options">
        ${options
          .map(
            (option) => `
              <label class="assessment-option">
                <input
                  type="radio"
                  name="${baseName}"
                  data-self-assessment-id="${item.id}"
                  value="${option.value}"
                  ${currentValue !== null && currentValue === option.value ? "checked" : ""}
                />
                <span>${option.label}</span>
              </label>
            `
          )
          .join("")}
      </div>
    `;
    selfAssessmentForm.appendChild(card);
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
  primaryScoreBadge.textContent = `${plan.primary_score ?? topMatch?.score ?? 0} 分`;
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
  fillList(reviewTargets, plan.next_review_targets || []);
  productSignature.textContent = plan.product_signature || "用一句话讲清这套系统最不一样的地方。";
}

function renderLearningLoop(items) {
  learningSprints.innerHTML = "";
  if (!items || items.length === 0) {
    learningSprints.innerHTML = `<div class="empty-inline compact">当前还没有训练闭环任务。</div>`;
    return;
  }

  items.forEach((item) => {
    const card = document.createElement("article");
    card.className = "sprint-card";
    card.innerHTML = `
      <div class="sprint-top">
        <strong>${item.title || "训练任务"}</strong>
        <span class="tag">${item.type || "训练"}</span>
      </div>
      <p>${item.reason || ""}</p>
      <div class="sprint-deliverable">
        <span class="summary-label">交付物</span>
        <p>${item.deliverable || "暂无"}</p>
      </div>
    `;
    learningSprints.appendChild(card);
  });
}

function renderGrowthComparison(data) {
  if (!data || !data.summary) {
    growthComparison.innerHTML = `<div class="empty-inline compact">还没有成长对比结果。</div>`;
    return;
  }

  const deltas = [];
  if (typeof data.score_delta === "number") {
    deltas.push(`主岗位分数 ${data.score_delta >= 0 ? "+" : ""}${data.score_delta}`);
  }
  if (typeof data.completeness_delta === "number") {
    deltas.push(`完整度 ${data.completeness_delta >= 0 ? "+" : ""}${data.completeness_delta}`);
  }
  if (typeof data.competitiveness_delta === "number") {
    deltas.push(`竞争力 ${data.competitiveness_delta >= 0 ? "+" : ""}${data.competitiveness_delta}`);
  }

  growthComparison.innerHTML = `
    <div class="comparison-card ${data.has_baseline ? "with-baseline" : ""}">
      <p class="comparison-summary">${data.summary}</p>
      ${deltas.length ? `<div class="tag-list">${deltas.map((item) => `<span class="tag">${escapeHtml(item)}</span>`).join("")}</div>` : ""}
      <ul class="comparison-list">
        ${(data.progress_items || []).map((item) => `<li>${escapeHtml(item)}</li>`).join("")}
      </ul>
    </div>
  `;
}

function renderStakeholderViews(items) {
  stakeholderViews.innerHTML = "";
  if (!items || items.length === 0) {
    stakeholderViews.innerHTML = `<div class="empty-inline compact">当前还没有多角色视角。</div>`;
    return;
  }

  items.forEach((item) => {
    const card = document.createElement("article");
    card.className = "stakeholder-card";
    card.innerHTML = `
      <span class="mini-label">${item.role || "角色"}</span>
      <h4>${item.headline || "暂无摘要"}</h4>
      <ul>${(item.items || []).map((line) => `<li>${escapeHtml(line)}</li>`).join("")}</ul>
    `;
    stakeholderViews.appendChild(card);
  });
}

function renderEvaluationMetrics(items) {
  evaluationMetrics.innerHTML = "";
  if (!items || items.length === 0) {
    evaluationMetrics.innerHTML = `<div class="empty-inline compact">当前还没有评测快照。</div>`;
    return;
  }

  items.forEach((item) => {
    const card = document.createElement("article");
    card.className = "metric-snapshot";
    card.innerHTML = `
      <div class="metric-snapshot-top">
        <span>${item.name || "指标"}</span>
        <strong>${item.score ?? 0}</strong>
      </div>
      <p>${item.detail || ""}</p>
    `;
    evaluationMetrics.appendChild(card);
  });
}

function renderBenchmark(data) {
  benchmarkSummaryCards.innerHTML = "";
  benchmarkCases.innerHTML = "";

  if (!data || !(data.summary_cards || []).length) {
    benchmarkVerdict.textContent = "等待运行内置样例验证。";
    benchmarkSummaryCards.innerHTML = `<div class="empty-inline compact">运行样例验证后，这里会展示命中率、解释覆盖和交付就绪度。</div>`;
    return;
  }

  (data.summary_cards || []).forEach((item) => {
    const card = document.createElement("article");
    card.className = "school-summary-card";
    card.innerHTML = `
      <span>${item.label || "指标"}</span>
      <strong>${item.value ?? 0}</strong>
      <p>${item.detail || ""}</p>
    `;
    benchmarkSummaryCards.appendChild(card);
  });

  benchmarkVerdict.innerHTML = `
    <div class="benchmark-verdict-top">
      <span class="mini-label">评测结论</span>
      <strong>${escapeHtml(data.verdict?.label || "待评估")}</strong>
    </div>
    <p>${escapeHtml(data.verdict?.detail || "")}</p>
    <ul class="comparison-list">
      ${(data.judge_notes || []).map((item) => `<li>${escapeHtml(item)}</li>`).join("")}
    </ul>
  `;

  (data.cases || []).forEach((item) => {
    const card = document.createElement("article");
    card.className = "stakeholder-card benchmark-case-card";
    card.innerHTML = `
      <span class="mini-label">${escapeHtml(item.label || "样例")}</span>
      <h4>${escapeHtml(item.primary_role || "未生成")} · ${item.primary_score ?? 0} 分</h4>
      <p class="benchmark-focus">${escapeHtml(item.focus || "")}</p>
      <div class="tag-list">
        <span class="tag ${item.top1_hit ? "tag-hit" : "tag-warn"}">Top1 ${item.top1_hit ? "命中" : "未命中"}</span>
        <span class="tag ${item.top3_hit ? "tag-hit" : "tag-warn"}">Top3 ${item.top3_hit ? "命中" : "未命中"}</span>
        <span class="tag">解释 ${item.explanation_coverage ?? 0}</span>
        <span class="tag">报告 ${item.report_readiness ?? 0}</span>
        <span class="tag">闭环 ${item.loop_readiness ?? 0}</span>
      </div>
      <p>预期主岗：${escapeHtml((item.expected_primary_roles || []).join("、") || "未配置")}</p>
      <p>当前 Top3：${escapeHtml((item.top_roles || []).join("、") || "暂无")}</p>
      <ul class="comparison-list">
        ${(item.observations || []).map((line) => `<li>${escapeHtml(line)}</li>`).join("")}
      </ul>
    `;
    benchmarkCases.appendChild(card);
  });
}

function renderTechnicalModules(items, keywords) {
  technicalModules.innerHTML = "";
  if (!items || items.length === 0) {
    technicalModules.innerHTML = `<div class="empty-inline compact">当前还没有技术表达模块。</div>`;
    return;
  }

  if (keywords && keywords.length) {
    const keywordCard = document.createElement("article");
    keywordCard.className = "innovation-card panel";
    keywordCard.innerHTML = `
      <span class="metric-label">Keyword System</span>
      <h4>技术关键词体系</h4>
      <div class="tag-list">${keywords.map((item) => `<span class="tag">${escapeHtml(item)}</span>`).join("")}</div>
    `;
    technicalModules.appendChild(keywordCard);
  }

  items.forEach((item) => {
    const card = document.createElement("article");
    card.className = "innovation-card panel";
    card.innerHTML = `
      <span class="metric-label">${item.tag || "技术模块"}</span>
      <h4>${item.name || item.title || "技术能力"}</h4>
      <p>${item.detail || ""}</p>
    `;
    technicalModules.appendChild(card);
  });
}

function renderCompetencyDimensions(items) {
  competencyDimensions.innerHTML = "";
  if (!items || items.length === 0) {
    competencyDimensions.innerHTML = `<div class="empty-inline compact">当前还没有胜任力维度。</div>`;
    competencyRadar.innerHTML = `<div class="empty-inline compact">等待生成胜任力可视化。</div>`;
    return;
  }

  renderCompetencyRadar(items);

  items.forEach((item) => {
    const card = document.createElement("article");
    card.className = "metric-snapshot";
    card.innerHTML = `
      <div class="metric-snapshot-top">
        <span>${item.name || "维度"} · ${item.weight || ""}</span>
        <strong>${item.score ?? 0}</strong>
      </div>
      <p>${item.note || ""}</p>
    `;
    competencyDimensions.appendChild(card);
  });
}

function renderCompetencyRadar(items) {
  const width = 320;
  const height = 280;
  const cx = 150;
  const cy = 136;
  const radius = 92;
  const count = items.length;
  const points = items.map((item, index) => {
    const angle = (-Math.PI / 2) + (Math.PI * 2 * index) / count;
    const valueRadius = radius * ((Number(item.score) || 0) / 100);
    return {
      label: item.name || `维度${index + 1}`,
      x: cx + Math.cos(angle) * valueRadius,
      y: cy + Math.sin(angle) * valueRadius,
      ax: cx + Math.cos(angle) * radius,
      ay: cy + Math.sin(angle) * radius,
      lx: cx + Math.cos(angle) * (radius + 24),
      ly: cy + Math.sin(angle) * (radius + 24),
    };
  });

  const polygon = points.map((point) => `${point.x},${point.y}`).join(" ");
  competencyRadar.innerHTML = `
    <svg viewBox="0 0 ${width} ${height}" role="img" aria-label="胜任力雷达图">
      <circle class="radar-ring" cx="${cx}" cy="${cy}" r="${radius}"></circle>
      <circle class="radar-ring" cx="${cx}" cy="${cy}" r="${radius * 0.66}"></circle>
      <circle class="radar-ring" cx="${cx}" cy="${cy}" r="${radius * 0.33}"></circle>
      ${points.map((point) => `<line class="radar-axis" x1="${cx}" y1="${cy}" x2="${point.ax}" y2="${point.ay}"></line>`).join("")}
      <polygon class="radar-shape" points="${polygon}"></polygon>
      ${points
        .map(
          (point) => `
            <circle class="radar-point" cx="${point.x}" cy="${point.y}" r="4"></circle>
            <text class="radar-label" x="${point.lx}" y="${point.ly}">${escapeHtml(point.label)}</text>
          `
        )
        .join("")}
    </svg>
  `;
}

function renderServiceLoop(items) {
  serviceLoop.innerHTML = "";
  if (!items || items.length === 0) {
    serviceLoop.innerHTML = `<div class="empty-inline compact">当前还没有成长闭环阶段。</div>`;
    return;
  }

  items.forEach((item, index) => {
    const card = document.createElement("div");
    card.className = "service-step";
    card.innerHTML = `
      <span class="path-index">0${index + 1}</span>
      <div>
        <strong>${item.stage || "阶段"} · ${item.status || ""}</strong>
        <p>${item.detail || ""}</p>
      </div>
    `;
    serviceLoop.appendChild(card);
  });
}

function renderResourceMap(items) {
  resourceMap.innerHTML = "";
  if (!items || items.length === 0) {
    resourceMap.innerHTML = `<div class="empty-inline compact">当前还没有资源映射建议。</div>`;
    return;
  }

  items.forEach((item) => {
    const card = document.createElement("article");
    card.className = "resource-card";
    card.innerHTML = `
      <div class="resource-top">
        <span class="mini-label">${item.category || "资源"}</span>
        <span class="tag">${item.priority || "中"}</span>
      </div>
      <h4>${item.title || "资源项"}</h4>
      <p>${item.description || ""}</p>
      <div class="sprint-deliverable">
        <span class="summary-label">输出物</span>
        <p>${item.deliverable || ""}</p>
      </div>
    `;
    resourceMap.appendChild(card);
  });
}

function renderSelfAssessmentSummary(data) {
  if (!data || !data.items || data.items.length === 0) {
    selfAssessmentSummary.innerHTML = `<div class="empty-inline compact">完成岗位自测后，这里会展示能力回放结果。</div>`;
    return;
  }

  selfAssessmentSummary.innerHTML = `
    <div class="comparison-card with-baseline">
      <p class="comparison-summary">${data.title || "岗位自测"}：${data.score ?? 0} 分</p>
      <div class="tag-list">
        ${(data.items || [])
          .map((item) => `<span class="tag">${escapeHtml(item.focus || item.prompt)} · ${escapeHtml(item.level || "待补强")}</span>`)
          .join("")}
      </div>
      <ul class="comparison-list">
        <li>${escapeHtml(data.summary || "暂无结论")}</li>
      </ul>
    </div>
  `;
}

function renderSchoolDashboard(data) {
  schoolSummaryCards.innerHTML = "";
  schoolDistribution.innerHTML = "";
  schoolFollowUp.innerHTML = "";
  if (!data || !(data.summary_cards || []).length) {
    schoolSummaryCards.innerHTML = `<div class="empty-inline compact">生成多条历史分析后，这里会自动形成学校运营看板。</div>`;
    return;
  }

  (data.summary_cards || []).forEach((item) => {
    const card = document.createElement("article");
    card.className = "school-summary-card";
    card.innerHTML = `
      <span>${item.label || "指标"}</span>
      <strong>${item.value ?? 0}</strong>
      <p>${item.detail || ""}</p>
    `;
    schoolSummaryCards.appendChild(card);
  });

  const sections = [
    { title: "主岗位 Top5", items: data.top_roles || [] },
    { title: "专业分布 Top5", items: data.major_distribution || [] },
    { title: "城市偏好 Top5", items: data.city_distribution || [] },
  ];

  sections.forEach((section) => {
    const card = document.createElement("div");
    card.className = "distribution-card";
    card.innerHTML = `
      <h4>${section.title}</h4>
      <div class="distribution-list">
        ${(section.items || [])
          .map(
            (item) => `
              <div class="distribution-row">
                <span>${escapeHtml(item.name || "未命名")}</span>
                <strong>${item.count ?? 0}</strong>
              </div>
            `
          )
          .join("")}
      </div>
    `;
    schoolDistribution.appendChild(card);
  });

  const followUps = data.follow_up_students || [];
  if (!followUps.length) {
    schoolFollowUp.innerHTML = `<div class="empty-inline compact">当前没有重点跟进对象。</div>`;
  } else {
    followUps.forEach((item) => {
      const card = document.createElement("div");
      card.className = "follow-up-card";
      card.innerHTML = `
        <strong>${item.name || "学生"} · ${item.primary_role || "待生成"}</strong>
        <p>${item.major || "专业未填写"}｜主岗分 ${item.primary_score ?? 0}｜完整度 ${item.completeness ?? 0}</p>
      `;
      schoolFollowUp.appendChild(card);
    });
  }

  if ((data.advice || []).length) {
    const adviceCard = document.createElement("div");
    adviceCard.className = "distribution-card";
    adviceCard.innerHTML = `
      <h4>运营建议</h4>
      <ul class="comparison-list">
        ${(data.advice || []).map((item) => `<li>${escapeHtml(item)}</li>`).join("")}
      </ul>
    `;
    schoolDistribution.appendChild(adviceCard);
  }
}

function renderInnovationHighlights(items) {
  innovationHighlights.innerHTML = "";
  if (!items || items.length === 0) {
    innovationHighlights.innerHTML = `<div class="empty-inline compact">当前还没有创新锚点。</div>`;
    return;
  }

  items.forEach((item) => {
    const card = document.createElement("article");
    card.className = "innovation-card panel";
    card.innerHTML = `
      <span class="metric-label">${item.tag || "创新"}</span>
      <h4>${item.title || "创新点"}</h4>
      <p>${item.detail || ""}</p>
    `;
    innovationHighlights.appendChild(card);
  });
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
  renderLearningLoop(data.career_plan?.learning_sprints || []);
  renderGrowthComparison(data.career_plan?.growth_comparison || {});
  renderCompetencyDimensions(data.career_plan?.competency_dimensions || []);
  renderServiceLoop(data.career_plan?.service_loop || []);
  fillList(assessmentTasks, data.career_plan?.assessment_tasks || []);
  renderSelfAssessmentForm(data.career_plan?.self_assessment || {});
  renderSelfAssessmentSummary(data.career_plan?.self_assessment || {});
  renderResourceMap(data.career_plan?.resource_map || []);
  renderStakeholderViews(data.career_plan?.stakeholder_views || []);
  renderEvaluationMetrics(data.career_plan?.evaluation_metrics || []);
  renderBenchmark(state.benchmark);
  renderTechnicalModules(data.career_plan?.technical_modules || [], data.career_plan?.technical_keywords || []);
  renderInnovationHighlights(data.career_plan?.innovation_highlights || []);
  renderAgentQuestions(data.career_plan?.agent_questions || [], data.student_profile?.agent_answers || {});
  renderSchoolDashboard(state.schoolDashboard);
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

async function refreshSchoolDashboard() {
  const response = await fetch("/api/school-dashboard?limit=80");
  const data = await response.json();
  state.schoolDashboard = data;
  if (state.latestResult) {
    renderSchoolDashboard(data);
  }
}

async function refreshBenchmark(showLoading = false) {
  if (showLoading) {
    benchmarkStatus.textContent = "正在运行 4 个内置样例验证...";
  }
  const response = await fetch("/api/benchmark?parser_mode=rule");
  const data = await response.json();
  state.benchmark = data;
  benchmarkStatus.textContent = `验证完成：${data.generated_at || "刚刚"} · ${data.verdict?.label || "已生成"}`;
  if (state.latestResult) {
    renderBenchmark(data);
  }
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
        prior_analysis_id: state.currentAnalysisId,
        agent_answers: collectAgentAnswers(),
        self_assessment_answers: collectSelfAssessmentAnswers(),
      }),
    });
    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.error || "请求失败");
    }
    renderResults(data);
    await refreshHistory();
    await refreshSchoolDashboard();
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

runBenchmarkButton.addEventListener("click", () => {
  refreshBenchmark(true).catch((error) => {
    benchmarkStatus.textContent = `验证失败：${error.message}`;
  });
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
  Promise.all([initSamples(), refreshHistory(), refreshSystemChecks(), refreshSchoolDashboard(), refreshBenchmark()])
    .then(() => loadSampleResume("demo_resume_backend.txt"))
    .catch((error) => {
      setStatus(`初始化样例失败：${error.message}`, "error");
    });
});
