<script setup>
import { ref, nextTick } from 'vue';
import { chatService } from '../../services/chatService';

const isOpen = ref(false);
const isLoading = ref(false);
const inputMessage = ref('');
const chatBox = ref(null);

// Initial greeting from the AI
const messages = ref([
  { 
    role: 'assistant', 
    content: 'Hello! I am your AI Data Analyst. You can ask me questions about tasks, staff performance, and project metrics in plain English.' 
  }
]);

const toggleChat = () => {
  isOpen.value = !isOpen.value;
  if (isOpen.value) scrollToBottom();
};

const scrollToBottom = async () => {
  await nextTick();
  if (chatBox.value) {
    chatBox.value.scrollTop = chatBox.value.scrollHeight;
  }
};

const sendMessage = async () => {
  if (!inputMessage.value.trim() || isLoading.value) return;

  const userText = inputMessage.value.trim();
  
  // 1. Add user message to UI instantly
  messages.value.push({ role: 'user', content: userText });
  inputMessage.value = '';
  isLoading.value = true;
  await scrollToBottom();

  try {
    // 2. Send to backend LangChain agent
    const reply = await chatService.sendMessage(userText);
    
    // 3. Add AI response to UI
    messages.value.push({ role: 'assistant', content: reply });
  } catch (error) {
    messages.value.push({ 
      role: 'assistant', 
      content: 'Sorry, I am having trouble accessing the database right now.' 
    });
  } finally {
    isLoading.value = false;
    await scrollToBottom();
  }
};
</script>

<template>
  <div class="chatbot-container">
    <button @click="toggleChat" class="chat-trigger" :class="{ 'is-open': isOpen }">
      <span v-if="!isOpen">✨</span>
      <span v-else>✖</span>
    </button>

    <transition name="chat-slide">
      <div v-if="isOpen" class="chat-window">
        <div class="chat-header">
          <h3>Ops Analyst AI</h3>
          <span class="header-badge">SQL Agent</span>
        </div>
        
        <div class="chat-messages" ref="chatBox">
          <div 
            v-for="(msg, index) in messages" 
            :key="index"
            :class="['message-bubble', msg.role === 'user' ? 'user-msg' : 'ai-msg']"
          >
            {{ msg.content }}
          </div>
          
          <div v-if="isLoading" class="message-bubble ai-msg loading-indicator">
            <span class="dot"></span><span class="dot"></span><span class="dot"></span>
          </div>
        </div>

        <div class="chat-input-area">
          <input 
            v-model="inputMessage" 
            @keyup.enter="sendMessage" 
            type="text" 
            placeholder="Ask about tasks or users..." 
            :disabled="isLoading"
          />
          <button @click="sendMessage" :disabled="isLoading || !inputMessage.trim()">
            ➤
          </button>
        </div>
      </div>
    </transition>
  </div>
</template>

<style scoped>
.chatbot-container {
  position: fixed;
  bottom: 2rem;
  right: 2rem;
  z-index: 9999;
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  font-family: "Inter", sans-serif;
}

.chat-trigger {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  box-shadow: 0 6px 16px rgba(118, 75, 162, 0.4);
  transition: transform 0.2s ease, background 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

.chat-trigger:hover {
  transform: scale(1.08);
}

.chat-trigger.is-open {
  background: #374151;
  box-shadow: 0 4px 10px rgba(0, 0, 0, 0.2);
}

.chat-window {
  position: absolute;
  bottom: 80px;
  right: 0;
  width: 360px;
  height: 500px;
  background: white;
  border-radius: 16px;
  box-shadow: 0 15px 40px rgba(0, 0, 0, 0.15);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  border: 1px solid #e5e7eb;
}

.chat-header {
  background: #1f2937;
  color: white;
  padding: 1rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.chat-header h3 {
  margin: 0;
  font-size: 1.05rem;
  font-weight: 600;
}

.header-badge {
  background: #4f46e5;
  font-size: 0.7rem;
  padding: 0.2rem 0.5rem;
  border-radius: 12px;
  font-weight: bold;
}

.chat-messages {
  flex: 1;
  padding: 1rem;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 1rem;
  background: #f9fafb;
}

.message-bubble {
  max-width: 85%;
  padding: 0.8rem 1rem;
  border-radius: 16px;
  font-size: 0.9rem;
  line-height: 1.4;
  word-wrap: break-word;
}

.user-msg {
  background: #4f46e5;
  color: white;
  align-self: flex-end;
  border-bottom-right-radius: 4px;
}

.ai-msg {
  background: white;
  color: #1f2937;
  align-self: flex-start;
  border-bottom-left-radius: 4px;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.05);
  border: 1px solid #f3f4f6;
}

.chat-input-area {
  padding: 1rem;
  background: white;
  display: flex;
  gap: 0.5rem;
  border-top: 1px solid #f3f4f6;
}

.chat-input-area input {
  flex: 1;
  padding: 0.75rem 1rem;
  border: 1px solid #d1d5db;
  border-radius: 24px;
  outline: none;
  font-size: 0.9rem;
  transition: border-color 0.2s;
}

.chat-input-area input:focus {
  border-color: #4f46e5;
}

.chat-input-area button {
  background: #4f46e5;
  color: white;
  border: none;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: opacity 0.2s, transform 0.2s;
}

.chat-input-area button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.chat-input-area button:not(:disabled):hover {
  transform: scale(1.05);
}

/* Animations */
.chat-slide-enter-active, .chat-slide-leave-active {
  transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
  transform-origin: bottom right;
}
.chat-slide-enter-from, .chat-slide-leave-to {
  opacity: 0;
  transform: scale(0.85) translateY(20px);
}

.loading-indicator {
  display: flex;
  gap: 4px;
  align-items: center;
  padding: 1rem;
}
.dot {
  width: 8px;
  height: 8px;
  background: #9ca3af;
  border-radius: 50%;
  animation: bounce 1.4s infinite ease-in-out both;
}
.dot:nth-child(1) { animation-delay: -0.32s; }
.dot:nth-child(2) { animation-delay: -0.16s; }
@keyframes bounce {
  0%, 80%, 100% { transform: scale(0); }
  40% { transform: scale(1); }
}
</style>