// ==========================================
// 全局状态管理
// ==========================================
const state = {
  samples: [],
  currentSampleName: null,
  currentReport: "",
  currentAnalysisId: null,
  latestResult: null,
  schoolDashboard: null,
  benchmark: null,
};

// ==========================================
// DOM 元素安全获取工具 (包含所有原版+新版节点)
// ==========================================
const getEl = (id) => document.getElementById(id);

const dom = {
  // 左侧操作区
  resumeInput: getEl("resume-input"),
  analyzeBtn: getEl("analyze-btn"),
  uploadFileBtn: getEl("upload-file-btn"),
  resumeFileInput: getEl("resume-file-input"),
  parserModeSelect: getEl("parser-mode-select"),
  statusPanel: getEl("status-panel"),
  statusText: getEl("status-text"),
  sampleGallery: getEl("sample-gallery"),
  
  // 容器
  emptyState: getEl("empty-state"),
  resultsContent: getEl("results-content"),
  reportPreview: getEl("report-preview"),
  
  // 画像与评测
  studentMeta: getEl("student-meta"),
  parserMeta: getEl("parser-meta"),
  completenessScore: getEl("completeness-score"),
  competitivenessScore: getEl("competitiveness-score"),
  skillsTags: getEl("skills-tags"),
  softSkillsTags: getEl("soft-skills-tags"),
  evaluationMetrics: getEl("evaluation-metrics"),
  competencyRadar: getEl("radar-chart") || getEl("competency-radar"),
  competencyDimensions: getEl("competency-dimensions"),
  
  // 匹配与规划
  matchCards: getEl("match-cards"),
  primaryRole: getEl("primary-role"),
  primaryScoreBadge: getEl("primary-score-badge"),
  backupRoles: getEl("backup-roles"),
  planOverview: getEl("plan-overview"),
  strengthsList: getEl("strengths-list"),
  risksList: getEl("risks-list"),
  actionPlan30: getEl("action-plan-30"),
  actionPlan90: getEl("action-plan-90"),
  actionPlan180: getEl("action-plan-180"),
  recommendedProjects: getEl("recommended-projects"),
  growthPathList: getEl("growth-path-list"),
  transitionPathList: getEl("transition-path-list"),
  careerGraph: getEl("career-graph"),
  
  // 学习与诊断
  learningSprints: getEl("learning-sprints"),
  reviewTargets: getEl("review-targets"),
  growthComparison: getEl("growth-comparison"),
  resourceMap: getEl("resource-map"),
  stakeholderViews: getEl("stakeholder-views"),
  agentQuestionList: getEl("agent-question-list"),
  selfAssessmentForm: getEl("self-assessment-form"),
  selfAssessmentSummary: getEl("self-assessment-summary"),
  serviceLoop: getEl("service-loop"),
  assessmentTasks: getEl("assessment-tasks"),
  
  // 溯源中心
  evidenceSummary: getEl("evidence-summary"),
  matchedTerms: getEl("matched-terms"),
  evidenceSnippets: getEl("evidence-snippets") || getEl("grounded-evidence-list"),
  templateEvidence: getEl("template-evidence"),
  jdSearchInput: getEl("jd-search-input"),
  jdSearchBtn: getEl("jd-search-btn"),
  jdSearchResults: getEl("jd-search-results"),
  
  // 后台看板
  historyList: getEl("history-list"),
  systemCheckList: getEl("system-check-list"),
  schoolDashboardStats: getEl("school-dashboard-stats") || getEl("school-summary-cards"),
  schoolDistribution: getEl("school-distribution"),
  schoolFollowUp: getEl("school-follow-up"),
  schoolServiceSegments: getEl("school-service-segments"),
  schoolPushRecommendations: getEl("school-push-recommendations"),
  schoolGovernanceMetrics: getEl("school-governance-metrics"),
  schoolAuditQueue: getEl("school-audit-queue"),
  runBenchmarkBtn: getEl("run-benchmark-btn"),
  benchmarkStatus: getEl("benchmark-status"),
  benchmarkSummaryCards: getEl("benchmark-summary-cards"),
  benchmarkVerdict: getEl("benchmark-verdict"),
  benchmarkCases: getEl("benchmark-cases"),
  
  // 技术亮点
  innovationHighlights: getEl("innovation-highlights"),
  technicalModules: getEl("technical-modules"),
  technicalKeywords: getEl("technical-keywords"),
  productSignature: getEl("product-signature"),
  
  // 导出
  copyReportBtn: getEl("copy-report-btn"),
  downloadReportBtn: getEl("download-report-btn"),
  downloadHtmlBtn: getEl("download-html-btn"),
  downloadDocxBtn: getEl("download-docx-btn"),
  printPdfBtn: getEl("print-pdf-btn")
};

// ==========================================
// 基础工具函数
// ==========================================
function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}

function escapeRegex(value) {
  return String(value ?? "").replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}

function highlightTerms(text, terms = []) {
  let html = escapeHtml(text ?? "");
  const uniqueTerms = [...new Set((terms || []).map((i) => String(i || "").trim()).filter(Boolean))].sort((a, b) => b.length - a.length);
  uniqueTerms.forEach((term) => {
    const pattern = new RegExp(escapeRegex(term), "gi");
    html = html.replace(pattern, (match) => `<mark style="background:transparent; color:var(--primary); font-weight:600; border-bottom:1px dashed var(--primary); padding:0;">${match}</mark>`);
  });
  return html;
}

function setStatus(text, type = "idle") {
  if (!dom.statusText || !dom.statusPanel) return;
  dom.statusText.textContent = text;
  dom.statusPanel.className = "status-panel"; 
  if (type === "loading") dom.statusPanel.classList.add("is-loading");
  if (type === "success") dom.statusPanel.classList.add("is-success");
  if (type === "error") dom.statusPanel.classList.add("is-error");
}

function setBusy(isBusy) {
  [dom.analyzeBtn, dom.uploadFileBtn, dom.resumeFileInput, dom.parserModeSelect, dom.runBenchmarkBtn].forEach(el => {
    if(el) el.disabled = isBusy;
  });
}

function fillTagList(container, items, emptyLabel = "暂无数据") {
  if (!container) return; container.innerHTML = "";
  if (!items || items.length === 0) { container.innerHTML = `<span class="tag" style="color:var(--text-muted); background:transparent; border-color:var(--border);">${emptyLabel}</span>`; return; }
  items.forEach((item) => { container.innerHTML += `<span class="tag">${escapeHtml(item)}</span>`; });
}

function fillList(container, items) {
  if (!container) return; container.innerHTML = "";
  const source = items && items.length ? items : ["暂无内容"];
  source.forEach((item) => {
    const li = document.createElement("li"); li.textContent = item; container.appendChild(li);
  });
}

// ==========================================
// 报告生成器 (无损保留Markdown解析)
// ==========================================
function renderMarkdownPreview(markdownText) {
  if (!markdownText || !markdownText.trim()) return '<div style="color:var(--text-muted); text-align:center; padding:40px;">报告生成中...</div>';
  const parts = [];
  let listItems = [];
  const flushList = () => {
    if (!listItems.length) return;
    parts.push(`<ul style="margin:12px 0 24px 24px; color:var(--text-reading);">${listItems.join("")}</ul>`);
    listItems = [];
  };
  markdownText.split(/\r?\n/).forEach((rawLine) => {
    const line = rawLine.trimEnd(); const trimmed = line.trim();
    if (!trimmed) { flushList(); return; }
    if (trimmed.startsWith("# ")) { flushList(); parts.push(`<h1 style="font-family:var(--font-serif); color:var(--primary); margin:32px 0 16px; border-bottom:1px solid var(--border); padding-bottom:8px;">${escapeHtml(trimmed.slice(2).trim())}</h1>`); return; }
    if (trimmed.startsWith("## ")) { flushList(); parts.push(`<h2 style="font-family:var(--font-serif); color:var(--text-main); margin:24px 0 12px;">${escapeHtml(trimmed.slice(3).trim())}</h2>`); return; }
    if (trimmed.startsWith("### ")) { flushList(); parts.push(`<h3 style="color:var(--text-main); margin:16px 0 8px;">${escapeHtml(trimmed.slice(4).trim())}</h3>`); return; }
    if (trimmed.startsWith("- ")) { listItems.push(`<li style="margin-bottom:8px; line-height:1.6;">${escapeHtml(trimmed.slice(2).trim())}</li>`); return; }
    flushList();
    parts.push(`<p style="color:var(--text-reading); line-height:1.7; margin-bottom:16px;">${escapeHtml(trimmed)}</p>`);
  });
  flushList();
  return parts.join("");
}

// ==========================================
// 业务组件渲染逻辑 (全维度无损恢复)
// ==========================================

function initTabs() {
  const tabs = document.querySelectorAll(".tab-btn");
  const panes = document.querySelectorAll(".tab-pane");
  tabs.forEach(tab => {
    tab.addEventListener("click", () => {
      tabs.forEach(t => t.classList.remove("active"));
      panes.forEach(p => p.classList.remove("active"));
      tab.classList.add("active");
      const targetPane = getEl(tab.dataset.target);
      if (targetPane) targetPane.classList.add("active");
      if (tab.dataset.target === "tab-overview" && window.radarChartInstance) window.radarChartInstance.resize();
    });
  });
}

function renderStudentProfile(student) {
  if (dom.studentMeta) {
    const rows = [
      ["姓名", student.name || "未填写"], ["学校", student.school_name || "未填写"],
      ["专业", student.major || "未填写"], ["学历", student.education_level || "未识别"],
      ["意向岗位", (student.target_roles || []).join("、") || "未填写"], ["意向城市", student.city_preference || "未填写"],
    ];
    dom.studentMeta.innerHTML = rows.map(([label, val]) => `<div style="display:flex; justify-content:space-between; padding:8px 0; border-bottom:1px dashed var(--border);"><span style="color:var(--text-muted);">${label}</span><strong style="color:var(--text-main);">${escapeHtml(val)}</strong></div>`).join("");
  }
  if (dom.completenessScore) dom.completenessScore.textContent = student.profile_completeness ?? 0;
  if (dom.competitivenessScore) dom.competitivenessScore.textContent = student.competitiveness_score ?? 0;
  fillTagList(dom.skillsTags, student.skills || []);
  fillTagList(dom.softSkillsTags, student.soft_skills || []);
}

function renderParserMeta(parser) {
  if (!dom.parserMeta || !parser) return;
  dom.parserMeta.innerHTML = [
    `解析引擎：${parser.used_mode?.toUpperCase()}`, `回退机制：${parser.fallback_used ? "已触发" : "未触发"}`,
  ].map(txt => `<span class="tag" style="border-radius:99px; background:var(--surface); border:1px solid var(--border-strong);">${txt}</span>`).join("");
  if (parser.message) dom.parserMeta.innerHTML += `<p style="font-size:0.85rem; color:var(--text-muted); margin-top:8px;">${escapeHtml(parser.message)}</p>`;
}

function createBreakdownLine(label, value) {
  const percent = Math.max(0, Math.min(100, Number(value) || 0));
  return `
    <div style="display:grid; gap:6px; margin-bottom:10px;">
      <div style="display:flex; justify-content:space-between; font-size:0.85rem; color:var(--text-muted);">
        <span>${label}</span><strong style="color:var(--text-main);">${percent}</strong>
      </div>
      <div style="height:6px; background:var(--surface-alt); border-radius:99px; overflow:hidden; border:1px solid var(--border);">
        <div style="height:100%; width:${percent}%; background:var(--primary); border-radius:99px;"></div>
      </div>
    </div>`;
}

function renderMatches(matches) {
  if (!dom.matchCards) return; dom.matchCards.innerHTML = "";
  (matches || []).forEach((match, idx) => {
    dom.matchCards.innerHTML += `
      <div class="card" style="padding:24px; border-radius:16px;">
        <div style="display:flex; justify-content:space-between; align-items:start; margin-bottom:16px;">
          <div>
            <span style="font-size:0.75rem; font-weight:700; color:var(--text-muted); text-transform:uppercase;">Top ${idx + 1}</span>
            <h4 style="margin:4px 0 0 0; color:var(--primary); font-size:1.15rem;">${escapeHtml(match.role_title)}</h4>
          </div>
          <span class="tag" style="background:var(--primary); color:white; font-weight:700; border:none; margin:0;">${match.score} 分</span>
        </div>
        <p style="font-size:0.9rem; color:var(--text-reading); line-height:1.6; margin-bottom:20px; background:var(--surface-alt); padding:12px; border-radius:8px;">${escapeHtml(match.explanation)}</p>
        <div style="margin-bottom:20px;">
          ${createBreakdownLine("基本门槛", match.breakdown?.basic_requirements ?? 0)}
          ${createBreakdownLine("专业技能", match.breakdown?.professional_skills ?? 0)}
          ${createBreakdownLine("职业素养", match.breakdown?.professional_literacy ?? 0)}
          ${createBreakdownLine("发展潜力", match.breakdown?.growth_potential ?? 0)}
        </div>
        <button class="btn btn-dashed full-width" onclick="loadTemplateEvidence('${escapeHtml(match.role_title)}')">核查底层 JD 样本库</button>
      </div>`;
  });
}

function renderCompetencyRadar(items) {
  if (!dom.competencyRadar || !items || items.length === 0) return;
  if (window.radarChartInstance) window.radarChartInstance.dispose();
  window.radarChartInstance = echarts.init(dom.competencyRadar);
  const option = {
    tooltip: { trigger: 'item', backgroundColor: 'rgba(255, 255, 255, 0.95)', borderColor: '#e7e5e4', textStyle: { color: '#292524' }, padding: [12, 16] },
    radar: {
      indicator: items.map(item => ({ name: item.name, max: 100 })), radius: '65%', center: ['50%', '50%'], splitNumber: 4, shape: 'polygon',
      axisName: { color: '#44403c', fontFamily: 'Georgia, serif', fontSize: 13 },
      splitArea: { areaStyle: { color: ['rgba(15, 118, 110, 0.02)', 'rgba(15, 118, 110, 0.04)', 'rgba(15, 118, 110, 0.06)', 'rgba(15, 118, 110, 0.08)'].reverse() } },
      axisLine: { lineStyle: { color: 'rgba(15, 118, 110, 0.2)' } }, splitLine: { lineStyle: { color: 'rgba(15, 118, 110, 0.3)' } }
    },
    series: [{
      type: 'radar',
      data: [{
        value: items.map(item => item.score), name: '胜任力量化', symbol: 'circle', symbolSize: 6,
        itemStyle: { color: '#0f766e', borderColor: '#fff', borderWidth: 2 },
        areaStyle: { color: 'rgba(15, 118, 110, 0.15)' }, lineStyle: { width: 2, color: '#0f766e' }
      }]
    }]
  };
  window.radarChartInstance.setOption(option);
}

function renderCompetencyDimensions(items) {
  if (!dom.competencyDimensions) return; dom.competencyDimensions.innerHTML = "";
  (items || []).forEach(item => {
    dom.competencyDimensions.innerHTML += `
      <div style="display:flex; justify-content:space-between; align-items:center; padding:12px; background:var(--surface-alt); border-radius:12px; margin-bottom:8px; border:1px solid var(--border);">
        <div><strong style="color:var(--text-main); font-size:0.95rem;">${escapeHtml(item.name)}</strong> <span style="font-size:0.8rem; color:var(--text-muted); margin-left:6px;">权 ${escapeHtml(item.weight)}</span></div>
        <strong style="color:var(--primary); font-family:var(--font-serif); font-size:1.2rem;">${item.score}</strong>
      </div>`;
  });
}

function renderCareerPlan(plan, matches) {
  const topMatch = matches && matches.length ? matches[0] : null;
  if (dom.primaryRole) dom.primaryRole.textContent = plan.primary_role || topMatch?.role_title || "待生成";
  if (dom.primaryScoreBadge) dom.primaryScoreBadge.textContent = plan.primary_score ?? topMatch?.score ?? 0;
  if (dom.planOverview) dom.planOverview.textContent = plan.overview || "暂无解读";
  if (dom.productSignature) dom.productSignature.textContent = plan.product_signature || "数据驱动的职业智能体";
  
  fillTagList(dom.backupRoles, plan.backup_roles || []);
  fillList(dom.strengthsList, plan.strengths || []); fillList(dom.risksList, plan.risks || []);
  fillList(dom.actionPlan30, plan.action_plan_30_days || []); fillList(dom.actionPlan90, plan.action_plan_90_days || []); fillList(dom.actionPlan180, plan.action_plan_180_days || []);
  fillList(dom.recommendedProjects, plan.recommended_projects || []); fillList(dom.growthPathList, plan.primary_growth_path || []);
  fillList(dom.transitionPathList, plan.transition_paths || []); fillList(dom.assessmentTasks, plan.assessment_tasks || []);
  fillList(dom.reviewTargets, plan.next_review_targets || []);
}

function renderEvaluationMetrics(items) {
  if (!dom.evaluationMetrics) return; dom.evaluationMetrics.innerHTML = "";
  if (!items || items.length === 0) { dom.evaluationMetrics.innerHTML = `<p class="text-muted">暂无系统置信度评估。</p>`; return; }
  dom.evaluationMetrics.style.display = "grid"; dom.evaluationMetrics.style.gridTemplateColumns = "repeat(auto-fit, minmax(220px, 1fr))"; dom.evaluationMetrics.style.gap = "16px";
  items.forEach((item) => {
    dom.evaluationMetrics.innerHTML += `
      <div style="background:var(--surface-alt); padding:20px; border-radius:16px; border:1px solid var(--border);">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
          <span style="font-size:0.9rem; color:var(--text-muted); font-weight:600;">${escapeHtml(item.name)}</span>
          <strong style="font-size:1.6rem; color:var(--primary); font-family:var(--font-serif);">${item.score ?? 0}</strong>
        </div>
        <p style="font-size:0.85rem; margin:0; color:var(--text-reading); line-height:1.5;">${escapeHtml(item.detail)}</p>
      </div>`;
  });
}

function renderLearningLoop(items) {
  if (!dom.learningSprints) return; dom.learningSprints.innerHTML = "";
  if (!items || items.length === 0) { dom.learningSprints.innerHTML = `<p class="text-muted">暂无专项补强节点。</p>`; return; }
  items.forEach((item) => {
    dom.learningSprints.innerHTML += `
      <div style="background:var(--surface-alt); padding:20px; border-radius:16px; border:1px solid var(--border); margin-bottom:16px;">
        <div style="display:flex; justify-content:space-between; align-items:start; margin-bottom:12px;">
          <strong style="color:var(--text-main); font-size:1.05rem; line-height:1.4;">${escapeHtml(item.title)}</strong>
          <span class="tag" style="border:1px solid var(--primary); color:var(--primary); background:transparent; margin:0;">${escapeHtml(item.type)}</span>
        </div>
        <p style="font-size:0.95rem; color:var(--text-reading); margin-bottom:16px;">${escapeHtml(item.reason)}</p>
        <div style="border-top:1px dashed var(--border-strong); padding-top:12px; font-size:0.9rem;">
          <strong style="color:var(--primary);">交付物闭环：</strong> <span style="color:var(--text-muted);">${escapeHtml(item.deliverable)}</span>
        </div>
      </div>`;
  });
}

function renderGrowthComparison(data) {
  if (!dom.growthComparison) return; dom.growthComparison.innerHTML = "";
  if (!data || !data.summary) { dom.growthComparison.innerHTML = `<p class="text-muted">首轮分析暂无对比，补充问答后将呈现成长曲线。</p>`; return; }
  const tags = [];
  if (data.score_delta) tags.push(`匹配分 ${data.score_delta > 0 ? '+' : ''}${data.score_delta}`);
  if (data.completeness_delta) tags.push(`完整度 ${data.completeness_delta > 0 ? '+' : ''}${data.completeness_delta}`);
  
  dom.growthComparison.innerHTML = `
    <div style="padding:20px; border-radius:16px; background:linear-gradient(135deg, rgba(15, 118, 110, 0.05), var(--surface-alt)); border:1px solid var(--border);">
      <p style="margin:0 0 16px 0; font-size:0.95rem; color:var(--text-main); font-weight:500;">${escapeHtml(data.summary)}</p>
      <div style="margin-bottom:16px;">${tags.map(t => `<span class="tag" style="background:var(--primary); color:white; border:none;">${t}</span>`).join("")}</div>
      <ul style="margin:0; padding-left:20px; color:var(--text-reading); font-size:0.9rem; line-height:1.6;">
        ${(data.progress_items || []).map(i => `<li>${escapeHtml(i)}</li>`).join("")}
      </ul>
    </div>`;
}

function renderResourceMap(items) {
  if (!dom.resourceMap) return; dom.resourceMap.innerHTML = "";
  if (!items || items.length === 0) { dom.resourceMap.innerHTML = `<p class="text-muted">暂无落地资源映射。</p>`; return; }
  dom.resourceMap.style.display = "grid"; dom.resourceMap.style.gridTemplateColumns = "repeat(auto-fit, minmax(280px, 1fr))"; dom.resourceMap.style.gap = "20px";
  items.forEach((item) => {
    const isHigh = item.priority === '高';
    dom.resourceMap.innerHTML += `
      <div style="background:var(--surface); padding:24px; border-radius:16px; border:1px solid ${isHigh ? 'var(--accent)' : 'var(--border)'}; display:flex; flex-direction:column;">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:16px;">
          <span style="font-size:0.8rem; font-weight:600; color:var(--text-muted);">${escapeHtml(item.category)}</span>
          <span style="font-size:0.8rem; color:${isHigh ? 'var(--accent)' : 'var(--text-muted)'}; font-weight:500;">优先级: ${escapeHtml(item.priority)}</span>
        </div>
        <h5 style="margin:0 0 12px 0; color:var(--text-main); font-size:1.1rem; font-weight:600;">${escapeHtml(item.title)}</h5>
        <p style="font-size:0.95rem; color:var(--text-reading); margin-bottom:20px; flex-grow:1;">${escapeHtml(item.description)}</p>
        <div style="background:var(--surface-alt); padding:12px; border-radius:8px; font-size:0.85rem; border-left:3px solid var(--primary);">
          <strong style="color:var(--text-main);">核心产出：</strong> <span style="color:var(--text-muted);">${escapeHtml(item.deliverable)}</span>
        </div>
      </div>`;
  });
}

function renderStakeholderViews(items) {
  if (!dom.stakeholderViews) return; dom.stakeholderViews.innerHTML = "";
  if (!items || items.length === 0) return;
  dom.stakeholderViews.style.display = "grid"; dom.stakeholderViews.style.gridTemplateColumns = "repeat(auto-fit, minmax(260px, 1fr))"; dom.stakeholderViews.style.gap = "16px";
  items.forEach(item => {
    dom.stakeholderViews.innerHTML += `
      <div style="padding:20px; border-radius:16px; border:1px solid var(--border); background:var(--surface-alt);">
        <span style="font-size:0.8rem; font-weight:700; color:var(--primary); text-transform:uppercase;">${escapeHtml(item.role)}</span>
        <h4 style="margin:8px 0 12px 0; font-size:1.05rem; color:var(--text-main);">${escapeHtml(item.headline)}</h4>
        <ul style="margin:0; padding-left:18px; font-size:0.9rem; color:var(--text-muted); line-height:1.6;">
          ${(item.items || []).map(line => `<li>${escapeHtml(line)}</li>`).join("")}
        </ul>
      </div>`;
  });
}

function renderAgentQuestions(questions, existingAnswers = {}) {
  if (!dom.agentQuestionList) return; dom.agentQuestionList.innerHTML = "";
  if (!questions || questions.length === 0) { dom.agentQuestionList.innerHTML = `<p class="text-muted">情境已充分对齐，无需追问。</p>`; return; }
  questions.forEach((q) => {
    const preset = existingAnswers?.[q.id] || q.suggested_answer || "";
    dom.agentQuestionList.innerHTML += `
      <div class="form-group" style="margin-bottom:20px; background:var(--surface-alt); padding:16px; border-radius:16px; border:1px solid var(--border);">
        <label style="display:block; margin-bottom:8px; font-weight:600; color:var(--text-main);">${escapeHtml(q.question)}</label>
        <p style="font-size:0.85rem; color:var(--text-muted); margin-bottom:12px;">${escapeHtml(q.rationale || "补充此信息以提升规划精度")}</p>
        <input type="text" class="input-field" data-agent-id="${q.id}" placeholder="${escapeHtml(q.placeholder)}" value="${escapeHtml(preset)}">
      </div>`;
  });
}

function renderSelfAssessmentForm(selfAssessment) {
  if (!dom.selfAssessmentForm) return; dom.selfAssessmentForm.innerHTML = "";
  const items = selfAssessment?.items || [];
  if (!items.length) { dom.selfAssessmentForm.innerHTML = `<p class="text-muted">待确立基准岗位后生成专业量表。</p>`; return; }
  items.forEach((item, idx) => {
    const baseName = `assessment-${item.id}-${idx}`;
    const score = item.score !== null ? Number(item.score) : null;
    dom.selfAssessmentForm.innerHTML += `
      <div class="form-group" style="background:var(--surface-alt); border:1px solid var(--border); padding:16px; border-radius:16px; margin-bottom:16px;">
        <label style="display:block; margin-bottom:6px; font-weight:600; color:var(--text-main);">${escapeHtml(item.prompt)}</label>
        <p style="font-size:0.85rem; color:var(--primary); margin-bottom:12px;">考察点: ${escapeHtml(item.focus)}</p>
        <div style="display:flex; gap:20px; font-size:0.95rem;">
          <label style="cursor:pointer;"><input type="radio" name="${baseName}" data-self-assessment-id="${item.id}" value="0" ${score === 0 ? 'checked' : ''}> <span style="color:var(--text-muted);">待补强</span></label>
          <label style="cursor:pointer;"><input type="radio" name="${baseName}" data-self-assessment-id="${item.id}" value="1" ${score === 1 ? 'checked' : ''}> <span style="color:var(--text-muted);">基础掌握</span></label>
          <label style="cursor:pointer;"><input type="radio" name="${baseName}" data-self-assessment-id="${item.id}" value="2" ${score === 2 ? 'checked' : ''}> <span style="color:var(--text-muted);">可实战</span></label>
        </div>
      </div>`;
  });
}

function renderSelfAssessmentSummary(data) {
  if (!dom.selfAssessmentSummary) return; dom.selfAssessmentSummary.innerHTML = "";
  if (!data || !data.items || data.items.length === 0) return;
  dom.selfAssessmentSummary.innerHTML = `
    <div style="padding:20px; border-radius:16px; background:var(--surface-alt); border:1px solid var(--border);">
      <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
        <strong style="font-size:1.1rem;">${escapeHtml(data.title)}</strong>
        <span class="tag" style="background:var(--primary); color:white; border:none; margin:0;">${data.score ?? 0} 分</span>
      </div>
      <p style="font-size:0.95rem; color:var(--text-reading); margin-bottom:16px;">${escapeHtml(data.summary)}</p>
      <div>${(data.items || []).map(i => `<span class="tag" style="background:var(--surface); border-color:var(--border-strong);">${escapeHtml(i.focus)}: ${escapeHtml(i.level)}</span>`).join("")}</div>
    </div>`;
}

function renderServiceLoop(items) {
  if (!dom.serviceLoop) return; dom.serviceLoop.innerHTML = "";
  if (!items || items.length === 0) { dom.serviceLoop.innerHTML = `<p class="text-muted">暂无生命周期数据。</p>`; return; }
  items.forEach((item, index) => {
    dom.serviceLoop.innerHTML += `
      <div style="display:flex; margin-bottom:20px; align-items:flex-start;">
        <div style="background:transparent; border:1px solid var(--primary); color:var(--primary); width:32px; height:32px; border-radius:50%; display:flex; align-items:center; justify-content:center; font-size:0.9rem; font-family:var(--font-serif); margin-right:16px; flex-shrink:0;">${index + 1}</div>
        <div>
          <strong style="display:block; margin-bottom:6px; color:var(--text-main); font-size:1.05rem;">${escapeHtml(item.stage)} <span style="font-size:0.8rem; padding:2px 8px; border-radius:99px; background:var(--surface-alt); color:var(--text-muted); border:1px solid var(--border); font-weight:normal; margin-left:8px;">${escapeHtml(item.status)}</span></strong>
          <p style="margin:0; font-size:0.95rem; color:var(--text-reading); line-height:1.6;">${escapeHtml(item.detail)}</p>
        </div>
      </div>`;
  });
}

function renderGroundedEvidence(bundle) {
  if (dom.evidenceSummary) dom.evidenceSummary.textContent = bundle?.summary || "检索队列执行中...";
  fillTagList(dom.matchedTerms, bundle?.query_terms || [], "暂无关联词元");
  if (!dom.evidenceSnippets) return; dom.evidenceSnippets.innerHTML = "";
  const items = bundle?.items || [];
  if (!items.length) { dom.evidenceSnippets.innerHTML = `<div class="empty-inline compact">未命中高维切片。</div>`; return; }
  items.forEach((item) => {
    dom.evidenceSnippets.innerHTML += `
      <div style="margin-bottom:16px; background:var(--surface-alt); padding:20px; border-left:4px solid var(--primary); border-radius:12px; border:1px solid var(--border); border-left-width:4px;">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">
          <strong style="color:var(--text-main); font-size:1.05rem;">${escapeHtml(item.job_title || item.source_title)}</strong>
          <span class="tag" style="background:transparent; border-color:var(--border-strong); margin:0;">相关度: ${item.score ?? 0}</span>
        </div>
        <p style="font-size:0.85rem; color:var(--text-muted); margin-bottom:12px;">${escapeHtml(item.company_name)} | ${escapeHtml(item.city)}</p>
        <p style="margin:0; color:var(--text-reading); font-size:0.95rem; line-height:1.7;">${highlightTerms(item.snippet, item.matched_terms || [])}</p>
      </div>`;
  });
}

function renderTemplateEvidence(data) {
  if (!dom.templateEvidence) return;
  if (!data) { dom.templateEvidence.innerHTML = `<div class="empty-inline compact">请先点击岗位卡片的核查按钮。</div>`; return; }
  const jobs = (data.representative_jobs || []).map(item => `
    <div style="margin-bottom:16px; background:var(--surface-alt); padding:20px; border:1px solid var(--border); border-radius:12px;">
      <strong style="color:var(--text-main); display:block; font-size:1.05rem; margin-bottom:8px;">${escapeHtml(item.company_name)}</strong>
      <p style="font-size:0.85rem; color:var(--text-muted); margin:0 0 12px 0;">${escapeHtml(item.job_title)} | ${escapeHtml(item.city)} | ${escapeHtml(item.salary_range)}</p>
      <p style="margin:0; font-size:0.95rem; color:var(--text-reading); line-height:1.7;">${escapeHtml(item.job_detail)}</p>
    </div>
  `).join("");
  dom.templateEvidence.innerHTML = `
    <div style="margin-bottom:24px; padding-bottom:16px; border-bottom:1px dashed var(--border-strong);">
      <h5 style="margin:0 0 8px 0; color:var(--primary); font-size:1.2rem;">${escapeHtml(data.role_title)}</h5>
      <span style="font-size:0.85rem; color:var(--text-muted);">模板覆盖聚合源: ${data.dataset_job_count}个真实企业样本</span>
    </div>
    ${jobs}
  `;
}

function renderJdSearchResults(items) {
  if (!dom.jdSearchResults) return; dom.jdSearchResults.innerHTML = "";
  if (!items || items.length === 0) { dom.jdSearchResults.innerHTML = `<div class="empty-inline compact">本地库未检索到该词元信息。</div>`; return; }
  items.forEach((item) => {
    dom.jdSearchResults.innerHTML += `
      <div class="card" style="margin-bottom:16px; padding:24px; border-radius:16px;">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
          <strong style="color:var(--text-main); font-size:1.1rem;">${escapeHtml(item.job_title)}</strong>
          <span class="tag" style="background:var(--surface-alt); border-color:var(--primary); color:var(--primary); margin:0;">匹配度: ${item.score}</span>
        </div>
        <p style="font-size:0.85rem; color:var(--text-muted); margin-bottom:16px;">${escapeHtml(item.company_name)} | ${escapeHtml(item.city)} | ${escapeHtml(item.salary_range)}</p>
        <p style="font-size:0.95rem; margin:0; color:var(--text-reading); line-height:1.7;">${escapeHtml(item.job_detail)}</p>
      </div>`;
  });
}

function renderSchoolDashboard(data) {
  if (dom.schoolDashboardStats) {
    dom.schoolDashboardStats.innerHTML = "";
    const cards = data?.summary_cards || [];
    if (!cards.length) dom.schoolDashboardStats.innerHTML = `<div class="empty-inline compact">全局指标聚合中...</div>`;
    else {
      dom.schoolDashboardStats.style.display = "grid"; dom.schoolDashboardStats.style.gridTemplateColumns = "repeat(auto-fit, minmax(200px, 1fr))"; dom.schoolDashboardStats.style.gap = "16px";
      cards.forEach(item => {
        dom.schoolDashboardStats.innerHTML += `
          <div style="background:var(--surface-alt); padding:20px; border-radius:16px; border:1px solid var(--border);">
            <div style="font-size:0.85rem; color:var(--text-muted); margin-bottom:10px; font-weight:600;">${escapeHtml(item.label)}</div>
            <div style="font-size:2rem; font-family:var(--font-serif); color:var(--primary); line-height:1;">${item.value}</div>
            <p style="font-size:0.8rem; color:var(--text-muted); margin:10px 0 0 0;">${escapeHtml(item.detail)}</p>
          </div>`;
      });
    }
  }
  
  // 渲染大盘分布图表列表
  const distributions = [
    { container: dom.schoolDistribution, items: data?.major_distribution || [] },
    { container: dom.schoolPushRecommendations, items: data?.city_distribution || [] },
    { container: dom.schoolServiceSegments, items: data?.service_segments || [] }
  ];
  distributions.forEach(({container, items}) => {
    if (!container) return; container.innerHTML = "";
    items.forEach(item => {
      container.innerHTML += `<div style="display:flex; justify-content:space-between; padding:10px 0; border-bottom:1px dashed var(--border);"><span style="color:var(--text-muted);">${escapeHtml(item.name || item.label || '分类')}</span><strong style="color:var(--text-main);">${item.count ?? item.value ?? 0}</strong></div>`;
    });
  });

  if (dom.schoolFollowUp) {
    dom.schoolFollowUp.innerHTML = "";
    (data?.follow_up_students || []).forEach(student => {
      dom.schoolFollowUp.innerHTML += `<div style="padding:12px; background:var(--surface-alt); border-radius:12px; margin-bottom:8px; border:1px solid var(--border);"><strong>${escapeHtml(student.name)}</strong> <span style="font-size:0.85rem; color:var(--text-muted); margin-left:8px;">${escapeHtml(student.primary_role)} (评 ${student.primary_score}分)</span></div>`;
    });
  }
}

function renderHistory(items) {
  if (!dom.historyList) return; dom.historyList.innerHTML = "";
  if (!items || items.length === 0) { dom.historyList.innerHTML = `<div class="empty-inline compact">系统空置，暂无分析快照。</div>`; return; }
  items.forEach((item) => {
    const btn = document.createElement("button");
    btn.className = "btn btn-outline full-width";
    btn.style.textAlign = "left"; btn.style.marginBottom = "12px"; btn.style.padding = "16px"; btn.style.borderRadius = "16px";
    btn.innerHTML = `<strong style="color:var(--primary); font-size:1.05rem;">#${item.id}</strong> <span style="color:var(--text-main); margin-left:8px; font-weight:600;">${escapeHtml(item.student_name)} → ${escapeHtml(item.primary_role)}</span><br><small style="color:var(--text-muted); display:block; margin-top:8px;">${item.created_at} | ${escapeHtml(item.parser_used_mode)}</small>`;
    btn.addEventListener("click", () => loadAnalysis(item.id));
    dom.historyList.appendChild(btn);
  });
}

function renderSystemChecks(payload) {
  if (!dom.systemCheckList) return; dom.systemCheckList.innerHTML = "";
  (payload.checks || []).forEach((check) => {
    dom.systemCheckList.innerHTML += `
      <li style="margin-bottom:12px; font-size:0.95rem; list-style:none; display:flex; align-items:center; background:var(--surface-alt); padding:12px 16px; border-radius:12px; border:1px solid var(--border);">
        <span style="display:inline-block; width:10px; height:10px; border-radius:50%; background:${check.status === 'success' ? 'var(--success)' : 'var(--danger)'}; margin-right:12px;"></span>
        <strong style="color:var(--text-main); margin-right:12px; min-width:140px;">${escapeHtml(check.name)}</strong> 
        <span style="color:var(--text-muted);">${escapeHtml(check.detail)}</span>
      </li>`;
  });
}

function renderBenchmark(data) {
  if (dom.benchmarkStatus) {
    dom.benchmarkStatus.innerHTML = !data ? `>// 终端挂起，等待指令...` : `<span style="color:#a7f3d0;">$ [SUCCESS]</span> ${escapeHtml(data.verdict?.label || "任务完毕")}<br><span style="color:#64748b;">> ${escapeHtml(data.verdict?.detail || "")}</span>`;
  }
  if (dom.benchmarkSummaryCards) {
    dom.benchmarkSummaryCards.innerHTML = "";
    (data?.summary_cards || []).forEach(item => {
      dom.benchmarkSummaryCards.innerHTML += `<div class="card" style="padding:16px; border-radius:16px;"><span style="font-size:0.85rem; color:var(--text-muted);">${escapeHtml(item.label)}</span><strong style="display:block; font-size:1.6rem; color:var(--primary); margin-top:8px;">${item.value}</strong></div>`;
    });
  }
  if (dom.benchmarkCases) {
    dom.benchmarkCases.innerHTML = "";
    (data?.cases || []).forEach(item => {
      dom.benchmarkCases.innerHTML += `
        <div class="card" style="padding:20px; border-radius:16px; margin-bottom:16px;">
          <div style="display:flex; justify-content:space-between; margin-bottom:12px;">
            <strong style="color:var(--text-main);">${escapeHtml(item.label)}</strong>
            <span class="tag" style="background:var(--surface-alt); margin:0;">${item.primary_score}分 | ${item.primary_role}</span>
          </div>
          <div style="margin-bottom:12px;">${['top1_hit', 'top3_hit'].map(k => `<span class="tag" style="border-color:${item[k] ? 'var(--success)' : 'var(--danger)'}; color:${item[k] ? 'var(--success)' : 'var(--danger)'};">${k.replace('_hit','')} ${item[k] ? '命中' : 'MISS'}</span>`).join("")}</div>
          <ul style="padding-left:18px; margin:0; font-size:0.85rem; color:var(--text-muted); line-height:1.6;">${(item.observations || []).map(o => `<li>${escapeHtml(o)}</li>`).join("")}</ul>
        </div>`;
    });
  }
}

function renderInnovationHighlights(items) {
  if (!dom.innovationHighlights) return; dom.innovationHighlights.innerHTML = "";
  (items || []).forEach(item => {
    dom.innovationHighlights.innerHTML += `
      <div style="margin-bottom:24px; background:var(--surface-alt); padding:20px; border-radius:16px; border:1px solid var(--border);">
        <div style="display:flex; align-items:center; gap:12px; margin-bottom:10px;">
          <strong style="color:var(--text-main); font-size:1.1rem;">${escapeHtml(item.title)}</strong> 
          <span class="tag" style="background:var(--teal-soft); color:var(--primary); border:none; margin:0;">${escapeHtml(item.tag)}</span>
        </div>
        <p style="margin:0; font-size:0.95rem; color:var(--text-reading); line-height:1.7;">${escapeHtml(item.detail)}</p>
      </div>`;
  });
}

function renderTechnicalModules(items, keywords) {
  if (dom.technicalKeywords) fillTagList(dom.technicalKeywords, keywords || []);
  if (!dom.technicalModules) return; dom.technicalModules.innerHTML = "";
  (items || []).forEach(item => {
    dom.technicalModules.innerHTML += `
      <div style="margin-bottom:20px; padding-bottom:16px; border-bottom:1px dashed var(--border-strong);">
        <strong style="color:var(--text-main); font-size:1.05rem;">${escapeHtml(item.name)}</strong> 
        <span class="tag" style="margin-left:8px; background:transparent; border-color:var(--border-strong);">${escapeHtml(item.tag)}</span>
        <p style="margin:10px 0 0 0; font-size:0.95rem; color:var(--text-reading); line-height:1.6;">${escapeHtml(item.detail)}</p>
      </div>`;
  });
}

function renderCareerGraph(student, plan, matches) {
  if (!dom.careerGraph) return;
  const primary = plan.primary_role || matches?.[0]?.role_title || "基准节点";
  const backups = plan.backup_roles || [];
  const path = plan.primary_growth_path || [];
  
  // 使用新的社论风配色渲染 SVG
  const width = 940; const height = 340; const centerY = 148;
  const upperY = 86; const lowerY = 228; const nodeWidth = 150; const nodeHeight = 56;
  
  const nodes = [
    { id: "student", label: student.name || "初始锚点", x: 74, y: centerY, tone: "teal", meta: "当前画像" },
    { id: "primary", label: primary, x: 286, y: centerY, tone: "accent", meta: "首推枢纽" },
  ];
  path.slice(1, 4).forEach((item, i) => nodes.push({ id: `path-${i}`, label: item, x: 510 + i * 160, y: upperY, tone: "teal", meta: "纵向演进" }));
  backups.slice(0, 2).forEach((item, i) => nodes.push({ id: `backup-${i}`, label: item, x: 510 + i * 160, y: lowerY, tone: "muted", meta: "横向发散" }));

  const nodeMap = new Map(nodes.map(n => [n.id, n]));
  const centerYOf = (node) => node.y + nodeHeight / 2;
  const rightEdge = (node) => node.x + nodeWidth;
  const leftEdge = (node) => node.x;

  const lines = [];
  const connect = (fromId, toId, tone, mode = "horizontal") => {
    const from = nodeMap.get(fromId); const to = nodeMap.get(toId);
    if (!from || !to) return;
    if (mode === "diagonal") { lines.push({ x1: rightEdge(from) - 8, y1: centerYOf(from), x2: leftEdge(to) + 8, y2: centerYOf(to), tone }); return; }
    lines.push({ x1: rightEdge(from), y1: centerYOf(from), x2: leftEdge(to), y2: centerYOf(to), tone });
  };

  connect("student", "primary", "accent");
  if (nodeMap.has("path-0")) {
    connect("primary", "path-0", "teal", "diagonal");
    for (let i = 0; i < 2; i++) if (nodeMap.has(`path-${i}`) && nodeMap.has(`path-${i + 1}`)) connect(`path-${i}`, `path-${i + 1}`, "teal");
  }
  if (nodeMap.has("backup-0")) {
    connect("primary", "backup-0", "muted", "diagonal");
    if (nodeMap.has("backup-1")) connect("backup-0", "backup-1", "muted");
  }

  // 映射新配色
  const colorMap = { "accent": "#d97706", "teal": "#0f766e", "muted": "#78716c" };

  dom.careerGraph.innerHTML = `
    <svg viewBox="0 0 ${width} ${height}" style="width:100%; height:auto; min-width:720px; background:var(--surface-alt); border-radius:16px; border:1px solid var(--border);">
      ${lines.map(line => `<line x1="${line.x1}" y1="${line.y1}" x2="${line.x2}" y2="${line.y2}" stroke="${colorMap[line.tone]}" stroke-width="3" stroke-linecap="round" opacity="0.6" />`).join("")}
      ${nodes.map(node => `
        <g transform="translate(${node.x}, ${node.y})">
          <rect rx="28" ry="28" width="${nodeWidth}" height="${nodeHeight}" fill="#ffffff" stroke="${colorMap[node.tone]}" stroke-width="2" style="filter:drop-shadow(0 4px 6px rgba(0,0,0,0.05));"></rect>
          <text x="${nodeWidth / 2}" y="22" fill="#78716c" font-size="11" text-anchor="middle">${node.meta}</text>
          <text x="${nodeWidth / 2}" y="40" fill="#292524" font-size="14" font-weight="700" text-anchor="middle">${node.label}</text>
        </g>
      `).join("")}
    </svg>`;
}

function renderSampleGallery(samples) {
  if (!dom.sampleGallery) return; dom.sampleGallery.innerHTML = "";
  samples.forEach((sample) => {
    const chip = document.createElement("button");
    chip.className = "chip"; chip.textContent = sample.label;
    chip.addEventListener("click", () => loadSampleResume(sample.name));
    dom.sampleGallery.appendChild(chip);
  });
}

// ==========================================
// 核心 API 交互与调度 (全量无损触发)
// ==========================================
async function loadSampleResume(sampleName = null) {
  setBusy(true); setStatus("调度样本资源...", "loading");
  try {
    const url = sampleName ? `/api/demo-resume?name=${encodeURIComponent(sampleName)}` : "/api/demo-resume";
    const response = await fetch(url);
    const data = await response.json();
    if (dom.resumeInput) dom.resumeInput.value = data.resume_text || "";
    state.currentSampleName = data.sample_name || sampleName;
    document.querySelectorAll('#sample-gallery .chip').forEach(chip => {
      chip.style.backgroundColor = chip.textContent === state.currentSampleName ? 'var(--surface)' : 'var(--surface-alt)';
      chip.style.borderColor = chip.textContent === state.currentSampleName ? 'var(--primary)' : 'var(--border)';
      chip.style.color = chip.textContent === state.currentSampleName ? 'var(--primary)' : 'var(--text-muted)';
    });
    setStatus(`样本挂载完毕: ${state.currentSampleName || "default"}`, "success");
  } catch (error) { setStatus(`IO异常: ${error.message}`, "error"); } finally { setBusy(false); }
}

async function analyzeResume() {
  const resumeText = dom.resumeInput?.value.trim();
  if (!resumeText) return setStatus("指令终止：履历流为空，请先录入。", "error");
  setBusy(true); setStatus("开启智能体多阶段并行演推...", "loading");
  
  const agentAnswers = {};
  document.querySelectorAll("[data-agent-id]").forEach(el => { if (el.value.trim()) agentAnswers[el.dataset.agentId] = el.value.trim(); });
  const selfAnswers = {};
  document.querySelectorAll("[data-self-assessment-id]:checked").forEach(el => { selfAnswers[el.dataset.selfAssessmentId] = Number(el.value); });

  try {
    const response = await fetch("/api/career-plan", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ resume_text: resumeText, top_k: 5, parser_mode: dom.parserModeSelect?.value || "llm", sample_name: state.currentSampleName, prior_analysis_id: state.currentAnalysisId, agent_answers: agentAnswers, self_assessment_answers: selfAnswers }),
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || "计算节点拒绝响应");
    
    if (dom.emptyState) dom.emptyState.classList.add("hidden");
    if (dom.resultsContent) dom.resultsContent.classList.remove("hidden");
    
    state.latestResult = data; state.currentAnalysisId = data.analysis_id || data.id || null; state.currentReport = data.report_markdown || "";

    // 🚀 全维度无损重绘流水线
    renderStudentProfile(data.student_profile || {});
    renderParserMeta(data.parser);
    renderMatches(data.matches || []);
    renderCareerPlan(data.career_plan || {}, data.matches || []);
    renderCompetencyRadar(data.career_plan?.competency_dimensions || []);
    renderCompetencyDimensions(data.career_plan?.competency_dimensions || []);
    renderEvaluationMetrics(data.career_plan?.evaluation_metrics || []);
    
    renderLearningLoop(data.career_plan?.learning_sprints || []);
    renderGrowthComparison(data.career_plan?.growth_comparison || {});
    renderResourceMap(data.career_plan?.resource_map || []);
    renderStakeholderViews(data.career_plan?.stakeholder_views || []);
    
    renderAgentQuestions(data.career_plan?.agent_questions || [], data.student_profile?.agent_answers || {});
    renderSelfAssessmentForm(data.career_plan?.self_assessment || {});
    renderSelfAssessmentSummary(data.career_plan?.self_assessment || {});
    renderServiceLoop(data.career_plan?.service_loop || []);
    
    renderGroundedEvidence(data.career_plan?.evidence_bundle || {});
    renderInnovationHighlights(data.career_plan?.innovation_highlights || []);
    renderTechnicalModules(data.career_plan?.technical_modules || [], data.career_plan?.technical_keywords || []);
    renderCareerGraph(data.student_profile || {}, data.career_plan || {}, data.matches || []);
    
    if (dom.reportPreview) dom.reportPreview.innerHTML = renderMarkdownPreview(state.currentReport);

    // 异步更新大盘
    refreshHistory(); refreshSchoolDashboard();

    const topRole = data.career_plan?.primary_role || data.matches?.[0]?.role_title || "";
    if (topRole) {
      if (dom.jdSearchInput) dom.jdSearchInput.value = topRole;
      if (dom.templateEvidence) dom.templateEvidence.innerHTML = `<div class="empty-inline compact">基准底座核验中...</div>`;
      loadTemplateEvidence(topRole).catch(e => console.error(e));
    }
    
    setStatus("决策视图渲染完成，各项指标均已就绪", "success");
    document.querySelector('.tab-btn[data-target="tab-overview"]')?.click();
    
    // 如果用户是在原版的单页流布局下，无需切 Tab 也能自动滚到顶部
    dom.resultsContent?.scrollIntoView({ behavior: "smooth", block: "start" });
  } catch (error) { setStatus(`链路熔断：${error.message}`, "error"); } finally { setBusy(false); }
}

// ==========================================
// 后台数据通信接口
// ==========================================
async function loadAnalysis(analysisId) {
  setBusy(true); setStatus(`拉取历史快照 #${analysisId}...`, "loading");
  try {
    const response = await fetch(`/api/history/${analysisId}`);
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || "云端节点异常");
    if (dom.resumeInput) dom.resumeInput.value = data.resume_text || "";
    setStatus(`快照 #${analysisId} 解包成功，请点击分析以唤醒状态。`, "success");
  } catch (error) { setStatus(`提取失败：${error.message}`, "error"); } finally { setBusy(false); }
}

async function searchJd() {
  const query = dom.jdSearchInput?.value.trim();
  if (!query) return setStatus("参数非法：检索词元不可为空", "error");
  setStatus(`启动向量机匹配：${query}...`, "loading");
  try {
    const response = await fetch(`/api/jd-search?q=${encodeURIComponent(query)}&limit=8`);
    const data = await response.json();
    renderJdSearchResults(data.items || []);
    setStatus(`底层样本切片检索完毕。`, "success");
  } catch (error) { setStatus(`检索节点离线：${error.message}`, "error"); }
}

async function loadTemplateEvidence(roleTitle) {
  try {
    const response = await fetch(`/api/template-evidence?role_title=${encodeURIComponent(roleTitle)}`);
    const data = await response.json();
    if (response.ok) renderTemplateEvidence(data);
  } catch (e) {}
}

async function refreshHistory() { try { const r = await fetch("/api/history"); renderHistory((await r.json()).items || []); } catch (e) {} }
async function refreshSystemChecks() { try { const r = await fetch("/api/system-check"); renderSystemChecks(await r.json()); } catch (e) {} }
async function refreshSchoolDashboard() { try { const r = await fetch("/api/school-dashboard?limit=80"); const d = await r.json(); state.schoolDashboard = d; renderSchoolDashboard(d); } catch (e) {} }
async function refreshBenchmark(showLoading = false) {
  if (showLoading && dom.benchmarkStatus) dom.benchmarkStatus.innerHTML = ">// Benchmark Engine 预热中...";
  try { const r = await fetch("/api/benchmark?parser_mode=rule"); const d = await r.json(); state.benchmark = d; renderBenchmark(d); } catch (e) { if (dom.benchmarkStatus) dom.benchmarkStatus.innerHTML = `> [ERR] Runner Panic：${e.message}`; }
}

// ==========================================
// 应用初始化与监听
// ==========================================
async function initSystem() {
  initTabs();
  window.addEventListener('resize', () => { if (window.radarChartInstance) window.radarChartInstance.resize(); });
  try {
    const [samplesRes] = await Promise.all([ fetch("/api/demo-resumes").then(r => r.json()), refreshSystemChecks(), refreshHistory(), refreshSchoolDashboard(), refreshBenchmark() ]);
    renderSampleGallery(samplesRes.samples || []);
    if (samplesRes.samples && samplesRes.samples.length > 0) loadSampleResume(samplesRes.samples[0].name);
  } catch (error) { console.warn("IO Warning:", error); }
}

if (dom.analyzeBtn) dom.analyzeBtn.addEventListener("click", analyzeResume);
if (dom.uploadFileBtn) dom.uploadFileBtn.addEventListener("click", () => dom.resumeFileInput?.click());
if (dom.jdSearchBtn) dom.jdSearchBtn.addEventListener("click", searchJd);
if (dom.runBenchmarkBtn) dom.runBenchmarkBtn.addEventListener("click", () => refreshBenchmark(true));

if (dom.resumeFileInput) {
  dom.resumeFileInput.addEventListener("change", async () => {
    const file = dom.resumeFileInput.files[0]; if (!file) return;
    const formData = new FormData(); formData.append("resume_file", file);
    setBusy(true); setStatus(`建立外部数据流：${file.name}...`, "loading");
    try {
      const response = await fetch("/api/upload-resume-file", { method: "POST", body: formData });
      const data = await response.json();
      if (!response.ok) throw new Error(data.error || "反序列化受阻");
      dom.resumeInput.value = data.resume_text || "";
      setStatus(`物理数据装载成功，允许向下游分发。`, "success");
    } catch (error) { setStatus(`通道建立失败：${error.message}`, "error"); } finally { setBusy(false); }
  });
}

function downloadStoredExport(format) {
  if (!state.currentAnalysisId) return setStatus("空指针警告：未捕获到有效引用", "error");
  window.open(`/api/export/analysis/${state.currentAnalysisId}?format=${format}`, "_blank");
}

if (dom.downloadDocxBtn) dom.downloadDocxBtn.addEventListener("click", () => downloadStoredExport("docx"));
if (dom.downloadHtmlBtn) dom.downloadHtmlBtn.addEventListener("click", () => downloadStoredExport("html"));
if (dom.printPdfBtn) {
  dom.printPdfBtn.addEventListener("click", () => {
    if (!state.currentAnalysisId) return setStatus("当前容器缺少可打印的数据帧", "error");
    window.open(`/print-report/${state.currentAnalysisId}`, "_blank");
  });
}
if (dom.copyReportBtn) {
  dom.copyReportBtn.addEventListener("click", async () => {
    if (!state.currentReport) return setStatus("存储区为空", "error");
    await navigator.clipboard.writeText(state.currentReport);
    setStatus("Markdown 流已导入系统剪贴板", "success");
  });
}

window.addEventListener("load", initSystem);