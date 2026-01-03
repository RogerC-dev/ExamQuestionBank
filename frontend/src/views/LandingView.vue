<template>
  <div class="landing-view">
    <!-- Hero Section -->
    <section class="hero-section">
      <div class="hero-content">
        <h1 class="hero-title">一站式法律學習平台</h1>
        <p class="hero-subtitle">題庫練習 + 案例閱讀 + AI 助手</p>
        <p class="hero-description">
          整合歷屆司法官／律師考題，提供智慧複習、學習追蹤與快閃卡管理
        </p>
        <div class="hero-cta">
          <button class="btn btn-primary" @click="handleStartFree">免費試用</button>
          <a 
            href="https://chrome.google.com/webstore" 
            target="_blank" 
            class="btn btn-secondary"
          >
            下載擴充功能
          </a>
        </div>
      </div>
    </section>

    <!-- Features Grid -->
    <section class="features-section">
      <div class="container">
        <h2 class="section-title">核心功能</h2>
        <div class="features-grid">
          <div class="feature-card">
            <div class="feature-icon blue">
              <i class="bi bi-journal-bookmark"></i>
            </div>
            <h3>歷屆試題庫</h3>
            <p>完整收錄各類國家考試歷屆試題，支援多種練習模式</p>
          </div>
          <div class="feature-card">
            <div class="feature-icon purple">
              <i class="bi bi-cpu"></i>
            </div>
            <h3>AI 智慧分析</h3>
            <p>運用 AI 分析作答錯誤，提供個人化學習建議</p>
          </div>
          <div class="feature-card">
            <div class="feature-icon green">
              <i class="bi bi-layers"></i>
            </div>
            <h3>智慧閃卡</h3>
            <p>結合間隔重複演算法，有效提升長期記憶效果</p>
          </div>
          <div class="feature-card">
            <div class="feature-icon orange">
              <i class="bi bi-bar-chart-line"></i>
            </div>
            <h3>學習分析</h3>
            <p>詳細的學習數據與進度追蹤，量化你的進步</p>
          </div>
          <div class="feature-card">
            <div class="feature-icon red">
              <i class="bi bi-bullseye"></i>
            </div>
            <h3>模擬考試</h3>
            <p>仿真考試環境，計時測驗讓你提前適應實戰</p>
          </div>
          <div class="feature-card">
            <div class="feature-icon cyan">
              <i class="bi bi-clock-history"></i>
            </div>
            <h3>錯題複習</h3>
            <p>自動收集錯題，針對弱點進行強化訓練</p>
          </div>
          <div class="feature-card">
            <div class="feature-icon pink">
              <i class="bi bi-stars"></i>
            </div>
            <h3>申論題分析</h3>
            <p>AI 批改申論題，提供評分與改進建議</p>
          </div>
          <div class="feature-card">
            <div class="feature-icon yellow">
              <i class="bi bi-lightning-charge"></i>
            </div>
            <h3>Chrome 擴充</h3>
            <p>一鍵收集網路上的題目，自動建立個人題庫</p>
          </div>
        </div>
      </div>
    </section>

    <!-- Extension Showcase -->
    <section class="extension-section">
      <div class="container">
        <div class="extension-content">
          <div class="extension-text">
            <h2 class="section-title">Precedent 擴充功能</h2>
            <p class="section-description">
              在瀏覽網頁時自動識別法律條文、釋字、判決書等法源資料，
              提供即時法律資訊查詢，讓閱讀案例新聞更輕鬆
            </p>
            <ul class="extension-features">
              <li>自動識別網頁中的法條引用</li>
              <li>即時彈窗預覽法律資訊</li>
              <li>書籤管理與同步</li>
              <li>與題庫平台無縫整合</li>
            </ul>
            <a 
              href="https://chrome.google.com/webstore" 
              target="_blank" 
              class="btn btn-primary btn-large"
            >
              立即下載擴充功能
            </a>
          </div>
          <div class="extension-demo">
            <div class="demo-placeholder">
              <p>擴充功能示範</p>
              <p class="demo-note"><img src="../assets/demo.png" alt="ext-demo" width="600px"></p>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Integration Benefits -->
    <section class="integration-section">
      <div class="container">
        <h2 class="section-title">整合優勢</h2>
        <div class="benefits-grid">
          <div class="benefit-card">
            <div class="benefit-icon">標</div>
            <h3>自動標記相關考題</h3>
            <p>在網頁閱讀案例時，系統自動標記相關考題，方便後續練習</p>
          </div>
          <div class="benefit-card">
            <div class="benefit-icon">同步</div>
            <h3>書籤同步</h3>
            <p>擴充功能的書籤與網頁平台同步，隨時隨地複習</p>
          </div>
          <div class="benefit-card">
            <div class="benefit-icon">AI</div>
            <h3>AI 推薦練習</h3>
            <p>AI 分析案例內容，自動推薦相關練習題目</p>
          </div>
          <div class="benefit-card">
            <div class="benefit-icon">進</div>
            <h3>學習進度追蹤</h3>
            <p>跨平台學習數據整合，完整追蹤學習進度</p>
          </div>
        </div>
      </div>
    </section>

    <!-- Pricing Preview -->
    <section class="pricing-section">
      <div class="container">
        <h2 class="section-title">方案選擇</h2>
        <div class="pricing-grid">
          <div class="pricing-card">
            <h3>免費版</h3>
            <div class="price">NT$ 0</div>
            <ul class="pricing-features">
              <li>基礎題庫存取</li>
              <li>AI 聊天（每日 10 次）</li>
              <li>基礎快閃卡</li>
              <li>擴充功能基礎功能</li>
            </ul>
            <i style="flex: 1"></i>
            <button class="btn btn-outline" @click="handleStartFree">開始使用</button>
          </div>
          <div class="pricing-card featured">
            <div class="badge">推薦</div>
            <h3>進階版</h3>
            <div class="price">NT$ 500<span>/月</span></div>
            <ul class="pricing-features">
              <li>無限題庫存取</li>
              <li>無限 AI 聊天</li>
              <li>AI 申論批改</li>
              <li>進階分析報表</li>
              <li>優先客服支援</li>
              <li>擴充功能進階功能</li>
            </ul>
            <button class="btn btn-primary" @click="handleSubscribe">立即升級</button>
          </div>
        </div>
      </div>
    </section>

    <!-- Stats Section -->
    <section class="stats-section">
      <div class="container">
        <div class="stats-grid">
          <div class="stat-item">
            <div class="stat-number">3,000+</div>
            <div class="stat-label">歷屆考題</div>
          </div>
          <div class="stat-item">
            <div class="stat-number">10,000+</div>
            <div class="stat-label">活躍使用者</div>
          </div>
          <div class="stat-item">
            <div class="stat-number">95%</div>
            <div class="stat-label">使用者滿意度</div>
          </div>
          <div class="stat-item">
            <div class="stat-number">24/7</div>
            <div class="stat-label">AI 助手服務</div>
          </div>
        </div>
      </div>
    </section>

    <!-- Footer Section -->
    <footer class="site-footer">
      <div class="container">
        <div class="footer-grid">
          <!-- Brand Column -->
          <div class="footer-brand">
            <div class="footer-logo">
              <span class="logo-icon">📚</span>
              <span class="logo-text">ExamBank</span>
            </div>
            <p class="footer-description">
              專為台灣國家考試設計的智慧學習平台，幫助考生更有效率地準備考試。
            </p>
          </div>

          <!-- Product Links -->
          <div class="footer-column">
            <h4 class="footer-heading">產品</h4>
            <ul class="footer-links">
              <li><a href="#features">功能介紹</a></li>
              <li><a href="#pricing">方案價格</a></li>
              <li><a href="https://chrome.google.com/webstore" target="_blank">Chrome 擴充</a></li>
              <li><a href="#">更新日誌</a></li>
            </ul>
          </div>

          <!-- Support Links -->
          <div class="footer-column">
            <h4 class="footer-heading">支援</h4>
            <ul class="footer-links">
              <li><a href="#">使用教學</a></li>
              <li><a href="#">常見問題</a></li>
              <li><a href="#">聯繫我們</a></li>
              <li><a href="#">意見回饋</a></li>
            </ul>
          </div>

          <!-- Legal Links -->
          <div class="footer-column">
            <h4 class="footer-heading">法律</h4>
            <ul class="footer-links">
              <li><a href="#">服務條款</a></li>
              <li><a href="#">隱私政策</a></li>
              <li><a href="#">Cookie 政策</a></li>
            </ul>
          </div>
        </div>

        <!-- Footer Bottom -->
        <div class="footer-bottom">
          <p class="copyright">© 2024 ExamBank. All rights reserved.</p>
          <div class="social-links">
            <a href="#" class="social-link" aria-label="Facebook">Facebook</a>
            <a href="#" class="social-link" aria-label="Instagram">Instagram</a>
            <a href="#" class="social-link" aria-label="Discord">Discord</a>
          </div>
        </div>
      </div>
    </footer>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import authService from '@/services/authService'

const router = useRouter()

const handleStartFree = () => {
  if (authService.isAuthenticated()) {
    router.push('/practice')
  } else {
    window.dispatchEvent(new Event('show-login'))
  }
}

const handleSubscribe = () => {
  router.push('/subscription')
}
</script>

<style scoped>
.landing-view {
  width: 100%;
  background: var(--bg-page);
  color: var(--text-primary);
}

/* Hero Section */
.hero-section {
  background: var(--bg-page);
  color: var(--text-primary);
  padding: 120px 24px 80px;
  text-align: center;
}

.hero-content {
  max-width: 840px;
  margin: 0 auto;
}

.hero-title {
  font-size: 42px;
  font-weight: 700;
  margin-bottom: 16px;
  line-height: 1.2;
  letter-spacing: -0.02em;
  color: var(--text-primary);
}

.hero-subtitle {
  font-size: 22px;
  margin-bottom: 10px;
  color: var(--text-secondary);
}

.hero-description {
  font-size: 17px;
  margin-bottom: 36px;
  color: var(--text-secondary);
  line-height: 1.7;
}

.hero-cta {
  display: flex;
  gap: 14px;
  justify-content: center;
  flex-wrap: wrap;
}

.btn {
  padding: 12px 26px;
  border: 1px solid transparent;
  border-radius: 12px;
  font-size: 15px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s ease;
  text-decoration: none;
  display: inline-block;
}

.btn-primary {
  background: var(--primary);
  color: #fff;
  border: 1px solid transparent;
  box-shadow: 0 2px 5px rgba(0,0,0,0.05);
}

.btn-primary:hover {
  background: var(--primary-hover);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}

.btn-secondary {
  background: var(--surface);
  color: var(--text-primary);
  border: 1px solid var(--border);
}

.btn-secondary:hover {
  background: var(--primary-soft);
  border-color: var(--primary);
  color: var(--primary);
}

.btn-large {
  padding: 14px 32px;
  font-size: 16px;
}

.btn-outline {
  background: transparent;
  color: var(--primary);
  border: 1px solid var(--primary);
}

.btn-outline:hover {
  background: var(--primary);
  color: #f7f9fc;
}

/* Container */
.container {
  max-width: 1180px;
  margin: 0 auto;
  padding: 0 20px;
}

/* Section shared */
.section-title {
  font-size: 30px;
  font-weight: 800;
  text-align: center;
  margin-bottom: 36px;
  color: var(--text-primary);
  letter-spacing: 0.01em;
}

/* Features Section */
.features-section {
  padding: 70px 0;
  background: var(--surface);
  border-top: 1px solid var(--border);
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
}

.feature-card {
  text-align: left;
  padding: 28px 22px;
  border-radius: var(--radius);
  background: var(--surface);
  border: 1px solid var(--border);
  transition: all 0.3s ease;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.02);
}

.feature-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 30px rgba(0, 0, 0, 0.08);
  border-color: rgba(71, 105, 150, 0.2);
}

.feature-card:hover .feature-icon {
  transform: scale(1.1);
}

.feature-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: grid;
  place-items: center;
  margin-bottom: 14px;
  font-size: 20px;
  transition: transform 0.3s ease;
}

/* Colored icon backgrounds */
.feature-icon.blue {
  background: #eff6ff;
  color: #3b82f6;
}

.feature-icon.purple {
  background: #f5f3ff;
  color: #8b5cf6;
}

.feature-icon.green {
  background: #ecfdf5;
  color: #10b981;
}

.feature-icon.orange {
  background: #fff7ed;
  color: #f97316;
}

.feature-icon.red {
  background: #fef2f2;
  color: #ef4444;
}

.feature-icon.cyan {
  background: #ecfeff;
  color: #06b6d4;
}

.feature-icon.pink {
  background: #fdf2f8;
  color: #ec4899;
}

.feature-icon.yellow {
  background: #fefce8;
  color: #eab308;
}

.feature-card h3 {
  font-size: 17px;
  font-weight: 700;
  margin-bottom: 8px;
  color: var(--text-primary);
}

.feature-card p {
  color: var(--text-secondary);
  line-height: 1.6;
  font-size: 14px;
}

/* Extension Section */
.extension-section {
  padding: 70px 0;
  background: #f8fafc;
}

.extension-content {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 38px;
  align-items: center;
}

.extension-text {
  max-width: 600px;
}

.section-description {
  font-size: 16px;
  color: var(--text-secondary);
  line-height: 1.8;
  margin-bottom: 20px;
}

.extension-features {
  list-style: none;
  padding: 0;
  margin: 22px 0 28px;
}

.extension-features li {
  padding: 8px 0 8px 0;
  font-size: 15px;
  color: var(--text-primary);
  position: relative;
}

.extension-features li::before {
  content: '';
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--primary);
  display: inline-block;
  margin-right: 10px;
  position: relative;
  top: -1px;
}

.extension-demo {
  background: var(--surface);
  border-radius: var(--radius);
  padding: 32px;
  box-shadow: var(--shadow);
  min-height: 280px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1px solid var(--border);
}

.demo-placeholder {
  text-align: center;
  color: var(--text-secondary);
}

.demo-note {
  font-size: 13px;
  margin-top: 6px;
  color: var(--text-secondary);
}

/* Integration Section */
.integration-section {
  padding: 70px 0;
  background: var(--surface);
}

.benefits-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 22px;
}

.benefit-card {
  text-align: left;
  padding: 24px 22px;
  border-radius: var(--radius);
  background: var(--surface);
  border: 1px solid var(--border);
  transition: all 0.2s ease;
  box-shadow: none;
}

.benefit-card:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow);
  border-color: var(--primary);
}

.benefit-icon {
  width: 42px;
  height: 42px;
  border-radius: 50%;
  background: var(--primary-soft);
  color: var(--primary);
  font-weight: 800;
  display: grid;
  place-items: center;
  margin-bottom: 10px;
  font-size: 14px;
  letter-spacing: 0.05em;
}

.benefit-card h3 {
  font-size: 18px;
  font-weight: 700;
  margin-bottom: 8px;
  color: var(--text-primary);
}

.benefit-card p {
  color: var(--text-secondary);
  line-height: 1.6;
}

/* Pricing Section */
.pricing-section {
  padding: 70px 0;
  background: var(--surface-muted);
}

.pricing-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 20px;
  max-width: 820px;
  margin: 0 auto;
}

.pricing-card {
  display: flex;
  flex-direction: column;
  background: var(--surface);
  border-radius: var(--radius);
  padding: 32px 26px;
  text-align: center;
  border: 1px solid var(--border);
  transition: all 0.2s ease;
  position: relative;
  box-shadow: 0 12px 30px rgba(15, 23, 42, 0.06);
}

.pricing-card.featured {
  display: flex;
  flex-direction: column;
  border-color: var(--primary);
  box-shadow: var(--shadow-hover);
  transform: translateY(-4px);
  background: #fff;
}

.badge {
  position: absolute;
  top: -12px;
  left: 50%;
  transform: translateX(-50%);
  background: var(--primary);
  color: #f7f9fc;
  padding: 6px 14px;
  border-radius: 16px;
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.02em;
}

.pricing-card h3 {
  font-size: 20px;
  font-weight: 700;
  margin-bottom: 12px;
  color: var(--text-primary);
}

.price {
  font-size: 40px;
  font-weight: 800;
  color: var(--primary);
  margin-bottom: 24px;
}

.price span {
  font-size: 16px;
  color: var(--text-secondary);
}

.pricing-features {
  list-style: none;
  padding: 0;
  margin: 0 0 24px;
  text-align: left;
}

.pricing-features li {
  padding: 10px 0;
  font-size: 15px;
  color: var(--text-primary);
  border-bottom: 1px solid #f0f2f4;
  position: relative;
}

.pricing-features li::before {
  content: '';
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--primary);
  display: inline-block;
  margin-right: 10px;
  position: relative;
  top: -1px;
}

.pricing-features li:last-child {
  border-bottom: none;
}

/* Stats Section */
.stats-section {
  padding: 54px 0;
  background: var(--bg-page);
  color: var(--text-primary);
  border-top: 1px solid var(--border);
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 20px;
  text-align: center;
}

.stat-item {
  padding: 20px;
  background: transparent;
  border: none;
}

.stat-number {
  font-size: 34px;
  font-weight: 800;
  margin-bottom: 6px;
  color: var(--primary);
}

.stat-label {
  font-size: 14px;
  color: var(--text-secondary);
}

/* Responsive */
@media (max-width: 900px) {
  .hero-title {
    font-size: 34px;
  }

  .hero-subtitle {
    font-size: 19px;
  }

  .extension-content {
    grid-template-columns: 1fr;
  }

  .pricing-card.featured {
    transform: translateY(0);
  }

  .features-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 640px) {
  .hero-section {
    padding: 80px 16px 70px;
  }

  .hero-title {
    font-size: 28px;
  }

  .hero-description {
    font-size: 15px;
  }

  .features-grid,
  .benefits-grid {
    grid-template-columns: 1fr;
  }
}

/* Dark Mode Overrides */
:global(.dark) .features-section,
:global(.dark) .integration-section,
:global(.dark) .extension-section {
    background: var(--surface) !important;
    border-color: var(--border) !important;
}

:global(.dark) .feature-card,
:global(.dark) .benefit-card {
    background: var(--surface) !important;
    border-color: var(--border) !important;
}

:global(.dark) .feature-card:hover,
:global(.dark) .benefit-card:hover {
    background: var(--surface-muted) !important;
    border-color: var(--primary) !important;
}

:global(.dark) .extension-demo {
    background: var(--surface-muted) !important;
    border-color: var(--border) !important;
}

:global(.dark) .pricing-section {
    background: var(--bg-page) !important;
}

:global(.dark) .pricing-card {
    background: var(--surface) !important;
    border-color: var(--border) !important;
}

:global(.dark) .pricing-card.featured {
    background: var(--surface) !important;
    border-color: var(--primary) !important;
}

:global(.dark) .pricing-features li {
    border-color: var(--border) !important;
    color: var(--text-primary) !important;
}

:global(.dark) .stats-section {
    background: var(--surface) !important;
    border-color: var(--border) !important;
}

/* Footer Section */
.site-footer {
  padding: 60px 0 0;
  background: var(--bg-page);
  border-top: 1px solid var(--border);
}

.footer-grid {
  display: grid;
  grid-template-columns: 1.5fr 1fr 1fr 1fr;
  gap: 40px;
  margin-bottom: 40px;
}

.footer-brand {
  max-width: 280px;
}

.footer-logo {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 16px;
}

.logo-icon {
  font-size: 24px;
}

.logo-text {
  font-size: 20px;
  font-weight: 700;
  color: var(--text-primary);
}

.footer-description {
  font-size: 14px;
  color: var(--text-secondary);
  line-height: 1.7;
  margin: 0;
}

.footer-column {
  min-width: 120px;
}

.footer-heading {
  font-size: 15px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 16px;
}

.footer-links {
  list-style: none;
  padding: 0;
  margin: 0;
}

.footer-links li {
  margin-bottom: 10px;
}

.footer-links a {
  font-size: 14px;
  color: var(--text-secondary);
  text-decoration: none;
  transition: color 0.2s;
}

.footer-links a:hover {
  color: var(--primary);
}

.footer-bottom {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 24px 0;
  border-top: 1px solid var(--border);
}

.copyright {
  font-size: 13px;
  color: var(--text-secondary);
  margin: 0;
}

.social-links {
  display: flex;
  gap: 24px;
}

.social-link {
  font-size: 13px;
  color: var(--text-secondary);
  text-decoration: none;
  transition: color 0.2s;
}

.social-link:hover {
  color: var(--primary);
}

/* Footer responsive */
@media (max-width: 900px) {
  .footer-grid {
    grid-template-columns: 1fr 1fr;
    gap: 32px;
  }

  .footer-brand {
    max-width: 100%;
    grid-column: 1 / -1;
  }
}

@media (max-width: 640px) {
  .footer-grid {
    grid-template-columns: 1fr;
    gap: 28px;
  }

  .footer-bottom {
    flex-direction: column;
    gap: 16px;
    text-align: center;
  }
}

/* Dark mode footer */
:global(.dark) .site-footer {
    background: var(--surface) !important;
    border-color: var(--border) !important;
}

:global(.dark) .footer-bottom {
    border-color: var(--border) !important;
}
</style>

