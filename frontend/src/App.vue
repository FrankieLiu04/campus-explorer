<template>
  <div id="app">
    <el-container>
      <el-header>
        <nav class="nav-bar">
          <div class="nav-brand">
            <span class="brand-text">Campus Explorer</span>
          </div>
          <div class="nav-links">
            <router-link to="/" class="nav-link" :class="{ active: $route.path === '/' }">Home</router-link>
            <router-link to="/map" class="nav-link" :class="{ active: $route.path === '/map' }">Map</router-link>
            <router-link to="/chat" class="nav-link" :class="{ active: $route.path === '/chat' }">Chat</router-link>
          </div>
          <div class="nav-actions">
            <template v-if="authStore.isAuthenticated">
              <div class="user-pill">
                <el-avatar :src="fullAvatarUrl" :size="32" class="user-avatar"></el-avatar>
                <span class="user-name">{{ authStore.user?.username }}</span>
              </div>
              <button @click="$router.push('/profile')" class="btn-ghost">
                Profile
              </button>
              <button @click="logout" class="btn-ghost btn-danger">
                Logout
              </button>
            </template>
            <template v-else>
              <button @click="$router.push('/login')" class="btn-ghost">Login</button>
              <button @click="$router.push('/register')" class="btn-primary">Register</button>
            </template>
          </div>
        </nav>
      </el-header>
      <el-main>
        <router-view />
      </el-main>
    </el-container>
  </div>
</template>

<script setup>
import { useAuthStore } from './stores/auth'
import { useRouter } from 'vue-router'
import { computed } from 'vue'

const authStore = useAuthStore()
const router = useRouter()

const fullAvatarUrl = computed(() => {
  const avatarUrl = authStore.user?.avatar_url;
  if (!avatarUrl) {
    return 'https://cube.elemecdn.com/3/7c/3ea6beec64369c2642b92c6726f1epng.png';
  }
  if (avatarUrl.startsWith('http')) {
    return avatarUrl;
  }
  return `http://localhost:5000${avatarUrl}`;
});


const logout = () => {
  authStore.logout()
  router.push('/login')
}
</script>

<style>
* {
  box-sizing: border-box;
}

#app {
  font-family: var(--font-family);
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: var(--color-text-primary);
  line-height: var(--line-height);
}

.el-header {
  padding: 0;
  height: auto !important;
  background: var(--color-bg-elevated);
  border-bottom: 1px solid var(--color-border);
}

.el-main {
  min-height: calc(100vh - 120px);
  background: var(--color-bg-base);
  padding: var(--spacing-lg);
}

/* Navigation Bar */
.nav-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 var(--spacing-xl);
  height: 56px;
}

.nav-brand {
  display: flex;
  align-items: center;
}

.brand-text {
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
  letter-spacing: -0.02em;
}

.nav-links {
  display: flex;
  gap: var(--spacing-xs);
}

.nav-link {
  padding: var(--spacing-sm) var(--spacing-md);
  color: var(--color-text-secondary);
  text-decoration: none;
  font-size: var(--font-size-base);
  font-weight: var(--font-weight-medium);
  border-radius: var(--radius-md);
  transition: all var(--transition-fast);
}

.nav-link:hover {
  color: var(--color-text-primary);
  background: var(--color-bg-muted);
}

.nav-link.active {
  color: var(--color-primary);
  background: var(--color-bg-subtle);
}

.nav-actions {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
}

.user-pill {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  padding: var(--spacing-xs) var(--spacing-md) var(--spacing-xs) var(--spacing-xs);
  background: var(--color-bg-subtle);
  border-radius: 100px;
  margin-right: var(--spacing-sm);
}

.user-avatar {
  border: 2px solid var(--color-bg-elevated);
}

.user-name {
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  color: var(--color-text-primary);
}

/* Buttons */
.btn-ghost {
  padding: var(--spacing-sm) var(--spacing-md);
  background: transparent;
  border: none;
  color: var(--color-text-secondary);
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  cursor: pointer;
  border-radius: var(--radius-md);
  transition: all var(--transition-fast);
}

.btn-ghost:hover {
  color: var(--color-text-primary);
  background: var(--color-bg-muted);
}

.btn-ghost.btn-danger:hover {
  color: var(--color-danger);
  background: rgba(158, 112, 112, 0.1);
}

.btn-primary {
  padding: var(--spacing-sm) var(--spacing-md);
  background: var(--color-primary);
  border: none;
  color: #fff;
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  cursor: pointer;
  border-radius: var(--radius-md);
  transition: all var(--transition-fast);
}

.btn-primary:hover {
  background: var(--color-primary-dark);
}

.btn-primary:active {
  transform: scale(0.98);
}

/* Footer */
.app-footer {
  height: 48px !important;
  background: var(--color-bg-elevated);
  border-top: 1px solid var(--color-border);
  display: flex;
  align-items: center;
  justify-content: center;
}

.footer-text {
  color: var(--color-text-muted);
  font-size: var(--font-size-sm);
}

/* Override Element Plus styles */
.el-card {
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-sm);
}

.el-card__header {
  border-bottom: 1px solid var(--color-border-light);
  padding: var(--spacing-md) var(--spacing-lg);
}

.el-card__body {
  padding: var(--spacing-lg);
}

.el-button--primary {
  background: var(--color-primary);
  border-color: var(--color-primary);
}

.el-button--primary:hover {
  background: var(--color-primary-light);
  border-color: var(--color-primary-light);
}

.el-button--success {
  background: var(--color-success);
  border-color: var(--color-success);
}

.el-button--danger {
  background: var(--color-danger);
  border-color: var(--color-danger);
}

.el-input__wrapper {
  border-radius: var(--radius-md);
  box-shadow: none;
  border: 1px solid var(--color-border);
  transition: border-color var(--transition-fast);
}

.el-input__wrapper:hover {
  border-color: var(--color-primary-light);
}

.el-input__wrapper.is-focus {
  border-color: var(--color-primary);
  box-shadow: 0 0 0 2px rgba(90, 107, 124, 0.1);
}

.el-dialog {
  border-radius: var(--radius-lg);
}

.el-dialog__header {
  border-bottom: 1px solid var(--color-border-light);
  padding: var(--spacing-md) var(--spacing-lg);
  margin: 0;
}

.el-dialog__body {
  padding: var(--spacing-lg);
}
</style>