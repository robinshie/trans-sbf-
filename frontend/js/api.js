import { ui } from './ui.js';
import { logger } from './logger.js';

// API 配置
const API_BASE = 'http://localhost:8000/api/v1';

// 日志级别
const LogLevel = {
    ERROR: 'error',
    WARN: 'warn',
    INFO: 'info',
    DEBUG: 'debug'
};

// API 请求函数
export const api = {
    // 获取可用模型列表
    async getModels() {
        try {
            logger.info('Fetching available models');
            
            const response = await fetch(`${API_BASE}/models`);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            logger.debug('Models fetched:', data);
            return data;
        } catch (error) {
            logger.error('Failed to fetch models:', error);
            throw new Error('获取模型列表失败');
        }
    },

    // 获取模板列表
    async getPromptTemplates() {
        try {
            const response = await fetch(`${API_BASE}/prompt/templates`);
            if (!response.ok) {
                throw new Error('Failed to fetch templates');
            }
            return await response.json();
        } catch (error) {
            logger.error('API Error - Failed to fetch templates:', error);
            throw error;
        }
    },

        // 上传文件
    async uploadFile(file) {
            try {
                const formData = new FormData();
                formData.append('file', file);
    
                const response = await fetch(`${API_BASE}/upload`, {
                    method: 'POST',
                    body: formData
                });
    
                if (!response.ok) {
                    throw new Error(`Upload failed with status: ${response.status}`);
                }
    
                return await response.json();
            } catch (error) {
                logger.error('Failed to upload file:', error);
                throw error;
            }
    },

    // 发送聊天消息
    async sendChatMessage(data) {
        try {
            logger.info('Sending chat message:', data);
            
            // 验证请求数据
            if (!data.message || !data.model_choice) {
                throw new Error('Invalid request data: missing required fields');
            }

            if (!data.model_choice.manufacturer || !data.model_choice.model) {
                throw new Error('Invalid model choice data');
            }
            
            const response = await fetch(`${API_BASE}/chat/stream`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            });
            
            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.message || `Server error: ${response.status}`);
            }
            
            if (!response.body) {
                throw new Error('Server response has no body');
            }
            
            return response.body;
        } catch (error) {
            logger.error('Failed to send chat message:', error);
            throw error;
        }
    }
};
