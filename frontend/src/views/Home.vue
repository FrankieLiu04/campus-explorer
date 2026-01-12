<template>
  <div class="home">
    <section class="hero">
      <h1 class="hero-title">Campus Explorer</h1>
      <p class="hero-subtitle">Interactive Map & Social Platform for CUHK</p>
      <p class="hero-description">
        Discover campus locations, connect with fellow students, and navigate your way around.
      </p>
    </section>

    <section class="features">
      <div class="feature-grid">
        <article class="feature-card" @click="$router.push('/map')">
          <div class="feature-icon">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/>
              <circle cx="12" cy="10" r="3"/>
            </svg>
          </div>
          <h3 class="feature-title">Campus Map</h3>
          <p class="feature-desc">Discover and mark locations across campus — libraries, cafes, study spots.</p>
          <span class="feature-action">Explore →</span>
        </article>

        <article class="feature-card" @click="$router.push('/chat')">
          <div class="feature-icon">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
            </svg>
          </div>
          <h3 class="feature-title">Student Chat</h3>
          <p class="feature-desc">Connect with other students in real-time. Share tips and discuss campus life.</p>
          <span class="feature-action">Join →</span>
        </article>

        <article class="feature-card" @click="handleProfileClick">
          <div class="feature-icon">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
              <circle cx="12" cy="7" r="4"/>
            </svg>
          </div>
          <h3 class="feature-title">Your Profile</h3>
          <p class="feature-desc">Personalize your experience and manage your account settings.</p>
          <span class="feature-action">{{ authStore.isAuthenticated ? 'View →' : 'Login →' }}</span>
        </article>
      </div>
    </section>
  </div>
</template>

<script setup>
import { useAuthStore } from '../stores/auth'
import { useRouter } from 'vue-router'

const authStore = useAuthStore()
const router = useRouter()

const handleProfileClick = () => {
  if (authStore.isAuthenticated) {
    router.push('/profile')
  } else {
    router.push('/login')
  }
}
</script>

<style scoped>
.home {
  max-width: 960px;
  margin: 0 auto;
  padding: var(--spacing-xl) var(--spacing-lg);
}

.hero {
  text-align: center;
  padding: var(--spacing-2xl) 0;
}

.hero-title {
  font-size: 36px;
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
  margin: 0 0 var(--spacing-sm);
  letter-spacing: -0.03em;
}

.hero-subtitle {
  font-size: var(--font-size-lg);
  color: var(--color-text-secondary);
  margin: 0 0 var(--spacing-md);
  font-weight: var(--font-weight-normal);
}

.hero-description {
  font-size: var(--font-size-base);
  color: var(--color-text-muted);
  max-width: 480px;
  margin: 0 auto;
}

.features {
  margin-top: var(--spacing-xl);
}

.feature-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: var(--spacing-lg);
}

.feature-card {
  background: var(--color-bg-elevated);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: var(--spacing-xl) var(--spacing-lg);
  cursor: pointer;
  transition: all var(--transition-normal);
}

.feature-card:hover {
  border-color: var(--color-border-focus);
  box-shadow: var(--shadow-md);
  transform: translateY(-2px);
}

.feature-card:active {
  transform: translateY(0);
}

.feature-icon {
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--color-bg-subtle);
  border-radius: var(--radius-md);
  color: var(--color-primary);
  margin-bottom: var(--spacing-md);
}

.feature-title {
  font-size: var(--font-size-md);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
  margin: 0 0 var(--spacing-sm);
}

.feature-desc {
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
  margin: 0 0 var(--spacing-md);
  line-height: 1.5;
}

.feature-action {
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  color: var(--color-primary);
  transition: color var(--transition-fast);
}

.feature-card:hover .feature-action {
  color: var(--color-primary-dark);
}

@media (max-width: 768px) {
  .feature-grid {
    grid-template-columns: 1fr;
  }
  
  .hero-title {
    font-size: 28px;
  }
}
</style>