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
            <div class="feature-icon">題</div>
            <h3>歷屆考題題庫</h3>
            <p>整合完整歷屆司法官、律師考試題目，提供多種練習模式與詳細解析</p>
          </div>
          <div class="feature-card">
            <div class="feature-icon">案</div>
            <h3>智能案例閱讀</h3>
            <p>Chrome 擴充功能自動識別網頁中的法條與判決，提供即時法律資訊</p>
          </div>
          <div class="feature-card">
            <div class="feature-icon">AI</div>
            <h3>AI 法律助手</h3>
            <p>AI 問答系統協助解答法律問題，分析案例並推薦相關練習題目</p>
          </div>
          <div class="feature-card">
            <div class="feature-icon">追</div>
            <h3>學習追蹤分析</h3>
            <p>完整的學習統計與進度追蹤，幫助您掌握學習狀況</p>
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
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 22px;
}

.feature-card {
  text-align: left;
  padding: 32px 24px;
  border-radius: var(--radius);
  background: var(--surface);
  border: 1px solid transparent;
  transition: all 0.3s ease;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.02);
}

.feature-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 20px rgba(0, 0, 0, 0.04);
  background: #fff;
}

.feature-icon {
  width: 44px;
  height: 44px;
  border-radius: 12px;
  background: var(--primary-soft);
  color: var(--primary);
  font-weight: 800;
  display: grid;
  place-items: center;
  margin-bottom: 12px;
  font-size: 15px;
  letter-spacing: 0.05em;
}

.feature-card h3 {
  font-size: 18px;
  font-weight: 700;
  margin-bottom: 10px;
  color: var(--text-primary);
}

.feature-card p {
  color: var(--text-secondary);
  line-height: 1.6;
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
</style>

