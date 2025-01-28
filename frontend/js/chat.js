import { api } from './api.js';
import { ui } from './ui.js';
import { logger } from './logger.js';
import { toolbar } from './toolbar.js';
// 绑定事件
let isEventsBound = false;
// 聊天模块
export const chat = {
    // 状态管理
    state: {
        isProcessing: false,
        currentModel: null,
        currentTemplate: null,
        currentPdfFile: null,
        messageHistory: [],
        streamController: null,
    },

    // UI元素引用
    elements: {
        userInput: null,
        messagesContainer: null,
        sendButton: null,
        exportButton: null,
        clearButton: null,
        outtoolButton: null,
        modelInfo: null
    },
    

    // 初始化
    async init() {
        try {
            logger.info('Initializing chat module');
            this.initializeElements();
            await this.initializeModel();
            this.bindEvents();
            logger.info('Chat module initialized successfully');
         
        } catch (error) {
            logger.error('Failed to initialize chat module:', error);
            ui.showNotification('聊天模块初始化失败', 'error');
        }
    },

    // 初始化UI元素
    initializeElements() {
        const elements = [
            'userInput',
            'messagesContainer',
            'sendButton',
            'exportButton',
            'clearButton',
            'outtoolButton',
            'modelInfo'
        ];

        elements.forEach(id => {
            this.elements[id] = document.getElementById(id);
            if (!this.elements[id]) {
                throw new Error(`Required element not found: ${id}`);
            }
        });
    },

    // 初始化默认模型
    async initializeModel() {
        const defaultModel = {
            id: 'qwen2.5:latest',
            name: 'qwen2.5:latest',
            manufacturer: 'ollama',
            description: 'Ollama的Qwen2.5模型，适合一般对话和翻译任务'
        };
        await this.setModel(defaultModel);
    },

    bindEvents() {
        if (isEventsBound) return; // 避免重复绑定
        isEventsBound = true;
    
        this.elements.sendButton.addEventListener('click', () => this.sendMessage());
        this.elements.userInput.addEventListener('keydown', this.handleInputKeydown.bind(this));
        this.elements.exportButton.addEventListener('click', () => this.exportChat());
        this.elements.clearButton.addEventListener('click', () => this.clearChat());
        this.elements.outtoolButton.addEventListener('click', () => this.outindexChat());
    }
    ,

    // 处理输入框按键事件
    handleInputKeydown(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            this.sendMessage();
        }
    },
    // 使用默认模板
    setDefaultTemplate(template = 'prompts') {
        this.state.currentTemplate = template;
    },


    // 设置PDF文件
    setPdfFile(filename) {
        try {
            if (this.state.isProcessing) {
                logger.warn('Message processing in progress');
                return;
            }
            this.state.isProcessing = true;
            logger.info('Setting PDF file:', filename);
            this.state.currentPdfFile = filename;
        } catch (error) {
            logger.error('Failed to set PDF file', error);
            ui.showNotification('设置PDF文件失败', 'error');
        }finally{
            this.state.isProcessing = false;
        }
    },

    outindexChat() {
        if (this.state.isProcessing) {
            logger.warn('Message processing in progress');
            return;
        }
        try {
            this.state.isProcessing = true;
            this.updateUIState(true, this.elements.outtoolButton);
            toolbar.openMultiplePages([
                `./readmode.html`,
                `https://www.google.com/`,
                `https://translate.google.com/?hl=zh-cn&sl=auto&tl=zh-CN&op=translate`,
                `https://chatgpt.com/`
            ]);
    
            ui.showNotification('已切换到外链模式', 'success');
        } catch (error) {
            logger.error('Failed to switch to external mode', error);
            ui.showNotification('切换到外链模式失败', 'error');
        } finally {
            // Any cleanup or finalization code can go here
            this.state.isProcessing = false; // Ensure isProcessing is reset
            this.updateUIState(false, this.elements.outtoolButton);
        }
    },
    // 设置模型
    async setModel(model) {
        try {
            if (!model?.name) {
                throw new Error('Invalid model data');
            }

            const modelData = {
                id: model.id || model.name,
                name: model.name,
                manufacturer: model.manufacturer || 'Unknown',
                description: model.description || ''
            };

            this.state.currentModel = modelData;
            this.updateModelInfo(modelData);
            ui.showNotification(`已选择模型: ${modelData.name}`, 'success');
        } catch (error) {
            logger.error('Failed to set model', error);
            ui.showNotification('设置模型失败', 'error');
        }
    },

    // 更新模型信息显示
    updateModelInfo(modelData) {
        if (this.elements.modelInfo) {
            this.elements.modelInfo.textContent = `已选择: ${modelData.name}`;
        }
    },
    // 发送消息
    async sendMessage() {
        debugger;
        if (this.state.isProcessing) {
            logger.warn('Message processing in progress');
            return;
        }

        const message = this.elements.userInput.value.trim();
        if (!message) return;

        try {
            this.state.isProcessing = true;
            this.updateUIState(true, this.elements.sendButton);
            this.elements.userInput.value = '';

            const messageId = this.addMessage('user', message);
            await this.processMessage(message, messageId);
        } catch (error) {
            logger.error('Error in sendMessage:', error);
            this.addMessage('error', `发送消息失败: ${error.message}`);
        } finally {
            this.state.isProcessing = false;
            this.updateUIState(false, this.elements.sendButton);
        }
    },

    // 处理消息
    async processMessage(message, messageId) {
        const requestData = this.prepareRequestData(message);
        const stream = await api.sendChatMessage(requestData);
        
        if (!stream) {
            throw new Error('No response stream received');
        }

        const responseMessageId = this.addMessage('system', '');
        await this.handleStreamResponse(stream, responseMessageId);
    },

    // 准备请求数据
    prepareRequestData(message) {
        const requestData = {
            message,
            model_choice: {
                manufacturer: this.state.currentModel.manufacturer,
                model: this.state.currentModel.name
            },
            history: this.state.messageHistory.slice(-5).map(msg => ({
                role: msg.role,
                content: msg.content
            })),
            prompt_type: this.state.currentTemplate
        };

        if (this.state.currentPdfFile) {
            requestData.pdf_context = this.state.currentPdfFile;
        }

        return requestData;
    },

    // 处理流式响应
    async handleStreamResponse(stream, messageId) {
        const reader = stream.getReader();
        const decoder = new TextDecoder();
        let responseText = '';

        try {
            while (true) {
                const { done, value } = await reader.read();
                if (done) break;
                
                responseText += decoder.decode(value, { stream: true });
                this.updateMessage(messageId, responseText);
            }
        } catch (error) {
            logger.error('Error reading stream:', error);
            throw new Error('读取响应流时出错');
        }
    },

    // 添加消息到界面
    addMessage(role, content, title = '') {
        try {
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${role}`; // Use role for styling
            messageDiv.id = `msg-${Date.now()}`;
    
            // Create a title div if a title is provided
            if (title) {
                const titleDiv = document.createElement('div');
                titleDiv.className = 'message-title'; // Add a class for the title
                titleDiv.textContent = title; // Set the title text
                messageDiv.appendChild(titleDiv); // Append title to the message div
            }
    
            const contentDiv = document.createElement('div');
            contentDiv.className = 'message-content'; // Use existing class for content
    
            // Add an Emoji based on the role
            let emoji = '';
            if (role === 'user') {
                emoji = '👤'; // User Emoji
            } else if (role === 'ai') {
                emoji = '🤖'; // AI Emoji
            } else if (role === 'system') {
                emoji = '🤖'; // System Emoji
            }
    
            // Create a span for the emoji
            const emojiSpan = document.createElement('span');
            emojiSpan.textContent = emoji;
            emojiSpan.className = 'emoji'; // Optional: add a class for styling
            // Check if the content is a PDF
            if (content.startsWith('data:application/pdf')) {
                const iframe = this.createPdfIframe(content);
                contentDiv.appendChild(iframe);
            } else {
                contentDiv.innerHTML = content; // Set the content
            }
    
            // Append the emoji and content to the message div
            messageDiv.appendChild(emojiSpan);
            messageDiv.appendChild(contentDiv); // Append content to the message div
            this.elements.messagesContainer.appendChild(messageDiv); // Append message div to the container
            this.scrollToBottom();
            this.state.messageHistory.push({ role, content });
    
            return messageDiv.id;
        } catch (error) {
            logger.error('Failed to add message:', error);
            ui.showNotification('添加消息失败', 'error');
        }
    },

    // 创建PDF iframe
    createPdfIframe(content) {
        const iframe = document.createElement('iframe');
        iframe.src = content;
        iframe.style.width = '100%';
        iframe.style.height = '500px';
        iframe.style.border = 'none';
        return iframe;
    },

    // 更新消息内容
    updateMessage(messageId, content) {
        try {
            const messageDiv = document.getElementById(messageId);
            if (messageDiv) {
                const contentDiv = messageDiv.querySelector('.message-content');
                if (contentDiv) {
                    contentDiv.textContent = content;
                    if (this.state.messageHistory.length > 0) {
                        this.state.messageHistory[this.state.messageHistory.length - 1].content = content;
                    }
                }
            }
        } catch (error) {
            logger.error('Failed to update message:', error);
        }
    },

    // 滚动到底部
    scrollToBottom() {
        this.elements.messagesContainer.scrollTop = this.elements.messagesContainer.scrollHeight;
    },

    // 更新UI状态
    updateUIState(processing, button) {
        button.disabled = processing;
        button.disabled = processing;
    },

    // 导出聊天记录
    exportChat() {
        try {
            if (this.state.isProcessing) {
                logger.warn('Message processing in progress');
                return;
            }    
            this.state.isProcessing = true;
            this.updateUIState(true, this.elements.exportButton);
    
            // Get the HTML content of the messages container
            const messagesContainer = document.getElementById('messagesContainer');
            const chatContent = messagesContainer.innerHTML; // Get the inner HTML
    
            // Fetch the CSS styles and then create the blob
            this.getStyles().then(styles => {
                const blob = new Blob([`<html><head>${styles}</head><body><div class="messages-container">${chatContent}</div></body></html>`], { type: 'text/html;charset=utf-8' });
                const url = URL.createObjectURL(blob);
                
                const a = document.createElement('a');
                a.href = url;
                a.download = `chat_export_${new Date().toISOString()}.html`;
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
                URL.revokeObjectURL(url);
    
                ui.showNotification('聊天记录导出成功', 'success');
            });
        } catch (error) {
            logger.error('Failed to export chat', error);
            ui.showNotification('导出聊天记录失败', 'error');
        } finally {
            this.state.isProcessing = false;
            this.updateUIState(false, this.elements.exportButton);
        }
    },
    
    async getStyles() {
        const files = ['/styles/animations.css', '/styles/components.css', '/styles/layout.css', '/styles/variables.css'];
        const cssPromises = files.map(file => fetch(file).then(response => response.text()));
        const cssTexts = await Promise.all(cssPromises);
        return `<style>${cssTexts.join('\n')}</style>`;
    },

    // 清空聊天记录
    clearChat() {
        try {
            if (this.state.isProcessing) {
                logger.warn('Message processing in progress');
                return;
            }    
            this.state.isProcessing = true;
            this.updateUIState(true, this.elements.clearButton);
            this.elements.messagesContainer.innerHTML = '';
            this.state.messageHistory = [];
            ui.showNotification('聊天记录已清空', 'success');
        } catch (error) {
            logger.error('Failed to clear chat', error);
            ui.showNotification('清空聊天记录失败', 'error');
        }finally{
            this.state.isProcessing = false;
            this.updateUIState(false, this.elements.clearButton);
        }
    },
    
};

// 导出聊天模块
export default chat;