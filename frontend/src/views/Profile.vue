<template>
  <div class="profile-page">
    <div class="profile-container">
      <header class="profile-header">
        <h1 class="profile-title">Profile</h1>
        <button 
          v-if="!loading && !error" 
          class="btn-secondary" 
          @click="editMode = !editMode"
        >
          {{ editMode ? 'Cancel' : 'Edit' }}
        </button>
      </header>

      <div v-if="loading" class="loading-state">
        <div class="skeleton skeleton-avatar"></div>
        <div class="skeleton skeleton-line"></div>
        <div class="skeleton skeleton-line short"></div>
      </div>

      <div v-else-if="error" class="error-state">
        <p>{{ error }}</p>
      </div>

      <div v-else class="profile-content">
        <el-form :model="profileForm" :rules="rules" ref="profileFormRef" label-position="top" class="profile-form">
          
          <div class="avatar-section">
            <div class="avatar-wrapper">
              <el-upload
                class="avatar-upload"
                action="#"
                :show-file-list="false"
                :auto-upload="false"
                @change="handleAvatarChange"
                :disabled="!editMode"
              >
                <img v-if="avatarPreview" :src="avatarPreview" class="avatar-image" />
                <div v-else class="avatar-placeholder">
                  <span>+</span>
                </div>
                <div v-if="editMode" class="avatar-overlay">Change</div>
              </el-upload>
            </div>
            <div class="user-basic">
              <h2 class="user-name">{{ profileForm.username }}</h2>
              <p class="user-email">{{ profileForm.email }}</p>
            </div>
          </div>

          <div class="form-grid">
            <el-form-item label="First Name" prop="first_name">
              <el-input v-model="profileForm.first_name" :disabled="!editMode" placeholder="First name" />
            </el-form-item>

            <el-form-item label="Last Name" prop="last_name">
              <el-input v-model="profileForm.last_name" :disabled="!editMode" placeholder="Last name" />
            </el-form-item>

            <el-form-item label="Age" prop="age">
              <el-input-number 
                v-model="profileForm.age" 
                :min="1" 
                :max="150"
                :disabled="!editMode"
                style="width: 100%;"
              />
            </el-form-item>

            <el-form-item label="Gender" prop="gender">
              <el-select v-model="profileForm.gender" :disabled="!editMode" placeholder="Select" style="width: 100%;">
                <el-option label="Male" value="male" />
                <el-option label="Female" value="female" />
                <el-option label="Other" value="other" />
                <el-option label="Prefer not to say" value="prefer_not_to_say" />
              </el-select>
            </el-form-item>

            <el-form-item label="Phone" prop="phone">
              <el-input v-model="profileForm.phone" :disabled="!editMode" placeholder="Phone number" />
            </el-form-item>

            <el-form-item label="Location" prop="location">
              <el-input v-model="profileForm.location" :disabled="!editMode" placeholder="Location" />
            </el-form-item>
          </div>

          <el-form-item label="Bio" prop="bio" class="bio-field">
            <el-input 
              v-model="profileForm.bio" 
              type="textarea" 
              rows="3"
              :disabled="!editMode"
              placeholder="Tell us about yourself..."
            />
          </el-form-item>

          <div v-if="editMode" class="form-actions">
            <button type="button" class="btn-primary" @click="handleUpdate" :disabled="saving">
              {{ saving ? 'Saving...' : 'Save Changes' }}
            </button>
            <button type="button" class="btn-ghost" @click="cancelEdit">Cancel</button>
          </div>
        </el-form>

        <div class="security-section">
          <button class="btn-secondary" @click="passwordDialogVisible = true">
            Change Password
          </button>
        </div>
      </div>
    </div>

    <el-dialog v-model="passwordDialogVisible" title="Change Password" width="400px">
      <el-form :model="passwordForm" :rules="passwordRules" ref="passwordFormRef" label-position="top">
        <el-form-item label="Current Password" prop="current_password">
          <el-input v-model="passwordForm.current_password" type="password" show-password />
        </el-form-item>
        <el-form-item label="New Password" prop="new_password">
          <el-input v-model="passwordForm.new_password" type="password" show-password />
        </el-form-item>
        <el-form-item label="Confirm Password" prop="confirm_password">
          <el-input v-model="passwordForm.confirm_password" type="password" show-password />
        </el-form-item>
      </el-form>
      <template #footer>
        <button class="btn-ghost" @click="passwordDialogVisible = false">Cancel</button>
        <button class="btn-primary" @click="handleChangePassword" :disabled="changingPassword">
          {{ changingPassword ? 'Changing...' : 'Change Password' }}
        </button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { useAuthStore } from '../stores/auth'
import { ElMessage } from 'element-plus'
import axios from 'axios'

const authStore = useAuthStore()
const loading = ref(true)
const error = ref(null)
const editMode = ref(false)
const saving = ref(false)
const passwordDialogVisible = ref(false)
const changingPassword = ref(false)
const avatarFile = ref(null)

const profileForm = ref({
  username: '',
  email: '',
  first_name: '',
  last_name: '',
  age: null,
  gender: '',
  phone: '',
  location: '',
  bio: '',
  avatar_url: ''
})

const originalProfile = ref({})

const passwordForm = ref({
  current_password: '',
  new_password: '',
  confirm_password: ''
})

const rules = {
  first_name: [
    { max: 50, message: 'Maximum 50 characters', trigger: 'blur' }
  ],
  last_name: [
    { max: 50, message: 'Maximum 50 characters', trigger: 'blur' }
  ],
  age: [
    { type: 'number', min: 1, max: 150, message: 'Age must be between 1 and 150', trigger: 'blur' }
  ],
  phone: [
    { max: 20, message: 'Maximum 20 characters', trigger: 'blur' }
  ],
  location: [
    { max: 100, message: 'Maximum 100 characters', trigger: 'blur' }
  ],
  bio: [
    { max: 500, message: 'Maximum 500 characters', trigger: 'blur' }
  ],
  avatar_url: [
    { type: 'url', message: 'Please enter a valid URL', trigger: 'blur' }
  ]
}

const avatarPreview = computed(() => {
  if (avatarFile.value) {
    return URL.createObjectURL(avatarFile.value);
  }
  if (profileForm.value.avatar_url) {
    const baseUrl = 'http://localhost:5000';
    // If avatar_url is already a full URL, use it. Otherwise, prepend the base URL.
    if (profileForm.value.avatar_url.startsWith('http')) {
      return profileForm.value.avatar_url;
    }
    // Ensure we don't have double slashes
    const path = profileForm.value.avatar_url.startsWith('/')
      ? profileForm.value.avatar_url
      : `/${profileForm.value.avatar_url}`;
    return `${baseUrl}${path}`;
  }
  return '';
});

const validateConfirmPassword = (rule, value, callback) => {
  if (value !== passwordForm.value.new_password) {
    callback(new Error('Passwords do not match'))
  } else {
    callback()
  }
}

const passwordRules = {
  current_password: [
    { required: true, message: 'Please enter current password', trigger: 'blur' }
  ],
  new_password: [
    { required: true, message: 'Please enter new password', trigger: 'blur' },
    { min: 6, message: 'Password must be at least 6 characters', trigger: 'blur' }
  ],
  confirm_password: [
    { required: true, message: 'Please confirm new password', trigger: 'blur' },
    { validator: validateConfirmPassword, trigger: 'blur' }
  ]
}

const loadProfile = async () => {
  loading.value = true
  try {
    const token = localStorage.getItem('token')
    const response = await axios.get('/api/profile/profile', {
      headers: { Authorization: `Bearer ${token}` }
    })
    
    profileForm.value = { ...response.data.user }
    originalProfile.value = { ...response.data.user }
  } catch (error) {
    error.value = error.response?.data?.error || 'Failed to load profile'
    ElMessage.error(error.value)
  } finally {
    loading.value = false
  }
}

const handleAvatarChange = (file) => {
  const isJpgOrPng = file.raw.type === 'image/jpeg' || file.raw.type === 'image/png';
  if (!isJpgOrPng) {
    ElMessage.error('Avatar must be JPG or PNG format!');
    return;
  }
  const isLt2M = file.raw.size / 1024 / 1024 < 2;
  if (!isLt2M) {
    ElMessage.error('Avatar size can not exceed 2MB!');
    return;
  }
  avatarFile.value = file.raw;
}

const handleUpdate = async () => {
  saving.value = true;
  try {
    const token = localStorage.getItem('token');
    
    // If a new avatar is selected, upload it as form-data
    if (avatarFile.value) {
      const formData = new FormData();
      Object.keys(profileForm.value).forEach(key => {
        if (key !== 'avatar_url') { // Don't send the old URL
          formData.append(key, profileForm.value[key]);
        }
      });
      formData.append('avatar', avatarFile.value);

      const response = await axios.put('/api/profile/profile', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
          Authorization: `Bearer ${token}`
        }
      });
      profileForm.value = { ...response.data.user };
      avatarFile.value = null; // Reset after upload
    } else {
      // Otherwise, just update profile data as JSON
      const response = await axios.put('/api/profile/profile', profileForm.value, {
        headers: { Authorization: `Bearer ${token}` }
      });
      profileForm.value = { ...response.data.user };
    }
    
    ElMessage.success('Profile updated successfully');
    editMode.value = false;
    originalProfile.value = { ...profileForm.value };
    authStore.user.avatar_url = profileForm.value.avatar_url; // Update auth store
  } catch (error) {
    ElMessage.error(error.response?.data?.error || 'Failed to update profile');
  } finally {
    saving.value = false;
  }
}

const cancelEdit = () => {
  profileForm.value = { ...originalProfile.value };
  avatarFile.value = null; // Discard selected file on cancel
  editMode.value = false;
}

const handleChangePassword = async () => {
  changingPassword.value = true
  try {
    const token = localStorage.getItem('token')
    const response = await axios.post('/api/profile/change-password', passwordForm.value, {
      headers: { Authorization: `Bearer ${token}` }
    })
    
    ElMessage.success('Password changed successfully')
    passwordDialogVisible.value = false
    passwordForm.value = {
      current_password: '',
      new_password: '',
      confirm_password: ''
    }
  } catch (error) {
    ElMessage.error(error.response?.data?.error || 'Failed to change password')
  } finally {
    changingPassword.value = false
  }
}

onMounted(() => {
  loadProfile()
})
</script>

<style scoped>
.profile-page {
  max-width: 640px;
  margin: 0 auto;
  padding: var(--spacing-lg);
}

.profile-container {
  background: var(--color-bg-elevated);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  overflow: hidden;
}

.profile-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--spacing-md) var(--spacing-lg);
  border-bottom: 1px solid var(--color-border-light);
}

.profile-title {
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
  margin: 0;
}

.btn-secondary {
  padding: var(--spacing-sm) var(--spacing-md);
  background: var(--color-bg-subtle);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  color: var(--color-text-secondary);
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.btn-secondary:hover {
  border-color: var(--color-border-focus);
  color: var(--color-text-primary);
}

.loading-state {
  padding: var(--spacing-xl);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--spacing-md);
}

.skeleton {
  background: linear-gradient(90deg, var(--color-bg-muted) 25%, var(--color-bg-subtle) 50%, var(--color-bg-muted) 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
  border-radius: var(--radius-md);
}

.skeleton-avatar {
  width: 80px;
  height: 80px;
  border-radius: 50%;
}

.skeleton-line {
  width: 200px;
  height: 16px;
}

.skeleton-line.short {
  width: 120px;
}

@keyframes shimmer {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}

.error-state {
  padding: var(--spacing-xl);
  text-align: center;
  color: var(--color-danger);
}

.profile-content {
  padding: var(--spacing-xl);
}

.avatar-section {
  display: flex;
  align-items: center;
  gap: var(--spacing-lg);
  margin-bottom: var(--spacing-xl);
  padding-bottom: var(--spacing-xl);
  border-bottom: 1px solid var(--color-border-light);
}

.avatar-wrapper {
  position: relative;
}

.avatar-upload {
  display: block;
}

.avatar-image {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  object-fit: cover;
  border: 2px solid var(--color-border);
}

.avatar-placeholder {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  background: var(--color-bg-muted);
  border: 2px dashed var(--color-border);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  color: var(--color-text-muted);
}

.avatar-overlay {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  background: rgba(0, 0, 0, 0.6);
  color: #fff;
  font-size: var(--font-size-xs);
  text-align: center;
  padding: 4px;
  border-radius: 0 0 40px 40px;
  cursor: pointer;
}

.user-basic {
  flex: 1;
}

.user-name {
  font-size: var(--font-size-xl);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
  margin: 0 0 var(--spacing-xs);
}

.user-email {
  font-size: var(--font-size-sm);
  color: var(--color-text-muted);
  margin: 0;
}

.profile-form :deep(.el-form-item__label) {
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  color: var(--color-text-secondary);
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: var(--spacing-md);
}

.bio-field {
  margin-top: var(--spacing-md);
}

.form-actions {
  display: flex;
  gap: var(--spacing-sm);
  margin-top: var(--spacing-lg);
  padding-top: var(--spacing-lg);
  border-top: 1px solid var(--color-border-light);
}

.btn-primary {
  padding: var(--spacing-sm) var(--spacing-lg);
  background: var(--color-primary);
  border: none;
  border-radius: var(--radius-md);
  color: #fff;
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.btn-primary:hover:not(:disabled) {
  background: var(--color-primary-dark);
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-ghost {
  padding: var(--spacing-sm) var(--spacing-md);
  background: transparent;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  color: var(--color-text-secondary);
  font-size: var(--font-size-sm);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.btn-ghost:hover {
  border-color: var(--color-border-focus);
  color: var(--color-text-primary);
}

.security-section {
  margin-top: var(--spacing-xl);
  padding-top: var(--spacing-xl);
  border-top: 1px solid var(--color-border-light);
}
</style>