// [Trace: Guyue/FrontendExpert] 注入 GSAP 三幕剧叙事

gsap.registerPlugin(ScrollTrigger);

document.addEventListener("DOMContentLoaded", () => {
    initHeroAnimation();
    setupAuditButton();
});

// 幕 1: 初始进场
function initHeroAnimation() {
    const tl = gsap.timeline({ defaults: { ease: 'power3.out' } });

    tl.from('.hero-badge', { duration: 0.8, y: -20, opacity: 0, delay: 0.2 })
      .from('.hero-title', { duration: 1, y: 30, opacity: 0 }, '-=0.4')
      .from('.hero-subtitle', { duration: 0.8, y: 20, opacity: 0 }, '-=0.6')
      .from('.hero-input-group', { duration: 0.8, y: 20, opacity: 0, scale: 0.95 }, '-=0.6');
}

// 按钮绑定与诊断交互流程
function setupAuditButton() {
    const btn = document.getElementById('startAuditBtn');
    const input = document.getElementById('targetUrl');
    const scanningProgress = document.getElementById('scanningProgress');
    const scanBar = document.getElementById('scanBar');
    const scanStatus = document.getElementById('scanStatus');
    const scanPercentage = document.getElementById('scanPercentage');
    const resultsSection = document.getElementById('resultsSection');
    
    // Fake logs for trace discipline
    const logs = [
        "[Trace: Guyue/DebuggingMindset] 发起 DNS 解析与 TLS 握手验证...",
        "[Trace: Guyue/RequirementAnalysis] 扫描首页关键表单节点与 reCAPTCHA 埋点...",
        "[WARNING] 未检测到有效的 reCAPTCHA token 发放逻辑",
        "[Trace: Guyue/ProductSense] 提取产品规格参数表，评估技术信任度...",
        "[WARNING] 发现内容重合度高，缺少独家资质证书背书",
        "[Trace: Guyue/SystemDesign] 评估首屏 LCP 渲染耗时...",
        "[ERROR] DOMContentLoaded > 3500ms, 预估跳出率增加 18%",
        "[Trace: Guyue/SystemDesign] 聚合分析完成，正在计算转化率损耗..."
    ];

    btn.addEventListener('click', () => {
        const url = input.value.trim();
        if(!url) return;

        // 按钮进入 Loading 态
        btn.disabled = true;
        document.getElementById('btnText').innerText = "扫描中...";
        gsap.to('.btn-arrow', { x: 50, opacity: 0, duration: 0.3 });
        
        // 显示进度条
        scanningProgress.classList.remove('hidden');
        gsap.fromTo(scanningProgress, { opacity: 0, y: -10 }, { opacity: 1, y: 0, duration: 0.3 });

        // 模拟诊断进度
        let progress = 0;
        let logIndex = 0;
        const logConsole = document.getElementById('logConsole');
        logConsole.innerHTML = '';

        const progressInterval = setInterval(() => {
            progress += Math.random() * 15;
            if(progress >= 100) {
                progress = 100;
                clearInterval(progressInterval);
                finishAudit();
            }
            
            scanBar.style.width = `${progress}%`;
            scanPercentage.innerText = `${Math.floor(progress)}%`;

            // 随机吐出日志
            if (Math.random() > 0.4 && logIndex < logs.length) {
                const p = document.createElement('div');
                const text = logs[logIndex++];
                p.innerText = `> ${text}`;
                
                // Colorize warnings/errors
                if (text.includes('[WARNING]')) p.className = 'text-yellow-400';
                else if (text.includes('[ERROR]')) p.className = 'text-red-400';
                
                logConsole.appendChild(p);
                logConsole.scrollTop = logConsole.scrollHeight;
            }

        }, 400);
    });

    function finishAudit() {
        scanStatus.innerText = "诊断完成，正在生成商业代价报告";
        document.getElementById('btnText').innerText = "查看报告";
        gsap.to('.btn-arrow', { x: 0, opacity: 1, duration: 0.3, clearProps: "all" });
        btn.disabled = false;

        // 隐藏进度条，展现结果区
        const tl = gsap.timeline({ defaults: { ease: 'power3.out' } });
        
        resultsSection.classList.remove('hidden');
        
        tl.to(scanningProgress, { duration: 0.4, opacity: 0, height: 0, onComplete: () => scanningProgress.classList.add('hidden') })
          .to(resultsSection, { duration: 0.8, opacity: 1, y: 0, ease: 'power2.out' }, '-=0.2')
          // 幕 2: 核心指标卡片交错入场 (Stagger)
          .from('.result-card', { 
              duration: 0.8, 
              y: 40, 
              opacity: 0, 
              stagger: 0.15 
          }, '-=0.4')
          // 幕 3: 日志控制台入场
          .from('.trace-logs', { duration: 0.6, y: 20, opacity: 0 }, '-=0.4');
          
        // 如果页面较长，可以滚动到结果区
        gsap.to(window, { duration: 1, scrollTo: "#resultsSection", ease: "power3.inOut" });
    }
}
