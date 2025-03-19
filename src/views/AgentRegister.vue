<template>
  <div class="agent-register">
    <h1>创建新智能体</h1>
    <form @submit.prevent="handleSubmit" class="register-form">
      <div class="form-group">
        <label for="avatar">智能体头像 <span class="required">*</span></label>
        <div class="avatar-upload">
          <div class="avatar-preview" :class="{ 'empty-avatar': !avatarPreview }">
            <img v-if="avatarPreview" :src="avatarPreview" alt="头像预览">
            <div v-else class="avatar-placeholder">
              <span>AI</span>
            </div>
          </div>
          <div class="upload-controls">
            <label for="avatar-input" class="upload-btn">
              <span>选择图片</span>
              <input 
                type="file" 
                id="avatar-input" 
                ref="avatarInput"
                @change="handleAvatarChange" 
                accept="image/*"
                required
                style="display: none;"
              >
            </label>
            <div v-if="avatarPreview" class="file-name">{{ avatarFileName }}</div>
            <button 
              v-if="avatarPreview" 
              type="button" 
              class="remove-btn"
              @click="removeAvatar"
            >
              移除
            </button>
          </div>
        </div>
        <div class="form-hint">请上传JPG, PNG或GIF格式的图片，最大5MB</div>
      </div>
      
      <div class="form-group">
        <label for="name">智能体名称</label>
        <input 
          type="text" 
          id="name" 
          v-model="form.name" 
          required
          placeholder="请输入智能体名称"
        >
      </div>
      
      <div class="form-group">
        <label for="description">智能体描述</label>
        <textarea 
          id="description" 
          v-model="form.description" 
          required
          placeholder="请输入智能体描述"
          rows="4"
        ></textarea>
      </div>
      
      <div class="form-group">
        <label for="price">智能体标价 <span class="required">*</span></label>
        <div class="price-input-container">
          <input 
            type="number" 
            id="price" 
            v-model="form.price" 
            required
            placeholder="请输入智能体价格"
            min="0.01"
            step="0.01"
          >
          <span class="currency-label">ETH</span>
        </div>
        <div class="form-hint">请设置合理的以太币价格，最小0.01 ETH</div>
      </div>
      
      <div class="form-actions">
        <router-link to="/agents" class="cancel-btn">取消</router-link>
        <button type="submit" class="submit-btn" :disabled="!isFormValid || loading">
          <span v-if="loading">正在创建...</span>
          <span v-else>创建智能体</span>
        </button>
      </div>
    </form>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import { useRouter } from 'vue-router';
import { useAgentStore } from '../store/agents';

const router = useRouter();
const agentStore = useAgentStore();
const form = ref({
  name: '',
  description: '',
  price: '',
  avatar: null
});

const avatarInput = ref(null);
const avatarPreview = ref('');
const avatarFileName = ref('');
const avatarFile = ref(null);
const loading = ref(false);

// 检查表单是否有效
const isFormValid = computed(() => {
  const validPrice = form.value.price && !isNaN(form.value.price) && parseFloat(form.value.price) >= 0.01;
  return form.value.name && 
         form.value.description && 
         validPrice &&
         avatarFile.value;
});

// 处理头像选择
const handleAvatarChange = (event) => {
  const file = event.target.files[0];
  if (!file) return;
  
  // 检查文件大小
  if (file.size > 5 * 1024 * 1024) {
    alert('图片大小不能超过5MB');
    return;
  }
  
  // 检查文件类型
  if (!file.type.match('image.*')) {
    alert('请选择图片文件');
    return;
  }
  
  avatarFile.value = file;
  avatarFileName.value = file.name;
  
  // 创建预览URL
  const reader = new FileReader();
  reader.onload = (e) => {
    avatarPreview.value = e.target.result;
  };
  reader.readAsDataURL(file);
};

// 移除头像
const removeAvatar = () => {
  avatarPreview.value = '';
  avatarFileName.value = '';
  avatarFile.value = null;
  if (avatarInput.value) {
    avatarInput.value.value = '';
  }
};

const handleSubmit = async () => {
  // 确保有头像
  if (!avatarFile.value) {
    alert('请上传智能体头像');
    return;
  }

  // 确保价格有效
  if (!form.value.price || isNaN(form.value.price) || parseFloat(form.value.price) < 0.01) {
    alert('请输入有效的价格，至少0.01 ETH');
    return;
  }
  
  // 将头像转换为base64并添加到表单
  const reader = new FileReader();
  reader.onloadend = async () => {
    try {
      // 创建智能体时显示loading状态
      loading.value = true;
      
      // 使用 store 创建智能体
      const result = await agentStore.createAgent({
        name: form.value.name,
        description: form.value.description,
        role: "智能体", // 默认角色
        price: parseFloat(form.value.price),
        avatar: reader.result
      });
      
      if (result && result.success) {
        console.log('创建智能体成功:', result.agent);
        
        // 显示成功消息
        alert(`智能体 "${result.agent.name}" 创建成功！`);
        
        // 导航到智能体详情页
        router.push(`/agent/${result.agent.id}`);
      } else {
        alert(`创建失败: ${result.message || '未知错误'}`);
      }
    } catch (error) {
      console.error('创建智能体失败:', error);
      alert(`创建智能体时出错: ${error.message || '未知错误'}`);
    } finally {
      loading.value = false;
    }
  };
  reader.readAsDataURL(avatarFile.value);
};
</script>

<style scoped>
.agent-register {
  padding: 2rem;
  max-width: 800px;
  margin: 0 auto;
}

h1 {
  text-align: center;
  margin-bottom: 2rem;
  color: var(--primary-color);
  text-shadow: var(--text-shadow);
}

.register-form {
  background: rgba(0, 255, 0, 0.1);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  padding: 2rem;
}

.light-mode .register-form {
  background: rgba(0, 102, 51, 0.05);
}

.form-group {
  margin-bottom: 1.5rem;
}

label {
  display: block;
  color: var(--primary-color);
  margin-bottom: 0.5rem;
}

input, textarea {
  width: 100%;
  padding: 0.8rem;
  background: var(--input-bg);
  border: 1px solid var(--border-color);
  border-radius: 4px;
  color: var(--input-text);
  font-size: 1rem;
}

input:focus, textarea:focus {
  outline: none;
  box-shadow: 0 0 10px rgba(0, 255, 0, 0.3);
}

.light-mode input:focus, .light-mode textarea:focus {
  box-shadow: 0 0 10px rgba(0, 102, 51, 0.3);
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  margin-top: 2rem;
}

.cancel-btn, .submit-btn {
  padding: 0.8rem 1.5rem;
  border-radius: 4px;
  font-size: 1rem;
  cursor: pointer;
  transition: all 0.3s ease;
}

.cancel-btn {
  background: transparent;
  border: 1px solid #00ff00;
  color: #00ff00;
  text-decoration: none;
}

.submit-btn {
  background: rgba(0, 255, 0, 0.2);
  border: 1px solid #00ff00;
  color: #00ff00;
}

.cancel-btn:hover, .submit-btn:hover {
  background: rgba(0, 255, 0, 0.3);
  box-shadow: 0 0 10px rgba(0, 255, 0, 0.3);
}

.avatar-upload {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-top: 0.5rem;
}

.avatar-preview {
  width: 100px;
  height: 100px;
  border-radius: 50%;
  border: 2px solid var(--primary-color);
  overflow: hidden;
  background: var(--bg-color);
  display: flex;
  align-items: center;
  justify-content: center;
}

.empty-avatar {
  background: rgba(0, 255, 0, 0.05);
}

.avatar-placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 100%;
  color: #00ff00;
  font-size: 2rem;
  font-weight: bold;
  opacity: 0.5;
}

.avatar-preview img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.upload-controls {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.upload-btn {
  display: inline-block;
  padding: 0.5rem 1rem;
  background: rgba(0, 255, 0, 0.1);
  border: 1px solid var(--primary-color);
  color: var(--primary-color);
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.3s ease;
  text-align: center;
}

.light-mode .upload-btn {
  background: rgba(0, 102, 51, 0.1);
}

.upload-btn:hover {
  background: rgba(0, 255, 0, 0.2);
  box-shadow: 0 0 10px rgba(0, 255, 0, 0.3);
}

.light-mode .upload-btn:hover {
  background: rgba(0, 102, 51, 0.2);
  box-shadow: 0 0 10px rgba(0, 102, 51, 0.3);
}

.file-name {
  color: var(--text-secondary);
  font-size: 0.9rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 200px;
}

.remove-btn {
  padding: 0.3rem 0.6rem;
  background: rgba(255, 0, 0, 0.1);
  border: 1px solid rgba(255, 0, 0, 0.3);
  color: #ff6666;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 0.9rem;
  align-self: flex-start;
}

.remove-btn:hover {
  background: rgba(255, 0, 0, 0.2);
  box-shadow: 0 0 10px rgba(255, 0, 0, 0.3);
}

.form-hint {
  color: #999;
  font-size: 0.8rem;
  margin-top: 0.5rem;
}

.required {
  color: #ff6666;
  margin-left: 2px;
}

.submit-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.submit-btn:disabled:hover {
  background: rgba(0, 255, 0, 0.2);
  box-shadow: none;
}

.price-input-container {
  position: relative;
}

.currency-label {
  position: absolute;
  right: 10px;
  top: 50%;
  transform: translateY(-50%);
  color: var(--text-secondary);
  font-size: 0.9rem;
}
</style> 