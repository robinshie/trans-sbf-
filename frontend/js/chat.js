import { api } from './api.js';
import { ui } from './ui.js';
import { logger } from './logger.js';

// 聊天模块
export const chat = {
    // 状态
    isProcessing: false,
    currentModel: null,
    currentTemplate: null,
    currentPdfFile: null,
    messageHistory: [],

    // 初始化
    init() {
        try {
            logger.info('Initializing chat module');
            debugger;
            // 获取必要的DOM元素




            
            this.userInput = document.getElementById('userInput');
            this.chatMessages = document.getElementById('messagesContainer');
            this.sendButton = document.getElementById('sendButton');
            this.templateTypeSelect = document.getElementById('templateTypeSelect');
            this.templateSubtypeSelect = document.getElementById('templateSubtypeSelect');
            this.exportButton = document.getElementById('exportButton');
            this.clearButton = document.getElementById('clearButton');
            
            if (!this.userInput || !this.chatMessages || !this.sendButton || 
                !this.templateTypeSelect || !this.templateSubtypeSelect || 
                !this.exportButton || !this.clearButton) {
                throw new Error('Required chat elements not found');
            }

            // 设置默认模型
            this.setModel({
                id: 'qwen2.5:latest',
                name: 'qwen2.5:latest',
                manufacturer: 'ollama',
                description: 'Ollama的Qwen2.5模型，适合一般对话和翻译任务'
            });

            // 绑定事件处理器
            this.sendButton.addEventListener('click', () => this.sendMessage());
            
            // 处理输入框的回车事件
            this.userInput.addEventListener('keydown', (e) => {
                // 检查是否按下了Enter键
                if (e.key === 'Enter') {
                    // 如果按住了Shift键，添加换行
                    if (e.shiftKey) {
                        return;  // 让浏览器处理换行
                    }
                    // 否则发送消息
                    e.preventDefault();  // 阻止默认的换行行为
                    this.sendMessage();
                }
            });

            // 绑定模板选择事件
            this.templateTypeSelect.addEventListener('change', (e) => {
                this.setTemplate(e.target.value);
            });

            this.templateSubtypeSelect.addEventListener('change', (e) => {
                if (e.target.value) {
                    this.setTemplate(e.target.value);
                }
            });

            this.exportButton.addEventListener('click', () => this.exportChat());
            this.clearButton.addEventListener('click', () => this.clearChat());

            // 初始化模板选择器
            this.initializeTemplateSelectors();

            logger.info('Chat module initialized successfully');
        } catch (error) {
            logger.error('Failed to initialize chat module:', error);
            ui.showNotification('聊天模块初始化失败', 'error');
        }
    },

    // 初始化模板选择器
    async initializeTemplateSelectors() {
        try {
            debugger;
            // 从API获取模板列表
            const templates = await api.getPromptTemplates();
            
            // 更新模板选择器
            const templateSelector = document.getElementById('templateTypeSelect');
            templateSelector.innerHTML = ''; // 清空现有选项
            
            // 添加模板选项
            templates.forEach(template => {
                const option = document.createElement('option');
                option.value = template.type;
                option.textContent = template.name;
                templateSelector.appendChild(option);
            });

            // 设置默认选项
            if (templates.length > 0) {
                this.currentTemplate = templates[0].type;
            }
        } catch (error) {
            logger.error('Failed to initialize templates:', error);
            // 使用默认模板作为后备
            const defaultTemplates = [
                { type: 'query', name: '普通对话' },
                { type: 'translate', name: '翻译' },
                { type: 'summarize', name: '总结' }
            ];
            
            const templateSelector = document.getElementById('templateTypeSelect');
            templateSelector.innerHTML = '';
            defaultTemplates.forEach(template => {
                const option = document.createElement('option');
                option.value = template.type;
                option.textContent = template.name;
                templateSelector.appendChild(option);
            });
            
            this.currentTemplate = 'query';
        }
    },

    // 设置PDF文件
    setPdfFile(filename) {
        try {
            logger.info('Setting PDF file:', filename);
            this.currentPdfFile = filename;
            this.clearChat(); // 清空聊天记录
        } catch (error) {
            logger.error('Failed to set PDF file', error);
            ui.showNotification('设置PDF文件失败', 'error');
        }
    },

    // 设置当前模型
    setModel(model) {
        try {
            if (!model || typeof model !== 'object') {
                logger.error('Invalid model data: model is null or not an object');
                throw new Error('Invalid model data');
            }

            if (!model.name) {
                logger.error('Invalid model data: missing name');
                throw new Error('Invalid model data');
            }

            // 如果没有id，使用name作为id
            const modelData = {
                id: model.id || model.name,
                name: model.name,
                manufacturer: model.manufacturer || 'Unknown',
                description: model.description || ''
            };
            
            logger.info('Setting model:', modelData);
            this.currentModel = modelData;
            logger.debug('Current model after setting:', this.currentModel);
            
            // 更新UI显示
            const modelInfo = document.getElementById('modelInfo');
            if (modelInfo) {
                modelInfo.textContent = `已选择: ${modelData.name}`;
            }

            ui.showNotification(`已选择模型: ${modelData.name}`, 'success');
        } catch (error) {
            logger.error('Failed to set model', error);
            this.currentModel = null;
            ui.showNotification('设置模型失败', 'error');
        }
    },

    // 设置当前模板
    setTemplate(template) {
        try {
            this.currentTemplate = template;
            logger.info('Template set to:', template);
        } catch (error) {
            logger.error('Failed to set template:', error);
            ui.showNotification('设置模板失败', 'error');
        }
    },

    // 发送消息
    async sendMessage() {
        try {
            debugger;
            if (this.isProcessing) {
                logger.warn('Message processing in progress, please wait');
                return;
            }

            const message = this.userInput.value.trim();

            if (!message) {
                logger.warn('Empty message, ignoring');
                return;
            }

            this.isProcessing = true;
            this.userInput.value = '';
            
            // 添加用户消息到界面
            this.addMessage('user', message);

            // 准备请求数据
            const requestData = {
                message: message,
                model_choice: {
                    manufacturer: this.currentModel.manufacturer || 'openai',
                    model: this.currentModel.name || 'gpt-3.5-turbo'
                },
                history: this.messageHistory.map(msg => ({
                    role: msg.role,
                    content: msg.content
                })),
                prompt_type: this.currentTemplate || "query"
            };

            // 如果有PDF文件，添加到请求中
            if (this.currentPdfFile) {
                requestData.pdf_filename = this.currentPdfFile;
            }

            logger.info('Sending request data:', requestData);

            try {
                // 获取流式响应
                const stream = await api.sendChatMessage(requestData);
                
                if (!stream) {
                    throw new Error('No response stream received');
                }

                // 创建响应消息容器
                const responseMessageId = this.addMessage('assistant', '');
                
                try {
                    const reader = stream.getReader();
                    const decoder = new TextDecoder();
                    let responseText = '';

                    while (true) {
                        const { done, value } = await reader.read();
                        
                        if (done) {
                            break;
                        }

                        // 解码并添加新的文本
                        const text = decoder.decode(value, { stream: true });
                        responseText += text;
                        
                        // 更新消息内容
                        this.updateMessage(responseMessageId, responseText);
                    }
                } catch (error) {
                    logger.error('Error reading stream:', error);
                    throw new Error('读取响应流时出错');
                }
            } catch (error) {
                logger.error('Failed to process chat message:', error);
                this.addMessage('error', `发送消息失败: ${error.message}`);
            }
        } catch (error) {
            logger.error('Error in sendMessage:', error);
            ui.showNotification(error.message || '发送消息失败', 'error');
        } finally {
            this.isProcessing = false;
        }
    },

    // 添加消息到界面
    addMessage(role, content) {
        try {
            console.log('Adding message with role:', role);
            console.log('Content starts with:', content.substring(0, 100));
            
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${role}-message`;
            
            const contentDiv = document.createElement('div');
            contentDiv.className = 'message-content';
            
            // 如果是 PDF 文件，创建一个 iframe 来显示
            if (content.startsWith('data:application/pdf')) {
                console.log('Detected PDF content, creating iframe');
                const iframe = document.createElement('iframe');
                iframe.src = content;
                iframe.style.width = '100%';
                iframe.style.height = '500px';
                iframe.style.border = 'none';
                contentDiv.appendChild(iframe);
            } else {
                console.log('Using regular text content');
                // 对于普通文本，使用 innerHTML
                contentDiv.innerHTML = content;
            }
            
            messageDiv.appendChild(contentDiv);
            this.chatMessages.appendChild(messageDiv);
            
            // 滚动到底部
            this.chatMessages.scrollTop = this.chatMessages.scrollHeight;

            // 添加到历史记录
            this.messageHistory.push({ role, content });

            // 返回消息ID（用于更新流式响应）
            return messageDiv.id = `msg-${Date.now()}`;
        } catch (error) {
            logger.error('Failed to add message:', error);
            ui.showNotification('添加消息失败', 'error');
            console.error('Error details:', error);
        }
    },

    // 更新消息内容
    updateMessage(messageId, content) {
        try {
            const messageDiv = document.getElementById(messageId);
            if (messageDiv) {
                const contentDiv = messageDiv.querySelector('.message-content');
                if (contentDiv) {
                    contentDiv.textContent = content;
                    // 更新历史记录中的最后一条消息
                    if (this.messageHistory.length > 0) {
                        this.messageHistory[this.messageHistory.length - 1].content = content;
                    }
                }
            }
        } catch (error) {
            logger.error('Failed to update message:', error);
        }
    },

    // 导出聊天记录
    exportChat() {
        try {
            logger.info('Exporting chat history');
            
            const chatContent = this.messageHistory.map(msg => 
                `${msg.role === 'user' ? '用户' : 'AI'}: ${msg.content}`
            ).join('\n\n');
            
            const blob = new Blob([chatContent], { type: 'text/plain;charset=utf-8' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `chat_export_${new Date().toISOString()}.txt`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
            
            logger.info('Chat history exported successfully');
            ui.showNotification('聊天记录导出成功', 'success');
        } catch (error) {
            logger.error('Failed to export chat', error);
            ui.showNotification('导出聊天记录失败', 'error');
        }
    },

    // 清空聊天记录
    clearChat() {
        try {
            logger.info('Clearing chat history');
            
            const messagesContainer = document.getElementById('messagesContainer');
            messagesContainer.innerHTML = '';
            this.messageHistory = [];
            
            logger.info('Chat history cleared successfully');
            ui.showNotification('聊天记录已清空', 'success');
        } catch (error) {
            logger.error('Failed to clear chat', error);
            ui.showNotification('清空聊天记录失败', 'error');
        }
    }
};
