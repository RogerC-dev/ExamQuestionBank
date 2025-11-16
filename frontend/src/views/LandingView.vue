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
            <div class="feature-icon">📚</div>
            <h3>歷屆考題題庫</h3>
            <p>整合完整歷屆司法官、律師考試題目，提供多種練習模式與詳細解析</p>
          </div>
          <div class="feature-card">
            <div class="feature-icon">🔖</div>
            <h3>智能案例閱讀</h3>
            <p>Chrome 擴充功能自動識別網頁中的法條與判決，提供即時法律資訊</p>
          </div>
          <div class="feature-card">
            <div class="feature-icon">🤖</div>
            <h3>AI 法律助手</h3>
            <p>AI 問答系統協助解答法律問題，分析案例並推薦相關練習題目</p>
          </div>
          <div class="feature-card">
            <div class="feature-icon">📊</div>
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
              <li>✅ 自動識別網頁中的法條引用</li>
              <li>✅ 即時彈窗預覽法律資訊</li>
              <li>✅ 書籤管理與同步</li>
              <li>✅ 與題庫平台無縫整合</li>
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
              <p class="demo-note">（可放置 GIF 或截圖）</p>
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
            <div class="benefit-icon">🔄</div>
            <h3>自動標記相關考題</h3>
            <p>在網頁閱讀案例時，系統自動標記相關考題，方便後續練習</p>
          </div>
          <div class="benefit-card">
            <div class="benefit-icon">📱</div>
            <h3>書籤同步</h3>
            <p>擴充功能的書籤與網頁平台同步，隨時隨地複習</p>
          </div>
          <div class="benefit-card">
            <div class="benefit-icon">🎯</div>
            <h3>AI 推薦練習</h3>
            <p>AI 分析案例內容，自動推薦相關練習題目</p>
          </div>
          <div class="benefit-card">
            <div class="benefit-icon">📈</div>
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
              <li>✅ 基礎題庫存取</li>
              <li>✅ AI 聊天（每日 10 次）</li>
              <li>✅ 基礎快閃卡</li>
              <li>✅ 擴充功能基礎功能</li>
            </ul>
            <button class="btn btn-outline" @click="handleStartFree">開始使用</button>
          </div>
          <div class="pricing-card featured">
            <div class="badge">推薦</div>
            <h3>進階版</h3>
            <div class="price">NT$ 500<span>/月</span></div>
            <ul class="pricing-features">
              <li>✅ 無限題庫存取</li>
              <li>✅ 無限 AI 聊天</li>
              <li>✅ AI 申論批改</li>
              <li>✅ 進階分析報表</li>
              <li>✅ 優先客服支援</li>
              <li>✅ 擴充功能進階功能</li>
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
  background: linear-gradient(180deg, #f8f9fa 0%, #ffffff 100%);
}

/* Hero Section */
.hero-section {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 120px 24px;
  text-align: center;
}

.hero-content {
  max-width: 800px;
  margin: 0 auto;
}

.hero-title {
  font-size: 48px;
  font-weight: bold;
  margin-bottom: 16px;
  line-height: 1.2;
}

.hero-subtitle {
  font-size: 24px;
  margin-bottom: 12px;
  opacity: 0.95;
}

.hero-description {
  font-size: 18px;
  margin-bottom: 40px;
  opacity: 0.9;
  line-height: 1.6;
}

.hero-cta {
  display: flex;
  gap: 16px;
  justify-content: center;
  flex-wrap: wrap;
}

.btn {
  padding: 14px 32px;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
  text-decoration: none;
  display: inline-block;
}

.btn-primary {
  background: white;
  color: #667eea;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.2);
}

.btn-secondary {
  background: transparent;
  color: white;
  border: 2px solid white;
}

.btn-secondary:hover {
  background: rgba(255, 255, 255, 0.1);
}

.btn-large {
  padding: 16px 40px;
  font-size: 18px;
}

.btn-outline {
  background: transparent;
  color: #667eea;
  border: 2px solid #667eea;
}

.btn-outline:hover {
  background: #667eea;
  color: white;
}

/* Container */
.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 24px;
}

/* Features Section */
.features-section {
  padding: 80px 0;
  background: white;
}

.section-title {
  font-size: 36px;
  font-weight: bold;
  text-align: center;
  margin-bottom: 48px;
  color: #2c3e50;
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 32px;
}

.feature-card {
  text-align: center;
  padding: 32px 24px;
  border-radius: 12px;
  background: #f8f9fa;
  transition: all 0.3s;
}

.feature-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
}

.feature-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

.feature-card h3 {
  font-size: 20px;
  font-weight: 600;
  margin-bottom: 12px;
  color: #2c3e50;
}

.feature-card p {
  color: #666;
  line-height: 1.6;
}

/* Extension Section */
.extension-section {
  padding: 80px 0;
  background: #f8f9fa;
}

.extension-content {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 48px;
  align-items: center;
}

.extension-text {
  max-width: 600px;
}

.section-description {
  font-size: 16px;
  color: #666;
  line-height: 1.8;
  margin-bottom: 24px;
}

.extension-features {
  list-style: none;
  padding: 0;
  margin: 24px 0 32px;
}

.extension-features li {
  padding: 8px 0;
  font-size: 16px;
  color: #333;
}

.extension-demo {
  background: white;
  border-radius: 12px;
  padding: 40px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  min-height: 300px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.demo-placeholder {
  text-align: center;
  color: #999;
}

.demo-note {
  font-size: 14px;
  margin-top: 8px;
}

/* Integration Section */
.integration-section {
  padding: 80px 0;
  background: white;
}

.benefits-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 32px;
}

.benefit-card {
  text-align: center;
  padding: 32px 24px;
  border-radius: 12px;
  background: linear-gradient(135deg, #f8f9fa 0%, #ffffff 100%);
  border: 1px solid #e0e0e0;
  transition: all 0.3s;
}

.benefit-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
  border-color: #667eea;
}

.benefit-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

.benefit-card h3 {
  font-size: 20px;
  font-weight: 600;
  margin-bottom: 12px;
  color: #2c3e50;
}

.benefit-card p {
  color: #666;
  line-height: 1.6;
}

/* Pricing Section */
.pricing-section {
  padding: 80px 0;
  background: #f8f9fa;
}

.pricing-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 32px;
  max-width: 800px;
  margin: 0 auto;
}

.pricing-card {
  background: white;
  border-radius: 12px;
  padding: 40px 32px;
  text-align: center;
  border: 2px solid #e0e0e0;
  transition: all 0.3s;
  position: relative;
}

.pricing-card.featured {
  border-color: #667eea;
  box-shadow: 0 8px 24px rgba(102, 126, 234, 0.2);
  transform: scale(1.05);
}

.badge {
  position: absolute;
  top: -12px;
  left: 50%;
  transform: translateX(-50%);
  background: #667eea;
  color: white;
  padding: 6px 16px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
}

.pricing-card h3 {
  font-size: 24px;
  font-weight: 600;
  margin-bottom: 16px;
  color: #2c3e50;
}

.price {
  font-size: 48px;
  font-weight: bold;
  color: #667eea;
  margin-bottom: 32px;
}

.price span {
  font-size: 20px;
  color: #666;
}

.pricing-features {
  list-style: none;
  padding: 0;
  margin: 0 0 32px;
  text-align: left;
}

.pricing-features li {
  padding: 12px 0;
  font-size: 16px;
  color: #333;
  border-bottom: 1px solid #f0f0f0;
}

.pricing-features li:last-child {
  border-bottom: none;
}

/* Stats Section */
.stats-section {
  padding: 60px 0;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 32px;
  text-align: center;
}

.stat-item {
  padding: 24px;
}

.stat-number {
  font-size: 48px;
  font-weight: bold;
  margin-bottom: 8px;
}

.stat-label {
  font-size: 18px;
  opacity: 0.9;
}

/* Responsive */
@media (max-width: 768px) {
  .hero-title {
    font-size: 32px;
  }

  .hero-subtitle {
    font-size: 20px;
  }

  .extension-content {
    grid-template-columns: 1fr;
  }

  .pricing-card.featured {
    transform: scale(1);
  }

  .features-grid,
  .benefits-grid {
    grid-template-columns: 1fr;
  }
}
</style>

