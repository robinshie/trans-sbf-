// UI 相关函数
export const ui = {
    // 初始化UI
    init() {
        try {
            debugger;
            console.info('Initializing UI module');
            
            // 初始化通知容器
            this.notificationContainer = document.getElementById('notificationContainer');
            if (!this.notificationContainer) {
                throw new Error('Notification container not found');
            }
            
            // 初始化加载指示器
            this.loadingIndicator = document.getElementById('loadingIndicator');
            if (!this.loadingIndicator) {
                throw new Error('Loading indicator not found');
            }
            
            // 初始化消息容器
            this.messagesContainer = document.getElementById('messagesContainer');
            if (!this.messagesContainer) {
                throw new Error('Messages container not found');
            }
            
            // 初始化加载状态计数器
            this.loadingCount = 0;
            
            console.info('UI module initialized successfully');
        } catch (error) {
            console.error('Failed to initialize UI module:', error);
            this.showNotification('UI初始化失败', 'error');
        }
    },

    // 显示通知
    showNotification(message, type = 'info') {
        if (!message) {
            console.warn('Empty notification message');
            return;
        }

        try {
            // 创建通知元素
            const notification = document.createElement('div');
            notification.className = `notification ${type}`;
            
            // 创建消息文本
            const messageText = document.createElement('span');
            messageText.textContent = message;
            notification.appendChild(messageText);
            
            // 添加到容器
            if (!this.notificationContainer) {
                this.notificationContainer = document.getElementById('notificationContainer');
                if (!this.notificationContainer) {
                    throw new Error('Notification container not found');
                }
            }
            
            // 移除旧通知
            const oldNotifications = this.notificationContainer.getElementsByClassName('notification');
            if (oldNotifications.length > 2) {
                this.notificationContainer.removeChild(oldNotifications[0]);
            }
            
            // 添加新通知
            this.notificationContainer.appendChild(notification);
            
            // 自动移除
            setTimeout(() => {
                notification.classList.add('fade-out');
                setTimeout(() => {
                    if (notification.parentNode === this.notificationContainer) {
                        this.notificationContainer.removeChild(notification);
                    }
                }, 300);
            }, 3000);
        } catch (error) {
            console.error('Failed to show notification:', error);
        }
    },

    // 设置加载状态
    setLoading(loading) {
        try {
            // 获取加载指示器
            if (!this.loadingIndicator) {
                this.loadingIndicator = document.getElementById('loadingIndicator');
                if (!this.loadingIndicator) {
                    console.error('Loading indicator not found');
                    return;
                }
            }

            // 更新加载计数器
            if (loading) {
                this.loadingCount = (this.loadingCount || 0) + 1;
            } else {
                this.loadingCount = Math.max(0, (this.loadingCount || 0) - 1);
            }

            // 根据计数器更新显示状态
            const isLoading = this.loadingCount > 0;
            this.loadingIndicator.classList.toggle('active', isLoading);
            
            // 添加/移除body类，用于禁用页面交互
            document.body.classList.toggle('loading', isLoading);

        } catch (error) {
            console.error('Failed to set loading state:', error);
        }
    },

    // 添加消息到对话框
    addMessage(role, content, messageId = null) {
        try {
            if (!this.messagesContainer) {
                this.messagesContainer = document.getElementById('messagesContainer');
                if (!this.messagesContainer) {
                    throw new Error('Messages container not found');
                }
            }

            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${role}`;
            if (messageId) {
                messageDiv.id = messageId;
            }
            
            const contentDiv = document.createElement('div');
            contentDiv.className = 'message-content';
            contentDiv.textContent = content;
            
            messageDiv.appendChild(contentDiv);
            this.messagesContainer.appendChild(messageDiv);
            
            this.messagesContainer.scrollTop = this.messagesContainer.scrollHeight;
        } catch (error) {
            console.error('Failed to add message:', error);
            this.showNotification('添加消息失败', 'error');
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
                    messageDiv.scrollIntoView({ behavior: 'smooth', block: 'end' });
                }
            }
        } catch (error) {
            console.error('Failed to update message:', error);
            this.showNotification('更新消息失败', 'error');
        }
    },

    // 清空对话
    clearChat() {
        try {
            if (!this.messagesContainer) {
                this.messagesContainer = document.getElementById('messagesContainer');
                if (!this.messagesContainer) {
                    throw new Error('Messages container not found');
                }
            }

            this.messagesContainer.innerHTML = '';
            this.showNotification('对话已清空', 'success');
            return true;
        } catch (error) {
            console.error('Failed to clear chat:', error);
            this.showNotification('清空对话失败', 'error');
            return false;
        }
    }
};
