// // ==========================================
// // 1. 全局状态管理 (无损保留队友所有状态)
// // ==========================================
// const state = {
//   samples: [],
//   currentSampleName: null,
//   currentReport: "",
//   currentAnalysisId: null,
//   latestResult: null,
//   schoolDashboard: null,
//   benchmark: null,
//   analysisReviews: [], // 队友新增：审批流记录
// };

// // ==========================================
// // 2. DOM 元素安全获取工具 (全面映射所有新老 ID)
// // ==========================================
// const getEl = (id) => document.getElementById(id);

// const dom = {
//   // 左侧操作区
//   resumeInput: getEl("resume-input"),
//   analyzeBtn: getEl("analyze-btn"),
//   uploadFileBtn: getEl("upload-file-btn"),
//   resumeFileInput: getEl("resume-file-input"),
//   parserModeSelect: getEl("parser-mode-select"),
//   statusPanel: getEl("status-panel"),
//   statusText: getEl("status-text"),
//   sampleGallery: getEl("sample-gallery"),
  
//   // 容器与 Tabs
//   emptyState: getEl("empty-state"),
//   resultsContent: getEl("results-content"),
//   reportPreview: getEl("report-preview"),
  
//   // Tab 1: 诊断总览
//   primaryRole: getEl("primary-role"),
//   primaryScoreBadge: getEl("primary-score-badge"),
//   backupRoles: getEl("backup-roles"),
//   planOverview: getEl("plan-overview"),
//   strengthsList: getEl("strengths-list"),
//   risksList: getEl("risks-list"),
//   evaluationMetrics: getEl("evaluation-metrics"),
//   competencyRadar: getEl("radar-chart") || getEl("competency-radar"),
//   competencyDimensions: getEl("competency-dimensions"),
//   studentMeta: getEl("student-meta"),
//   parserMeta: getEl("parser-meta"),
//   completenessScore: getEl("completeness-score"),
//   competitivenessScore: getEl("competitiveness-score"),
//   skillsTags: getEl("skills-tags"),
//   softSkillsTags: getEl("soft-skills-tags"),
//   matchCards: getEl("match-cards"),
  
//   // Tab 2: 演进路径
//   actionPlan30: getEl("action-plan-30") || getEl("plan-30"),
//   actionPlan90: getEl("action-plan-90") || getEl("plan-90"),
//   actionPlan180: getEl("action-plan-180") || getEl("plan-180"),
//   recommendedProjects: getEl("recommended-projects"),
//   learningSprints: getEl("learning-sprints"),
//   growthPathList: getEl("growth-path-list") || getEl("growth-path"),
//   transitionPathList: getEl("transition-path-list") || getEl("transition-paths"),
//   resourceMap: getEl("resource-map"),
//   gapBenefitGrid: getEl("gap-benefit-grid"), // 队友新增
//   planSelfChecks: getEl("plan-self-checks"), // 队友新增
//   careerGraph: getEl("career-graph"), // 队友新增
  
//   // Tab 3: 深度诊断
//   agentQuestionList: getEl("agent-question-list"),
//   selfAssessmentForm: getEl("self-assessment-form"),
//   selfAssessmentSummary: getEl("self-assessment-summary"),
//   serviceLoop: getEl("service-loop"),
//   assessmentTasks: getEl("assessment-tasks"),
//   reviewTargets: getEl("review-targets"),
  
//   // Tab 4: 数据溯源
//   evidenceSummary: getEl("evidence-summary") || getEl("grounded-summary"),
//   matchedTerms: getEl("matched-terms") || getEl("grounded-query"),
//   evidenceSnippets: getEl("evidence-snippets") || getEl("grounded-evidence-list"),
//   templateEvidence: getEl("template-evidence"),
//   jdSearchInput: getEl("jd-search-input"),
//   jdSearchBtn: getEl("jd-search-btn"),
//   jdSearchResults: getEl("jd-search-results"),
//   similarCases: getEl("similar-cases"), // 队友新增
  
//   // Tab 5: 运行看板
//   historyList: getEl("history-list"),
//   systemCheckList: getEl("system-check-list"),
//   schoolDashboardStats: getEl("school-dashboard-stats") || getEl("school-summary-cards"),
//   schoolDistribution: getEl("school-distribution"),
//   schoolFollowUp: getEl("school-follow-up"),
//   schoolServiceSegments: getEl("school-service-segments"),
//   schoolPushRecommendations: getEl("school-push-recommendations"),
//   schoolGovernanceMetrics: getEl("school-governance-metrics"),
//   schoolAuditQueue: getEl("school-audit-queue"),
//   runBenchmarkBtn: getEl("run-benchmark-btn"),
//   benchmarkStatus: getEl("benchmark-status"),
//   benchmarkSummaryCards: getEl("benchmark-summary-cards"),
//   benchmarkVerdict: getEl("benchmark-verdict"),
//   benchmarkCases: getEl("benchmark-cases"),
//   innovationHighlights: getEl("innovation-highlights"),
//   technicalModules: getEl("technical-modules"),
//   technicalKeywords: getEl("technical-keywords"),
//   productSignature: getEl("product-signature"),
  
//   // 辅导员审批流 (队友新增)
//   schoolReviewMetrics: getEl("school-review-metrics"),
//   schoolRecentReviews: getEl("school-recent-reviews"),
//   currentReviewAnalysis: getEl("current-review-analysis"),
//   reviewerNameInput: getEl("reviewer-name-input"),
//   reviewerRoleSelect: getEl("reviewer-role-select"),
//   reviewDecisionSelect: getEl("review-decision-select"),
//   reviewNotesInput: getEl("review-notes-input"),
//   submitReviewBtn: getEl("submit-review-btn"),
//   reviewRecords: getEl("review-records"),
  
//   // 导出按钮
//   copyReportBtn: getEl("copy-report-btn"),
//   downloadReportBtn: getEl("download-report-btn"),
//   downloadHtmlBtn: getEl("download-html-btn"),
//   downloadDocxBtn: getEl("download-docx-btn"),
//   printPdfBtn: getEl("print-pdf-btn")
// };

// // ==========================================
// // 3. 基础工具与格式化引擎
// // ==========================================
// function escapeHtml(value) {
//   return String(value ?? "").replaceAll("&", "&amp;").replaceAll("<", "&lt;").replaceAll(">", "&gt;").replaceAll('"', "&quot;").replaceAll("'", "&#39;");
// }

// function escapeRegex(value) {
//   return String(value ?? "").replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
// }

// // 高级社论风词元高亮
// function highlightTerms(text, terms = []) {
//   let html = escapeHtml(text ?? "");
//   const uniqueTerms = [...new Set((terms || []).map((i) => String(i || "").trim()).filter(Boolean))].sort((a, b) => b.length - a.length);
//   uniqueTerms.forEach((term) => {
//     const pattern = new RegExp(escapeRegex(term), "gi");
//     html = html.replace(pattern, (match) => `<mark style="background:transparent; color:var(--primary); font-weight:600; border-bottom:1px dashed var(--primary); padding:0;">${match}</mark>`);
//   });
//   return html;
// }

// // 队友的内联文献引用格式化
// function formatInlineCitations(text) {
//   return escapeHtml(text ?? "").replace(/(\[E\d+\])/g, '<span class="citation-inline">$1</span>');
// }

// // 队友的 Markdown 报告渲染器 (适配了我们的无边框学术阅读排版)
// function renderMarkdownPreview(markdownText) {
//   if (!markdownText || !markdownText.trim()) return '<div class="empty-inline compact">当前还没有生成报告内容。</div>';
//   const parts = [];
//   let listItems = [];
//   const flushList = () => {
//     if (!listItems.length) return;
//     parts.push(`<ul>${listItems.join("")}</ul>`);
//     listItems = [];
//   };

//   markdownText.split(/\r?\n/).forEach((rawLine) => {
//     const line = rawLine.trimEnd();
//     const trimmed = line.trim();
//     if (!trimmed) { flushList(); return; }
//     if (trimmed.startsWith("# ")) { flushList(); parts.push(`<h1>${escapeHtml(trimmed.slice(2).trim())}</h1>`); return; }
//     if (trimmed.startsWith("## ")) { flushList(); parts.push(`<h2>${escapeHtml(trimmed.slice(3).trim())}</h2>`); return; }
//     if (trimmed.startsWith("### ")) { flushList(); parts.push(`<h3>${escapeHtml(trimmed.slice(4).trim())}</h3>`); return; }
//     if (trimmed.startsWith("- ")) { listItems.push(`<li>${escapeHtml(trimmed.slice(2).trim())}</li>`); return; }
//     flushList();
//     parts.push(`<p>${escapeHtml(trimmed)}</p>`);
//   });
//   flushList();
//   return parts.join("");
// }

// // UI 状态控制
// function setStatus(text, type = "idle") {
//   if (!dom.statusText || !dom.statusPanel) return;
//   dom.statusText.textContent = text;
//   dom.statusPanel.className = "status-panel"; 
//   if (type === "loading") dom.statusPanel.classList.add("is-loading");
//   if (type === "success") dom.statusPanel.classList.add("is-success");
//   if (type === "error") dom.statusPanel.classList.add("is-error");
// }

// function setBusy(isBusy) {
//   [dom.analyzeBtn, dom.uploadFileBtn, dom.resumeFileInput, dom.parserModeSelect, dom.runBenchmarkBtn, dom.submitReviewBtn].forEach(el => {
//     if(el) el.disabled = isBusy;
//   });
//   document.querySelectorAll(".sample-card, .history-card").forEach(el => el.disabled = isBusy);
// }

// // ==========================================
// // 4. Tabs 初始化 (职徒未来现代化入口)
// // ==========================================
// function initTabs() {
//   const tabs = document.querySelectorAll(".tab-btn");
//   const panes = document.querySelectorAll(".tab-pane");
//   tabs.forEach(tab => {
//     tab.addEventListener("click", () => {
//       tabs.forEach(t => t.classList.remove("active"));
//       panes.forEach(p => p.classList.remove("active"));
//       tab.classList.add("active");
//       const targetPane = getEl(tab.dataset.target);
//       if (targetPane) targetPane.classList.add("active");
//       if (tab.dataset.target === "tab-overview" && window.radarChartInstance) window.radarChartInstance.resize();
//     });
//   });
// }

// // ==========================================
// // 5. 核心业务组件渲染逻辑 (全面适配灵动胶囊风格)
// // ==========================================
// function fillTagList(container, items, emptyLabel = "暂无数据") {
//   if (!container) return; container.innerHTML = "";
//   if (!items || items.length === 0) { container.innerHTML = `<span class="tag" style="background:transparent; border:1px dashed var(--border-strong); color:var(--text-muted);">${emptyLabel}</span>`; return; }
//   items.forEach((item) => { container.innerHTML += `<span class="tag">${escapeHtml(item)}</span>`; });
// }

// function fillList(container, items) {
//   if (!container) return; container.innerHTML = "";
//   const source = items && items.length ? items : ["暂无数据"];
//   source.forEach((item) => { const li = document.createElement("li"); li.textContent = item; container.appendChild(li); });
// }

// // 队友的新增：学生画像基准
// function renderStudentProfile(student) {
//   if (!dom.studentMeta || !student) return;
//   const rows = [
//     ["姓名", student.name || "未填写"], ["学校", student.school_name || "未填写"],
//     ["专业", student.major || "未填写"], ["学历", student.education_level || "未识别"],
//     ["目标岗位", (student.target_roles || []).join("、") || "未填写"], ["意向城市", student.city_preference || "未填写"]
//   ];
//   dom.studentMeta.innerHTML = rows.map(([l, v]) => `<div style="display:flex; justify-content:space-between; padding:8px 0; border-bottom:1px dashed var(--border);"><span style="color:var(--text-muted); font-size:0.9rem;">${l}</span><strong style="color:var(--text-main); font-size:0.95rem;">${escapeHtml(v)}</strong></div>`).join("");
//   if (dom.completenessScore) dom.completenessScore.textContent = student.profile_completeness ?? 0;
//   if (dom.competitivenessScore) dom.competitivenessScore.textContent = student.competitiveness_score ?? 0;
//   if (dom.skillsTags) fillTagList(dom.skillsTags, student.skills || []);
//   if (dom.softSkillsTags) fillTagList(dom.softSkillsTags, student.soft_skills || []);
// }

// function renderParserMeta(parser) {
//   if (!dom.parserMeta || !parser) return;
//   const items = [`请求模式：${parser.requested_mode}`, `实际解析：${parser.used_mode.toUpperCase()}`, `回退状态：${parser.fallback_used ? "已触发" : "未触发"}`];
//   dom.parserMeta.innerHTML = items.map(i => `<span class="tag" style="border:1px solid var(--border-strong); background:transparent;">${i}</span>`).join("");
//   if (parser.message) dom.parserMeta.innerHTML += `<p style="font-size:0.85rem; color:var(--text-muted); margin-top:8px; line-height:1.6;">${escapeHtml(parser.message)}</p>`;
// }

// function createBreakdownLine(label, value) {
//   const percent = Math.max(0, Math.min(100, Number(value) || 0));
//   return `
//     <div style="margin-bottom:10px;">
//       <div style="display:flex; justify-content:space-between; font-size:0.85rem; color:var(--text-muted); margin-bottom:6px;">
//         <span>${label}</span><strong style="color:var(--text-main);">${percent}</strong>
//       </div>
//       <div style="height:6px; background:var(--surface-alt); border-radius:99px; overflow:hidden; border:1px solid var(--border);">
//         <div style="height:100%; width:${percent}%; background:linear-gradient(90deg, var(--primary), #60a5fa); border-radius:99px;"></div>
//       </div>
//     </div>`;
// }

// // 匹配详情长卡片 (队友改进版)
// function renderMatches(matches) {
//   if (!dom.matchCards) return; dom.matchCards.innerHTML = "";
//   (matches || []).forEach((match, idx) => {
//     dom.matchCards.innerHTML += `
//       <div class="card" style="padding:24px; margin-bottom:16px;">
//         <div style="display:flex; justify-content:space-between; align-items:start; margin-bottom:16px;">
//           <div>
//             <span class="mini-label">Top ${idx + 1}</span>
//             <h4 style="margin:4px 0 0 0; color:var(--primary); font-size:1.15rem;">${escapeHtml(match.role_title)}</h4>
//           </div>
//           <span class="tag" style="background:var(--primary); color:white; border:none; font-weight:600; padding:6px 12px; font-size:0.9rem;">${match.score} 分 · ${match.confidence_label || "中"}</span>
//         </div>
//         <p style="font-size:0.95rem; color:var(--text-main); line-height:1.6; margin-bottom:12px;">${escapeHtml(match.summary || "暂无岗位摘要")}</p>
//         <p style="font-size:0.9rem; color:var(--primary); line-height:1.6; margin-bottom:20px; background:rgba(15, 118, 110, 0.05); padding:12px 16px; border-radius:12px;">${formatInlineCitations(match.explanation || "暂无解释")}</p>
//         <div style="margin-bottom:24px;">
//           ${createBreakdownLine("基础要求", match.breakdown?.basic_requirements ?? 0)}
//           ${createBreakdownLine("专业技能", match.breakdown?.professional_skills ?? 0)}
//           ${createBreakdownLine("职业素养", match.breakdown?.professional_literacy ?? 0)}
//           ${createBreakdownLine("成长潜力", match.breakdown?.growth_potential ?? 0)}
//         </div>
//         <div style="margin-bottom:16px;">
//           <span class="summary-label" style="display:block; margin-bottom:8px;">优势亮点</span>
//           <div class="chip-group">${(match.strengths || []).slice(0,3).map(i => `<span class="tag" style="background:rgba(4, 120, 87, 0.05); border-color:rgba(4, 120, 87, 0.2); color:var(--success);">${escapeHtml(i)}</span>`).join("") || '<span class="tag">暂无</span>'}</div>
//         </div>
//         <div style="margin-bottom:16px;">
//           <span class="summary-label" style="display:block; margin-bottom:8px;">核心差距</span>
//           <div class="chip-group">${(match.gaps || []).slice(0,3).map(i => `<span class="tag" style="background:rgba(185, 28, 28, 0.05); border-color:rgba(185, 28, 28, 0.2); color:var(--danger);">${escapeHtml(i)}</span>`).join("") || '<span class="tag">暂无</span>'}</div>
//         </div>
//         <button class="btn btn-dashed full-width" style="margin-top:8px;" onclick="loadTemplateEvidence('${escapeHtml(match.role_title)}')">查阅官方底层 JD 样本</button>
//       </div>`;
//   });
// }

// function renderCareerPlan(plan, matches) {
//   const topMatch = matches && matches.length ? matches[0] : null;
//   if (dom.primaryRole) dom.primaryRole.textContent = plan.primary_role || topMatch?.role_title || "待生成";
//   if (dom.primaryScoreBadge) dom.primaryScoreBadge.textContent = plan.primary_score ?? topMatch?.score ?? 0;
//   if (dom.planOverview) dom.planOverview.innerHTML = formatInlineCitations(plan.overview || "暂无解读");
  
//   fillTagList(dom.backupRoles, plan.backup_roles || []);
//   fillTagList(dom.transitionPathList, plan.transition_paths || []);
//   fillList(dom.strengthsList, plan.strengths || []); 
//   fillList(dom.risksList, plan.risks || []);
//   fillList(dom.actionPlan30, plan.action_plan_30_days || []); 
//   fillList(dom.actionPlan90, plan.action_plan_90_days || []); 
//   fillList(dom.actionPlan180, plan.action_plan_180_days || []);
//   fillList(dom.recommendedProjects, plan.recommended_projects || []); 
//   fillList(dom.assessmentTasks, plan.assessment_tasks || []);
//   fillList(dom.reviewTargets, plan.next_review_targets || []);
  
//   if (dom.productSignature) dom.productSignature.textContent = plan.product_signature || "数据驱动的职业智能体";

//   if (dom.growthPathList) {
//     dom.growthPathList.innerHTML = "";
//     (plan.primary_growth_path || []).forEach((item, index) => {
//       dom.growthPathList.innerHTML += `
//         <div style="display:flex; align-items:center; gap:16px; padding:12px 16px; background:var(--surface-alt); border:1px solid var(--border); border-radius:12px; margin-bottom:10px;">
//           <span style="display:flex; align-items:center; justify-content:center; width:36px; height:36px; border-radius:10px; background:rgba(15, 118, 110, 0.1); color:var(--primary); font-weight:800; font-size:0.85rem;">0${index + 1}</span>
//           <strong style="color:var(--text-main); font-size:1rem;">${escapeHtml(item)}</strong>
//         </div>`;
//     });
//   }
// }

// // 胜任力雷达 (Echarts 社论风)
// function renderCompetencyRadar(items) {
//   const chartDom = dom.competencyRadar;
//   if (!chartDom || !items || items.length === 0) return;
//   if (window.radarChartInstance) window.radarChartInstance.dispose();
//   window.radarChartInstance = echarts.init(chartDom);
  
//   const option = {
//     tooltip: { trigger: 'item', backgroundColor: 'rgba(255, 255, 255, 0.95)', borderColor: '#e7e5e4', padding: [12, 16], textStyle: { color: '#292524' } },
//     radar: {
//       indicator: items.map(item => ({ name: item.name, max: 100 })), radius: '65%', center: ['50%', '50%'], splitNumber: 4, shape: 'polygon',
//       axisName: { color: '#44403c', fontFamily: 'Georgia, serif', fontSize: 13 },
//       splitArea: { areaStyle: { color: ['rgba(15, 118, 110, 0.02)', 'rgba(15, 118, 110, 0.04)', 'rgba(15, 118, 110, 0.06)', 'rgba(15, 118, 110, 0.08)'].reverse() } },
//       axisLine: { lineStyle: { color: 'rgba(15, 118, 110, 0.2)' } }, splitLine: { lineStyle: { color: 'rgba(15, 118, 110, 0.3)' } }
//     },
//     series: [{
//       type: 'radar',
//       data: [{
//         value: items.map(item => item.score), name: '胜任力量化评估', symbol: 'circle', symbolSize: 6,
//         itemStyle: { color: '#0f766e', borderColor: '#fff', borderWidth: 2 },
//         areaStyle: { color: 'rgba(15, 118, 110, 0.15)' }, lineStyle: { width: 2, color: '#0f766e' }
//       }]
//     }]
//   };
//   window.radarChartInstance.setOption(option);
// }

// function renderCompetencyDimensions(items) {
//   if (!dom.competencyDimensions) return; dom.competencyDimensions.innerHTML = "";
//   (items || []).forEach(item => {
//     dom.competencyDimensions.innerHTML += `
//       <div style="background:var(--surface-alt); padding:16px; border-radius:12px; border:1px solid var(--border); margin-bottom:10px;">
//         <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:6px;">
//           <strong style="color:var(--text-main); font-size:0.95rem;">${escapeHtml(item.name)} <span style="font-weight:normal; color:var(--text-muted); font-size:0.8rem; margin-left:6px;">权 ${item.weight || ""}</span></strong>
//           <strong style="color:var(--primary); font-family:var(--font-serif); font-size:1.2rem;">${item.score ?? 0}</strong>
//         </div>
//         <p style="margin:0; font-size:0.85rem; color:var(--text-reading); line-height:1.6;">${escapeHtml(item.note || "")}</p>
//       </div>`;
//   });
// }

// function renderLearningLoop(items) {
//   if (!dom.learningSprints) return; dom.learningSprints.innerHTML = "";
//   if (!items || items.length === 0) { dom.learningSprints.innerHTML = `<div class="empty-inline compact">暂无专项补强节点。</div>`; return; }
//   items.forEach((item) => {
//     dom.learningSprints.innerHTML += `
//       <div style="background:var(--surface-alt); padding:20px; border-radius:16px; border:1px solid var(--border); margin-bottom:16px;">
//         <div style="display:flex; justify-content:space-between; align-items:start; margin-bottom:12px;">
//           <strong style="color:var(--text-main); font-size:1.05rem; line-height:1.4;">${escapeHtml(item.title)}</strong>
//           <span class="tag" style="border:1px solid var(--primary); color:var(--primary); background:transparent; margin:0;">${escapeHtml(item.type)}</span>
//         </div>
//         <p style="font-size:0.95rem; color:var(--text-reading); margin-bottom:16px;">${escapeHtml(item.reason)}</p>
//         <div style="border-top:1px dashed var(--border-strong); padding-top:12px; font-size:0.9rem;">
//           <strong style="color:var(--primary);">交付闭环：</strong> <span style="color:var(--text-muted);">${escapeHtml(item.deliverable)}</span>
//         </div>
//       </div>`;
//   });
// }

// // 队友新增：差距收益分析
// function renderGapBenefitAnalysis(items) {
//   if (!dom.gapBenefitGrid) return; dom.gapBenefitGrid.innerHTML = "";
//   if (!items || items.length === 0) { dom.gapBenefitGrid.innerHTML = `<div class="empty-inline compact">当前还没有差距-收益分析。</div>`; return; }
//   items.forEach((item) => {
//     dom.gapBenefitGrid.innerHTML += `
//       <div class="card gap-benefit-card" style="padding:20px; margin-bottom:16px;">
//         <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
//           <span class="mini-label">${escapeHtml(item.dimension || "维度")}</span>
//           <span class="tag" style="background:rgba(217, 119, 6, 0.1); color:var(--accent); border:none; margin:0; font-weight:700;">+${item.expected_gain ?? 0} 分</span>
//         </div>
//         <h4 style="margin:0 0 8px 0; font-size:1.05rem; color:var(--text-main);">${escapeHtml(item.gap || "差距项")}</h4>
//         <p style="font-size:0.9rem; color:var(--text-muted); margin-bottom:16px;">${escapeHtml(item.detail || "")}</p>
//         <div style="background:var(--surface-alt); border-radius:12px; padding:16px; border:1px solid var(--border);">
//           <p style="margin:0 0 10px 0; font-size:0.9rem; font-weight:600; color:var(--primary);">预计：${item.current_score ?? 0} → ${item.projected_score ?? 0} 分</p>
//           <ul class="feature-list" style="font-size:0.85rem; padding-left:16px; margin-bottom:12px;">
//             <li>${escapeHtml(item.action || "暂无动作")}</li>
//             <li>${escapeHtml(item.expected_evidence || "暂无证据建议")}</li>
//           </ul>
//           <div class="chip-group">${(item.citations || []).map(c => `<span class="tag">${escapeHtml(c)}</span>`).join("")}</div>
//         </div>
//       </div>`;
//   });
// }

// // 队友新增：计划自检
// function renderPlanSelfChecks(items) {
//   if (!dom.planSelfChecks) return; dom.planSelfChecks.innerHTML = "";
//   if (!items || items.length === 0) { dom.planSelfChecks.innerHTML = `<div class="empty-inline compact">当前还没有计划自检结果。</div>`; return; }
//   items.forEach((item) => {
//     const isPass = item.status === "通过";
//     const isWarn = item.status === "关注";
//     const borderColor = isPass ? 'var(--primary)' : (isWarn ? 'var(--accent)' : 'var(--border-strong)');
//     const bgGradient = isPass ? 'linear-gradient(180deg, rgba(15,118,110,0.05), var(--surface))' : (isWarn ? 'linear-gradient(180deg, rgba(217,119,6,0.05), var(--surface))' : 'var(--surface-alt)');
    
//     dom.planSelfChecks.innerHTML += `
//       <div class="card" style="padding:20px; border-radius:16px; border-color:${borderColor}; background:${bgGradient}; margin-bottom:16px;">
//         <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
//           <span style="font-size:0.9rem; color:var(--text-main); font-weight:600;">${escapeHtml(item.name || "自检项")}</span>
//           <strong style="font-size:1.4rem; font-family:var(--font-serif); color:${borderColor};">${item.score ?? 0}</strong>
//         </div>
//         <p style="font-size:0.9rem; color:var(--text-reading); margin:0 0 10px 0;"><strong style="color:${borderColor};">${escapeHtml(item.status || "待检查")}</strong> · ${escapeHtml(item.detail || "")}</p>
//         <p style="font-size:0.85rem; color:var(--text-muted); margin:0;">${escapeHtml(item.action || "")}</p>
//       </div>`;
//   });
// }

// // 队友新增：相似案例参考
// function renderSimilarCases(items) {
//   if (!dom.similarCases) return; dom.similarCases.innerHTML = "";
//   if (!items || items.length === 0) { dom.similarCases.innerHTML = `<div class="empty-inline compact">当前还没有可参考的相似案例。</div>`; return; }
//   items.forEach((item) => {
//     dom.similarCases.innerHTML += `
//       <div class="card" style="padding:20px; border-radius:16px; margin-bottom:16px;">
//         <span class="mini-label">${escapeHtml(item.student_name || "相似案例")}</span>
//         <h4 style="margin:8px 0 12px 0; font-size:1.1rem; color:var(--text-main);">${escapeHtml(item.primary_role || "未生成")} · ${item.primary_score ?? 0} 分</h4>
//         <p style="font-size:0.85rem; color:var(--text-muted); margin-bottom:12px;">${escapeHtml(item.major || "专业未填写")}｜${escapeHtml(item.created_at || "")}｜复核：${escapeHtml(item.review_status || "未复核")}</p>
//         <div class="chip-group" style="margin-bottom:16px;">
//           <span class="tag" style="background:rgba(15,118,110,0.1); color:var(--primary); border:none;">相似度 ${item.similarity_score ?? 0}</span>
//           ${(item.reasons || []).map(r => `<span class="tag">${escapeHtml(r)}</span>`).join("")}
//         </div>
//         <ul class="feature-list" style="font-size:0.9rem; padding-left:16px;"><li>${escapeHtml(item.takeaway || "暂无启发")}</li></ul>
//       </div>`;
//   });
// }

// function renderAgentQuestions(questions, existingAnswers = {}) {
//   if (!dom.agentQuestionList) return; dom.agentQuestionList.innerHTML = "";
//   if (!questions || questions.length === 0) { dom.agentQuestionList.innerHTML = `<div class="empty-inline compact">情境对齐完毕，暂无追问。</div>`; return; }
//   questions.forEach((q) => {
//     const preset = existingAnswers?.[q.id] || q.suggested_answer || "";
//     dom.agentQuestionList.innerHTML += `
//       <div class="form-group" style="margin-bottom:20px; background:var(--surface-alt); padding:20px; border-radius:16px; border:1px solid var(--border);">
//         <label style="display:block; margin-bottom:8px; font-weight:600; color:var(--text-main);">${escapeHtml(q.question)}</label>
//         <p style="font-size:0.85rem; color:var(--text-muted); margin-bottom:16px;">${escapeHtml(q.rationale || "补充此信息以提升规划精度")}</p>
//         <input type="text" class="input-field" data-agent-id="${q.id}" placeholder="${escapeHtml(q.placeholder)}" value="${escapeHtml(preset)}">
//       </div>`;
//   });
// }

// function renderSelfAssessmentForm(selfAssessment) {
//   if (!dom.selfAssessmentForm) return; dom.selfAssessmentForm.innerHTML = "";
//   const items = selfAssessment?.items || [];
//   if (!items.length) { dom.selfAssessmentForm.innerHTML = `<div class="empty-inline compact">待确立基准岗位后生成专业量表。</div>`; return; }
//   items.forEach((item, idx) => {
//     const baseName = `assessment-${item.id}-${idx}`;
//     const currentVal = item.score === null || item.score === undefined ? null : Number(item.score);
//     dom.selfAssessmentForm.innerHTML += `
//       <div class="form-group" style="background:var(--surface-alt); border:1px solid var(--border); padding:20px; border-radius:16px; margin-bottom:16px;">
//         <label style="display:block; margin-bottom:8px; font-weight:600; color:var(--text-reading);">${escapeHtml(item.prompt)}</label>
//         <p style="font-size:0.85rem; color:var(--primary); margin-bottom:16px;">考察点: ${escapeHtml(item.focus)}</p>
//         <div style="display:flex; gap:24px;">
//           <label style="cursor:pointer; display:flex; align-items:center; gap:6px;"><input type="radio" name="${baseName}" data-self-assessment-id="${item.id}" value="0" ${currentVal === 0 ? 'checked' : ''}> <span style="color:var(--text-muted); font-size:0.9rem;">待沉淀</span></label>
//           <label style="cursor:pointer; display:flex; align-items:center; gap:6px;"><input type="radio" name="${baseName}" data-self-assessment-id="${item.id}" value="1" ${currentVal === 1 ? 'checked' : ''}> <span style="color:var(--text-muted); font-size:0.9rem;">已入门</span></label>
//           <label style="cursor:pointer; display:flex; align-items:center; gap:6px;"><input type="radio" name="${baseName}" data-self-assessment-id="${item.id}" value="2" ${currentVal === 2 ? 'checked' : ''}> <span style="color:var(--text-muted); font-size:0.9rem;">可实战</span></label>
//         </div>
//       </div>`;
//   });
// }

// function renderSelfAssessmentSummary(data) {
//   if (!dom.selfAssessmentSummary) return; dom.selfAssessmentSummary.innerHTML = "";
//   if (!data || !data.items || data.items.length === 0) { dom.selfAssessmentSummary.innerHTML = `<div class="empty-inline compact">完成岗位自测后展示雷达回放。</div>`; return; }
//   dom.selfAssessmentSummary.innerHTML = `
//     <div style="padding:20px; border-radius:16px; background:linear-gradient(180deg, rgba(15,118,110,0.05), var(--surface-alt)); border:1px solid var(--border);">
//       <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
//         <strong style="font-size:1.05rem; color:var(--text-main);">${escapeHtml(data.title || "岗位自测")}</strong>
//         <span class="tag" style="background:var(--primary); color:white; border:none; margin:0; font-weight:600;">${data.score ?? 0} 分</span>
//       </div>
//       <p style="font-size:0.95rem; color:var(--text-reading); margin-bottom:16px;">${escapeHtml(data.summary || "暂无结论")}</p>
//       <div class="chip-group">${(data.items || []).map(i => `<span class="tag" style="background:var(--surface); border-color:var(--border-strong);">${escapeHtml(i.focus || i.prompt)}: ${escapeHtml(i.level || "待补强")}</span>`).join("")}</div>
//     </div>`;
// }

// function renderServiceLoop(items) {
//   if (!dom.serviceLoop) return; dom.serviceLoop.innerHTML = "";
//   if (!items || items.length === 0) { dom.serviceLoop.innerHTML = `<div class="empty-inline compact">暂无生命周期数据。</div>`; return; }
//   items.forEach((item, index) => {
//     dom.serviceLoop.innerHTML += `
//       <div style="display:flex; margin-bottom:24px; align-items:flex-start; background:var(--surface-alt); padding:16px; border-radius:16px; border:1px solid var(--border);">
//         <div style="background:transparent; border:1px solid var(--primary); color:var(--primary); width:32px; height:32px; border-radius:50%; display:flex; align-items:center; justify-content:center; font-size:0.9rem; font-weight:700; margin-right:16px; flex-shrink:0;">0${index + 1}</div>
//         <div>
//           <strong style="display:block; margin-bottom:8px; color:var(--text-main); font-size:1.05rem;">${escapeHtml(item.stage || "阶段")} <span class="tag" style="margin-left:8px; font-weight:normal; background:var(--surface);">${escapeHtml(item.status || "")}</span></strong>
//           <p style="margin:0; font-size:0.9rem; color:var(--text-muted); line-height:1.6;">${escapeHtml(item.detail || "")}</p>
//         </div>
//       </div>`;
//   });
// }

// function renderResourceMap(items) {
//   if (!dom.resourceMap) return; dom.resourceMap.innerHTML = "";
//   if (!items || items.length === 0) { dom.resourceMap.innerHTML = `<div class="empty-inline compact">暂无落地资源映射。</div>`; return; }
//   dom.resourceMap.style.display = "grid"; dom.resourceMap.style.gridTemplateColumns = "repeat(auto-fit, minmax(280px, 1fr))"; dom.resourceMap.style.gap = "20px";
//   items.forEach((item) => {
//     const isHigh = item.priority === '高';
//     dom.resourceMap.innerHTML += `
//       <div class="card" style="padding:24px; border-radius:16px; border-color:${isHigh ? 'var(--accent)' : 'var(--border)'}; display:flex; flex-direction:column;">
//         <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:16px;">
//           <span class="mini-label">${escapeHtml(item.category || "资源")}</span>
//           <span class="tag" style="background:transparent; border:none; color:${isHigh ? 'var(--accent)' : 'var(--text-muted)'}; font-weight:600; margin:0;">优先级: ${escapeHtml(item.priority || "中")}</span>
//         </div>
//         <h5 style="margin:0 0 12px 0; color:var(--text-main); font-size:1.1rem; font-weight:600;">${escapeHtml(item.title)}</h5>
//         <p style="font-size:0.95rem; color:var(--text-reading); margin-bottom:20px; flex-grow:1;">${escapeHtml(item.description)}</p>
//         <div style="background:var(--surface-alt); padding:12px; border-radius:8px; font-size:0.85rem; border-left:3px solid var(--primary);">
//           <strong style="color:var(--text-main);">阶段产出：</strong> <span style="color:var(--text-muted);">${escapeHtml(item.deliverable)}</span>
//         </div>
//       </div>`;
//   });
// }

// function renderGroundedEvidence(bundle) {
//   if (dom.evidenceSummary) dom.evidenceSummary.textContent = bundle?.summary || "生成分析后展示证据链摘要。";
//   if (dom.matchedTerms) fillTagList(dom.matchedTerms, bundle?.query_terms || [], "等待生成检索词");
//   if (!dom.evidenceSnippets) return; dom.evidenceSnippets.innerHTML = "";
//   const items = bundle?.items || [];
  
//   if (!items.length) { dom.evidenceSnippets.innerHTML = `<div class="empty-inline compact">本次解析未命中有效切片。</div>`; return; }
  
//   const summaryCard = document.createElement("article");
//   summaryCard.className = "card"; summaryCard.style.padding = "20px"; summaryCard.style.marginBottom = "16px";
//   summaryCard.innerHTML = `
//     <div style="display:flex; justify-content:space-between; margin-bottom:12px;">
//       <div><span class="mini-label">Evidence Hit Rate</span><h4 style="margin:4px 0 0 0; font-size:1.1rem;">${bundle?.evidence_hit_rate ?? 0}% · ${escapeHtml(bundle?.retrieval_mode || "未生成")}</h4></div>
//       <div class="score-badge">${(bundle?.hit_terms || []).length}/${(bundle?.target_terms || []).length || 1}</div>
//     </div>
//     <p style="font-size:0.9rem; color:var(--primary); margin-bottom:6px;">命中术语：${escapeHtml((bundle?.hit_terms || []).join("、") || "无")}</p>
//     <p style="font-size:0.9rem; color:var(--text-muted); margin:0;">目标术语：${escapeHtml((bundle?.target_terms || []).join("、") || "无")}</p>
//   `;
//   dom.evidenceSnippets.appendChild(summaryCard);

//   items.forEach((item) => {
//     dom.evidenceSnippets.innerHTML += `
//       <div class="card" style="margin-bottom:16px; padding:20px; border-left:4px solid var(--primary); border-radius:12px;">
//         <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
//           <strong style="color:var(--text-main); font-size:1.05rem;">${escapeHtml(item.job_title || item.source_title || "证据片段")} <span class="citation-inline">${escapeHtml(item.citation_id || "[E]")}</span></strong>
//           <span class="tag" style="background:transparent; border-color:var(--border-strong); margin:0;">相关度 ${item.score ?? 0}</span>
//         </div>
//         <p style="font-size:0.85rem; color:var(--text-muted); margin-bottom:12px;">${escapeHtml(item.company_name || "岗位模板")}｜${escapeHtml(item.city || "未知")}｜命中词：${highlightTerms((item.matched_terms || []).join("、") || "无", item.matched_terms || [])}</p>
//         <p style="margin:0; color:var(--text-reading); font-size:0.95rem; line-height:1.7;">${highlightTerms(item.snippet || "暂无片段", item.matched_terms || [])}</p>
//       </div>`;
//   });
// }

// function renderTemplateEvidence(data) {
//   if (!dom.templateEvidence) return;
//   if (!data) { dom.templateEvidence.innerHTML = `<div class="empty-inline compact">请先点击匹配卡片的核查按钮。</div>`; return; }
//   const jobs = (data.representative_jobs || []).map(item => `
//     <div class="card" style="margin-bottom:16px; padding:20px; border-radius:12px;">
//       <strong style="color:var(--text-main); display:block; font-size:1.05rem; margin-bottom:8px;">${escapeHtml(item.company_name || "未知企业")}</strong>
//       <p style="font-size:0.85rem; color:var(--text-muted); margin:0 0 12px 0;">${escapeHtml(item.job_title || "")} | ${escapeHtml(item.city || "")} | ${escapeHtml(item.salary_range || "")}</p>
//       <p style="margin:0; font-size:0.95rem; color:var(--text-reading); line-height:1.7;">${escapeHtml(item.job_detail || "暂无详情")}</p>
//     </div>
//   `).join("");
//   dom.templateEvidence.innerHTML = `
//     <div style="margin-bottom:24px; padding-bottom:16px; border-bottom:1px dashed var(--border-strong);">
//       <h5 style="margin:0 0 8px 0; color:var(--primary); font-size:1.2rem;">${escapeHtml(data.role_title)}</h5>
//       <p style="font-size:0.85rem; color:var(--text-muted); margin:0;">源岗位名：${escapeHtml(data.source_title)} ｜ 覆盖底层样本数：${data.dataset_job_count}</p>
//       <div class="chip-group" style="margin-top:12px;">${(data.dataset_evidence?.top_skills || []).slice(0,8).map(i => `<span class="tag">${escapeHtml(i[0])} · ${i[1]}</span>`).join("")}</div>
//     </div>
//     ${jobs || '<div class="empty-inline compact">暂无代表样本。</div>'}
//   `;
// }

// function renderJdSearchResults(items) {
//   if (!dom.jdSearchResults) return; dom.jdSearchResults.innerHTML = "";
//   if (!items || items.length === 0) { dom.jdSearchResults.innerHTML = `<div class="empty-inline compact">本地库未检索到相关 JD。</div>`; return; }
//   items.forEach((item) => {
//     dom.jdSearchResults.innerHTML += `
//       <div class="card" style="margin-bottom:16px; padding:24px; border-radius:16px;">
//         <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
//           <strong style="color:var(--text-main); font-size:1.1rem;">${escapeHtml(item.job_title)}</strong>
//           <span class="tag" style="background:var(--surface-alt); border-color:var(--primary); color:var(--primary); margin:0;">匹配度: ${item.score}</span>
//         </div>
//         <p style="font-size:0.85rem; color:var(--text-muted); margin-bottom:16px;">${escapeHtml(item.company_name)} | ${escapeHtml(item.city)} | ${escapeHtml(item.salary_range)}</p>
//         <p style="font-size:0.95rem; margin:0; color:var(--text-reading); line-height:1.7;">${escapeHtml(item.job_detail)}</p>
//       </div>`;
//   });
// }

// function renderStakeholderViews(items) {
//   if (!dom.stakeholderViews) return; dom.stakeholderViews.innerHTML = "";
//   if (!items || items.length === 0) { dom.stakeholderViews.innerHTML = `<div class="empty-inline compact">当前还没有多角色视角。</div>`; return; }
//   dom.stakeholderViews.style.display = "grid"; dom.stakeholderViews.style.gridTemplateColumns = "repeat(auto-fit, minmax(260px, 1fr))"; dom.stakeholderViews.style.gap = "16px";
//   items.forEach(item => {
//     dom.stakeholderViews.innerHTML += `
//       <div class="card" style="padding:24px; border-radius:16px; background:var(--surface-alt);">
//         <span class="mini-label" style="color:var(--primary);">${escapeHtml(item.role || "角色")}</span>
//         <h4 style="margin:8px 0 12px 0; font-size:1.05rem; color:var(--text-main);">${escapeHtml(item.headline || "摘要")}</h4>
//         <ul class="feature-list" style="font-size:0.9rem; padding-left:18px;">
//           ${(item.items || []).map(line => `<li>${escapeHtml(line)}</li>`).join("")}
//         </ul>
//       </div>`;
//   });
// }

// function renderEvaluationMetrics(items) {
//   if (!dom.evaluationMetrics) return; dom.evaluationMetrics.innerHTML = "";
//   if (!items || items.length === 0) { dom.evaluationMetrics.innerHTML = `<div class="empty-inline compact">暂无评测快照。</div>`; return; }
//   dom.evaluationMetrics.style.display = "grid"; dom.evaluationMetrics.style.gridTemplateColumns = "repeat(auto-fit, minmax(220px, 1fr))"; dom.evaluationMetrics.style.gap = "16px";
//   items.forEach((item) => {
//     dom.evaluationMetrics.innerHTML += `
//       <div class="card" style="background:var(--surface-alt); padding:20px; border-radius:16px;">
//         <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
//           <span style="font-size:0.9rem; color:var(--text-muted); font-weight:600;">${escapeHtml(item.name || "指标")}</span>
//           <strong style="font-size:1.6rem; color:var(--primary); font-family:var(--font-serif);">${item.score ?? 0}</strong>
//         </div>
//         <p style="font-size:0.85rem; margin:0; color:var(--text-reading); line-height:1.5;">${escapeHtml(item.detail || "")}</p>
//       </div>`;
//   });
// }

// // 队友新增：全维度大盘
// function renderSchoolDashboard(data) {
//   if (dom.schoolDashboardStats) {
//     dom.schoolDashboardStats.innerHTML = "";
//     if (!data || !(data.summary_cards || []).length) {
//       dom.schoolDashboardStats.innerHTML = `<div class="empty-inline compact">生成分析后形成学校运营看板。</div>`;
//     } else {
//       dom.schoolDashboardStats.style.display = "grid"; dom.schoolDashboardStats.style.gridTemplateColumns = "repeat(auto-fit, minmax(200px, 1fr))"; dom.schoolDashboardStats.style.gap = "16px";
//       (data.summary_cards || []).forEach(item => {
//         dom.schoolDashboardStats.innerHTML += `
//           <div class="card" style="background:var(--surface-alt); padding:20px; border-radius:16px;">
//             <div style="font-size:0.85rem; color:var(--text-muted); margin-bottom:10px; font-weight:600;">${escapeHtml(item.label)}</div>
//             <div style="font-size:2rem; font-family:var(--font-serif); color:var(--primary); line-height:1;">${item.value}</div>
//             <p style="font-size:0.8rem; color:var(--text-muted); margin:10px 0 0 0;">${escapeHtml(item.detail)}</p>
//           </div>`;
//       });
//     }
//   }
  
//   const distributions = [
//     { container: dom.schoolDistribution, items: data?.major_distribution || [], title: "专业分布" },
//     { container: dom.schoolPushRecommendations, items: data?.city_distribution || [], title: "城市偏好" },
//     { container: dom.schoolServiceSegments, items: data?.service_segments || [], title: "服务分层" }
//   ];
//   distributions.forEach(({container, items, title}) => {
//     if (!container) return; container.innerHTML = "";
//     if (items.length) {
//       items.forEach(item => {
//         container.innerHTML += `<div style="display:flex; justify-content:space-between; padding:10px 0; border-bottom:1px dashed var(--border);"><span style="color:var(--text-muted); font-size:0.9rem;">${escapeHtml(item.name || item.label || '分类')}</span><strong style="color:var(--text-main);">${item.count ?? item.value ?? 0}</strong></div>`;
//       });
//     }
//   });

//   const listRenderers = [
//     { container: dom.schoolFollowUp, items: data?.follow_up_students || [], type: 'student' },
//     { container: dom.schoolAuditQueue, items: data?.audit_queue || [], type: 'audit' }
//   ];
//   listRenderers.forEach(({container, items, type}) => {
//     if (!container) return; container.innerHTML = "";
//     items.forEach(item => {
//       container.innerHTML += `
//         <div class="card" style="padding:16px; border-radius:12px; margin-bottom:12px; background:var(--surface-alt);">
//           <strong style="color:var(--text-main); font-size:1.05rem;">${escapeHtml(item.name || "学生")} · ${escapeHtml(item.primary_role || "未生成")}</strong>
//           <p style="font-size:0.85rem; color:var(--text-muted); margin:8px 0 0 0;">${escapeHtml(item.major || "专业未填写")}｜主岗分 ${item.primary_score ?? 0}｜复核 ${escapeHtml(item.review_status || "待复核")}</p>
//           ${type === 'audit' ? `<p style="font-size:0.85rem; color:var(--accent); margin:6px 0 0 0;">原因：${escapeHtml((item.reasons || []).join("、") || "无")}</p>` : ''}
//         </div>`;
//     });
//   });

//   if (dom.schoolGovernanceMetrics) {
//     dom.schoolGovernanceMetrics.innerHTML = "";
//     (data?.governance_metrics || []).concat(data?.review_metrics || []).forEach(item => {
//       dom.schoolGovernanceMetrics.innerHTML += `
//         <div class="card" style="padding:16px; border-radius:12px; margin-bottom:12px; display:flex; justify-content:space-between; align-items:center;">
//           <span style="font-size:0.9rem; color:var(--text-muted);">${escapeHtml(item.label)}</span>
//           <strong style="font-size:1.2rem; color:var(--primary); font-family:var(--font-serif);">${item.value}</strong>
//         </div>`;
//     });
//   }
// }

// // 队友新增：审批记录列表
// function renderReviewRecords(items) {
//   if (!dom.reviewRecords) return; dom.reviewRecords.innerHTML = "";
//   if (!items || items.length === 0) { dom.reviewRecords.innerHTML = `<div class="empty-inline compact">当前分析还没有老师复核记录。</div>`; return; }
//   items.forEach((item) => {
//     dom.reviewRecords.innerHTML += `
//       <div class="card" style="padding:16px; border-radius:12px; margin-bottom:12px; border-left:4px solid var(--primary);">
//         <strong style="display:block; font-size:1.05rem; color:var(--text-main); margin-bottom:6px;">${escapeHtml(item.reviewer_name || "老师")} · ${escapeHtml(item.decision || "待定")}</strong>
//         <p style="font-size:0.85rem; color:var(--text-muted); margin:0 0 8px 0;">${escapeHtml(item.reviewer_role || "辅导员")}｜${escapeHtml(item.created_at || "")}</p>
//         <p style="font-size:0.95rem; color:var(--text-reading); background:var(--surface-alt); padding:10px; border-radius:8px; margin:0;">${escapeHtml(item.notes || "未填写复核备注")}</p>
//       </div>`;
//   });
// }

// function renderBenchmark(data) {
//   if (dom.benchmarkSummaryCards) dom.benchmarkSummaryCards.innerHTML = "";
//   if (dom.benchmarkCases) dom.benchmarkCases.innerHTML = "";

//   if (!data || !(data.summary_cards || []).length) {
//     if (dom.benchmarkVerdict) dom.benchmarkVerdict.innerHTML = `<div class="terminal-box" style="height:auto;">>// 等待运行内置样例压测...</div>`;
//     if (dom.benchmarkSummaryCards) dom.benchmarkSummaryCards.innerHTML = `<div class="empty-inline compact">运行验证后展示核心指标。</div>`;
//     return;
//   }

//   (data.summary_cards || []).forEach((item) => {
//     dom.benchmarkSummaryCards.innerHTML += `
//       <div class="card" style="padding:20px; border-radius:16px; background:var(--surface-alt);">
//         <span style="font-size:0.85rem; color:var(--text-muted);">${escapeHtml(item.label || "指标")}</span>
//         <strong style="display:block; font-size:1.8rem; color:var(--primary); font-family:var(--font-serif); margin-top:8px;">${item.value ?? 0}</strong>
//       </div>`;
//   });

//   if (dom.benchmarkVerdict) {
//     dom.benchmarkVerdict.innerHTML = `
//       <div class="terminal-box" style="height:auto; border-color:rgba(15,118,110,0.4);">
//         <div style="display:flex; justify-content:space-between; margin-bottom:12px;">
//           <span style="color:#a7f3d0;">$ [SUCCESS] 评测跑通</span>
//           <strong style="color:#fff;">${escapeHtml(data.verdict?.label || "待评估")}</strong>
//         </div>
//         <p style="margin:0 0 12px 0; color:#64748b;">> ${escapeHtml(data.verdict?.detail || "")}</p>
//         <ul style="padding-left:16px; margin:0; color:#94a3b8;">${(data.judge_notes || []).map(i => `<li>${escapeHtml(i)}</li>`).join("")}</ul>
//       </div>`;
//   }

//   (data.cases || []).forEach((item) => {
//     dom.benchmarkCases.innerHTML += `
//       <div class="card" style="padding:24px; border-radius:16px; margin-bottom:16px;">
//         <span class="mini-label" style="display:block; margin-bottom:8px;">${escapeHtml(item.label || "样例")}</span>
//         <h4 style="margin:0 0 12px 0; font-size:1.15rem; color:var(--text-main);">${escapeHtml(item.primary_role || "未生成")} · ${item.primary_score ?? 0} 分</h4>
//         <p style="font-size:0.9rem; color:var(--text-muted); margin-bottom:16px;">${escapeHtml(item.focus || "")}</p>
//         <div class="chip-group" style="margin-bottom:16px;">
//           <span class="tag" style="background:${item.top1_hit ? 'rgba(4,120,87,0.1)' : 'rgba(185,28,28,0.1)'}; color:${item.top1_hit ? 'var(--success)' : 'var(--danger)'}; border:none;">Top1 ${item.top1_hit ? "命中" : "未命中"}</span>
//           <span class="tag" style="background:${item.pass_case ? 'rgba(4,120,87,0.1)' : 'rgba(185,28,28,0.1)'}; color:${item.pass_case ? 'var(--success)' : 'var(--danger)'}; border:none;">通过 ${item.pass_case ? "是" : "否"}</span>
//           <span class="tag">证据 ${item.evidence_hit_rate ?? 0}</span>
//           <span class="tag">回退 ${item.fallback_used ? "是" : "否"}</span>
//         </div>
//         <ul class="feature-list" style="font-size:0.85rem; padding-left:16px; margin:0;">${(item.observations || []).map((line) => `<li>${escapeHtml(line)}</li>`).join("")}</ul>
//       </div>`;
//   });
// }

// function renderInnovationHighlights(items) {
//   if (!dom.innovationHighlights) return; dom.innovationHighlights.innerHTML = "";
//   (items || []).forEach(item => {
//     dom.innovationHighlights.innerHTML += `
//       <div class="card" style="margin-bottom:16px; background:var(--surface-alt); padding:20px; border-radius:16px;">
//         <div style="display:flex; align-items:center; gap:12px; margin-bottom:10px;">
//           <strong style="color:var(--text-main); font-size:1.05rem;">${escapeHtml(item.title)}</strong> 
//           <span class="tag" style="background:rgba(15,118,110,0.1); color:var(--primary); border:none; margin:0;">${escapeHtml(item.tag)}</span>
//         </div>
//         <p style="margin:0; font-size:0.95rem; color:var(--text-reading); line-height:1.7;">${escapeHtml(item.detail)}</p>
//       </div>`;
//   });
// }

// function renderTechnicalModules(items, keywords) {
//   if (dom.technicalKeywords) fillTagList(dom.technicalKeywords, keywords || []);
//   if (!dom.technicalModules) return; dom.technicalModules.innerHTML = "";
//   (items || []).forEach(item => {
//     dom.technicalModules.innerHTML += `
//       <div style="margin-bottom:20px; padding-bottom:16px; border-bottom:1px dashed var(--border-strong);">
//         <strong style="color:var(--text-main); font-size:1.05rem;">${escapeHtml(item.name || item.title)}</strong> 
//         <span class="tag" style="margin-left:8px; background:transparent; border-color:var(--border-strong);">${escapeHtml(item.tag)}</span>
//         <p style="margin:10px 0 0 0; font-size:0.95rem; color:var(--text-reading); line-height:1.6;">${escapeHtml(item.detail)}</p>
//       </div>`;
//   });
// }

// // 队友的 SVG 坐标构建 + 深翠青高级配色重绘
// function renderCareerGraph(student, plan, matches) {
//   if (!dom.careerGraph) return;
//   const primary = plan.primary_role || matches?.[0]?.role_title || "主岗位";
//   const backups = plan.backup_roles || [];
//   const path = plan.primary_growth_path || [];
//   const width = 940; const height = 340; const nodeWidth = 150; const nodeHeight = 56;
//   const centerY = 148; const upperY = 86; const lowerY = 228;

//   const nodes = [
//     { id: "student", label: student.name || "学生", x: 74, y: centerY, tone: "teal", meta: "当前画像" },
//     { id: "primary", label: primary, x: 286, y: centerY, tone: "accent", meta: "主推枢纽" },
//   ];
//   path.slice(1, 4).forEach((item, i) => nodes.push({ id: `path-${i}`, label: item, x: 510 + i * 160, y: upperY, tone: "teal", meta: "纵向演进" }));
//   backups.slice(0, 2).forEach((item, i) => nodes.push({ id: `backup-${i}`, label: item, x: 510 + i * 160, y: lowerY, tone: "muted", meta: "横向转移" }));

//   const nodeMap = new Map(nodes.map(n => [n.id, n]));
//   const centerYOf = (node) => node.y + nodeHeight / 2;
//   const rightEdge = (node) => node.x + nodeWidth;
//   const leftEdge = (node) => node.x;

//   const lines = [];
//   const connect = (fromId, toId, tone, mode = "horizontal") => {
//     const from = nodeMap.get(fromId); const to = nodeMap.get(toId);
//     if (!from || !to) return;
//     if (mode === "diagonal") { lines.push({ x1: rightEdge(from) - 8, y1: centerYOf(from), x2: leftEdge(to) + 8, y2: centerYOf(to), tone }); return; }
//     lines.push({ x1: rightEdge(from), y1: centerYOf(from), x2: leftEdge(to), y2: centerYOf(to), tone });
//   };

//   connect("student", "primary", "accent");
//   if (nodeMap.has("path-0")) {
//     connect("primary", "path-0", "teal", "diagonal");
//     for (let i = 0; i < 2; i++) if (nodeMap.has(`path-${i}`) && nodeMap.has(`path-${i + 1}`)) connect(`path-${i}`, `path-${i + 1}`, "teal");
//   }
//   if (nodeMap.has("backup-0")) {
//     connect("primary", "backup-0", "muted", "diagonal");
//     if (nodeMap.has("backup-1")) connect("backup-0", "backup-1", "muted");
//   }

//   const colorMap = { "accent": "#d97706", "teal": "#0f766e", "muted": "#78716c" };

//   dom.careerGraph.innerHTML = `
//     <svg viewBox="0 0 ${width} ${height}" style="width:100%; height:auto; min-width:720px; background:var(--surface-alt); border-radius:16px; border:1px solid var(--border);">
//       ${lines.map(line => `<line x1="${line.x1}" y1="${line.y1}" x2="${line.x2}" y2="${line.y2}" stroke="${colorMap[line.tone]}" stroke-width="3" stroke-linecap="round" opacity="0.6" />`).join("")}
//       ${nodes.map(node => `
//         <g transform="translate(${node.x}, ${node.y})">
//           <rect rx="28" ry="28" width="${nodeWidth}" height="${nodeHeight}" fill="#ffffff" stroke="${colorMap[node.tone]}" stroke-width="2" style="filter:drop-shadow(0 4px 6px rgba(0,0,0,0.05));"></rect>
//           <text x="${nodeWidth / 2}" y="22" fill="#78716c" font-size="11" text-anchor="middle">${node.meta}</text>
//           <text x="${nodeWidth / 2}" y="40" fill="#292524" font-size="14" font-weight="700" text-anchor="middle">${node.label}</text>
//         </g>
//       `).join("")}
//     </svg>`;
// }

// function renderHistory(items) {
//   if (!dom.historyList) return; dom.historyList.innerHTML = "";
//   if (!items || items.length === 0) { dom.historyList.innerHTML = `<div class="empty-inline compact">暂无归档切片。</div>`; return; }
//   items.forEach((item) => {
//     const btn = document.createElement("button");
//     btn.className = "btn btn-outline full-width history-card";
//     btn.style.textAlign = "left"; btn.style.marginBottom = "12px"; btn.style.padding = "16px"; btn.style.borderRadius = "16px";
//     btn.innerHTML = `<strong style="color:var(--primary); font-size:1.05rem;">#${item.id}</strong> <span style="color:var(--text-main); margin-left:8px; font-weight:600;">${escapeHtml(item.student_name)} → ${escapeHtml(item.primary_role)}</span><br><small style="color:var(--text-muted); display:block; margin-top:8px;">${item.created_at} | ${escapeHtml(item.parser_used_mode)}</small>`;
//     btn.addEventListener("click", () => loadAnalysis(item.id).catch(e => setStatus(`历史提取失败: ${e.message}`, "error")));
//     dom.historyList.appendChild(btn);
//   });
// }

// function renderSystemChecks(payload) {
//   if (!dom.systemCheckList) return; dom.systemCheckList.innerHTML = "";
//   (payload.checks || []).forEach((check) => {
//     dom.systemCheckList.innerHTML += `
//       <li style="margin-bottom:12px; font-size:0.95rem; list-style:none; display:flex; align-items:center; background:var(--surface-alt); padding:12px 16px; border-radius:12px; border:1px solid var(--border);">
//         <span style="display:inline-block; width:10px; height:10px; border-radius:50%; background:${check.status === 'success' ? 'var(--success)' : 'var(--danger)'}; margin-right:12px;"></span>
//         <strong style="color:var(--text-main); margin-right:12px; min-width:140px;">${escapeHtml(check.name)}</strong> 
//         <span style="color:var(--text-muted);">${escapeHtml(check.detail)}</span>
//       </li>`;
//   });
// }

// function renderSampleGallery(samples) {
//   if (!dom.sampleGallery) return; dom.sampleGallery.innerHTML = "";
//   samples.forEach((sample) => {
//     const chip = document.createElement("button");
//     chip.className = "chip sample-card"; chip.dataset.sampleName = sample.name; chip.textContent = sample.label;
//     chip.addEventListener("click", () => loadSampleResume(sample.name).catch(e => setStatus(`载入样例失败: ${e.message}`, "error")));
//     dom.sampleGallery.appendChild(chip);
//   });
//   syncActiveSample();
// }

// function syncActiveSample() {
//   if (!dom.sampleGallery) return;
//   dom.sampleGallery.querySelectorAll(".sample-card").forEach(btn => {
//     const isActive = btn.dataset.sampleName === state.currentSampleName;
//     btn.style.backgroundColor = isActive ? 'var(--surface)' : 'var(--surface-alt)';
//     btn.style.borderColor = isActive ? 'var(--primary)' : 'var(--border)';
//     btn.style.color = isActive ? 'var(--primary)' : 'var(--text-muted)';
//   });
// }

// // 收集表单数据
// function collectAgentAnswers() {
//   const answers = {};
//   if (dom.agentQuestionList) {
//     dom.agentQuestionList.querySelectorAll("[data-agent-id]").forEach(input => {
//       if (input.value.trim()) answers[input.dataset.agentId] = input.value.trim();
//     });
//   }
//   return answers;
// }

// function collectSelfAssessmentAnswers() {
//   const answers = {};
//   if (dom.selfAssessmentForm) {
//     dom.selfAssessmentForm.querySelectorAll("[data-self-assessment-id]:checked").forEach(input => {
//       answers[input.dataset.selfAssessmentId] = Number(input.value);
//     });
//   }
//   return answers;
// }

// // ==========================================
// // 6. 核心主渲染流 (The Master Pipeline)
// // ==========================================
// function renderResults(data) {
//   if (dom.emptyState) dom.emptyState.classList.add("hidden");
//   if (dom.resultsContent) dom.resultsContent.classList.remove("hidden");
  
//   state.latestResult = data;
//   state.currentAnalysisId = data.analysis_id || data.id || null;
//   state.currentReport = data.report_markdown || "";

//   // 执行全维度无损渲染
//   renderStudentProfile(data.student_profile);
//   renderParserMeta(data.parser);
//   renderMatches(data.matches || []);
//   renderGroundedEvidence(data.career_plan?.evidence_bundle || {});
//   renderGapBenefitAnalysis(data.career_plan?.gap_benefit_analysis || []);
//   renderPlanSelfChecks(data.career_plan?.plan_self_checks || []);
//   renderCareerPlan(data.career_plan || {}, data.matches || []);
//   renderLearningLoop(data.career_plan?.learning_sprints || []);
//   renderGrowthComparison(data.career_plan?.growth_comparison || {});
//   renderCompetencyDimensions(data.career_plan?.competency_dimensions || []);
//   renderServiceLoop(data.career_plan?.service_loop || []);
//   renderSelfAssessmentForm(data.career_plan?.self_assessment || {});
//   renderSelfAssessmentSummary(data.career_plan?.self_assessment || {});
//   renderResourceMap(data.career_plan?.resource_map || []);
//   renderSimilarCases(data.career_plan?.similar_cases || []);
//   renderStakeholderViews(data.career_plan?.stakeholder_views || []);
//   renderEvaluationMetrics(data.career_plan?.evaluation_metrics || []);
//   renderTechnicalModules(data.career_plan?.technical_modules || [], data.career_plan?.technical_keywords || []);
//   renderInnovationHighlights(data.career_plan?.innovation_highlights || []);
//   renderAgentQuestions(data.career_plan?.agent_questions || [], data.student_profile?.agent_answers || {});
//   renderCareerGraph(data.student_profile || {}, data.career_plan || {}, data.matches || []);
  
//   // 队友新增：渲染复核状态与 Markdown 预览
//   if (dom.currentReviewAnalysis) {
//     dom.currentReviewAnalysis.textContent = state.currentAnalysisId
//       ? `当前复核锁定：#${state.currentAnalysisId} · ${(data.student_profile?.name || "学生")} · ${(data.career_plan?.primary_role || "未生成")}`
//       : "当前还没有可复核的分析记录。";
//   }
//   state.analysisReviews = data.reviews || [];
//   renderReviewRecords(state.analysisReviews);
//   if (dom.reportPreview) dom.reportPreview.innerHTML = renderMarkdownPreview(state.currentReport);

//   // 异步渲染大盘与看板
//   renderBenchmark(state.benchmark);
//   renderSchoolDashboard(state.schoolDashboard);

//   // 自动触发底层模板加载
//   const topRole = data.career_plan?.primary_role || data.matches?.[0]?.role_title || "";
//   if (topRole) {
//     if (dom.jdSearchInput) dom.jdSearchInput.value = topRole;
//     if (dom.templateEvidence) dom.templateEvidence.innerHTML = `<div class="empty-inline compact">基准底座核验中...</div>`;
//     loadTemplateEvidence(topRole).catch(e => console.warn(e));
//   }

//   // 切回第一个 Tab 并滚动
//   document.querySelector('.tab-btn[data-target="tab-overview"]')?.click();
//   dom.resultsContent?.scrollIntoView({ behavior: "smooth", block: "start" });
// }

// // ==========================================
// // 7. API 网络交互与调度
// // ==========================================
// async function initSamples() {
//   const response = await fetch("/api/demo-resumes");
//   const data = await response.json();
//   state.samples = data.samples || [];
//   renderSampleGallery(state.samples);
// }

// async function refreshHistory() { try { const r = await fetch("/api/history"); renderHistory((await r.json()).items || []); } catch (e) {} }
// async function refreshSystemChecks() { try { const r = await fetch("/api/system-check"); renderSystemChecks(await r.json()); } catch (e) {} }
// async function refreshSchoolDashboard() {
//   try {
//     const r = await fetch("/api/school-dashboard?limit=80");
//     const d = await r.json(); state.schoolDashboard = d;
//     if (state.latestResult) renderSchoolDashboard(d);
//   } catch (e) {}
// }

// async function refreshBenchmark(showLoading = false) {
//   if (showLoading && dom.benchmarkStatus) dom.benchmarkStatus.innerHTML = ">// Benchmark Engine 预热中...";
//   try {
//     const mode = dom.parserModeSelect?.value || "auto";
//     const r = await fetch(`/api/benchmark?parser_mode=${encodeURIComponent(mode)}`);
//     const d = await r.json(); state.benchmark = d;
//     if (dom.benchmarkStatus) dom.benchmarkStatus.innerHTML = `<span style="color:#a7f3d0;">$ [SUCCESS]</span> ${escapeHtml(d.verdict?.label || "跑通")}`;
//     if (state.latestResult) renderBenchmark(d);
//   } catch (e) { if (dom.benchmarkStatus) dom.benchmarkStatus.innerHTML = `> [ERR] Runner Panic：${e.message}`; }
// }

// async function loadReviews(analysisId) {
//   if (!analysisId) { state.analysisReviews = []; renderReviewRecords([]); return; }
//   try {
//     const r = await fetch(`/api/reviews?analysis_id=${encodeURIComponent(analysisId)}`);
//     const d = await r.json(); state.analysisReviews = d.items || [];
//     renderReviewRecords(state.analysisReviews);
//   } catch (e) {}
// }

// async function loadSampleResume(sampleName = null) {
//   setBusy(true); setStatus("调度样本资源...", "loading");
//   const url = sampleName ? `/api/demo-resume?name=${encodeURIComponent(sampleName)}` : "/api/demo-resume";
//   const response = await fetch(url);
//   const data = await response.json();
//   if (dom.resumeInput) dom.resumeInput.value = data.resume_text || "";
//   state.currentSampleName = data.sample_name || sampleName;
//   syncActiveSample();
//   setStatus(`样本挂载完毕: ${state.currentSampleName || "default"}`, "success");
//   setBusy(false);
// }

// async function analyzeResume() {
//   const resumeText = dom.resumeInput?.value.trim();
//   if (!resumeText) return setStatus("指令终止：履历流为空，请先录入。", "error");
//   setBusy(true); setStatus("开启智能体多阶段并行演推...", "loading");

//   try {
//     const response = await fetch("/api/career-plan", {
//       method: "POST", headers: { "Content-Type": "application/json" },
//       body: JSON.stringify({
//         resume_text: resumeText, top_k: 5, parser_mode: dom.parserModeSelect?.value || "auto",
//         sample_name: state.currentSampleName, prior_analysis_id: state.currentAnalysisId,
//         agent_answers: collectAgentAnswers(), self_assessment_answers: collectSelfAssessmentAnswers(),
//       }),
//     });
//     const data = await response.json();
//     if (!response.ok) throw new Error(data.error || "计算节点拒绝响应");
    
//     renderResults(data);
//     await loadReviews(data.analysis_id);
//     await refreshHistory();
//     await refreshSchoolDashboard();
//     setStatus(data.parser ? `分析完成，底层驱动: ${data.parser.used_mode.toUpperCase()}` : "决策视图已刷新", "success");
//   } catch (error) { setStatus(`链路熔断：${error.message}`, "error"); } finally { setBusy(false); }
// }

// async function loadAnalysis(analysisId) {
//   setBusy(true); setStatus(`拉取历史快照 #${analysisId}...`, "loading");
//   try {
//     const response = await fetch(`/api/history/${analysisId}`);
//     const data = await response.json();
//     if (!response.ok) throw new Error(data.error || "云端节点异常");
//     if (dom.resumeInput) dom.resumeInput.value = data.resume_text || "";
//     state.currentSampleName = data.sample_name || null;
//     syncActiveSample();
    
//     // 兼容队友的历史回放数据结构
//     renderResults({
//       analysis_id: data.id, student_profile: data.student_profile, matches: data.matches,
//       career_plan: data.career_plan, report_markdown: data.report_markdown, reviews: data.reviews || [],
//       parser: { requested_mode: data.parser_requested_mode || "unknown", used_mode: data.parser_used_mode || "unknown", fallback_used: false, message: `复原于 ${data.created_at}` }
//     });
//     await loadReviews(data.id);
//     setStatus(`快照 #${analysisId} 解包成功。`, "success");
//   } catch (error) { setStatus(`提取失败：${error.message}`, "error"); } finally { setBusy(false); }
// }

// async function searchJd() {
//   const query = dom.jdSearchInput?.value.trim();
//   if (!query) return setStatus("参数非法：检索词元不可为空", "error");
//   setStatus(`启动向量机匹配：${query}...`, "loading");
//   try {
//     const response = await fetch(`/api/jd-search?q=${encodeURIComponent(query)}&limit=8`);
//     const data = await response.json();
//     renderJdSearchResults(data.items || []);
//     setStatus(`底层样本切片检索完毕。`, "success");
//   } catch (error) { setStatus(`检索节点离线：${error.message}`, "error"); }
// }

// async function loadTemplateEvidence(roleTitle) {
//   try {
//     const response = await fetch(`/api/template-evidence?role_title=${encodeURIComponent(roleTitle)}`);
//     const data = await response.json();
//     if (response.ok) renderTemplateEvidence(data);
//   } catch (e) {}
// }

// async function uploadResumeFile() {
//   const file = dom.resumeFileInput?.files[0];
//   if (!file) return setStatus("请先选择本地文件", "error");
//   const formData = new FormData(); formData.append("resume_file", file);
//   setBusy(true); setStatus(`建立外部数据流：${file.name}...`, "loading");
//   try {
//     const response = await fetch("/api/upload-resume-file", { method: "POST", body: formData });
//     const data = await response.json();
//     if (!response.ok) throw new Error(data.error || "反序列化受阻");
//     if (dom.resumeInput) dom.resumeInput.value = data.resume_text || "";
//     state.currentSampleName = null; syncActiveSample();
//     setStatus(data.message || `物理数据装载成功。`, "success");
//   } catch (error) { setStatus(`通道建立失败：${error.message}`, "error"); } finally { setBusy(false); }
// }

// // 队友新增：提交复核
// async function submitReview() {
//   if (!state.currentAnalysisId) return setStatus("空引用：请先锁定一条分析结果再提交审批", "error");
//   const reviewerName = dom.reviewerNameInput?.value.trim();
//   if (!reviewerName) return setStatus("非法提交：复核人署名不可为空", "error");

//   setBusy(true); setStatus("正在提交治理留痕...", "loading");
//   try {
//     const response = await fetch("/api/reviews", {
//       method: "POST", headers: { "Content-Type": "application/json" },
//       body: JSON.stringify({
//         analysis_id: state.currentAnalysisId, reviewer_name: reviewerName,
//         reviewer_role: dom.reviewerRoleSelect?.value, decision: dom.reviewDecisionSelect?.value,
//         notes: dom.reviewNotesInput?.value.trim()
//       }),
//     });
//     const data = await response.json();
//     if (!response.ok) throw new Error(data.error || "提交流水线故障");
//     state.analysisReviews = data.items || [];
//     renderReviewRecords(state.analysisReviews);
//     if (dom.reviewNotesInput) dom.reviewNotesInput.value = "";
//     await refreshSchoolDashboard();
//     setStatus("复核审批已完成上链。", "success");
//   } catch (error) { setStatus(`治理请求被拒：${error.message}`, "error"); } finally { setBusy(false); }
// }

// // ==========================================
// // 8. 事件绑定与初始化
// // ==========================================
// if (dom.analyzeBtn) dom.analyzeBtn.addEventListener("click", analyzeResume);
// if (dom.uploadFileBtn) dom.uploadFileBtn.addEventListener("click", uploadResumeFile);
// if (dom.jdSearchBtn) dom.jdSearchBtn.addEventListener("click", searchJd);
// if (dom.runBenchmarkBtn) dom.runBenchmarkBtn.addEventListener("click", () => refreshBenchmark(true));
// if (dom.submitReviewBtn) dom.submitReviewBtn.addEventListener("click", submitReview);

// if (dom.resumeFileInput) {
//   dom.resumeFileInput.addEventListener("change", () => {
//     if (dom.resumeFileInput.files && dom.resumeFileInput.files[0]) setStatus(`文件待命：${dom.resumeFileInput.files[0].name}`, "success");
//   });
// }

// function downloadStoredExport(format) {
//   if (!state.currentAnalysisId) return setStatus("缺失有效数据帧，无法执行序列化", "error");
//   window.open(`/api/export/analysis/${state.currentAnalysisId}?format=${format}`, "_blank");
// }

// if (dom.downloadDocxBtn) dom.downloadDocxBtn.addEventListener("click", () => downloadStoredExport("docx"));
// if (dom.downloadHtmlBtn) dom.downloadHtmlBtn.addEventListener("click", () => downloadStoredExport("html"));
// if (dom.printPdfBtn) dom.printPdfBtn.addEventListener("click", () => {
//   if (!state.currentAnalysisId) return setStatus("画布为空，拒绝执行渲染", "error");
//   window.open(`/print-report/${state.currentAnalysisId}`, "_blank");
// });
// if (dom.downloadReportBtn) dom.downloadReportBtn.addEventListener("click", () => {
//   if (!state.currentReport) return setStatus("Markdown AST为空", "error");
//   const blob = new Blob([state.currentReport], { type: "text/markdown;charset=utf-8" });
//   const url = URL.createObjectURL(blob);
//   const link = document.createElement("a"); link.href = url; link.download = "career_plan_report.md";
//   link.click(); URL.revokeObjectURL(url); setStatus("数据流已推送到本地磁盘。", "success");
// });
// if (dom.copyReportBtn) dom.copyReportBtn.addEventListener("click", async () => {
//   if (!state.currentReport) return setStatus("无法抓取文本", "error");
//   await navigator.clipboard.writeText(state.currentReport); setStatus("AST 数据已装载进系统剪贴板。", "success");
// });

// window.addEventListener("load", () => {
//   initTabs();
//   window.addEventListener('resize', () => { if (window.radarChartInstance) window.radarChartInstance.resize(); });
//   Promise.all([initSamples(), refreshHistory(), refreshSystemChecks(), refreshSchoolDashboard(), refreshBenchmark()])
//     .then(() => loadSampleResume("demo_resume_backend.txt"))
//     .catch((error) => console.warn("IO Warning:", error));
// });


// ==========================================
// 1. 全局状态与获取器
// ==========================================
const state = { samples: [], currentSampleName: null, currentReport: "", currentAnalysisId: null, latestResult: null, schoolDashboard: null, benchmark: null, analysisReviews: [] };
const getEl = (id) => document.getElementById(id);

const dom = {
  resumeInput: getEl("resume-input"), analyzeBtn: getEl("analyze-btn"), uploadFileBtn: getEl("upload-file-btn"),
  resumeFileInput: getEl("resume-file-input"), parserModeSelect: getEl("parser-mode-select"), statusPanel: getEl("status-panel"),
  statusText: getEl("status-text"), sampleGallery: getEl("sample-gallery"), emptyState: getEl("empty-state"),
  resultsContent: getEl("results-content"), primaryRole: getEl("primary-role"), primaryScoreBadge: getEl("primary-score-badge"),
  backupRoles: getEl("backup-roles"), planOverview: getEl("plan-overview"), strengthsList: getEl("strengths-list"),
  risksList: getEl("risks-list"), evaluationMetrics: getEl("evaluation-metrics"), competencyRadar: getEl("radar-chart"),
  competencyDimensions: getEl("competency-dimensions"), actionPlan30: getEl("action-plan-30"), actionPlan90: getEl("action-plan-90"),
  actionPlan180: getEl("action-plan-180"), recommendedProjects: getEl("recommended-projects"), learningSprints: getEl("learning-sprints"),
  growthPathList: getEl("growth-path-list"), transitionPathList: getEl("transition-path-list"), resourceMap: getEl("resource-map"),
  gapBenefitGrid: getEl("gap-benefit-grid"), planSelfChecks: getEl("plan-self-checks"), careerGraph: getEl("career-graph"),
  agentQuestionList: getEl("agent-question-list"), selfAssessmentForm: getEl("self-assessment-form"), selfAssessmentSummary: getEl("self-assessment-summary"),
  serviceLoop: getEl("service-loop"), assessmentTasks: getEl("assessment-tasks"), reviewTargets: getEl("review-targets"),
  evidenceSummary: getEl("evidence-summary"), matchedTerms: getEl("matched-terms"), evidenceSnippets: getEl("evidence-snippets"),
  templateEvidence: getEl("template-evidence"), jdSearchInput: getEl("jd-search-input"), jdSearchBtn: getEl("jd-search-btn"),
  jdSearchResults: getEl("jd-search-results"), similarCases: getEl("similar-cases"), historyList: getEl("history-list"),
  systemCheckList: getEl("system-check-list"), schoolDashboardStats: getEl("school-dashboard-stats"), schoolDistribution: getEl("school-distribution"),
  schoolFollowUp: getEl("school-follow-up"), schoolServiceSegments: getEl("school-service-segments"), schoolPushRecommendations: getEl("school-push-recommendations"),
  schoolGovernanceMetrics: getEl("school-governance-metrics"), schoolAuditQueue: getEl("school-audit-queue"), runBenchmarkBtn: getEl("run-benchmark-btn"),
  benchmarkStatus: getEl("benchmark-status"), benchmarkSummaryCards: getEl("benchmark-summary-cards"), benchmarkVerdict: getEl("benchmark-verdict"),
  benchmarkCases: getEl("benchmark-cases"), innovationHighlights: getEl("innovation-highlights"), technicalModules: getEl("technical-modules"),
  technicalKeywords: getEl("technical-keywords"), schoolReviewMetrics: getEl("school-review-metrics"), schoolRecentReviews: getEl("school-recent-reviews"),
  currentReviewAnalysis: getEl("current-review-analysis"), reviewerNameInput: getEl("reviewer-name-input"), reviewerRoleSelect: getEl("reviewer-role-select"),
  reviewDecisionSelect: getEl("review-decision-select"), reviewNotesInput: getEl("review-notes-input"), submitReviewBtn: getEl("submit-review-btn"),
  reviewRecords: getEl("review-records"), reportPreview: getEl("report-preview"), printPdfBtn: getEl("print-pdf-btn"),
  sysStatusBtn: getEl("system-status-btn"), mockNotif: getEl("mock-notification")
};

// ==========================================
// 2. 工具集与格式化
// ==========================================
function escapeHtml(value) { return String(value ?? "").replaceAll("&", "&amp;").replaceAll("<", "&lt;").replaceAll(">", "&gt;").replaceAll('"', "&quot;").replaceAll("'", "&#39;"); }
function escapeRegex(value) { return String(value ?? "").replace(/[.*+?^${}()|[\]\\]/g, "\\$&"); }
function highlightTerms(text, terms = []) {
  let html = escapeHtml(text ?? "");
  const uniqueTerms = [...new Set((terms || []).map((i) => String(i || "").trim()).filter(Boolean))].sort((a, b) => b.length - a.length);
  uniqueTerms.forEach((term) => { html = html.replace(new RegExp(escapeRegex(term), "gi"), (match) => `<mark style="background:transparent; color:var(--primary); font-weight:600; border-bottom:1px dashed var(--primary); padding:0;">${match}</mark>`); });
  return html;
}
function formatInlineCitations(text) { return escapeHtml(text ?? "").replace(/(\[E\d+\])/g, '<span class="citation-inline">$1</span>'); }

function renderMarkdownPreview(markdownText) {
  if (!markdownText || !markdownText.trim()) return '<div class="empty-inline compact">当前还没有生成报告内容。</div>';
  const parts = []; let listItems = [];
  const flushList = () => { if (listItems.length) { parts.push(`<ul>${listItems.join("")}</ul>`); listItems = []; } };
  markdownText.split(/\r?\n/).forEach((rawLine) => {
    const trimmed = rawLine.trimEnd().trim();
    if (!trimmed) return flushList();
    if (trimmed.startsWith("# ")) { flushList(); parts.push(`<h1>${escapeHtml(trimmed.slice(2).trim())}</h1>`); return; }
    if (trimmed.startsWith("## ")) { flushList(); parts.push(`<h2>${escapeHtml(trimmed.slice(3).trim())}</h2>`); return; }
    if (trimmed.startsWith("### ")) { flushList(); parts.push(`<h3>${escapeHtml(trimmed.slice(4).trim())}</h3>`); return; }
    if (trimmed.startsWith("- ")) { listItems.push(`<li>${escapeHtml(trimmed.slice(2).trim())}</li>`); return; }
    flushList(); parts.push(`<p>${escapeHtml(trimmed)}</p>`);
  });
  flushList(); return parts.join("");
}

function setStatus(text, type = "idle") {
  if (!dom.statusText || !dom.statusPanel) return;
  dom.statusText.textContent = text; dom.statusPanel.className = "status-panel"; 
  if (type === "loading") dom.statusPanel.classList.add("is-loading");
  if (type === "success") dom.statusPanel.classList.add("is-success");
  if (type === "error") dom.statusPanel.classList.add("is-error");
}
function setBusy(isBusy) {
  [dom.analyzeBtn, dom.uploadFileBtn, dom.resumeFileInput, dom.parserModeSelect, dom.runBenchmarkBtn, dom.submitReviewBtn].forEach(el => { if(el) el.disabled = isBusy; });
}

function initTabs() {
  const tabs = document.querySelectorAll(".tab-btn"); const panes = document.querySelectorAll(".tab-pane");
  tabs.forEach(tab => {
    tab.addEventListener("click", () => {
      tabs.forEach(t => t.classList.remove("active")); panes.forEach(p => p.classList.remove("active"));
      tab.classList.add("active");
      const targetPane = getEl(tab.dataset.target); if (targetPane) targetPane.classList.add("active");
      if (tab.dataset.target === "tab-overview" && window.radarChartInstance) window.radarChartInstance.resize();
    });
  });
}

function fillTagList(container, items, emptyLabel = "暂无数据") {
  if (!container) return; container.innerHTML = "";
  if (!items || items.length === 0) { container.innerHTML = `<span class="tag" style="background:transparent; border:1px dashed var(--border-strong); color:var(--text-muted);">${emptyLabel}</span>`; return; }
  items.forEach((item) => { container.innerHTML += `<span class="tag">${escapeHtml(item)}</span>`; });
}
function fillList(container, items) {
  if (!container) return; container.innerHTML = "";
  const source = items && items.length ? items : ["暂无数据"];
  source.forEach((item) => { const li = document.createElement("li"); li.textContent = item; container.appendChild(li); });
}

// ==========================================
// 3. 各模块子渲染函数
// ==========================================
function renderCareerPlan(plan, matches) {
  const topMatch = matches && matches.length ? matches[0] : null;
  if (dom.primaryRole) dom.primaryRole.textContent = plan.primary_role || topMatch?.role_title || "待生成";
  if (dom.primaryScoreBadge) dom.primaryScoreBadge.textContent = plan.primary_score ?? topMatch?.score ?? 0;
  
  // 🌟 清理简报中的 [E1] 乱码
  if (dom.planOverview) {
    const cleanOverview = (plan.overview || "暂无解读").replace(/\[E\d+\]/g, "");
    dom.planOverview.textContent = cleanOverview;
  }
  
  fillTagList(dom.backupRoles, plan.backup_roles || []);
  fillTagList(dom.transitionPathList, plan.transition_paths || []);
  fillList(dom.strengthsList, plan.strengths || []); 
  fillList(dom.risksList, plan.risks || []);
  fillList(dom.actionPlan30, plan.action_plan_30_days || []); 
  fillList(dom.actionPlan90, plan.action_plan_90_days || []); 
  fillList(dom.actionPlan180, plan.action_plan_180_days || []);
  fillList(dom.recommendedProjects, plan.recommended_projects || []); 
  fillList(dom.assessmentTasks, plan.assessment_tasks || []);
  fillList(dom.reviewTargets, plan.next_review_targets || []);
  
  if (dom.growthPathList) {
    dom.growthPathList.innerHTML = "";
    (plan.primary_growth_path || []).forEach((item, index) => {
      dom.growthPathList.innerHTML += `<div style="display:flex; align-items:center; gap:16px; padding:12px 16px; background:var(--surface-alt); border:1px solid var(--border); border-radius:12px; margin-bottom:10px;"><span style="display:flex; align-items:center; justify-content:center; width:36px; height:36px; border-radius:10px; background:rgba(15, 118, 110, 0.1); color:var(--primary); font-weight:800; font-size:0.85rem;">0${index + 1}</span><strong style="color:var(--text-main); font-size:1rem;">${escapeHtml(item)}</strong></div>`;
    });
  }
}

function renderCompetencyRadar(items) {
  const chartDom = dom.competencyRadar;
  if (!chartDom || !items || items.length === 0) return;
  if (window.radarChartInstance) window.radarChartInstance.dispose();
  window.radarChartInstance = echarts.init(chartDom);
  const option = {
    tooltip: { trigger: 'item', backgroundColor: 'rgba(255, 255, 255, 0.95)', borderColor: '#e7e5e4', padding: [12, 16], textStyle: { color: '#292524' } },
    radar: {
      indicator: items.map(item => ({ name: item.name, max: 100 })), radius: '65%', center: ['50%', '50%'], splitNumber: 4, shape: 'polygon',
      axisName: { color: '#44403c', fontFamily: 'Georgia, serif', fontSize: 13 },
      splitArea: { areaStyle: { color: ['rgba(15, 118, 110, 0.02)', 'rgba(15, 118, 110, 0.04)', 'rgba(15, 118, 110, 0.06)', 'rgba(15, 118, 110, 0.08)'].reverse() } },
      axisLine: { lineStyle: { color: 'rgba(15, 118, 110, 0.2)' } }, splitLine: { lineStyle: { color: 'rgba(15, 118, 110, 0.3)' } }
    },
    series: [{
      type: 'radar',
      data: [{ value: items.map(item => item.score), name: '胜任力量化评估', symbol: 'circle', symbolSize: 6, itemStyle: { color: '#0f766e', borderColor: '#fff', borderWidth: 2 }, areaStyle: { color: 'rgba(15, 118, 110, 0.15)' }, lineStyle: { width: 2, color: '#0f766e' } }]
    }]
  };
  window.radarChartInstance.setOption(option);
}

function renderEvaluationMetrics(items) {
  if (!dom.evaluationMetrics) return; dom.evaluationMetrics.innerHTML = "";
  if (!items || items.length === 0) return;
  dom.evaluationMetrics.style.display = "grid"; dom.evaluationMetrics.style.gridTemplateColumns = "repeat(auto-fit, minmax(220px, 1fr))"; dom.evaluationMetrics.style.gap = "16px";
  items.forEach((item) => {
    dom.evaluationMetrics.innerHTML += `
      <div class="card" style="background:var(--surface-alt); padding:20px; border-radius:16px;">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;">
          <span style="font-size:0.9rem; color:var(--text-muted); font-weight:600;">${escapeHtml(item.name || "指标")}</span>
          <strong style="font-size:1.6rem; color:var(--primary); font-family:var(--font-serif);">${item.score ?? 0}</strong>
        </div>
        <p style="font-size:0.85rem; margin:0; color:var(--text-reading); line-height:1.5;">${escapeHtml(item.detail || "")}</p>
      </div>`;
  });
}

function renderGapBenefitAnalysis(items) {
  if (!dom.gapBenefitGrid) return; dom.gapBenefitGrid.innerHTML = "";
  if (!items || items.length === 0) { dom.gapBenefitGrid.innerHTML = `<div class="empty-inline compact">当前还没有差距-收益分析。</div>`; return; }
  items.forEach((item) => {
    dom.gapBenefitGrid.innerHTML += `
      <div class="card gap-benefit-card" style="padding:20px; margin-bottom:16px;">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
          <span class="mini-label">${escapeHtml(item.dimension || "维度")}</span>
          <span class="tag" style="background:rgba(217, 119, 6, 0.1); color:var(--accent); border:none; margin:0; font-weight:700;">+${item.expected_gain ?? 0} 分</span>
        </div>
        <h4 style="margin:0 0 8px 0; font-size:1.05rem; color:var(--text-main);">${escapeHtml(item.gap || "差距项")}</h4>
        <p style="font-size:0.9rem; color:var(--text-muted); margin-bottom:16px;">${escapeHtml(item.detail || "")}</p>
        <div style="background:var(--surface-alt); border-radius:12px; padding:16px; border:1px solid var(--border);">
          <p style="margin:0 0 10px 0; font-size:0.9rem; font-weight:600; color:var(--primary);">预计：${item.current_score ?? 0} → ${item.projected_score ?? 0} 分</p>
          <ul class="feature-list" style="font-size:0.85rem; padding-left:16px; margin-bottom:12px;"><li>${escapeHtml(item.action || "暂无动作")}</li><li>${escapeHtml(item.expected_evidence || "暂无证据建议")}</li></ul>
          <div class="chip-group">${(item.citations || []).map(c => `<span class="tag">${escapeHtml(c)}</span>`).join("")}</div>
        </div>
      </div>`;
  });
}

function renderPlanSelfChecks(items) {
  if (!dom.planSelfChecks) return; dom.planSelfChecks.innerHTML = "";
  if (!items || items.length === 0) { dom.planSelfChecks.innerHTML = `<div class="empty-inline compact">当前还没有计划自检结果。</div>`; return; }
  items.forEach((item) => {
    const isPass = item.status === "通过"; const isWarn = item.status === "关注";
    const borderColor = isPass ? 'var(--primary)' : (isWarn ? 'var(--accent)' : 'var(--border-strong)');
    const bgGradient = isPass ? 'linear-gradient(180deg, rgba(15,118,110,0.05), var(--surface))' : (isWarn ? 'linear-gradient(180deg, rgba(217,119,6,0.05), var(--surface))' : 'var(--surface-alt)');
    dom.planSelfChecks.innerHTML += `
      <div class="card" style="padding:20px; border-radius:16px; border-color:${borderColor}; background:${bgGradient}; margin-bottom:16px;">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;">
          <span style="font-size:0.9rem; color:var(--text-main); font-weight:600;">${escapeHtml(item.name || "自检项")}</span>
          <strong style="font-size:1.4rem; font-family:var(--font-serif); color:${borderColor};">${item.score ?? 0}</strong>
        </div>
        <p style="font-size:0.9rem; color:var(--text-reading); margin:0 0 10px 0;"><strong style="color:${borderColor};">${escapeHtml(item.status || "待检查")}</strong> · ${escapeHtml(item.detail || "")}</p>
        <p style="font-size:0.85rem; color:var(--text-muted); margin:0;">${escapeHtml(item.action || "")}</p>
      </div>`;
  });
}

function renderLearningLoop(items) {
  if (!dom.learningSprints) return; dom.learningSprints.innerHTML = "";
  if (!items || items.length === 0) { dom.learningSprints.innerHTML = `<div class="empty-inline compact">暂无专项补强节点。</div>`; return; }
  items.forEach((item) => {
    dom.learningSprints.innerHTML += `
      <div style="background:var(--surface-alt); padding:20px; border-radius:16px; border:1px solid var(--border); margin-bottom:16px;">
        <div style="display:flex; justify-content:space-between; align-items:start; margin-bottom:12px;">
          <strong style="color:var(--text-main); font-size:1.05rem; line-height:1.4;">${escapeHtml(item.title)}</strong>
          <span class="tag" style="border:1px solid var(--primary); color:var(--primary); background:transparent; margin:0;">${escapeHtml(item.type)}</span>
        </div>
        <p style="font-size:0.95rem; color:var(--text-reading); margin-bottom:16px;">${escapeHtml(item.reason)}</p>
        <div style="border-top:1px dashed var(--border-strong); padding-top:12px; font-size:0.9rem;">
          <strong style="color:var(--primary);">交付闭环：</strong> <span style="color:var(--text-muted);">${escapeHtml(item.deliverable)}</span>
        </div>
      </div>`;
  });
}

function renderResourceMap(items) {
  if (!dom.resourceMap) return; dom.resourceMap.innerHTML = "";
  if (!items || items.length === 0) { dom.resourceMap.innerHTML = `<div class="empty-inline compact">暂无落地资源映射。</div>`; return; }
  dom.resourceMap.style.display = "grid"; dom.resourceMap.style.gridTemplateColumns = "repeat(auto-fit, minmax(280px, 1fr))"; dom.resourceMap.style.gap = "20px";
  items.forEach((item) => {
    const isHigh = item.priority === '高';
    dom.resourceMap.innerHTML += `
      <div class="card" style="padding:24px; border-radius:16px; border-color:${isHigh ? 'var(--accent)' : 'var(--border)'}; display:flex; flex-direction:column;">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:16px;"><span class="mini-label">${escapeHtml(item.category || "资源")}</span><span class="tag" style="background:transparent; border:none; color:${isHigh ? 'var(--accent)' : 'var(--text-muted)'}; font-weight:600; margin:0;">优先级: ${escapeHtml(item.priority || "中")}</span></div>
        <h5 style="margin:0 0 12px 0; color:var(--text-main); font-size:1.1rem; font-weight:600;">${escapeHtml(item.title)}</h5>
        <p style="font-size:0.95rem; color:var(--text-reading); margin-bottom:20px; flex-grow:1;">${escapeHtml(item.description)}</p>
        <div style="background:var(--surface-alt); padding:12px; border-radius:8px; font-size:0.85rem; border-left:3px solid var(--primary);"><strong style="color:var(--text-main);">阶段产出：</strong> <span style="color:var(--text-muted);">${escapeHtml(item.deliverable)}</span></div>
      </div>`;
  });
}

function renderSimilarCases(items) {
  if (!dom.similarCases) return; dom.similarCases.innerHTML = "";
  if (!items || items.length === 0) { dom.similarCases.innerHTML = `<div class="empty-inline compact">当前还没有可参考的相似案例。</div>`; return; }
  items.forEach((item) => {
    dom.similarCases.innerHTML += `
      <div class="card" style="padding:20px; border-radius:16px; margin-bottom:16px;">
        <span class="mini-label">${escapeHtml(item.student_name || "相似案例")}</span>
        <h4 style="margin:8px 0 12px 0; font-size:1.1rem; color:var(--text-main);">${escapeHtml(item.primary_role || "未生成")} · ${item.primary_score ?? 0} 分</h4>
        <p style="font-size:0.85rem; color:var(--text-muted); margin-bottom:12px;">${escapeHtml(item.major || "专业未填写")}｜${escapeHtml(item.created_at || "")}｜复核：${escapeHtml(item.review_status || "未复核")}</p>
        <div class="chip-group" style="margin-bottom:16px;"><span class="tag" style="background:rgba(15,118,110,0.1); color:var(--primary); border:none;">相似度 ${item.similarity_score ?? 0}</span>${(item.reasons || []).map(r => `<span class="tag">${escapeHtml(r)}</span>`).join("")}</div>
        <ul class="feature-list" style="font-size:0.9rem; padding-left:16px;"><li>${escapeHtml(item.takeaway || "暂无启发")}</li></ul>
      </div>`;
  });
}

function renderGroundedEvidence(bundle) {
  if (dom.evidenceSummary) dom.evidenceSummary.textContent = bundle?.summary || "生成分析后展示证据链摘要。";
  if (dom.matchedTerms) fillTagList(dom.matchedTerms, bundle?.query_terms || [], "等待生成检索词");
  if (!dom.evidenceSnippets) return; dom.evidenceSnippets.innerHTML = "";
  const items = bundle?.items || [];
  if (!items.length) { dom.evidenceSnippets.innerHTML = `<div class="empty-inline compact">本次解析未命中有效切片。</div>`; return; }
  
  dom.evidenceSnippets.innerHTML += `
    <div class="card" style="padding:20px; margin-bottom:16px;">
      <div style="display:flex; justify-content:space-between; margin-bottom:12px;"><div><span class="mini-label">Evidence Hit Rate</span><h4 style="margin:4px 0 0 0; font-size:1.1rem;">${bundle?.evidence_hit_rate ?? 0}% · ${escapeHtml(bundle?.retrieval_mode || "未生成")}</h4></div><div class="score-badge">${(bundle?.hit_terms || []).length}/${(bundle?.target_terms || []).length || 1}</div></div>
      <p style="font-size:0.9rem; color:var(--primary); margin-bottom:6px;">命中术语：${escapeHtml((bundle?.hit_terms || []).join("、") || "无")}</p>
      <p style="font-size:0.9rem; color:var(--text-muted); margin:0;">目标术语：${escapeHtml((bundle?.target_terms || []).join("、") || "无")}</p>
    </div>`;

  items.forEach((item) => {
    dom.evidenceSnippets.innerHTML += `
      <div class="card" style="margin-bottom:16px; padding:20px; border-left:4px solid var(--primary); border-radius:12px;">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px;"><strong style="color:var(--text-main); font-size:1.05rem;">${escapeHtml(item.job_title || item.source_title || "证据片段")} <span class="citation-inline">${escapeHtml(item.citation_id || "[E]")}</span></strong><span class="tag" style="background:transparent; border-color:var(--border-strong); margin:0;">相关度 ${item.score ?? 0}</span></div>
        <p style="font-size:0.85rem; color:var(--text-muted); margin-bottom:12px;">${escapeHtml(item.company_name || "岗位模板")}｜${escapeHtml(item.city || "未知")}｜命中词：${highlightTerms((item.matched_terms || []).join("、") || "无", item.matched_terms || [])}</p>
        <p style="margin:0; color:var(--text-reading); font-size:0.95rem; line-height:1.7;">${highlightTerms(item.snippet || "暂无片段", item.matched_terms || [])}</p>
      </div>`;
  });
}

// ==========================================
// 4. 核心主流水线 (The Master Pipeline)
// ==========================================
function renderResults(data) {
  if (dom.emptyState) dom.emptyState.classList.add("hidden");
  if (dom.resultsContent) dom.resultsContent.classList.remove("hidden");
  state.latestResult = data; state.currentAnalysisId = data.analysis_id || data.id || null;
  state.currentReport = data.report_markdown || "";

  // 渲染所有受保护的组件
  if (data.career_plan) renderCareerPlan(data.career_plan, data.matches);
  if (data.career_plan?.competency_dimensions) renderCompetencyRadar(data.career_plan.competency_dimensions);
  if (data.career_plan?.evaluation_metrics) renderEvaluationMetrics(data.career_plan.evaluation_metrics);
  if (data.career_plan?.gap_benefit_analysis) renderGapBenefitAnalysis(data.career_plan.gap_benefit_analysis);
  if (data.career_plan?.plan_self_checks) renderPlanSelfChecks(data.career_plan.plan_self_checks);
  if (data.career_plan?.learning_sprints) renderLearningLoop(data.career_plan.learning_sprints);
  if (data.career_plan?.resource_map) renderResourceMap(data.career_plan.resource_map);
  if (data.career_plan?.similar_cases) renderSimilarCases(data.career_plan.similar_cases);
  if (data.career_plan?.evidence_bundle) renderGroundedEvidence(data.career_plan.evidence_bundle);
  if (dom.reportPreview) dom.reportPreview.innerHTML = renderMarkdownPreview(state.currentReport);

  // 切回总览并滚动到顶
  document.querySelector('.tab-btn[data-target="tab-overview"]')?.click();
  dom.resultsContent?.scrollIntoView({ behavior: "smooth", block: "start" });
}

// ==========================================
// 5. API 交互与调度
// ==========================================
async function loadSampleResume(sampleName = null) {
  setBusy(true); setStatus("读取样本数据...", "loading");
  try {
    const url = sampleName ? `/api/demo-resume?name=${encodeURIComponent(sampleName)}` : "/api/demo-resume";
    const response = await fetch(url);
    const data = await response.json();
    if (dom.resumeInput) dom.resumeInput.value = data.resume_text || "";
    state.currentSampleName = data.sample_name || sampleName;
    setStatus(`样本就绪: ${state.currentSampleName || "default"}`, "success");
  } catch (error) { setStatus(`IO异常: ${error.message}`, "error"); } finally { setBusy(false); }
}

async function analyzeResume() {
  const resumeText = dom.resumeInput?.value.trim();
  if (!resumeText) return setStatus("指令终止：履历流为空，请先录入。", "error");
  setBusy(true); setStatus("开启智能体多阶段并行演推...", "loading");

  try {
    const response = await fetch("/api/career-plan", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        resume_text: resumeText, top_k: 5, parser_mode: dom.parserModeSelect?.value || "auto",
        sample_name: state.currentSampleName, prior_analysis_id: state.currentAnalysisId,
        agent_answers: {}, self_assessment_answers: {},
      }),
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || "计算节点拒绝响应");
    renderResults(data);
    setStatus("决策视图已生成", "success");
  } catch (error) { setStatus(`分析链路异常：${error.message}`, "error"); } finally { setBusy(false); }
}

// 🌟 修复 1：上传文件流完全接通
async function uploadResumeFile() {
  const file = dom.resumeFileInput?.files[0];
  if (!file) return setStatus("请选择本地文件", "error");
  const formData = new FormData(); formData.append("resume_file", file);
  setBusy(true); setStatus(`建立外部数据流：${file.name}...`, "loading");
  try {
    const response = await fetch("/api/upload-resume-file", { method: "POST", body: formData });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || "反序列化受阻");
    if (dom.resumeInput) dom.resumeInput.value = data.resume_text || "";
    setStatus(data.message || `物理数据装载成功。`, "success");
  } catch (error) { setStatus(`通道建立失败：${error.message}`, "error"); } finally { setBusy(false); }
}

// ==========================================
// 6. 初始化与事件监听
// ==========================================
window.addEventListener("load", () => {
  initTabs();
  window.addEventListener('resize', () => { if (window.radarChartInstance) window.radarChartInstance.resize(); });
  loadSampleResume("demo_resume_backend.txt").catch(() => {});
});

if (dom.analyzeBtn) dom.analyzeBtn.addEventListener("click", analyzeResume);

// 🌟 修复 2：按钮触发点击文件库，文件变化触发上传
if (dom.uploadFileBtn) dom.uploadFileBtn.addEventListener("click", () => dom.resumeFileInput?.click());
if (dom.resumeFileInput) {
  dom.resumeFileInput.addEventListener("change", () => {
    if (dom.resumeFileInput.files.length > 0) uploadResumeFile();
  });
}

// 🌟 修复 3：系统状态监控灯和通知响应
dom.sysStatusBtn?.addEventListener('click', () => setStatus('🟢 大模型与规则引擎均就绪', 'success'));

if (dom.printPdfBtn) dom.printPdfBtn.addEventListener("click", () => {
  if (!state.currentAnalysisId) return setStatus("画布为空，拒绝执行渲染", "error");
  window.open(`/print-report/${state.currentAnalysisId}`, "_blank");
});