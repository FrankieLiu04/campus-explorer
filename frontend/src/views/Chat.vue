<template>
  <div class="chat-page">
    <div class="chat-container">
      <header class="chat-header">
        <div class="header-left">
          <h1 class="chat-title">Chat</h1>
          <span class="online-badge">{{ onlineUsers }} online</span>
        </div>
      </header>
      
      <div class="chat-messages" ref="messagesContainer">
        <div 
          v-for="message in messages" 
          :key="message.id"
          :class="['message', message.type === 'system' ? 'system-message' : 'user-message']"
        >
          <template v-if="message.type === 'system'">
            <span class="system-text">{{ message.content }}</span>
          </template>
          <template v-else>
            <el-avatar :src="fullAvatarUrl(message.avatar_url)" :size="36" class="message-avatar"></el-avatar>
            <div class="message-body">
              <div class="message-meta">
                <span class="message-author">{{ message.username }}</span>
                <span class="message-time">{{ formatTime(message.timestamp) }}</span>
              </div>
              <div class="message-content">
                <template v-if="message.type === 'sticker'">
                  <img :src="getStickerUrl(message.content)" alt="Sticker" class="sticker-message" />
                </template>
                <template v-else-if="message.type === 'image'">
                  <img :src="message.content" alt="Image" class="image-message" @load="scrollToBottom" />
                </template>
                <template v-else-if="message.type === 'voice'">
                  <audio controls :src="message.content" class="voice-message"></audio>
                </template>
                <template v-else>
                  {{ message.content }}
                </template>
              </div>
            </div>
          </template>
        </div>
      </div>
      
      <div class="chat-input-area">
        <div v-if="!authStore.isAuthenticated" class="login-prompt">
          <span>Please login to chat</span>
          <button class="btn-link" @click="$router.push('/login')">Login →</button>
        </div>
        
        <template v-else>
          <div v-if="isRecording" class="recording-indicator">
            <span class="recording-dot"></span>
            <span>Recording {{ recordingTime }}s</span>
          </div>
          
          <div v-if="currentPicker" class="picker-panel">
            <div v-if="currentPicker === 'emoji'" class="emoji-grid">
              <span
                v-for="emoji in emojis"
                :key="emoji"
                @click="insertEmoji(emoji)"
                class="emoji-item"
              >{{ emoji }}</span>
            </div>
            <div v-if="currentPicker === 'sticker'" class="sticker-grid">
              <img
                v-for="sticker in stickers"
                :key="sticker.id"
                :src="sticker.url"
                @click="sendSticker(sticker)"
                class="sticker-item"
              />
            </div>
          </div>
          
          <div class="input-row">
            <div class="input-actions">
              <button 
                class="action-btn" 
                :class="{ active: currentPicker === 'emoji' }"
                @click="togglePicker('emoji')"
                title="Emoji"
              >😊</button>
              <button 
                class="action-btn"
                :class="{ active: currentPicker === 'sticker' }"
                @click="togglePicker('sticker')"
                title="Stickers"
              >🖼️</button>
              <el-upload
                action="#"
                :auto-upload="false"
                :show-file-list="false"
                :on-change="handleImageSelect"
                accept="image/*"
              >
                <button class="action-btn" title="Photo">📷</button>
              </el-upload>
              <button 
                class="action-btn"
                :class="{ active: isRecording, recording: isRecording }"
                @click="toggleRecording"
                title="Voice"
              >{{ isRecording ? '⏹️' : '🎤' }}</button>
            </div>
            <input
              v-model="newMessage"
              type="text"
              class="message-input"
              placeholder="Type a message..."
              @keyup.enter="sendMessage"
            />
            <button class="send-btn" @click="sendMessage" :disabled="!newMessage.trim()">
              Send
            </button>
          </div>
        </template>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick, watch, computed } from 'vue'
import { io } from 'socket.io-client'
import { useAuthStore } from '../stores/auth'
import { ElMessage } from 'element-plus'

const authStore = useAuthStore()
const socket = ref(null)
const messages = ref([])
const newMessage = ref('')
const onlineUsers = ref(0)
const messagesContainer = ref(null)
const isRecording = ref(false)
const mediaRecorder = ref(null)
const audioChunks = ref([])
const recordingTime = ref(0)
const recordingInterval = ref(null)

const formatTime = (timestamp) => {
  if (!timestamp) return '';
  const date = new Date(timestamp);
  return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
};

const fullAvatarUrl = (avatarUrl) => {
  if (!avatarUrl) {
    return 'https://cube.elemecdn.com/3/7c/3ea6beec64369c2642b92c6726f1epng.png';
  }
  if (avatarUrl.startsWith('http')) {
    return avatarUrl;
  }
  return `http://localhost:5000${avatarUrl}`;
};

const scrollToBottom = () => {
  nextTick(() => {
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
    }
  })
}

const sendMessage = () => {
  if (!newMessage.value.trim()) return
  
  const message = {
    username: authStore.user.username,
    content: newMessage.value.trim(),
    type: 'text',
    timestamp: Date.now(),
    avatar_url: authStore.user.avatar_url
  }
  
  socket.value.emit('message', message)
  newMessage.value = ''
}

onMounted(() => {
  socket.value = io('http://localhost:5000')
  
  socket.value.on('connect', () => {
    console.log('Connected to chat server')
  })
  
  socket.value.on('user_joined', (data) => {
    messages.value.push({
      id: Date.now(),
      id: Date.now(),
      type: 'system',
      username: 'System',
      content: `${data.username} has joined the chat`,
      timestamp: Date.now()
    })
    onlineUsers.value = data.online_users
    scrollToBottom()
  })
  
  socket.value.on('user_left', (data) => {
    messages.value.push({
      id: Date.now(),
      id: Date.now(),
      type: 'system',
      username: 'System',
      content: `${data.username} has left the chat`,
      timestamp: Date.now()
    })
    onlineUsers.value = data.online_users
    scrollToBottom()
  })
  
  socket.value.on('message', (message) => {
    messages.value.push({
      id: Date.now(),
      type: 'user',
      ...message
    })
    scrollToBottom()
  })
  
  socket.value.on('online_users', (count) => {
    onlineUsers.value = count
  })
  
  socket.value.on('previous_messages', (previousMessages) => {
    messages.value = previousMessages
    scrollToBottom()
  })
  
  // 如果用户已登录，发送加入事件
  if (authStore.isAuthenticated) {
    socket.value.emit('join', { username: authStore.user.username })
  }
  
  // 监听图片加载完成事件
  socket.value.on('image_loaded', scrollToBottom)
})

onUnmounted(() => {
  if (socket.value) {
    socket.value.disconnect()
  }
  if (isRecording.value) {
    stopRecording()
  }
})

// 监听登录状态变化
watch(() => authStore.isAuthenticated, (isAuthenticated) => {
  if (isAuthenticated && socket.value) {
    socket.value.emit('join', { username: authStore.user.username })
  }
})

// Media picker state
const currentPicker = ref(null)

const togglePicker = (type) => {
  currentPicker.value = currentPicker.value === type ? null : type
}

const emojis = [
  '😀', '😃', '😄', '😁', '😆', '😅', '🤣', '😂', '🙂', '🙃',
  '😊', '😇', '🥰', '😍', '🤩', '😘', '😗', '😚', '😙', '😋',
  '😛', '😜', '🤪', '😝', '🤑', '🤗', '🤭', '🤫', '🤔', '🤐',
  '🤨', '😐', '😑', '😶', '😏', '😒', '🙄', '😬', '🤥', '😔',
  '😪', '🤤', '😴', '😷', '🤒', '🤕', '🤢', '🤮', '🤧', '🥵',
  '🥶', '🥴', '😵', '🤯', '🤠', '🥳', '😎', '🤓', '🧐', '😕',
  '😟', '🙁', '☹️', '😮', '😯', '😲', '😳', '🥺', '😦', '😧',
  '😨', '😰', '😥', '😢', '😭', '😱', '😖', '😣', '😞', '😓',
  '😩', '😫', '🥱', '😤', '😡', '😠', '🤬', '😈', '👿', '💀',
  '☠️', '💩', '🤡', '👹', '👺', '👻', '👽', '👾', '🤖', '❤️',
  '🧡', '💛', '💚', '💙', '💜', '🤍', '🖤', '🤎', '💯', '💢'
]

const stickers = [
  { id: 1, url: '/stickers/sticker1.jpg' },
  { id: 2, url: '/stickers/sticker2.jpg' },
  { id: 3, url: '/stickers/sticker3.jpg' },
  { id: 4, url: '/stickers/sticker4.jpg' },
  { id: 5, url: '/stickers/sticker5.jpg' }
]

const insertEmoji = (emoji) => {
  newMessage.value += emoji
  currentPicker.value = null
}

const sendSticker = (sticker) => {
  const message = {
    username: authStore.user.username,
    content: `[STICKER:${sticker.id}]`,
    type: 'sticker',
    timestamp: Date.now(),
    avatar_url: authStore.user.avatar_url
  }
  
  socket.value.emit('message', message)
  currentPicker.value = null
}

const handleImageSelect = (file) => {
  const reader = new FileReader()
  reader.onload = (e) => {
    const imageData = e.target.result
    sendImage(imageData)
  }
  reader.readAsDataURL(file.raw)
}

const sendImage = (imageData) => {
  const message = {
    username: authStore.user.username,
    content: imageData,
    type: 'image',
    timestamp: Date.now(),
    avatar_url: authStore.user.avatar_url
  }
  
  socket.value.emit('message', message)
}
const getStickerUrl = (content) => {
  const match = content.match(/\[STICKER:(\d+)\]/)
  if (match) {
    const stickerId = parseInt(match[1])
    const sticker = stickers.find(s => s.id === stickerId)
    return sticker ? sticker.url : ''
  }
  return ''
}

const toggleRecording = async () => {
  if (!isRecording.value) {
    await startRecording()
  } else {
    stopRecording()
  }
}

const startRecording = async () => {
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
    mediaRecorder.value = new MediaRecorder(stream)
    audioChunks.value = []
    
    mediaRecorder.value.ondataavailable = (event) => {
      audioChunks.value.push(event.data)
    }
    
    mediaRecorder.value.onstop = () => {
      const audioBlob = new Blob(audioChunks.value, { type: 'audio/webm' })
      const reader = new FileReader()
      reader.onload = (e) => {
        sendVoiceMessage(e.target.result)
      }
      reader.readAsDataURL(audioBlob)
    }
    
    mediaRecorder.value.start()
    isRecording.value = true
    recordingTime.value = 0
    
    recordingInterval.value = setInterval(() => {
      recordingTime.value++
    }, 1000)
    
  } catch (error) {
    console.error('Error accessing microphone:', error)
    ElMessage.error('Cannot access microphone, please check permissions.')
  }
}

const stopRecording = () => {
  if (mediaRecorder.value && isRecording.value) {
    mediaRecorder.value.stop()
    isRecording.value = false
    
    if (recordingInterval.value) {
      clearInterval(recordingInterval.value)
      recordingInterval.value = null
    }
    
    // 停止所有音频轨道
    const tracks = mediaRecorder.value.stream.getTracks()
    tracks.forEach(track => track.stop())
  }
}

const sendVoiceMessage = (audioData) => {
  const message = {
    username: authStore.user.username,
    content: audioData,
    type: 'voice',
    timestamp: Date.now(),
    avatar_url: authStore.user.avatar_url
  }
  
  socket.value.emit('message', message)
}
</script>

<style scoped>
.chat-page {
  max-width: 800px;
  margin: 0 auto;
  height: calc(100vh - 120px);
  padding: var(--spacing-lg);
}

.chat-container {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: var(--color-bg-elevated);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  overflow: hidden;
}

.chat-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--spacing-md) var(--spacing-lg);
  border-bottom: 1px solid var(--color-border-light);
}

.header-left {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
}

.chat-title {
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
  margin: 0;
}

.online-badge {
  font-size: var(--font-size-xs);
  color: var(--color-success);
  background: rgba(107, 142, 122, 0.1);
  padding: var(--spacing-xs) var(--spacing-sm);
  border-radius: 100px;
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: var(--spacing-lg);
  background: var(--color-bg-subtle);
}

.message {
  margin-bottom: var(--spacing-md);
}

.system-message {
  text-align: center;
}

.system-text {
  font-size: var(--font-size-xs);
  color: var(--color-text-muted);
  background: var(--color-bg-muted);
  padding: var(--spacing-xs) var(--spacing-md);
  border-radius: 100px;
}

.user-message {
  display: flex;
  gap: var(--spacing-sm);
}

.message-avatar {
  flex-shrink: 0;
}

.message-body {
  flex: 1;
  min-width: 0;
}

.message-meta {
  display: flex;
  align-items: baseline;
  gap: var(--spacing-sm);
  margin-bottom: var(--spacing-xs);
}

.message-author {
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  color: var(--color-text-primary);
}

.message-time {
  font-size: var(--font-size-xs);
  color: var(--color-text-muted);
}

.message-content {
  font-size: var(--font-size-base);
  color: var(--color-text-primary);
  line-height: 1.5;
  word-wrap: break-word;
}

.sticker-message {
  max-width: 120px;
  border-radius: var(--radius-md);
}

.image-message {
  max-width: 240px;
  max-height: 240px;
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: opacity var(--transition-fast);
}

.image-message:hover {
  opacity: 0.9;
}

.voice-message {
  height: 36px;
  max-width: 280px;
}

.chat-input-area {
  border-top: 1px solid var(--color-border-light);
  padding: var(--spacing-md) var(--spacing-lg);
  background: var(--color-bg-elevated);
}

.login-prompt {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--spacing-md);
  padding: var(--spacing-md);
  color: var(--color-text-muted);
  font-size: var(--font-size-sm);
}

.btn-link {
  background: none;
  border: none;
  color: var(--color-primary);
  font-weight: var(--font-weight-medium);
  cursor: pointer;
}

.recording-indicator {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  padding: var(--spacing-sm) var(--spacing-md);
  background: rgba(158, 112, 112, 0.1);
  border-radius: var(--radius-md);
  margin-bottom: var(--spacing-sm);
  font-size: var(--font-size-sm);
  color: var(--color-danger);
}

.recording-dot {
  width: 8px;
  height: 8px;
  background: var(--color-danger);
  border-radius: 50%;
  animation: pulse 1s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.4; }
}

.picker-panel {
  background: var(--color-bg-subtle);
  border: 1px solid var(--color-border-light);
  border-radius: var(--radius-md);
  padding: var(--spacing-md);
  margin-bottom: var(--spacing-md);
  max-height: 200px;
  overflow-y: auto;
}

.emoji-grid {
  display: grid;
  grid-template-columns: repeat(10, 1fr);
  gap: 2px;
}

.emoji-item {
  font-size: 20px;
  padding: var(--spacing-xs);
  text-align: center;
  cursor: pointer;
  border-radius: var(--radius-sm);
  transition: background var(--transition-fast);
}

.emoji-item:hover {
  background: var(--color-bg-muted);
}

.sticker-grid {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: var(--spacing-sm);
}

.sticker-item {
  width: 100%;
  aspect-ratio: 1;
  object-fit: cover;
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: transform var(--transition-fast);
}

.sticker-item:hover {
  transform: scale(1.05);
}

.input-row {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
}

.input-actions {
  display: flex;
  gap: var(--spacing-xs);
}

.action-btn {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--color-bg-subtle);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  cursor: pointer;
  font-size: 16px;
  transition: all var(--transition-fast);
}

.action-btn:hover {
  background: var(--color-bg-muted);
  border-color: var(--color-border-focus);
}

.action-btn.active {
  background: var(--color-primary);
  border-color: var(--color-primary);
}

.action-btn.recording {
  background: var(--color-danger);
  border-color: var(--color-danger);
}

.message-input {
  flex: 1;
  height: 40px;
  padding: 0 var(--spacing-md);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  font-size: var(--font-size-base);
  font-family: inherit;
  transition: border-color var(--transition-fast);
}

.message-input:focus {
  outline: none;
  border-color: var(--color-primary);
}

.message-input::placeholder {
  color: var(--color-text-placeholder);
}

.send-btn {
  height: 40px;
  padding: 0 var(--spacing-lg);
  background: var(--color-primary);
  border: none;
  border-radius: var(--radius-md);
  color: #fff;
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-medium);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.send-btn:hover:not(:disabled) {
  background: var(--color-primary-dark);
}

.send-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>