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
const state = {
  samples: [],
  currentSampleName: null,
  currentReport: "",
  baseReport: "",
  currentAutoReport: "",
  currentAnalysisId: null,
  currentRoleSwitch: null,
  currentTemplateRole: null,
  templateEvidenceRequestToken: 0,
  latestResult: null,
  schoolDashboard: null,
  benchmark: null,
  analysisReviews: [],
};
const getEl = (id) => document.getElementById(id);

const dom = {
  resumeInput: getEl("resume-input"), analyzeBtn: getEl("analyze-btn"), uploadFileBtn: getEl("upload-file-btn"),
  resumeFileInput: getEl("resume-file-input"), parserModeSelect: getEl("parser-mode-select"), statusPanel: getEl("status-panel"),
  statusText: getEl("status-text"), sampleGallery: getEl("sample-gallery"), emptyState: getEl("empty-state"),
  resultsContent: getEl("results-content"), primaryRole: getEl("primary-role"), primaryScoreBadge: getEl("primary-score-badge"),
  primaryRoleSummary: getEl("primary-role-summary"), primaryRoleNote: getEl("primary-role-note"),
  primaryStrengthCount: getEl("primary-strength-count"), primaryRiskCount: getEl("primary-risk-count"),
  primaryEvidenceRate: getEl("primary-evidence-rate"), backupRoles: getEl("backup-roles"), planOverview: getEl("plan-overview"), strengthsList: getEl("strengths-list"),
  risksList: getEl("risks-list"), evaluationMetrics: getEl("evaluation-metrics"), competencyRadar: getEl("radar-chart"),
  roleComparisonSummary: getEl("role-comparison-summary"),
  jobSearchSnapshot: getEl("job-search-snapshot"),
  recommendationComparisons: getEl("recommendation-comparisons"),
  competencyDimensions: getEl("competency-dimensions"), actionPlan30: getEl("action-plan-30"), actionPlan90: getEl("action-plan-90"),
  actionPlan180: getEl("action-plan-180"), recommendedProjects: getEl("recommended-projects"), learningSprints: getEl("learning-sprints"),
  growthPathList: getEl("growth-path-list"), transitionPathList: getEl("transition-path-list"), resourceMap: getEl("resource-map"),
  roleSwitchToolbar: getEl("role-switch-toolbar"), roleSwitchSummary: getEl("role-switch-summary"),
  applicationStrategy: getEl("application-strategy"), resumeSurgery: getEl("resume-surgery"), interviewFocus: getEl("interview-focus"),
  gapBenefitGrid: getEl("gap-benefit-grid"), planSelfChecks: getEl("plan-self-checks"), careerGraph: getEl("career-graph"),
  agentQuestionList: getEl("agent-question-list"), selfAssessmentForm: getEl("self-assessment-form"), selfAssessmentSummary: getEl("self-assessment-summary"),
  serviceLoop: getEl("service-loop"), stakeholderViews: getEl("stakeholder-views"), assessmentTasks: getEl("assessment-tasks"), reviewTargets: getEl("review-targets"),
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
  // 🌟 P3: 报告内联编辑
  editReportBtn: getEl("edit-report-btn"), saveReportBtn: getEl("save-report-btn"),
  downloadEditedBtn: getEl("download-edited-btn"), reportEditorArea: getEl("report-editor-area"), reportEditor: getEl("report-editor"),
  // 🌟 P5: AI 评审意见
  aiCommentaryCard: getEl("ai-commentary-card"), aiCommentaryText: getEl("ai-commentary-text"),
};

// ==========================================
// 2. 工具集与格式化
// ==========================================
function escapeHtml(value) { return String(value ?? "").replaceAll("&", "&amp;").replaceAll("<", "&lt;").replaceAll(">", "&gt;").replaceAll('"', "&quot;").replaceAll("'", "&#39;"); }
function escapeRegex(value) { return String(value ?? "").replace(/[.*+?^${}()|[\]\\]/g, "\\$&"); }
function highlightTerms(text, terms = []) {
  let html = escapeHtml(text ?? "");
  const uniqueTerms = [...new Set((terms || []).map((item) => String(item || "").trim()).filter(Boolean))].sort((a, b) => b.length - a.length);
  uniqueTerms.forEach((term) => {
    html = html.replace(new RegExp(escapeRegex(term), "gi"), (match) => `<mark class="inline-highlight">${match}</mark>`);
  });
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

function cleanCitationText(text) {
  return String(text ?? "").replace(/\s*\[E\d+\]/g, "").trim();
}

function compactText(value, maxLength = 96) {
  const text = cleanCitationText(String(value ?? "").replace(/\s+/g, " ").trim());
  if (!text) return "";
  if (text.length <= maxLength) return text;
  const clipped = text.slice(0, maxLength);
  const punctuationIndex = Math.max(
    clipped.lastIndexOf("。"),
    clipped.lastIndexOf("；"),
    clipped.lastIndexOf("，"),
    clipped.lastIndexOf("、"),
    clipped.lastIndexOf(" ")
  );
  const cutIndex = punctuationIndex > Math.floor(maxLength * 0.58) ? punctuationIndex : maxLength;
  return `${clipped.slice(0, cutIndex).trim()}...`;
}

function formatScalar(value, emptyLabel = "未填写") {
  if (Array.isArray(value)) {
    const items = value.map((item) => String(item ?? "").trim()).filter(Boolean);
    return items.length ? items.join("、") : emptyLabel;
  }
  if (value === null || value === undefined) return emptyLabel;
  const text = String(value).trim();
  return text || emptyLabel;
}

function normalizeTextList(items) {
  return (items || []).map((item) => String(item ?? "").trim()).filter(Boolean);
}

function buildMarkdownList(items, emptyLabel = "无") {
  const lines = normalizeTextList(items);
  return lines.length ? lines.map((item) => `- ${item}`).join("\n") : `- ${emptyLabel}`;
}

function buildMarkdownObjectList(items, formatter, emptyLabel = "无") {
  const lines = (items || [])
    .map((item, index) => formatter(item, index))
    .map((item) => String(item ?? "").trim())
    .filter(Boolean);
  return lines.length ? lines.map((item) => `- ${item}`).join("\n") : `- ${emptyLabel}`;
}

function isReportEditing() {
  return Boolean(dom.reportEditorArea && dom.reportEditorArea.style.display !== "none");
}

function getCurrentRenderableReport() {
  if (isReportEditing()) {
    return dom.reportEditor?.value || state.currentReport || state.currentAutoReport || state.baseReport || "";
  }
  return state.currentReport || state.currentAutoReport || state.baseReport || "";
}

function renderCurrentReportPreview(markdownText) {
  if (!dom.reportPreview) return;
  dom.reportPreview.innerHTML = renderMarkdownPreview(markdownText);
  dom.reportPreview.style.display = "";
}

function getCurrentActiveRoleTitle() {
  const context = getActiveReportContext(state.latestResult || {});
  return context.activeRoleTitle || context.plan?.primary_role || "";
}

function getActiveEvidenceBundle(data = state.latestResult) {
  const plan = data?.career_plan || {};
  const activeSimulation = getActiveRoleSwitch(plan);
  return activeSimulation?.evidence_bundle || plan.evidence_bundle || {};
}

function syncEvidenceViewWithActiveRole() {
  renderGroundedEvidence(getActiveEvidenceBundle(state.latestResult));
}

function syncRoleLinkedPanels(roleTitle = null, { showLoading = true } = {}) {
  const targetRole = String(roleTitle || getCurrentActiveRoleTitle() || "").trim();
  if (!targetRole) return;
  if (dom.jdSearchInput) dom.jdSearchInput.value = targetRole;
  if (showLoading && dom.templateEvidence) {
    renderEmptyState(dom.templateEvidence, `正在加载 ${targetRole} 的标准基线样本...`);
  }
  loadTemplateEvidence(targetRole).catch(() => {});
}

function setElementHidden(element, hidden = true) {
  if (!element) return;
  element.classList.toggle("hidden", hidden);
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
  if (!items || items.length === 0) { container.innerHTML = `<span class="tag tag-ghost">${emptyLabel}</span>`; return; }
  items.forEach((item) => { container.innerHTML += `<span class="tag">${escapeHtml(item)}</span>`; });
}
function fillList(container, items) {
  if (!container) return; container.innerHTML = "";
  const source = items && items.length ? items : ["暂无数据"];
  source.forEach((item) => { const li = document.createElement("li"); li.textContent = item; container.appendChild(li); });
}

function fillListLimited(container, items, maxItems = 4, emptyLabel = "暂无数据") {
  if (!container) return;
  const source = (items || []).filter((item) => String(item ?? "").trim());
  const render = (expanded = false) => {
    container.innerHTML = "";
    if (!source.length) {
      const li = document.createElement("li");
      li.textContent = emptyLabel;
      container.appendChild(li);
      return;
    }
    const visibleItems = expanded ? source : source.slice(0, maxItems);
    visibleItems.forEach((item) => {
      const li = document.createElement("li");
      li.textContent = String(item);
      li.title = String(item);
      container.appendChild(li);
    });
    if (source.length > maxItems) {
      const li = document.createElement("li");
      li.className = "list-more";
      const button = document.createElement("button");
      button.type = "button";
      button.className = "list-more-btn";
      button.textContent = expanded ? "收起" : `展开剩余 ${source.length - maxItems} 项`;
      button.addEventListener("click", () => render(!expanded));
      li.appendChild(button);
      container.appendChild(li);
    }
  };
  render(false);
}

function renderEmptyState(container, label) {
  if (!container) return;
  container.innerHTML = `<div class="empty-inline compact">${escapeHtml(label)}</div>`;
}

function renderMetricCards(container, items, emptyLabel = "暂无数据") {
  if (!container) return;
  container.innerHTML = "";
  if (!items || items.length === 0) {
    renderEmptyState(container, emptyLabel);
    return;
  }
  container.style.display = "grid";
  container.style.gridTemplateColumns = "repeat(auto-fit, minmax(180px, 1fr))";
  container.style.gap = "16px";
  items.forEach((item) => {
    container.innerHTML += `
      <div class="metric-tile">
        <div class="metric-tile-label">${escapeHtml(item.label || item.name || "指标")}</div>
        <div class="metric-tile-score">${escapeHtml(item.value ?? item.count ?? 0)}</div>
        ${item.detail ? `<p class="metric-tile-copy" title="${escapeHtml(item.detail)}">${escapeHtml(compactText(item.detail, 40))}</p>` : ""}
      </div>`;
  });
}

function renderSimpleDistribution(container, sections, emptyLabel = "暂无分布数据") {
  if (!container) return;
  container.innerHTML = "";
  const usableSections = (sections || []).filter((section) => (section.items || []).length);
  if (!usableSections.length) {
    renderEmptyState(container, emptyLabel);
    return;
  }
  usableSections.forEach((section) => {
    container.innerHTML += `
      <div class="distribution-card">
        <h5 class="fold-panel-title">${escapeHtml(section.title)}</h5>
        <div class="distribution-list">
        ${(section.items || []).map((item) => `
          <div class="distribution-item">
            <span class="distribution-name">${escapeHtml(item.name || item.label || "分类")}</span>
            <strong class="distribution-value">${escapeHtml(item.count ?? item.value ?? 0)}</strong>
          </div>`).join("")}
        </div>
      </div>`;
  });
}

function renderRecordList(container, items, builder, emptyLabel) {
  if (!container) return;
  container.innerHTML = "";
  if (!items || items.length === 0) {
    renderEmptyState(container, emptyLabel);
    return;
  }
  items.forEach((item) => {
    container.innerHTML += builder(item);
  });
}

function syncActiveSample() {
  if (!dom.sampleGallery) return;
  dom.sampleGallery.querySelectorAll("[data-sample-name]").forEach((button) => {
    button.classList.toggle("active", button.dataset.sampleName === state.currentSampleName);
  });
}

function renderSampleGallery(samples) {
  if (!dom.sampleGallery) return;
  dom.sampleGallery.innerHTML = "";
  if (!samples || samples.length === 0) {
    renderEmptyState(dom.sampleGallery, "暂无答辩样例。");
    return;
  }
  samples.forEach((sample) => {
    const button = document.createElement("button");
    button.type = "button";
    button.className = "sample-chip";
    button.dataset.sampleName = sample.name || "";
    button.textContent = sample.label || sample.name || "样例";
    button.title = sample.description || sample.label || "";
    button.addEventListener("click", () => loadSampleResume(sample.name).catch((error) => {
      setStatus(`载入样例失败：${error.message}`, "error");
    }));
    dom.sampleGallery.appendChild(button);
  });
  syncActiveSample();
}

// ==========================================
// 3. 各模块子渲染函数
// ==========================================
function renderCareerPlan(plan, matches) {
  const topMatch = matches && matches.length ? matches[0] : null;
  if (dom.primaryRole) dom.primaryRole.textContent = plan.primary_role || topMatch?.role_title || "待生成";
  if (dom.primaryScoreBadge) dom.primaryScoreBadge.textContent = plan.primary_score ?? topMatch?.score ?? 0;
  const primarySummary = cleanCitationText(topMatch?.summary || plan.overview || "");
  const primaryAction = normalizeTextList(plan.action_plan_30_days || [])[0]
    || normalizeTextList(plan.primary_growth_path || [])[0]
    || normalizeTextList(plan.risks || [])[0]
    || "";
  if (dom.primaryRoleSummary) {
    dom.primaryRoleSummary.textContent = primarySummary || "主岗位解读将在生成后同步显示";
  }
  if (dom.primaryRoleNote) {
    dom.primaryRoleNote.textContent = primaryAction ? `优先动作：${primaryAction}` : "优先动作将在生成后同步显示";
  }
  if (dom.primaryStrengthCount) dom.primaryStrengthCount.textContent = String((plan.strengths || []).length || 0);
  if (dom.primaryRiskCount) dom.primaryRiskCount.textContent = String((plan.risks || []).length || 0);
  if (dom.primaryEvidenceRate) {
    const evidenceRate = plan.evidence_bundle?.evidence_hit_rate;
    dom.primaryEvidenceRate.textContent = evidenceRate === null || evidenceRate === undefined ? "待生成" : `${evidenceRate}%`;
  }
  
  // 🌟 清理简报中的 [E1] 乱码
  if (dom.planOverview) {
    const cleanOverview = (plan.overview || "暂无解读").replace(/\[E\d+\]/g, "");
    dom.planOverview.textContent = compactText(cleanOverview, 140);
    dom.planOverview.title = cleanOverview;
  }
  
  renderBackupRoleSwitches(plan);
  fillListLimited(dom.transitionPathList, plan.transition_paths || [], 4);
  fillListLimited(dom.strengthsList, plan.strengths || [], 3); 
  fillListLimited(dom.risksList, plan.risks || [], 3);
  fillListLimited(dom.recommendedProjects, plan.recommended_projects || [], 4); 
  fillListLimited(dom.assessmentTasks, plan.assessment_tasks || [], 4);
  
  if (dom.growthPathList) {
    fillListLimited(dom.growthPathList, plan.primary_growth_path || [], 4);
  }
}

function getRoleSwitchSimulations(plan) {
  return plan?.role_switch_simulations || [];
}

function getActiveRoleSwitch(plan) {
  const simulations = getRoleSwitchSimulations(plan);
  if (!simulations.length) return null;
  return simulations.find((item) => item.role_title === state.currentRoleSwitch) || simulations[0];
}

function getActiveReportContext(data) {
  const plan = data?.career_plan || {};
  const matches = data?.matches || [];
  const activeSimulation = getActiveRoleSwitch(plan);
  const activeRoleTitle = activeSimulation?.role_title || state.currentRoleSwitch || plan.primary_role || matches[0]?.role_title || "";
  const activeMatch = matches.find((item) => item.role_title === activeRoleTitle) || matches[0] || null;
  const activeStrategy = (plan.application_strategy || []).find((item) => item.role_title === activeRoleTitle) || activeSimulation || null;
  const activeComparison = (plan.recommendation_comparisons || []).find((item) => item.role_title === activeRoleTitle) || null;
  return {
    student: data?.student_profile || {},
    plan,
    matches,
    activeSimulation,
    activeRoleTitle,
    activeMatch,
    activeStrategy,
    activeComparison,
  };
}

function buildActiveRoleReport(data) {
  if (!data) return state.baseReport || "";

  const {
    student,
    plan,
    matches,
    activeSimulation,
    activeRoleTitle,
    activeMatch,
    activeStrategy,
    activeComparison,
  } = getActiveReportContext(data);

  if (!activeRoleTitle && !plan.primary_role && !matches.length) {
    return state.baseReport || data.report_markdown || "";
  }

  const activeLane = activeSimulation?.lane || activeStrategy?.lane || "当前岗位";
  const activeScore = activeSimulation?.fit_score ?? activeMatch?.score ?? plan.primary_score ?? 0;
  const actionPlan30 = activeSimulation?.action_plan_30_days || plan.action_plan_30_days || [];
  const actionPlan90 = activeSimulation?.action_plan_90_days || plan.action_plan_90_days || [];
  const actionPlan180 = activeSimulation?.action_plan_180_days || plan.action_plan_180_days || [];
  const reviewTargets = activeSimulation?.next_review_targets || plan.next_review_targets || [];
  const resumeSurgery = activeSimulation?.resume_surgery || plan.resume_surgery || [];
  const interviewFocus = activeSimulation?.interview_focus || plan.interview_focus || [];
  const orderedComparisons = [...(plan.recommendation_comparisons || [])].sort((left, right) => {
    if (left?.role_title === activeRoleTitle) return -1;
    if (right?.role_title === activeRoleTitle) return 1;
    return 0;
  });
  const orderedRadarRoles = [...(plan.role_comparison_radar?.roles || [])].sort((left, right) => {
    if (left?.role_title === activeRoleTitle) return -1;
    if (right?.role_title === activeRoleTitle) return 1;
    return 0;
  });
  const selfAssessment = plan.self_assessment || {};
  const evidence = activeSimulation?.evidence_bundle || plan.evidence_bundle || {};
  const isPrimaryRole = activeRoleTitle === plan.primary_role;

  const sections = [
    `# 大学生职业规划报告：${formatScalar(student.name, "学生")} · ${formatScalar(activeRoleTitle || plan.primary_role, "岗位模拟")}`,
    "## 1. 报告视角",
    buildMarkdownList([
      `当前模拟岗位：${formatScalar(activeRoleTitle || plan.primary_role)}`,
      `主推荐岗位：${formatScalar(plan.primary_role)}`,
      `当前岗位定位：${formatScalar(activeLane, "未生成")}`,
      `当前岗位匹配分：${formatScalar(activeScore, "0")}`,
      `报告模式：当前页面、下载与打印均跟随“岗位切换模拟器”的当前选择`,
    ]),
    "## 2. 学生画像摘要",
    buildMarkdownList([
      `学校：${formatScalar(student.school_name)}`,
      `专业：${formatScalar(student.major)}`,
      `学历：${formatScalar(student.education_level)}`,
      `意向岗位：${formatScalar(student.target_roles)}`,
      `意向城市：${formatScalar(student.city_preference)}`,
      `画像完整度：${formatScalar(student.profile_completeness, "0")}`,
      `就业竞争力：${formatScalar(student.competitiveness_score, "0")}`,
    ]),
    "### 技术技能",
    buildMarkdownList(student.skills, "待补充"),
    "### 软技能",
    buildMarkdownList(student.soft_skills, "待补充"),
    "## 3. 推荐总览",
    buildMarkdownObjectList(
      matches.slice(0, 3),
      (item) => `${formatScalar(item.role_title, "岗位")}：${formatScalar(item.score, "0")} 分（置信度：${formatScalar(item.confidence_label, "中")}）`,
      "暂无岗位推荐。"
    ),
    "### 主岗位优势",
    buildMarkdownList(plan.strengths, "暂无"),
    "### 当前风险与短板",
    buildMarkdownList(plan.risks, "暂无"),
    "### 求职场景画像",
    buildMarkdownObjectList(
      plan.job_search_snapshot || [],
      (item) => `${formatScalar(item.label, "画像项")}：${formatScalar(item.value, "待补充")}；说明：${formatScalar(item.detail, "暂无说明")}`,
      "暂无求职场景画像。"
    ),
    "## 4. 当前模拟岗位判断",
    buildMarkdownList([
      activeSimulation?.summary || activeStrategy?.rationale || cleanCitationText(plan.overview) || "暂无当前岗位判断。",
      `定位说明：${formatScalar(activeStrategy?.positioning || activeSimulation?.positioning)}`,
      `入选原因：${formatScalar(activeStrategy?.selection_reason || activeSimulation?.selection_reason)}`,
      `切换提醒：${formatScalar(activeStrategy?.risk_note || activeSimulation?.risk_note, "当前切换仅用于模拟方案，不改变系统主推荐岗位。")}`,
      isPrimaryRole
        ? "排序说明：当前岗位就是系统主推荐岗位，建议把项目举证、简历重写和投递动作集中到这一方向。"
        : `为什么没排第一：${formatScalar(activeComparison?.why_not_first, "当前岗位仍有关键短板，因此暂未升为首选。")}`,
      isPrimaryRole
        ? `主岗优势：${formatScalar(activeComparison?.primary_advantage, "该岗位与当前画像、目标技能和证据链最一致。")}`
        : `主岗排第一的原因：${formatScalar(activeComparison?.primary_advantage, "主推荐岗位的能力闭环和证据完整度更高。")}`,
      isPrimaryRole
        ? `当前保留价值：${formatScalar(activeComparison?.candidate_value, "该方向可直接进入投递和面试准备。")}`
        : `当前保留价值：${formatScalar(activeComparison?.candidate_value, "该岗位仍适合作为可进可退的备选投递方向。")}`,
      isPrimaryRole
        ? `继续拉开优势的动作：${formatScalar(activeComparison?.upgrade_path, "补强项目结果量化与岗位化表达，巩固领先优势。")}`
        : `如果想让它升到第一：${formatScalar(activeComparison?.upgrade_path, "优先补齐当前岗位最缺的技能证据与项目表达。")}`,
    ]),
    "## 5. 当前模拟岗位行动计划",
    "### 30 天",
    buildMarkdownList(actionPlan30, "暂无短期行动。"),
    "### 90 天",
    buildMarkdownList(actionPlan90, "暂无中期行动。"),
    "### 180 天",
    buildMarkdownList(actionPlan180, "暂无长期行动。"),
    "## 6. 当前模拟岗位投递策略",
    buildMarkdownList([
      `目标城市：${formatScalar(activeStrategy?.city_focus, "待补充")}`,
      `目标行业：${formatScalar(activeStrategy?.industry_focus, "待补充")}`,
      `薪资参考：${formatScalar(activeStrategy?.salary_hint, "待补充")}`,
      `检索关键词：${formatScalar(activeStrategy?.keywords, "待补充")}`,
      `执行动作：${formatScalar(activeStrategy?.action, "待补充")}`,
    ]),
    "### 投递交付物",
    buildMarkdownList(activeStrategy?.deliverables || [], "暂无交付物要求。"),
    "## 7. 当前模拟岗位简历改写",
    buildMarkdownObjectList(
      resumeSurgery,
      (item) => `${formatScalar(item.section, "改写项")}：问题=${formatScalar(item.issue, "待识别")}；动作=${formatScalar(item.action, "待补充")}；交付物=${formatScalar(item.deliverable, "待补充")}`,
      "暂无简历改写建议。"
    ),
    "## 8. 当前模拟岗位面试冲刺",
    buildMarkdownObjectList(
      interviewFocus,
      (item) => `${formatScalar(item.theme, "冲刺题")}：${formatScalar(item.question, "待补充")}；考察信号=${formatScalar(item.signal, "待补充")}；准备动作=${formatScalar(item.prep, "待补充")}`,
      "暂无面试冲刺题板。"
    ),
    "## 9. 复测与证据",
    buildMarkdownList([
      `复测结论：${formatScalar(selfAssessment.summary, "建议先完成岗位自测与项目举证。")}`,
      `复测得分：${formatScalar(selfAssessment.score, "0")}`,
      `检索模式：${formatScalar(evidence.retrieval_mode, "未生成")}`,
      `证据命中率：${formatScalar(evidence.evidence_hit_rate, "0")}%`,
      `检索关键词：${formatScalar(evidence.query_terms, "未生成")}`,
      `证据摘要：${formatScalar(evidence.summary, "暂无")}`,
    ]),
    "### 下一次复测目标",
    buildMarkdownList(reviewTargets, "暂无复测目标。"),
    "### 岗位自测任务",
    buildMarkdownList(plan.assessment_tasks, "暂无自测任务。"),
    "## 10. 多岗位对比参考",
    "### 推荐排序对比解释",
    buildMarkdownObjectList(
      orderedComparisons,
      (item) => `${formatScalar(item.role_title, "岗位")}：为什么没排第一=${formatScalar(item.why_not_first, "暂无")}；主岗优势=${formatScalar(item.primary_advantage, "暂无")}；保留价值=${formatScalar(item.candidate_value, "暂无")}；翻盘条件=${formatScalar(item.upgrade_path, "暂无")}`,
      "暂无排序对比解释。"
    ),
    "### 能力差异雷达结论",
    buildMarkdownList(plan.role_comparison_radar?.summary || [], "暂无雷达读图结论。"),
    "### 雷达角色快照",
    buildMarkdownObjectList(
      orderedRadarRoles,
      (item) => {
        const values = Array.isArray(item?.values) ? item.values : [];
        return `${formatScalar(item.lane, "候选")} ${formatScalar(item.role_title, "岗位")}：综合适配 ${formatScalar(values[0], "0")}，核心技能 ${formatScalar(values[1], "0")}，岗位胜任 ${formatScalar(values[2], "0")}，软技能协同 ${formatScalar(values[3], "0")}，证据举证 ${formatScalar(values[4], "0")}，成长潜力 ${formatScalar(values[5], "0")}`;
      },
      "暂无雷达数据。"
    ),
    "## 11. 产品亮点",
    buildMarkdownList([
      `产品标签：${formatScalar(plan.product_signature, "AI 大学生职业规划智能体")}`,
      ...normalizeTextList((plan.innovation_highlights || []).map((item) => `${formatScalar(item.title, "亮点")}：${formatScalar(item.detail, "暂无说明")}`)),
    ], "暂无产品亮点。"),
  ];

  return sections.join("\n\n").trim();
}

function syncReportWithActiveRole({ preserveEditor = false } = {}) {
  const autoReport = buildActiveRoleReport(state.latestResult);
  if (!autoReport) return;
  state.currentAutoReport = autoReport;
  if (preserveEditor && isReportEditing()) return;
  state.currentReport = autoReport;
  renderCurrentReportPreview(autoReport);
}

function buildPrintableReportHtml(markdownText) {
  const { student, plan, activeRoleTitle, activeSimulation } = getActiveReportContext(state.latestResult || {});
  const title = `${formatScalar(student.name, "学生")} · ${formatScalar(activeRoleTitle || plan.primary_role, "岗位规划报告")}`;
  const subtitle = `${formatScalar(activeSimulation?.lane || "当前视角")} · 匹配分 ${formatScalar(activeSimulation?.fit_score ?? plan.primary_score ?? 0, "0")} · 打印内容已跟随当前岗位模拟同步`;
  const content = renderMarkdownPreview(markdownText);
  return `<!doctype html>
<html lang="zh-CN">
  <head>
    <meta charset="utf-8" />
    <title>${escapeHtml(title)}</title>
    <style>
      :root {
        --ink: #1f2937;
        --muted: #6b7280;
        --line: #d1d5db;
        --accent: #0f766e;
        --paper: #ffffff;
      }
      * { box-sizing: border-box; }
      body {
        margin: 0;
        background: #f3f4f6;
        color: var(--ink);
        font: 15px/1.72 "Noto Sans SC", "PingFang SC", "Microsoft YaHei", sans-serif;
      }
      .page {
        max-width: 900px;
        margin: 0 auto;
        background: var(--paper);
        min-height: 100vh;
        padding: 48px 56px 64px;
      }
      .header {
        padding-bottom: 20px;
        border-bottom: 2px solid var(--accent);
        margin-bottom: 28px;
      }
      .header h1 {
        margin: 0 0 10px 0;
        color: var(--accent);
        font: 700 30px/1.25 "Noto Serif SC", "Songti SC", serif;
      }
      .header p {
        margin: 0;
        color: var(--muted);
        font-size: 14px;
      }
      .report-preview h1, .report-preview h2, .report-preview h3 {
        margin: 0;
        font-family: "Noto Serif SC", "Songti SC", serif;
      }
      .report-preview h1 {
        display: none;
      }
      .report-preview h2 {
        margin-top: 28px;
        margin-bottom: 12px;
        color: var(--ink);
        font-size: 22px;
        border-left: 4px solid var(--accent);
        padding-left: 12px;
      }
      .report-preview h3 {
        margin-top: 18px;
        margin-bottom: 8px;
        color: #374151;
        font-size: 17px;
      }
      .report-preview p {
        margin: 0 0 12px 0;
        color: #374151;
      }
      .report-preview ul {
        margin: 8px 0 18px 0;
        padding-left: 22px;
      }
      .report-preview li {
        margin-bottom: 8px;
      }
      @media print {
        body {
          background: #fff;
        }
        .page {
          max-width: none;
          min-height: auto;
          margin: 0;
          padding: 0;
        }
      }
    </style>
  </head>
  <body>
    <main class="page">
      <header class="header">
        <h1>${escapeHtml(title)}</h1>
        <p>${escapeHtml(subtitle)}</p>
      </header>
      <section class="report-preview">${content}</section>
    </main>
    <script>
      window.addEventListener("load", () => {
        setTimeout(() => window.print(), 160);
      });
      window.addEventListener("afterprint", () => {
        window.close();
      });
    </script>
  </body>
</html>`;
}

function printCurrentReport() {
  const markdownText = getCurrentRenderableReport();
  if (!markdownText) {
    setStatus("还没有可打印的报告内容，请先生成分析结果", "error");
    return;
  }
  const popup = window.open("", "_blank");
  if (!popup) {
    setStatus("浏览器阻止了打印窗口，请允许弹窗后重试", "error");
    return;
  }
  popup.document.open();
  popup.document.write(buildPrintableReportHtml(markdownText));
  popup.document.close();
}

function buildRoleSwitchButton(item, compact = false) {
  const button = document.createElement("button");
  const active = state.currentRoleSwitch === item.role_title;
  button.type = "button";
  button.className = `role-switch-btn${compact ? " role-switch-btn-compact" : ""}${active ? " is-active" : ""}`;
  button.title = `切换到 ${item.role_title} 模拟视角`;
  if (compact) {
    button.textContent = item.role_title || "备选岗位";
  } else {
    button.innerHTML = `
      <span class="role-switch-kicker">${escapeHtml(item.lane || "候选")} · ${escapeHtml(item.fit_score ?? 0)} 分</span>
      <strong class="role-switch-name">${escapeHtml(item.role_title || "岗位")}</strong>`;
  }
  button.addEventListener("click", () => setActiveRoleSwitch(item.role_title));
  return button;
}

function renderBackupRoleSwitches(plan) {
  if (!dom.backupRoles) return;
  const backups = getRoleSwitchSimulations(plan).slice(1);
  dom.backupRoles.innerHTML = "";
  dom.backupRoles.className = "text-body";
  if (!backups.length) {
    dom.backupRoles.textContent = (plan.backup_roles || []).join("、") || "无";
    return;
  }
  dom.backupRoles.className = "role-switch-pill-row";
  backups.forEach((item) => {
    dom.backupRoles.appendChild(buildRoleSwitchButton(item, true));
  });
}

function renderRoleSwitchSimulator(plan) {
  const simulations = getRoleSwitchSimulations(plan);
  const active = getActiveRoleSwitch(plan);

  if (dom.roleSwitchToolbar) {
    dom.roleSwitchToolbar.innerHTML = "";
    dom.roleSwitchToolbar.className = "";
    if (!simulations.length) {
      renderEmptyState(dom.roleSwitchToolbar, "当前还没有生成岗位切换方案。");
    } else {
      dom.roleSwitchToolbar.className = "role-switch-grid";
      simulations.forEach((item) => {
        dom.roleSwitchToolbar.appendChild(buildRoleSwitchButton(item));
      });
    }
  }

  if (!active) {
    if (dom.roleSwitchSummary) {
      dom.roleSwitchSummary.innerHTML = `<div class="empty-inline compact">生成分析后可在这里模拟主岗与备选岗切换。</div>`;
    }
    fillListLimited(dom.actionPlan30, plan.action_plan_30_days || [], 3);
    fillListLimited(dom.actionPlan90, plan.action_plan_90_days || [], 3);
    fillListLimited(dom.actionPlan180, plan.action_plan_180_days || [], 3);
    fillListLimited(dom.reviewTargets, plan.next_review_targets || [], 4);
    renderResumeSurgery(plan.resume_surgery || []);
    renderInterviewFocus(plan.interview_focus || []);
    return;
  }

  if (state.currentRoleSwitch !== active.role_title) {
    state.currentRoleSwitch = active.role_title;
  }
  renderBackupRoleSwitches(plan);

  if (dom.roleSwitchSummary) {
    dom.roleSwitchSummary.innerHTML = `
      <div class="summary-shell">
        <div class="summary-head">
          <strong class="summary-title">当前模拟：${escapeHtml(active.lane || "候选")} ${escapeHtml(active.role_title || "岗位")}</strong>
          <span class="tag inline-tag">匹配分 ${escapeHtml(active.fit_score ?? 0)}</span>
        </div>
        <p class="summary-copy" title="${escapeHtml(active.summary || "")}">${escapeHtml(compactText(active.summary || "", 96))}</p>
        <p class="summary-meta" title="${escapeHtml(active.selection_reason || active.positioning || "")}"><strong>保留原因：</strong>${escapeHtml(compactText(active.selection_reason || active.positioning || "", 76))}</p>
        <p class="summary-risk" title="${escapeHtml(active.risk_note || "当前切换仅用于模拟方案，不会改变主推荐岗位。")}"><strong>切换提醒：</strong>${escapeHtml(compactText(active.risk_note || "当前切换仅用于模拟方案，不会改变主推荐岗位。", 68))}</p>
      </div>`;
  }

  fillListLimited(dom.actionPlan30, active.action_plan_30_days || plan.action_plan_30_days || [], 3);
  fillListLimited(dom.actionPlan90, active.action_plan_90_days || plan.action_plan_90_days || [], 3);
  fillListLimited(dom.actionPlan180, active.action_plan_180_days || plan.action_plan_180_days || [], 3);
  fillListLimited(dom.reviewTargets, active.next_review_targets || plan.next_review_targets || [], 4);
  renderResumeSurgery(active.resume_surgery || plan.resume_surgery || []);
  renderInterviewFocus(active.interview_focus || plan.interview_focus || []);
}

function setActiveRoleSwitch(roleTitle) {
  state.currentRoleSwitch = roleTitle || null;
  renderRoleSwitchSimulator(state.latestResult?.career_plan || {});
  renderApplicationStrategy(state.latestResult?.career_plan?.application_strategy || []);
  syncEvidenceViewWithActiveRole();
  syncRoleLinkedPanels(roleTitle);
  const editing = isReportEditing();
  syncReportWithActiveRole({ preserveEditor: editing });
  if (editing) {
    setStatus(`已切换为 ${roleTitle} 视角；当前编辑器内容未被覆盖，保存后可继续导出。`, "success");
  } else {
    setStatus(`已切换为 ${roleTitle} 视角，报告预览已同步刷新。`, "success");
  }
}

function renderCompetencyDimensions(items) {
  if (!dom.competencyDimensions) return;
  dom.competencyDimensions.innerHTML = "";
  if (!items || items.length === 0) {
    dom.competencyDimensions.classList.add("hidden");
    return;
  }
  dom.competencyDimensions.classList.remove("hidden");
  items.forEach((item) => {
    dom.competencyDimensions.innerHTML += `
      <div class="metric-tile">
        <div class="metric-tile-head">
          <strong class="summary-title">${escapeHtml(item.name || "维度")}</strong>
          <strong class="metric-tile-score">${escapeHtml(item.score ?? 0)}</strong>
        </div>
        <p class="metric-tile-copy">${escapeHtml(item.note || item.detail || "")}</p>
      </div>`;
  });
}

function renderRoleComparisonSummary(items) {
  if (!dom.roleComparisonSummary) return;
  dom.roleComparisonSummary.innerHTML = "";
  if (!items || items.length === 0) {
    dom.roleComparisonSummary.innerHTML = `<div class="empty-inline compact">生成分析后展示多岗位雷达读图结论。</div>`;
    return;
  }
  dom.roleComparisonSummary.innerHTML = `
    <div class="note-stack">
      ${items.map((line) => `
        <div class="note-item" title="${escapeHtml(line)}">
          ${escapeHtml(compactText(line, 68))}
        </div>`).join("")}
    </div>`;
}

function renderCompetencyRadar(radarData, items) {
  const chartDom = dom.competencyRadar;
  if (!chartDom) return;
  if (window.radarChartInstance) window.radarChartInstance.dispose();
  const palette = ["#0f766e", "#c2410c", "#2563eb"];
  let option;
  if (radarData?.axes?.length && radarData?.roles?.length) {
    option = {
      color: palette,
      tooltip: {
        trigger: "item",
        backgroundColor: "rgba(255, 255, 255, 0.96)",
        borderColor: "#e7e5e4",
        padding: [12, 16],
        textStyle: { color: "#292524" },
      },
      legend: {
        bottom: 0,
        icon: "circle",
        itemWidth: 10,
        itemHeight: 10,
        textStyle: { color: "#57534e", fontSize: 12 },
      },
      radar: {
        indicator: (radarData.axes || []).map((item) => ({ name: item.name, max: item.max || 100 })),
        radius: "62%",
        center: ["50%", "45%"],
        splitNumber: 4,
        shape: "polygon",
        axisName: { color: "#44403c", fontFamily: "Georgia, serif", fontSize: 12 },
        splitArea: { areaStyle: { color: ["rgba(15, 118, 110, 0.02)", "rgba(15, 118, 110, 0.04)", "rgba(15, 118, 110, 0.06)", "rgba(15, 118, 110, 0.08)"].reverse() } },
        axisLine: { lineStyle: { color: "rgba(15, 118, 110, 0.2)" } },
        splitLine: { lineStyle: { color: "rgba(15, 118, 110, 0.25)" } },
      },
      series: [{
        type: "radar",
        data: (radarData.roles || []).map((role, index) => ({
          value: role.values || [],
          name: `${role.lane || "候选"} ${role.role_title || "岗位"}`,
          symbol: "circle",
          symbolSize: index === 0 ? 7 : 5,
          itemStyle: { color: palette[index % palette.length], borderColor: "#fff", borderWidth: 2 },
          areaStyle: { color: index === 0 ? "rgba(15, 118, 110, 0.16)" : "rgba(194, 65, 12, 0.08)" },
          lineStyle: { width: index === 0 ? 3 : 2, type: index === 0 ? "solid" : "dashed" },
        })),
      }],
    };
  } else if (items && items.length) {
    option = {
      tooltip: { trigger: "item", backgroundColor: "rgba(255, 255, 255, 0.95)", borderColor: "#e7e5e4", padding: [12, 16], textStyle: { color: "#292524" } },
      radar: {
        indicator: items.map((item) => ({ name: item.name, max: 100 })), radius: "65%", center: ["50%", "50%"], splitNumber: 4, shape: "polygon",
        axisName: { color: "#44403c", fontFamily: "Georgia, serif", fontSize: 13 },
        splitArea: { areaStyle: { color: ["rgba(15, 118, 110, 0.02)", "rgba(15, 118, 110, 0.04)", "rgba(15, 118, 110, 0.06)", "rgba(15, 118, 110, 0.08)"].reverse() } },
        axisLine: { lineStyle: { color: "rgba(15, 118, 110, 0.2)" } }, splitLine: { lineStyle: { color: "rgba(15, 118, 110, 0.3)" } },
      },
      series: [{
        type: "radar",
        data: [{ value: items.map((item) => item.score), name: "胜任力量化评估", symbol: "circle", symbolSize: 6, itemStyle: { color: "#0f766e", borderColor: "#fff", borderWidth: 2 }, areaStyle: { color: "rgba(15, 118, 110, 0.15)" }, lineStyle: { width: 2, color: "#0f766e" } }],
      }],
    };
  } else {
    chartDom.innerHTML = `<div class="empty-inline compact">生成分析后展示岗位雷达对照。</div>`;
    window.radarChartInstance = null;
    renderRoleComparisonSummary([]);
    return;
  }
  window.radarChartInstance = echarts.init(chartDom);
  window.radarChartInstance.setOption(option);
  renderRoleComparisonSummary(radarData?.summary || []);
}

function renderEvaluationMetrics(items) {
  if (!dom.evaluationMetrics) return; dom.evaluationMetrics.innerHTML = "";
  if (!items || items.length === 0) return;
  dom.evaluationMetrics.style.display = "grid"; dom.evaluationMetrics.style.gridTemplateColumns = "repeat(auto-fit, minmax(220px, 1fr))"; dom.evaluationMetrics.style.gap = "16px";
  items.forEach((item) => {
    dom.evaluationMetrics.innerHTML += `
      <div class="metric-tile">
        <div class="metric-tile-head">
          <span class="metric-tile-label">${escapeHtml(item.name || "指标")}</span>
          <strong class="metric-tile-score">${item.score ?? 0}</strong>
        </div>
        <p class="metric-tile-copy" title="${escapeHtml(item.detail || "")}">${escapeHtml(compactText(item.detail || "", 48))}</p>
      </div>`;
  });
}

function renderJobSearchSnapshot(items) {
  if (!dom.jobSearchSnapshot) return;
  dom.jobSearchSnapshot.innerHTML = "";
  dom.jobSearchSnapshot.className = "snapshot-grid";
  const source = (items || []).filter((item) => item && (item.label || item.name || item.value || item.detail));
  if (!source.length) {
    renderEmptyState(dom.jobSearchSnapshot, "生成分析后形成求职情境画像。");
    return;
  }
  source.forEach((item) => {
    const label = item.label || item.name || "画像项";
    const value = formatScalar(item.value ?? item.count ?? item.metric, "待补充");
    const detail = cleanCitationText(item.detail || item.description || "");
    dom.jobSearchSnapshot.innerHTML += `
      <article class="snapshot-card">
        <span class="snapshot-label">${escapeHtml(label)}</span>
        <strong class="snapshot-value">${escapeHtml(value)}</strong>
        ${detail ? `<p class="snapshot-detail">${escapeHtml(detail)}</p>` : ""}
      </article>`;
  });
}

function renderRecommendationComparisons(items) {
  if (!dom.recommendationComparisons) return;
  dom.recommendationComparisons.innerHTML = "";
  if (!items || items.length === 0) {
    renderEmptyState(dom.recommendationComparisons, "当前还没有生成排序对比解释。");
    return;
  }
  items.forEach((item) => {
    dom.recommendationComparisons.innerHTML += `
      <div class="insight-card">
        <div class="insight-card-head">
          <strong class="insight-card-title">${escapeHtml(item.role_title || "候选岗位")}</strong>
          <span class="tag inline-tag">原始第 ${escapeHtml(item.raw_rank ?? "-")} 位 · ${escapeHtml(item.lane || "候选")}</span>
        </div>
        <p class="insight-card-copy" title="${escapeHtml(item.why_not_first || "")}"><strong>为什么没排第一：</strong>${escapeHtml(compactText(item.why_not_first || "", 70))}</p>
        <p class="summary-copy" title="${escapeHtml(item.primary_advantage || "")}"><strong>主岗优势：</strong>${escapeHtml(compactText(item.primary_advantage || "", 64))}</p>
        <p class="insight-card-meta" title="${escapeHtml(item.candidate_value || "")}"><strong>保留价值：</strong>${escapeHtml(compactText(item.candidate_value || "", 58))}</p>
        <p class="insight-card-risk" title="${escapeHtml(item.upgrade_path || "")}"><strong>如果想让它升到第一：</strong>${escapeHtml(compactText(item.upgrade_path || "", 58))}</p>
      </div>`;
  });
}

function renderApplicationStrategy(items) {
  if (!dom.applicationStrategy) return;
  dom.applicationStrategy.innerHTML = "";
  if (!items || items.length === 0) {
    renderEmptyState(dom.applicationStrategy, "当前还没有投递作战包。");
    return;
  }
  items.forEach((item) => {
    const isActive = item.role_title === state.currentRoleSwitch;
    dom.applicationStrategy.innerHTML += `
      <div class="insight-card${isActive ? " is-active" : ""}">
        <div class="insight-card-head">
          <strong class="insight-card-title">${escapeHtml(item.role_title || "目标岗位")}</strong>
          <span class="tag inline-tag">${escapeHtml(item.lane || "投递层")} · ${escapeHtml(item.fit_score ?? 0)} 分</span>
        </div>
        <p class="summary-copy" title="${escapeHtml(item.positioning || "")}"><strong>定位：</strong>${escapeHtml(compactText(item.positioning || "", 54))}</p>
        <p class="insight-card-meta" title="${escapeHtml(item.selection_reason || "")}"><strong>入选原因：</strong>${escapeHtml(compactText(item.selection_reason || "", 52))}</p>
        <p class="insight-card-copy" title="${escapeHtml(item.rationale || "")}">${escapeHtml(compactText(item.rationale || "", 76))}</p>
        <div class="chip-row">
          <span class="tag">城市：${escapeHtml(item.city_focus || "待补充")}</span>
          <span class="tag">行业：${escapeHtml(item.industry_focus || "待补充")}</span>
          <span class="tag">薪资：${escapeHtml(item.salary_hint || "待补充")}</span>
        </div>
        <p class="insight-card-meta">检索关键词：${escapeHtml(compactText((item.keywords || []).join("、") || "暂无", 42))}</p>
        <p class="summary-copy" title="${escapeHtml(item.action || "")}"><strong>执行动作：</strong>${escapeHtml(compactText(item.action || "", 58))}</p>
        <p class="insight-card-risk" title="${escapeHtml(item.risk_note || "")}"><strong>注意：</strong>${escapeHtml(compactText(item.risk_note || "", 50))}</p>
        <div class="action-row">
          <span class="helper-copy">${isActive ? "当前模拟中的岗位" : "可一键切换为当前模拟岗位"}</span>
          <button type="button" class="btn ${isActive ? "btn-solid" : "btn-outline"} btn-compact" data-application-role="${escapeHtml(item.role_title || "")}">
            ${isActive ? "当前岗位" : "切换模拟"}
          </button>
        </div>
        <ul class="feature-list list-compact">${(item.deliverables || []).slice(0, 3).map((line) => `<li title="${escapeHtml(line)}">${escapeHtml(compactText(line, 48))}</li>`).join("")}</ul>
      </div>`;
  });
  dom.applicationStrategy.querySelectorAll("[data-application-role]").forEach((button) => {
    button.addEventListener("click", () => {
      const roleTitle = button.getAttribute("data-application-role") || "";
      if (roleTitle && roleTitle !== state.currentRoleSwitch) {
        setActiveRoleSwitch(roleTitle);
      }
    });
  });
}

function renderResumeSurgery(items) {
  if (!dom.resumeSurgery) return;
  dom.resumeSurgery.innerHTML = "";
  if (!items || items.length === 0) {
    renderEmptyState(dom.resumeSurgery, "当前还没有简历改写建议。");
    return;
  }
  items.forEach((item) => {
    dom.resumeSurgery.innerHTML += `
      <div class="insight-card">
        <div class="insight-card-head">
          <strong class="insight-card-title">${escapeHtml(item.section || "改写项")}</strong>
          <span class="tag inline-tag">简历补强</span>
        </div>
        <p class="summary-copy" title="${escapeHtml(item.issue || "")}"><strong>问题：</strong>${escapeHtml(compactText(item.issue || "", 54))}</p>
        <p class="insight-card-copy" title="${escapeHtml(item.action || "")}"><strong>动作：</strong>${escapeHtml(compactText(item.action || "", 58))}</p>
        <p class="insight-card-meta" title="${escapeHtml(item.deliverable || "")}"><strong>交付物：</strong>${escapeHtml(compactText(item.deliverable || "", 50))}</p>
      </div>`;
  });
}

function renderInterviewFocus(items) {
  if (!dom.interviewFocus) return;
  dom.interviewFocus.innerHTML = "";
  if (!items || items.length === 0) {
    renderEmptyState(dom.interviewFocus, "当前还没有面试冲刺题板。");
    return;
  }
  items.forEach((item) => {
    dom.interviewFocus.innerHTML += `
      <div class="insight-card">
        <div class="insight-card-head">
          <strong class="insight-card-title">${escapeHtml(item.theme || "冲刺题")}</strong>
          <span class="tag inline-tag">面试冲刺</span>
        </div>
        <p class="insight-card-copy" title="${escapeHtml(item.question || "")}">${escapeHtml(compactText(item.question || "", 72))}</p>
        <p class="summary-copy" title="${escapeHtml(item.signal || "")}"><strong>考察信号：</strong>${escapeHtml(compactText(item.signal || "", 48))}</p>
        <p class="insight-card-meta" title="${escapeHtml(item.prep || "")}"><strong>准备动作：</strong>${escapeHtml(compactText(item.prep || "", 48))}</p>
      </div>`;
  });
}

function renderGapBenefitAnalysis(items) {
  if (!dom.gapBenefitGrid) return; dom.gapBenefitGrid.innerHTML = "";
  if (!items || items.length === 0) { dom.gapBenefitGrid.innerHTML = `<div class="empty-inline compact">当前还没有差距-收益分析。</div>`; return; }
  items.forEach((item) => {
    dom.gapBenefitGrid.innerHTML += `
      <div class="stack-card stack-card-accent gap-benefit-card">
        <div class="stack-card-head">
          <span class="stack-card-kicker">${escapeHtml(item.dimension || "维度")}</span>
          <span class="tag tag-accent inline-tag">+${item.expected_gain ?? 0} 分</span>
        </div>
        <h4 class="stack-card-title">${escapeHtml(item.gap || "差距项")}</h4>
        <p class="stack-card-meta" title="${escapeHtml(item.detail || "")}">${escapeHtml(compactText(item.detail || "", 68))}</p>
        <div class="stack-card-foot">
          <p class="stack-card-note">预计：${item.current_score ?? 0} → ${item.projected_score ?? 0} 分</p>
          <ul class="feature-list list-compact stack-card-list">
            <li title="${escapeHtml(item.action || "暂无动作")}">动作：${escapeHtml(compactText(item.action || "暂无动作", 48))}</li>
            <li title="${escapeHtml(item.expected_evidence || "暂无证据建议")}">证据：${escapeHtml(compactText(item.expected_evidence || "暂无证据建议", 48))}</li>
          </ul>
          <div class="chip-row">${(item.citations || []).slice(0, 4).map((citation) => `<span class="tag">${escapeHtml(citation)}</span>`).join("")}</div>
        </div>
      </div>`;
  });
}

function renderPlanSelfChecks(items) {
  if (!dom.planSelfChecks) return; dom.planSelfChecks.innerHTML = "";
  if (!items || items.length === 0) { dom.planSelfChecks.innerHTML = `<div class="empty-inline compact">当前还没有计划自检结果。</div>`; return; }
  items.forEach((item) => {
    const isPass = item.status === "通过";
    const isWarn = item.status === "关注";
    const toneClass = isPass ? "stack-card-status-ok" : (isWarn ? "stack-card-status-warn" : "stack-card-status-risk");
    dom.planSelfChecks.innerHTML += `
      <div class="stack-card ${toneClass}">
        <div class="stack-card-head">
          <span class="stack-card-title">${escapeHtml(item.name || "自检项")}</span>
          <strong class="metric-tile-score">${item.score ?? 0}</strong>
        </div>
        <p class="summary-copy" title="${escapeHtml(item.detail || "")}"><strong>${escapeHtml(item.status || "待检查")}</strong> · ${escapeHtml(compactText(item.detail || "", 64))}</p>
        <p class="stack-card-meta" title="${escapeHtml(item.action || "")}">建议：${escapeHtml(compactText(item.action || "暂无建议", 56))}</p>
      </div>`;
  });
}

function renderLearningLoop(items) {
  if (!dom.learningSprints) return; dom.learningSprints.innerHTML = "";
  if (!items || items.length === 0) { dom.learningSprints.innerHTML = `<div class="empty-inline compact">暂无专项补强节点。</div>`; return; }
  items.forEach((item) => {
    dom.learningSprints.innerHTML += `
      <div class="stack-card stack-card-neutral">
        <div class="stack-card-head">
          <strong class="stack-card-title">${escapeHtml(item.title || "专项补强")}</strong>
          <span class="tag tag-ghost inline-tag">${escapeHtml(item.type || "任务")}</span>
        </div>
        <p class="stack-card-copy" title="${escapeHtml(item.reason || "")}">${escapeHtml(compactText(item.reason || "", 76))}</p>
        <div class="stack-card-foot">
          <span class="stack-card-note">交付闭环</span>
          <p class="stack-card-meta" title="${escapeHtml(item.deliverable || "")}">${escapeHtml(compactText(item.deliverable || "", 58))}</p>
        </div>
      </div>`;
  });
}

function renderAgentQuestions(questions, existingAnswers = {}) {
  if (!dom.agentQuestionList) return;
  dom.agentQuestionList.innerHTML = "";
  if (!questions || questions.length === 0) {
    renderEmptyState(dom.agentQuestionList, "情境对齐完毕，暂无追问。");
    return;
  }
  questions.forEach((question) => {
    const preset = existingAnswers?.[question.id] || question.suggested_answer || "";
    dom.agentQuestionList.innerHTML += `
      <div class="field-panel">
        <label class="field-panel-label">${escapeHtml(question.question || "补充问题")}</label>
        <p class="field-panel-hint" title="${escapeHtml(question.rationale || "补充此信息以提升规划精度。")}">${escapeHtml(compactText(question.rationale || "补充此信息以提升规划精度。", 44))}</p>
        <input type="text" class="input-field" data-agent-id="${escapeHtml(question.id || "")}" placeholder="${escapeHtml(question.placeholder || "请输入补充信息")}" value="${escapeHtml(preset)}" />
      </div>`;
  });
}

function renderSelfAssessmentForm(selfAssessment) {
  if (!dom.selfAssessmentForm) return;
  dom.selfAssessmentForm.innerHTML = "";
  const items = selfAssessment?.items || [];
  if (!items.length) {
    renderEmptyState(dom.selfAssessmentForm, "待确立基准岗位后生成专业量表。");
    return;
  }
  items.forEach((item, index) => {
    const currentValue = item.score === null || item.score === undefined ? null : Number(item.score);
    const fieldName = `assessment-${item.id}-${index}`;
    dom.selfAssessmentForm.innerHTML += `
      <div class="field-panel">
        <label class="field-panel-label">${escapeHtml(item.prompt || "题目")}</label>
        <p class="field-panel-hint" title="${escapeHtml(item.focus || "岗位基础能力")}">考察点：${escapeHtml(compactText(item.focus || "岗位基础能力", 42))}</p>
        <div class="choice-row">
          <label class="choice-option"><input type="radio" name="${fieldName}" data-self-assessment-id="${escapeHtml(item.id || "")}" value="0" ${currentValue === 0 ? "checked" : ""}> <span>待补强</span></label>
          <label class="choice-option"><input type="radio" name="${fieldName}" data-self-assessment-id="${escapeHtml(item.id || "")}" value="1" ${currentValue === 1 ? "checked" : ""}> <span>已入门</span></label>
          <label class="choice-option"><input type="radio" name="${fieldName}" data-self-assessment-id="${escapeHtml(item.id || "")}" value="2" ${currentValue === 2 ? "checked" : ""}> <span>可实战</span></label>
        </div>
      </div>`;
  });
}

function renderSelfAssessmentSummary(data) {
  if (!dom.selfAssessmentSummary) return;
  dom.selfAssessmentSummary.innerHTML = "";
  if (!data || !(data.items || []).length) {
    renderEmptyState(dom.selfAssessmentSummary, "完成岗位自测后展示摸底结论。");
    return;
  }
  const summaryItems = data.items || [];
  dom.selfAssessmentSummary.innerHTML = `
    <div class="summary-shell">
      <div class="summary-head">
        <strong class="summary-title">${escapeHtml(data.title || "岗位自测")}</strong>
        <span class="tag inline-tag">${escapeHtml(data.score ?? 0)} 分</span>
      </div>
      <p class="summary-copy" title="${escapeHtml(data.summary || "暂无结论")}">${escapeHtml(compactText(data.summary || "暂无结论", 88))}</p>
      <div class="chip-row">
        ${summaryItems.map((item) => `<span class="tag">${escapeHtml(item.focus || item.prompt || "考察点")}：${escapeHtml(item.level || "待补强")}</span>`).join("")}
      </div>
    </div>`;
}

function buildLiveSelfAssessmentState(baseAssessment) {
  const assessment = JSON.parse(JSON.stringify(baseAssessment || {}));
  const items = assessment.items || [];
  if (!items.length) return assessment;
  const levelMap = {
    0: "待补强",
    1: "已入门",
    2: "可实战",
  };
  let answeredCount = 0;
  let scoreSum = 0;
  const weakFocuses = [];
  items.forEach((item) => {
    const checked = dom.selfAssessmentForm?.querySelector(`[data-self-assessment-id="${item.id}"]:checked`);
    if (!checked) {
      item.score = null;
      item.level = "未作答";
      return;
    }
    const value = Number(checked.value);
    item.score = value;
    item.level = levelMap[value] || "未作答";
    answeredCount += 1;
    scoreSum += value;
    if (value === 0 && item.focus) weakFocuses.push(item.focus);
  });
  const percent = answeredCount ? Math.round((scoreSum / (answeredCount * 2)) * 100) : 0;
  assessment.score = percent;
  assessment.weak_focuses = weakFocuses;
  if (!answeredCount) {
    assessment.summary = "建议先完成岗位自测，验证推荐结果和能力证据。";
  } else if (answeredCount < items.length) {
    assessment.summary = `已完成 ${answeredCount}/${items.length} 项自测，建议继续补完剩余题目以获得更稳定的岗位判断。`;
  } else if (weakFocuses.length) {
    assessment.summary = `当前已完成全部自测，优先补强：${weakFocuses.join("、")}。`;
  } else {
    assessment.summary = "当前自测结果较好，可以进入项目举证与复测阶段。";
  }
  return assessment;
}

function refreshLiveSelfAssessmentSummary() {
  const baseAssessment = state.latestResult?.career_plan?.self_assessment;
  if (!baseAssessment) return;
  const liveAssessment = buildLiveSelfAssessmentState(baseAssessment);
  renderSelfAssessmentSummary(liveAssessment);
}

function renderServiceLoop(items) {
  if (!dom.serviceLoop) return;
  dom.serviceLoop.innerHTML = "";
  if (!items || items.length === 0) {
    renderEmptyState(dom.serviceLoop, "暂无生命周期数据。");
    return;
  }
  items.forEach((item, index) => {
    dom.serviceLoop.innerHTML += `
      <div class="process-card">
        <div class="process-index">0${index + 1}</div>
        <div>
          <strong class="process-title">${escapeHtml(item.stage || "阶段")} <span class="tag">${escapeHtml(item.status || "")}</span></strong>
          <p class="process-copy">${escapeHtml(item.detail || "")}</p>
        </div>
      </div>`;
  });
}

function renderResourceMap(items) {
  if (!dom.resourceMap) return; dom.resourceMap.innerHTML = "";
  if (!items || items.length === 0) { dom.resourceMap.innerHTML = `<div class="empty-inline compact">暂无落地资源映射。</div>`; return; }
  dom.resourceMap.style.display = "grid"; dom.resourceMap.style.gridTemplateColumns = "repeat(auto-fit, minmax(280px, 1fr))"; dom.resourceMap.style.gap = "20px";
  items.forEach((item) => {
    const isHigh = item.priority === "高";
    dom.resourceMap.innerHTML += `
      <div class="resource-card${isHigh ? " is-priority" : ""}">
        <div class="action-row"><span class="mini-label">${escapeHtml(item.category || "资源")}</span><span class="tag inline-tag">优先级: ${escapeHtml(item.priority || "中")}</span></div>
        <h5 class="insight-card-title">${escapeHtml(item.title)}</h5>
        <p class="insight-card-copy" title="${escapeHtml(item.description || "")}">${escapeHtml(compactText(item.description || "", 74))}</p>
        <div class="resource-card-output" title="${escapeHtml(item.deliverable || "")}"><strong class="summary-title">阶段产出：</strong> ${escapeHtml(compactText(item.deliverable || "", 52))}</div>
      </div>`;
  });
}

function renderSimilarCases(items) {
  if (!dom.similarCases) return; dom.similarCases.innerHTML = "";
  if (!items || items.length === 0) { dom.similarCases.innerHTML = `<div class="empty-inline compact">当前还没有可参考的相似案例。</div>`; return; }
  items.forEach((item) => {
    const reasons = item.reasons || [];
    dom.similarCases.innerHTML += `
      <div class="insight-card">
        <span class="mini-label">${escapeHtml(item.student_name || "相似案例")}</span>
        <h4 class="insight-card-title">${escapeHtml(item.primary_role || "未生成")} · ${item.primary_score ?? 0} 分</h4>
        <p class="insight-card-meta">${escapeHtml(item.major || "专业未填写")}｜${escapeHtml(item.created_at || "")}｜复核：${escapeHtml(item.review_status || "未复核")}</p>
        <div class="chip-row">
          <span class="tag">相似度 ${item.similarity_score ?? 0}</span>
          ${reasons.map((reason) => `<span class="tag">${escapeHtml(reason)}</span>`).join("")}
        </div>
        <ul class="feature-list list-compact"><li title="${escapeHtml(item.takeaway || "暂无启发")}">${escapeHtml(compactText(item.takeaway || "暂无启发", 58))}</li></ul>
      </div>`;
  });
}

function renderGroundedEvidence(bundle) {
  const roleTitle = String(bundle?.role_title || "").trim();
  const summaryText = compactText(bundle?.summary || "生成分析后展示证据链摘要。", 96);
  if (dom.evidenceSummary) {
    dom.evidenceSummary.textContent = roleTitle
      ? `当前证据视角：${roleTitle}｜${summaryText}`
      : summaryText;
  }
  if (dom.matchedTerms) fillTagList(dom.matchedTerms, bundle?.query_terms || [], "等待生成检索词");
  if (!dom.evidenceSnippets) return; dom.evidenceSnippets.innerHTML = "";
  const items = bundle?.items || [];
  if (!items.length) { dom.evidenceSnippets.innerHTML = `<div class="empty-inline compact">本次解析未命中有效切片。</div>`; return; }
  
  dom.evidenceSnippets.innerHTML += `
    <div class="summary-shell">
      <div class="summary-head">
        <div>
          <span class="mini-label">${escapeHtml(roleTitle || "Evidence Hit Rate")}</span>
          <h4 class="insight-card-title">${bundle?.evidence_hit_rate ?? 0}% · ${escapeHtml(bundle?.retrieval_mode || "未生成")}</h4>
        </div>
        <div class="score-badge">${(bundle?.hit_terms || []).length}/${(bundle?.target_terms || []).length || 1}</div>
      </div>
      <p class="summary-copy">命中术语：${escapeHtml(compactText((bundle?.hit_terms || []).join("、") || "无", 48))}</p>
      <p class="summary-meta">目标术语：${escapeHtml(compactText((bundle?.target_terms || []).join("、") || "无", 48))}</p>
    </div>`;

  items.forEach((item) => {
    dom.evidenceSnippets.innerHTML += `
      <div class="evidence-card is-accent">
        <div class="evidence-head"><strong class="evidence-title">${escapeHtml(item.job_title || item.source_title || "证据片段")} <span class="citation-inline">${escapeHtml(item.citation_id || "[E]")}</span></strong><span class="tag inline-tag">相关度 ${item.score ?? 0}</span></div>
        <p class="evidence-meta">${escapeHtml(item.company_name || "岗位模板")}｜${escapeHtml(item.city || "未知")}｜命中词：${highlightTerms(compactText((item.matched_terms || []).join("、") || "无", 44), item.matched_terms || [])}</p>
        <p class="evidence-copy" title="${escapeHtml(item.snippet || "暂无片段")}">${highlightTerms(compactText(item.snippet || "暂无片段", 150), item.matched_terms || [])}</p>
      </div>`;
  });
}

function renderTemplateEvidence(data) {
  if (!dom.templateEvidence) return;
  dom.templateEvidence.innerHTML = "";
  if (!data) {
    renderEmptyState(dom.templateEvidence, "请先生成分析结果，再查看主岗位基线样本。");
    return;
  }
  const activeLabel = state.currentTemplateRole === data.role_title ? "当前模拟岗位基线" : "岗位模板";
  const representativeJobs = data.representative_jobs || [];
  dom.templateEvidence.innerHTML = `
    <div class="template-shell">
      <div class="template-head">
        <h5 class="template-title">${escapeHtml(data.role_title || "岗位模板")}</h5>
        <span class="tag inline-tag">${escapeHtml(activeLabel)}</span>
      </div>
      <p class="summary-meta">源岗位名：${escapeHtml(data.source_title || data.role_title || "")}｜样本数：${escapeHtml(data.dataset_job_count ?? 0)}</p>
      <div class="chip-row">${(data.dataset_evidence?.top_skills || []).slice(0, 8).map((item) => `<span class="tag">${escapeHtml(item[0])} · ${escapeHtml(item[1])}</span>`).join("")}</div>
    </div>
    ${representativeJobs.length ? representativeJobs.map((item) => `
      <div class="evidence-card">
        <strong class="evidence-title">${escapeHtml(item.company_name || "未知企业")}</strong>
        <p class="evidence-meta">${escapeHtml(item.job_title || "")}｜${escapeHtml(item.city || "")}｜${escapeHtml(item.salary_range || "")}</p>
        <p class="evidence-copy" title="${escapeHtml(item.job_detail || "暂无详情")}">${escapeHtml(compactText(item.job_detail || "暂无详情", 110))}</p>
      </div>`).join("") : `<div class="empty-inline compact">暂无代表样本。</div>`}
  `;
}

function renderJdSearchResults(items) {
  if (!dom.jdSearchResults) return;
  dom.jdSearchResults.innerHTML = "";
  if (!items || items.length === 0) {
    renderEmptyState(dom.jdSearchResults, "本地库未检索到相关 JD。");
    return;
  }
  items.forEach((item) => {
    dom.jdSearchResults.innerHTML += `
      <div class="evidence-card">
        <div class="evidence-head">
          <strong class="evidence-title">${escapeHtml(item.job_title || "岗位")}</strong>
          <span class="tag inline-tag">匹配度 ${escapeHtml(item.score ?? 0)}</span>
        </div>
        <p class="evidence-meta">${escapeHtml(item.company_name || "未知企业")}｜${escapeHtml(item.city || "未知城市")}｜${escapeHtml(item.salary_range || "薪资未知")}</p>
        <p class="evidence-copy" title="${escapeHtml(item.job_detail || "暂无岗位详情")}">${escapeHtml(compactText(item.job_detail || "暂无岗位详情", 110))}</p>
      </div>`;
  });
}

function renderStakeholderViews(items) {
  if (!dom.stakeholderViews) return;
  dom.stakeholderViews.innerHTML = "";
  if (!items || items.length === 0) {
    renderEmptyState(dom.stakeholderViews, "当前还没有多角色视角。");
    return;
  }
  items.forEach((item) => {
    dom.stakeholderViews.innerHTML += `
      <div class="insight-card">
        <span class="mini-label">${escapeHtml(item.role || "角色")}</span>
        <h4 class="insight-card-title">${escapeHtml(item.headline || "摘要")}</h4>
        <ul class="feature-list list-compact">${(item.items || []).slice(0, 3).map((line) => `<li title="${escapeHtml(line)}">${escapeHtml(compactText(line, 58))}</li>`).join("")}</ul>
      </div>`;
  });
}

function renderTechnicalModules(items, keywords = []) {
  if (dom.technicalKeywords) fillTagList(dom.technicalKeywords, keywords || [], "等待生成技术关键词");
  if (!dom.technicalModules) return;
  dom.technicalModules.innerHTML = "";
  if (!items || items.length === 0) {
    renderEmptyState(dom.technicalModules, "当前还没有技术模块说明。");
    return;
  }
  items.forEach((item) => {
    dom.technicalModules.innerHTML += `
      <div class="stack-card stack-card-neutral">
        <div class="stack-card-head">
          <strong class="stack-card-title">${escapeHtml(item.name || item.title || "模块")}</strong>
          ${item.tag ? `<span class="tag tag-ghost inline-tag">${escapeHtml(item.tag)}</span>` : ""}
        </div>
        <p class="stack-card-copy" title="${escapeHtml(item.detail || "")}">${escapeHtml(compactText(item.detail || "", 90))}</p>
      </div>`;
  });
}

function renderInnovationHighlights(items) {
  if (!dom.innovationHighlights) return;
  dom.innovationHighlights.innerHTML = "";
  if (!items || items.length === 0) {
    renderEmptyState(dom.innovationHighlights, "当前还没有创新亮点摘要。");
    return;
  }
  items.forEach((item) => {
    dom.innovationHighlights.innerHTML += `
      <div class="insight-card">
        <div class="insight-card-head">
          <strong class="insight-card-title">${escapeHtml(item.title || "亮点")}</strong>
          ${item.tag ? `<span class="tag tag-success inline-tag">${escapeHtml(item.tag)}</span>` : ""}
        </div>
        <p class="insight-card-copy" title="${escapeHtml(item.detail || "")}">${escapeHtml(compactText(item.detail || "", 94))}</p>
      </div>`;
  });
}

function renderCareerGraph(student, plan, matches) {
  if (!dom.careerGraph) return;
  const primary = plan?.primary_role || matches?.[0]?.role_title || "主岗位";
  const backups = (plan?.backup_roles || []).slice(0, 2);
  const path = (plan?.primary_growth_path || []).slice(0, 4);
  const height = 340;
  const nodeWidth = 150;
  const nodeHeight = 56;
  const centerY = 148;
  const upperY = 86;
  const lowerY = 228;
  const nodes = [
    { id: "student", label: student?.name || "学生", x: 74, y: centerY, tone: "teal", meta: "当前画像" },
    { id: "primary", label: primary, x: 286, y: centerY, tone: "accent", meta: "主推枢纽" },
  ];
  path.slice(1, 4).forEach((item, index) => nodes.push({ id: `path-${index}`, label: item, x: 510 + index * 160, y: upperY, tone: "teal", meta: "纵向演进" }));
  backups.forEach((item, index) => nodes.push({ id: `backup-${index}`, label: item, x: 510 + index * 160, y: lowerY, tone: "muted", meta: "横向转移" }));
  const nodeMap = new Map(nodes.map((node) => [node.id, node]));
  const centerYOf = (node) => node.y + nodeHeight / 2;
  const rightEdge = (node) => node.x + nodeWidth;
  const leftEdge = (node) => node.x;
  const lines = [];
  const connect = (fromId, toId, tone, mode = "horizontal") => {
    const from = nodeMap.get(fromId);
    const to = nodeMap.get(toId);
    if (!from || !to) return;
    if (mode === "diagonal") {
      lines.push({ x1: rightEdge(from) - 8, y1: centerYOf(from), x2: leftEdge(to) + 8, y2: centerYOf(to), tone });
      return;
    }
    lines.push({ x1: rightEdge(from), y1: centerYOf(from), x2: leftEdge(to), y2: centerYOf(to), tone });
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
    if (nodeMap.has("backup-1")) connect("backup-0", "backup-1", "muted");
  }
  const colorMap = { accent: "#d97706", teal: "#0f766e", muted: "#78716c" };
  const width = Math.max(940, ...nodes.map((node) => node.x + nodeWidth)) + 56;
  dom.careerGraph.innerHTML = `
    <svg viewBox="0 0 ${width} ${height}" preserveAspectRatio="xMinYMin meet" style="width:100%; height:auto; background:var(--surface-alt); border-radius:16px; border:1px solid var(--border);">
      ${lines.map((line) => `<line x1="${line.x1}" y1="${line.y1}" x2="${line.x2}" y2="${line.y2}" stroke="${colorMap[line.tone]}" stroke-width="3" stroke-linecap="round" opacity="0.6"></line>`).join("")}
      ${nodes.map((node) => `
        <g transform="translate(${node.x}, ${node.y})">
          <rect rx="28" ry="28" width="${nodeWidth}" height="${nodeHeight}" fill="#ffffff" stroke="${colorMap[node.tone]}" stroke-width="2"></rect>
          <text x="${nodeWidth / 2}" y="22" fill="#78716c" font-size="11" text-anchor="middle">${escapeHtml(node.meta)}</text>
          <text x="${nodeWidth / 2}" y="40" fill="#292524" font-size="14" font-weight="700" text-anchor="middle">${escapeHtml(node.label)}</text>
        </g>`).join("")}
    </svg>`;
}

function renderHistory(items) {
  renderRecordList(
    dom.historyList,
    items,
    (item) => `
      <button class="history-card" data-history-id="${escapeHtml(item.id)}" type="button">
        <span class="history-card-index">#${escapeHtml(item.id)}</span>
        <span class="history-card-main">
          <strong class="history-card-title">${escapeHtml(item.student_name || "学生")} → ${escapeHtml(item.primary_role || "未生成")}</strong>
          <small class="history-card-meta">${escapeHtml(item.created_at || "")}｜${escapeHtml(item.parser_used_mode || "")}</small>
        </span>
      </button>`,
    "暂无归档快照。"
  );
  dom.historyList?.querySelectorAll("[data-history-id]").forEach((button) => {
    button.addEventListener("click", () => loadAnalysis(button.dataset.historyId));
  });
}

function renderSystemChecks(payload) {
  if (!dom.systemCheckList) return;
  dom.systemCheckList.innerHTML = "";
  const checks = payload?.checks || [];
  if (!checks.length) {
    renderEmptyState(dom.systemCheckList, "当前还没有系统健康数据。");
    return;
  }
  checks.forEach((check) => {
    const toneClass = check.status === "ok" ? "is-ok" : (check.status === "warn" ? "is-warn" : "is-risk");
    dom.systemCheckList.innerHTML += `
      <li class="status-item">
        <span class="status-dot ${toneClass}"></span>
        <div>
          <strong class="status-title">${escapeHtml(check.name || "检查项")}</strong>
          <span class="status-detail" title="${escapeHtml(check.detail || "")}">${escapeHtml(compactText(check.detail || "", 80))}</span>
        </div>
      </li>`;
  });
}

function renderReviewRecords(items) {
  renderRecordList(
    dom.reviewRecords,
    items,
    (item) => `
      <div class="review-card is-primary">
        <div class="stack-card-head">
          <strong class="stack-card-title">${escapeHtml(item.reviewer_name || "老师")} · ${escapeHtml(item.decision || "待定")}</strong>
        </div>
        <p class="history-card-meta">${escapeHtml(item.reviewer_role || "辅导员")}｜${escapeHtml(item.created_at || "")}</p>
        <p class="review-note" title="${escapeHtml(item.notes || "未填写复核备注")}">${escapeHtml(compactText(item.notes || "未填写复核备注", 110))}</p>
      </div>`,
    "当前分析还没有老师复核记录。"
  );
}

function renderSchoolDashboard(data) {
  renderMetricCards(dom.schoolDashboardStats, data?.summary_cards || [], "生成分析后形成学校运营看板。");
  renderSimpleDistribution(dom.schoolDistribution, [
    { title: "主岗位 Top5", items: data?.top_roles || [] },
    { title: "专业分布 Top5", items: data?.major_distribution || [] },
    { title: "城市偏好 Top5", items: data?.city_distribution || [] },
  ], "暂无结构分布数据。");
  renderMetricCards(dom.schoolServiceSegments, data?.service_segments || [], "暂无服务分层数据。");
  renderMetricCards(dom.schoolReviewMetrics, data?.review_metrics || [], "暂无复核指标。");
  renderMetricCards(dom.schoolGovernanceMetrics, data?.governance_metrics || [], "暂无治理指标。");

  renderRecordList(
    dom.schoolRecentReviews,
    data?.recent_reviews || [],
    (item) => `
      <div class="review-card is-muted">
        <strong class="stack-card-title">${escapeHtml(item.student_name || "学生")} · ${escapeHtml(item.decision || "待定")}</strong>
        <p class="history-card-meta">${escapeHtml(item.reviewer_name || "老师")}｜${escapeHtml(item.created_at || "")}</p>
      </div>`,
    "暂无复核留痕。"
  );

  renderRecordList(
    dom.schoolFollowUp,
    data?.follow_up_students || [],
    (item) => `
      <div class="review-card is-muted">
        <strong class="stack-card-title">${escapeHtml(item.name || "学生")} · ${escapeHtml(item.primary_role || "未生成")}</strong>
        <p class="history-card-meta">${escapeHtml(item.major || "专业未填写")}｜主岗分 ${escapeHtml(item.primary_score ?? 0)}｜完整度 ${escapeHtml(item.completeness ?? 0)}｜${escapeHtml(item.review_status || "待复核")}</p>
      </div>`,
    "暂无重点跟进学生。"
  );

  renderRecordList(
    dom.schoolPushRecommendations,
    data?.push_recommendations || [],
    (item) => `
      <div class="review-card">
        <div class="stack-card-head">
          <strong class="stack-card-title">${escapeHtml(item.title || "推岗建议")}</strong>
          <span class="tag inline-tag">${escapeHtml(item.type || "建议")} · ${escapeHtml(item.count ?? 0)}</span>
        </div>
        <p class="stack-card-meta" title="${escapeHtml(item.detail || "")}">${escapeHtml(compactText(item.detail || "", 92))}</p>
      </div>`,
    "暂无推岗建议。"
  );

  renderRecordList(
    dom.schoolAuditQueue,
    data?.audit_queue || [],
    (item) => `
      <div class="review-card is-muted">
        <strong class="stack-card-title">${escapeHtml(item.name || "学生")} · ${escapeHtml(item.primary_role || "未生成")}</strong>
        <p class="history-card-meta">${escapeHtml(item.major || "专业未填写")}｜${escapeHtml(item.city || "城市未填写")}｜主岗分 ${escapeHtml(item.primary_score ?? 0)}</p>
        <p class="stack-card-meta" title="${escapeHtml((item.reasons || []).join("、") || "无")}">原因：${escapeHtml(compactText((item.reasons || []).join("、") || "无", 78))}</p>
      </div>`,
    "暂无待抽检记录。"
  );
}

function renderBenchmark(data) {
  if (dom.benchmarkSummaryCards) dom.benchmarkSummaryCards.innerHTML = "";
  if (dom.benchmarkVerdict) dom.benchmarkVerdict.innerHTML = "";
  if (dom.benchmarkCases) dom.benchmarkCases.innerHTML = "";
  if (!data || !(data.summary_cards || []).length) {
    if (dom.benchmarkStatus) dom.benchmarkStatus.innerHTML = ">// 等待运行内置样例压测...";
    if (dom.benchmarkSummaryCards) renderEmptyState(dom.benchmarkSummaryCards, "运行验证后展示核心指标。");
    return;
  }
  if (dom.benchmarkStatus) {
    dom.benchmarkStatus.innerHTML = `<span class="benchmark-status-copy">$ [SUCCESS]</span> ${escapeHtml(data.verdict?.label || "验证完成")}<br/>parser_mode=${escapeHtml(data.parser_mode || "rule")} ｜ executed=${escapeHtml(data.executed_case_count ?? 0)} ｜ skipped=${escapeHtml(data.skipped_case_count ?? 0)}`;
  }
  renderMetricCards(dom.benchmarkSummaryCards, data.summary_cards || [], "暂无基准测试数据。");
  if (dom.benchmarkVerdict) {
    dom.benchmarkVerdict.innerHTML = `
      <div class="benchmark-verdict-box">
        <div class="benchmark-verdict-head">
          <span class="benchmark-status-copy">$ [SUCCESS] 评测跑通</span>
          <strong>${escapeHtml(data.verdict?.label || "待评估")}</strong>
        </div>
        <p class="stack-card-copy benchmark-detail" title="${escapeHtml(data.verdict?.detail || "")}">> ${escapeHtml(compactText(data.verdict?.detail || "", 132))}</p>
        <ul class="feature-list list-compact">${(data.judge_notes || []).slice(0, 4).map((item) => `<li title="${escapeHtml(item)}">${escapeHtml(compactText(item, 62))}</li>`).join("")}</ul>
      </div>`;
  }
  renderRecordList(
    dom.benchmarkCases,
    data.cases || [],
    (item) => `
      <div class="benchmark-case-card">
        <span class="mini-label">${escapeHtml(item.label || "样例")}</span>
        <h4 class="benchmark-case-title">${escapeHtml(item.primary_role || "未生成")} · ${escapeHtml(item.primary_score ?? 0)} 分</h4>
        <div class="chip-row">
          <span class="tag ${item.top1_hit ? "tag-success" : "tag-danger"}">Top1 ${item.top1_hit ? "命中" : "未命中"}</span>
          <span class="tag ${item.pass_case ? "tag-success" : "tag-danger"}">通过 ${item.pass_case ? "是" : "否"}</span>
          <span class="tag">证据 ${escapeHtml(item.evidence_hit_rate ?? 0)}</span>
          <span class="tag">回退 ${item.fallback_used ? "是" : "否"}</span>
        </div>
        <ul class="feature-list list-compact">${(item.observations || []).slice(0, 3).map((line) => `<li title="${escapeHtml(line)}">${escapeHtml(compactText(line, 62))}</li>`).join("")}</ul>
      </div>`,
    "暂无样例评测结果。"
  );
}

// ==========================================
// 4. 核心主流水线 (The Master Pipeline)
// ==========================================
function renderResults(data) {
  if (dom.emptyState) dom.emptyState.classList.add("hidden");
  if (dom.resultsContent) dom.resultsContent.classList.remove("hidden");
  state.latestResult = data; state.currentAnalysisId = data.analysis_id || data.id || null;
  state.currentRoleSwitch = data.career_plan?.role_switch_simulations?.[0]?.role_title || data.career_plan?.primary_role || null;
  state.baseReport = data.report_markdown || "";
  state.currentAutoReport = "";
  state.currentReport = state.baseReport;

  // 渲染所有受保护的组件
  if (data.career_plan) renderCareerPlan(data.career_plan, data.matches);
  renderCompetencyRadar(data.career_plan?.role_comparison_radar || {}, data.career_plan?.competency_dimensions || []);
  renderCompetencyDimensions(data.career_plan?.competency_dimensions || []);
  if (data.career_plan?.evaluation_metrics) renderEvaluationMetrics(data.career_plan.evaluation_metrics);
  renderJobSearchSnapshot(data.career_plan?.job_search_snapshot || []);
  renderRecommendationComparisons(data.career_plan?.recommendation_comparisons || []);
  if (data.career_plan?.gap_benefit_analysis) renderGapBenefitAnalysis(data.career_plan.gap_benefit_analysis);
  if (data.career_plan?.plan_self_checks) renderPlanSelfChecks(data.career_plan.plan_self_checks);
  if (data.career_plan?.learning_sprints) renderLearningLoop(data.career_plan.learning_sprints);
  if (data.career_plan?.resource_map) renderResourceMap(data.career_plan.resource_map);
  renderApplicationStrategy(data.career_plan?.application_strategy || []);
  renderRoleSwitchSimulator(data.career_plan || {});
  syncRoleLinkedPanels(state.currentRoleSwitch, { showLoading: true });
  syncReportWithActiveRole();
  if (data.career_plan?.similar_cases) renderSimilarCases(data.career_plan.similar_cases);
  syncEvidenceViewWithActiveRole();
  renderAgentQuestions(data.career_plan?.agent_questions || [], data.student_profile?.agent_answers || {});
  renderSelfAssessmentForm(data.career_plan?.self_assessment || {});
  renderSelfAssessmentSummary(data.career_plan?.self_assessment || {});
  renderServiceLoop(data.career_plan?.service_loop || []);
  renderStakeholderViews(data.career_plan?.stakeholder_views || []);
  renderTechnicalModules(data.career_plan?.technical_modules || [], data.career_plan?.technical_keywords || []);
  renderInnovationHighlights(data.career_plan?.innovation_highlights || []);
  renderCareerGraph(data.student_profile || {}, data.career_plan || {}, data.matches || []);
  if (dom.currentReviewAnalysis) {
    dom.currentReviewAnalysis.textContent = state.currentAnalysisId
      ? `当前复核锁定：#${state.currentAnalysisId} · ${(data.student_profile?.name || "学生")} · ${(data.career_plan?.primary_role || "未生成")}`
      : "暂无锁定记录";
  }

  // 🌟 P5: 渲染 AI 评审意见
  const commentary = data.career_plan?.ai_match_commentary;
  if (commentary && commentary.trim() && dom.aiCommentaryCard && dom.aiCommentaryText) {
    dom.aiCommentaryText.textContent = compactText(commentary.trim(), 150);
    dom.aiCommentaryText.title = commentary.trim();
    dom.aiCommentaryCard.classList.remove("hidden");
  } else if (dom.aiCommentaryCard) {
    dom.aiCommentaryCard.classList.add("hidden");
  }

  // 🌟 P3: 重置编辑器状态
  if (dom.reportEditorArea) dom.reportEditorArea.style.display = "none";
  if (dom.reportPreview) dom.reportPreview.style.display = "";
  setElementHidden(dom.editReportBtn, false);
  setElementHidden(dom.saveReportBtn, true);
  setElementHidden(dom.downloadEditedBtn, true);

  // 切回总览并滚动到顶
  document.querySelector('.tab-btn[data-target="tab-overview"]')?.click();
  dom.resultsContent?.scrollIntoView({ behavior: "smooth", block: "start" });
}

// ==========================================
// 5. API 交互与调度
// ==========================================
function collectAgentAnswers() {
  const answers = {};
  dom.agentQuestionList?.querySelectorAll("[data-agent-id]").forEach((input) => {
    const key = input.dataset.agentId;
    const value = input.value?.trim();
    if (key && value) answers[key] = value;
  });
  return answers;
}

function collectSelfAssessmentAnswers() {
  const answers = {};
  dom.selfAssessmentForm?.querySelectorAll("[data-self-assessment-id]:checked").forEach((input) => {
    const key = input.dataset.selfAssessmentId;
    const value = Number(input.value);
    if (key) answers[key] = value;
  });
  return answers;
}

async function refreshHistory() {
  try {
    const response = await fetch("/api/history");
    const data = await response.json();
    renderHistory(data.items || []);
  } catch (error) {
    renderEmptyState(dom.historyList, "历史分析快照加载失败。");
  }
}

async function refreshSystemChecks() {
  try {
    const response = await fetch("/api/system-check");
    const data = await response.json();
    renderSystemChecks(data);
  } catch (error) {
    renderEmptyState(dom.systemCheckList, "系统健康检查加载失败。");
  }
}

async function refreshSchoolDashboard() {
  try {
    const response = await fetch("/api/school-dashboard?limit=80");
    const data = await response.json();
    state.schoolDashboard = data;
    renderSchoolDashboard(data);
  } catch (error) {
    renderEmptyState(dom.schoolDashboardStats, "学校运营看板加载失败。");
  }
}

async function refreshBenchmark(showLoading = false) {
  if (showLoading && dom.benchmarkStatus) {
    dom.benchmarkStatus.innerHTML = ">// Benchmark Engine 预热中...";
  }
  try {
    const mode = dom.parserModeSelect?.value || "auto";
    const response = await fetch(`/api/benchmark?parser_mode=${encodeURIComponent(mode)}`);
    const data = await response.json();
    state.benchmark = data;
    renderBenchmark(data);
  } catch (error) {
    if (dom.benchmarkStatus) {
      dom.benchmarkStatus.innerHTML = `> [ERR] Runner Panic：${escapeHtml(error.message)}`;
    }
  }
}

async function loadReviews(analysisId) {
  if (!analysisId) {
    state.analysisReviews = [];
    renderReviewRecords([]);
    return;
  }
  try {
    const response = await fetch(`/api/reviews?analysis_id=${encodeURIComponent(analysisId)}`);
    const data = await response.json();
    state.analysisReviews = data.items || [];
    renderReviewRecords(state.analysisReviews);
  } catch (error) {
    renderReviewRecords([]);
  }
}

async function loadAnalysis(analysisId) {
  if (!analysisId) return;
  setBusy(true);
  setStatus(`拉取历史快照 #${analysisId}...`, "loading");
  try {
    const response = await fetch(`/api/history/${encodeURIComponent(analysisId)}`);
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || "历史分析加载失败");
    if (dom.resumeInput) dom.resumeInput.value = data.resume_text || "";
    state.currentSampleName = data.sample_name || null;
    syncActiveSample();
    renderResults({
      analysis_id: data.id,
      student_profile: data.student_profile,
      matches: data.matches,
      career_plan: data.career_plan,
      report_markdown: data.report_markdown,
      reviews: data.reviews || [],
      parser: {
        requested_mode: data.parser_requested_mode || "unknown",
        used_mode: data.parser_used_mode || "unknown",
        fallback_used: false,
        message: `复原于 ${data.created_at}`,
      },
    });
    await loadReviews(data.id);
    setStatus(`快照 #${analysisId} 已恢复。`, "success");
  } catch (error) {
    setStatus(`历史提取失败：${error.message}`, "error");
  } finally {
    setBusy(false);
  }
}

async function searchJd() {
  const query = dom.jdSearchInput?.value.trim();
  if (!query) return setStatus("参数非法：检索词不能为空。", "error");
  setStatus(`启动岗位库检索：${query}...`, "loading");
  try {
    const response = await fetch(`/api/jd-search?q=${encodeURIComponent(query)}&limit=8`);
    const data = await response.json();
    renderJdSearchResults(data.items || []);
    setStatus("岗位库检索完成。", "success");
  } catch (error) {
    setStatus(`检索失败：${error.message}`, "error");
  }
}

async function loadTemplateEvidence(roleTitle) {
  if (!roleTitle) {
    state.currentTemplateRole = null;
    renderTemplateEvidence(null);
    return;
  }
  const requestToken = state.templateEvidenceRequestToken + 1;
  state.templateEvidenceRequestToken = requestToken;
  try {
    const response = await fetch(`/api/template-evidence?role_title=${encodeURIComponent(roleTitle)}`);
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || "模板证据加载失败");
    if (requestToken !== state.templateEvidenceRequestToken) return;
    state.currentTemplateRole = roleTitle;
    renderTemplateEvidence(data);
  } catch (error) {
    if (requestToken !== state.templateEvidenceRequestToken) return;
    state.currentTemplateRole = roleTitle;
    renderEmptyState(dom.templateEvidence, "基线样本加载失败。");
  }
}

async function initSamples() {
  try {
    const response = await fetch("/api/demo-resumes");
    const data = await response.json();
    state.samples = data.samples || [];
    renderSampleGallery(state.samples);
  } catch (error) {
    renderEmptyState(dom.sampleGallery, "样例列表加载失败。");
  }
}

async function loadSampleResume(sampleName = null) {
  setBusy(true); setStatus("正在载入样例画像...", "loading");
  try {
    const url = sampleName ? `/api/demo-resume?name=${encodeURIComponent(sampleName)}` : "/api/demo-resume";
    const response = await fetch(url);
    const data = await response.json();
    if (dom.resumeInput) dom.resumeInput.value = data.resume_text || "";
    state.currentSampleName = data.sample_name || sampleName;
    syncActiveSample();
    setStatus(`样例已载入：${state.currentSampleName || "default"}`, "success");
  } catch (error) { setStatus(`样例载入失败：${error.message}`, "error"); } finally { setBusy(false); }
}

async function analyzeResume() {
  const resumeText = dom.resumeInput?.value.trim();
  if (!resumeText) return setStatus("请先输入或上传简历内容。", "error");
  setBusy(true); setStatus("正在生成职业规划，请稍候...", "loading");

  try {
    const response = await fetch("/api/career-plan", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        resume_text: resumeText, top_k: 5, parser_mode: dom.parserModeSelect?.value || "auto",
        sample_name: state.currentSampleName, prior_analysis_id: state.currentAnalysisId,
        agent_answers: collectAgentAnswers(), self_assessment_answers: collectSelfAssessmentAnswers(),
      }),
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || "计算节点拒绝响应");
    renderResults(data);
    await loadReviews(data.analysis_id);
    await Promise.all([refreshHistory(), refreshSchoolDashboard()]);
    setStatus(data.parser ? `职业规划已生成 · 解析模式 ${String(data.parser.used_mode || "").toUpperCase()}` : "职业规划已生成", "success");
  } catch (error) { setStatus(`生成失败：${error.message}`, "error"); } finally { setBusy(false); }
}

// 🌟 修复 1：上传文件流完全接通
async function uploadResumeFile() {
  const file = dom.resumeFileInput?.files[0];
  if (!file) return setStatus("请选择本地文件", "error");
  const formData = new FormData(); formData.append("resume_file", file);
  setBusy(true); setStatus(`正在读取文件：${file.name}...`, "loading");
  try {
    const response = await fetch("/api/upload-resume-file", { method: "POST", body: formData });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || "反序列化受阻");
    if (dom.resumeInput) dom.resumeInput.value = data.resume_text || "";
    state.currentSampleName = null;
    syncActiveSample();
    setStatus(data.message || "文件已成功导入。", "success");
  } catch (error) { setStatus(`文件导入失败：${error.message}`, "error"); } finally { setBusy(false); }
}

async function submitReview() {
  if (!state.currentAnalysisId) return setStatus("请先生成或加载一条分析结果再提交复核。", "error");
  const reviewerName = dom.reviewerNameInput?.value.trim();
  if (!reviewerName) return setStatus("复核人不能为空。", "error");
  setBusy(true);
  setStatus("正在提交复核记录...", "loading");
  try {
    const response = await fetch("/api/reviews", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        analysis_id: state.currentAnalysisId,
        reviewer_name: reviewerName,
        reviewer_role: dom.reviewerRoleSelect?.value || "辅导员",
        decision: dom.reviewDecisionSelect?.value || "通过",
        notes: dom.reviewNotesInput?.value.trim() || "",
      }),
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || "复核提交失败");
    state.analysisReviews = data.items || [];
    renderReviewRecords(state.analysisReviews);
    if (dom.reviewNotesInput) dom.reviewNotesInput.value = "";
    await refreshSchoolDashboard();
    setStatus("复核记录已提交。", "success");
  } catch (error) {
    setStatus(`复核提交失败：${error.message}`, "error");
  } finally {
    setBusy(false);
  }
}

// ==========================================
// 6. 初始化与事件监听
// ==========================================
window.addEventListener("load", () => {
  initTabs();
  window.addEventListener('resize', () => { if (window.radarChartInstance) window.radarChartInstance.resize(); });
  Promise.allSettled([
    initSamples(),
    loadSampleResume("demo_resume_backend.txt"),
    refreshHistory(),
    refreshSystemChecks(),
    refreshSchoolDashboard(),
    refreshBenchmark(),
  ]).catch(() => {});
});

if (dom.analyzeBtn) dom.analyzeBtn.addEventListener("click", analyzeResume);
if (dom.jdSearchBtn) dom.jdSearchBtn.addEventListener("click", searchJd);
if (dom.runBenchmarkBtn) dom.runBenchmarkBtn.addEventListener("click", () => refreshBenchmark(true));
if (dom.submitReviewBtn) dom.submitReviewBtn.addEventListener("click", submitReview);

// 🌟 修复 2：按钮触发点击文件库，文件变化触发上传
if (dom.uploadFileBtn) dom.uploadFileBtn.addEventListener("click", () => dom.resumeFileInput?.click());
if (dom.resumeFileInput) {
  dom.resumeFileInput.addEventListener("change", () => {
    if (dom.resumeFileInput.files.length > 0) uploadResumeFile();
  });
}

if (dom.selfAssessmentForm) {
  dom.selfAssessmentForm.addEventListener("change", () => {
    refreshLiveSelfAssessmentSummary();
  });
}

// ==========================================
// 🌟 P3: 报告内联编辑功能
// ==========================================
if (dom.editReportBtn) {
  dom.editReportBtn.addEventListener("click", () => {
    if (!state.currentReport) return setStatus("还没有报告内容，请先生成分析结果", "error");
    if (dom.reportEditor) dom.reportEditor.value = getCurrentRenderableReport();
    if (dom.reportEditorArea) dom.reportEditorArea.style.display = "block";
    if (dom.reportPreview) dom.reportPreview.style.display = "none";
    setElementHidden(dom.editReportBtn, true);
    setElementHidden(dom.saveReportBtn, false);
    setElementHidden(dom.downloadEditedBtn, false);
    setStatus("已进入报告编辑模式。", "success");
  });
}

if (dom.saveReportBtn) {
  dom.saveReportBtn.addEventListener("click", () => {
    const editedContent = dom.reportEditor?.value || "";
    state.currentReport = editedContent;
    renderCurrentReportPreview(editedContent);
    if (dom.reportEditorArea) dom.reportEditorArea.style.display = "none";
    if (dom.reportPreview) dom.reportPreview.style.display = "";
    setElementHidden(dom.editReportBtn, false);
    setElementHidden(dom.saveReportBtn, true);
    setElementHidden(dom.downloadEditedBtn, false);
    setStatus("报告已更新。", "success");
  });
}

if (dom.downloadEditedBtn) {
  dom.downloadEditedBtn.addEventListener("click", () => {
    const content = dom.reportEditor?.value || state.currentReport;
    if (!content) return setStatus("没有可下载的报告内容", "error");
    const blob = new Blob([content], { type: "text/markdown;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url; link.download = "career_plan_edited.md";
    link.click(); URL.revokeObjectURL(url);
    setStatus("编辑版报告已下载。", "success");
  });
}

if (dom.printPdfBtn) dom.printPdfBtn.addEventListener("click", () => {
  printCurrentReport();
});
