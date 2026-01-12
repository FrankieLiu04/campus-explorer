<template>
  <div class="auth-container">
    <div class="auth-card">
      <div class="auth-header">
        <h1 class="auth-title">Welcome back</h1>
        <p class="auth-subtitle">Sign in to continue to Campus Explorer</p>
      </div>
      
      <el-form :model="loginForm" :rules="rules" ref="loginFormRef" label-position="top" class="auth-form">
        <el-form-item label="Username" prop="username">
          <el-input v-model="loginForm.username" placeholder="Enter your username" size="large"></el-input>
        </el-form-item>
        <el-form-item label="Password" prop="password">
          <el-input v-model="loginForm.password" type="password" placeholder="Enter your password" show-password size="large"></el-input>
        </el-form-item>
        <el-form-item class="form-actions">
          <button type="button" class="btn-submit" @click="handleLogin" :disabled="loading">
            <span v-if="loading" class="loading-spinner"></span>
            {{ loading ? 'Signing in...' : 'Sign in' }}
          </button>
        </el-form-item>
      </el-form>
      
      <div class="auth-footer">
        <span class="footer-text">Don't have an account?</span>
        <button class="btn-link" @click="$router.push('/register')">Create one</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useAuthStore } from '../stores/auth'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'

const authStore = useAuthStore()
const router = useRouter()
const loginFormRef = ref()
const loading = ref(false)

const loginForm = reactive({
  username: '',
  password: ''
})

const rules = {
  username: [
    { required: true, message: 'Please enter username', trigger: 'blur' },
    { min: 3, max: 20, message: 'Length should be 3 to 20 characters', trigger: 'blur' }
  ],
  password: [
    { required: true, message: 'Please enter password', trigger: 'blur' },
    { min: 6, message: 'Password must be at least 6 characters', trigger: 'blur' }
  ]
}

const handleLogin = async () => {
  if (!loginFormRef.value) return
  
  await loginFormRef.value.validate(async (valid) => {
    if (valid) {
      loading.value = true
      try {
        await authStore.login(loginForm)
        ElMessage.success('Login successful!')
        router.push('/')
      } catch (error) {
        ElMessage.error(error.message || 'Login failed')
      } finally {
        loading.value = false
      }
    }
  })
}
</script>

<style scoped>
.auth-container {
  min-height: calc(100vh - 120px);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: var(--spacing-lg);
}

.auth-card {
  width: 100%;
  max-width: 400px;
  background: var(--color-bg-elevated);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: var(--spacing-2xl) var(--spacing-xl);
}

.auth-header {
  text-align: center;
  margin-bottom: var(--spacing-xl);
}

.auth-title {
  font-size: var(--font-size-2xl);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
  margin: 0 0 var(--spacing-xs);
  letter-spacing: -0.02em;
}

.auth-subtitle {
  font-size: var(--font-size-base);
  color: var(--color-text-muted);
  margin: 0;
}

.auth-form :deep(.el-form-item__label) {
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  color: var(--color-text-secondary);
  padding-bottom: var(--spacing-xs);
}

.form-actions {
  margin-top: var(--spacing-lg);
}

.btn-submit {
  width: 100%;
  padding: 12px var(--spacing-lg);
  background: var(--color-primary);
  border: none;
  border-radius: var(--radius-md);
  color: #fff;
  font-size: var(--font-size-base);
  font-weight: var(--font-weight-medium);
  cursor: pointer;
  transition: all var(--transition-fast);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--spacing-sm);
}

.btn-submit:hover:not(:disabled) {
  background: var(--color-primary-dark);
}

.btn-submit:active:not(:disabled) {
  transform: scale(0.98);
}

.btn-submit:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.loading-spinner {
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: #fff;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.auth-footer {
  text-align: center;
  margin-top: var(--spacing-xl);
  padding-top: var(--spacing-lg);
  border-top: 1px solid var(--color-border-light);
}

.footer-text {
  font-size: var(--font-size-sm);
  color: var(--color-text-muted);
  margin-right: var(--spacing-xs);
}

.btn-link {
  background: none;
  border: none;
  color: var(--color-primary);
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  cursor: pointer;
  transition: color var(--transition-fast);
}

.btn-link:hover {
  color: var(--color-primary-dark);
}
</style>