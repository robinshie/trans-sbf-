import { api } from './api.js';
import { ui } from './ui.js';
import { chat } from './chat.js';
import { logger } from './logger.js';

// 文件处理模块
export const fileHandler = {
    chat: null,
    pdfViewer: null,

    // 初始化
    init(chatModule) {
        try {
            logger.info('Initializing file handler...');
            this.chat = chatModule;
            
            // 获取PDF查看器元素
            this.pdfViewer = document.getElementById('pdfViewer');
            if (!this.pdfViewer) {
                throw new Error('PDF viewer element not found');
            }

            // 初始化文件拖放区域
            const dropZone = document.getElementById('dropZone');
            const fileInput = document.getElementById('fileInput');
            
            if (!dropZone || !fileInput) {
                throw new Error('Required file handler elements not found');
            }

            // 绑定事件处理器
            dropZone.addEventListener('dragover', this.handleDragOver.bind(this));
            dropZone.addEventListener('drop', this.handleDrop.bind(this));
            fileInput.addEventListener('change', this.handleFileSelect.bind(this));
            
            logger.info('File handler initialized successfully');
        } catch (error) {
            logger.error('Failed to initialize file handler:', error);
            ui.showNotification('文件处理模块初始化失败', 'error');
        }
    },

    // 处理拖拽悬停
    handleDragOver(event) {
        event.preventDefault();
        event.stopPropagation();
        event.dataTransfer.dropEffect = 'copy';
    },

    // 处理文件拖放
    handleDrop(event) {
        event.preventDefault();
        event.stopPropagation();
        
        const files = event.dataTransfer.files;
        if (files.length > 0) {
            this.handleFile(files[0]);
        }
    },

    // 处理文件选择
    handleFileSelect(event) {
        const files = event.target.files;
        if (files.length > 0) {
            this.handleFile(files[0]);
        }
    },

    // 读取文件内容
    async readFileContent(file) {
        return new Promise((resolve, reject) => {
            const reader = new FileReader();
            
            reader.onload = () => {
                resolve(reader.result);
            };
            
            reader.onerror = (error) => {
                logger.error('File reading error:', error);
                reject(new Error('文件读取失败'));
            };
            
            if (file.type === 'application/pdf') {
                reader.readAsArrayBuffer(file);  // 使用ArrayBuffer来读取PDF文件
            } else {
                reader.readAsText(file);
            }
        });
    },

    // 处理文件
// 处理文件
async handleFile(file) {
    try {
        ui.setLoading(true);
        
        if (!file) {
            throw new Error('No file provided');
        }

        // 检查文件类型
        console.log('File type:', file.type);
        if (file.type !== 'application/pdf' && file.type !== 'text/plain') {
            throw new Error('不支持的文件类型，请上传PDF或文本文件');
        }

        // 检查文件大小（20MB限制）
        const maxSize = 20 * 1024 * 1024;
        if (file.size > maxSize) {
            throw new Error('文件太大，请上传20MB以下的文件');
        }

        // 上传文件到服务器
        const uploadResponse = await api.uploadFile(file);
        if (!uploadResponse) {
            throw new Error('文件上传失败');
        }

        // 读取文件内容用于本地显示
        const content = await this.readFileContent(file);
        
        // 如果是PDF文件，创建blob URL并显示在查看器中
        if (file.type === 'application/pdf') {
            const blob = new Blob([content], { type: 'application/pdf' });
            const blobUrl = URL.createObjectURL(blob);
            if (this.pdfViewer) {
                this.pdfViewer.src = blobUrl;
            } else {
                throw new Error('PDF viewer element not found');
            }
        }

        // 确保聊天模块可用
        if (!this.chat) {
            throw new Error('Chat module not available');
        }

        // 更新聊天模块的文件名
        if (this.chat && typeof this.chat.setPdfFile === 'function') {
            this.chat.setPdfFile(file.name);
        }

        ui.showNotification('文件处理成功', 'success');
    } catch (error) {
        logger.error('Failed to handle file:', error);
        ui.showNotification(error.message || '文件处理失败', 'error');
    } finally {
        ui.setLoading(false);
    }
}
};
