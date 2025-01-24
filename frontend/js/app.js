import { api } from './api.js';
import { ui } from './ui.js';
import { theme } from './theme.js';
import { chat } from './chat.js';
import { fileHandler } from './fileHandler.js';

// 应用主模块
export const app = {
    // 全局状态
    modelsData: null,
    templateTypes: null,

    // 初始化应用
    async init() {
        try {
            debugger;
            console.log('Initializing application...');
            
            // 显示加载状态
            ui.setLoading(true);
            
            try {
                // 初始化UI和主题
                ui.init();
                if (typeof theme !== 'undefined') {
                    theme.init();
                }
                
                // 初始化聊天模块
                chat.init();
                
                // 获取并初始化模型数据
                await this.loadModels();
                
                // 初始化文件处理模块
                fileHandler.init(chat);
                
                console.log('Application initialized successfully');
                ui.showNotification('应用初始化成功', 'success');
            } catch (error) {
                console.error('Failed to initialize components:', error);
                ui.showNotification('初始化组件失败', 'error');
                throw error;
            } finally {
                ui.setLoading(false);
            }
        } catch (error) {
            console.error('Critical initialization error:', error);
            ui.showNotification('应用初始化失败', 'error');
        }
    },

    // 加载模型数据
    async loadModels() {
        try {
            console.log('Loading models...');
            
            // 尝试从API获取模型数据
            try {
                const modelsResponse = await api.getModels();
                if (modelsResponse && modelsResponse.models && Array.isArray(modelsResponse.models)) {
                    // 确保每个模型都有必要的字段
                    this.modelsData = modelsResponse.models.map(model => ({
                        id: model.name, // 使用name作为id
                        name: model.name,
                        manufacturer: model.manufacturer,
                        description: model.description
                    }));
                }
            } catch (error) {
                console.warn('Failed to load models from API, using default models:', error);
                // 使用默认模型数据
                this.modelsData = [
                    {
                        id: 'gpt-3.5-turbo',
                        name: 'GPT-3.5 Turbo',
                        manufacturer: 'OpenAI',
                        description: 'GPT-3.5 Turbo模型'
                    },
                    {
                        id: 'gpt-4',
                        name: 'GPT-4',
                        manufacturer: 'OpenAI',
                        description: 'GPT-4模型'
                    }
                ];
            }
            
            if (!this.modelsData || !Array.isArray(this.modelsData) || this.modelsData.length === 0) {
                throw new Error('No valid models data available');
            }
            
            // 初始化选择器
            await this.initializeModelSelectors();
            
            // 默认选择第一个模型
            const firstModel = this.modelsData[0];
            if (firstModel) {
                console.log('Setting default model:', firstModel);
                chat.setModel(firstModel);
                
                // 更新UI选择
                const manufacturerSelect = document.getElementById('manufacturerSelect');
                const modelSelect = document.getElementById('modelSelect');
                
                if (manufacturerSelect && modelSelect) {
                    // 设置制造商
                    manufacturerSelect.value = firstModel.manufacturer;
                    manufacturerSelect.dispatchEvent(new Event('change'));
                    
                    // 等待DOM更新后设置模型
                    await new Promise(resolve => setTimeout(resolve, 100));
                    modelSelect.value = firstModel.id;
                    modelSelect.dispatchEvent(new Event('change'));
                }
            }
            
            console.log('Models loaded and initialized successfully');
        } catch (error) {
            console.error('Failed to load models:', error);
            ui.showNotification('加载模型失败', 'error');
            throw error;
        }
    },

    // 初始化模型选择器
    initializeModelSelectors() {
        if (!this.modelsData || !Array.isArray(this.modelsData)) {
            console.error('Invalid models data');
            return;
        }

        const manufacturerSelect = document.getElementById('manufacturerSelect');
        const modelSelect = document.getElementById('modelSelect');
        
        if (!manufacturerSelect || !modelSelect) {
            console.error('Model select elements not found');
            return;
        }

        // 获取所有厂商
        const manufacturers = [...new Set(this.modelsData.map(model => model.manufacturer))];
        
        // 初始化厂商选择器
        manufacturerSelect.innerHTML = '<option value="">选择模型厂商</option>';
        manufacturers.forEach(manufacturer => {
            const option = document.createElement('option');
            option.value = manufacturer;
            option.textContent = manufacturer;
            manufacturerSelect.appendChild(option);
        });

        // 添加厂商选择事件监听
        manufacturerSelect.addEventListener('change', (event) => {
            const selectedManufacturer = event.target.value;
            
            // 清空并禁用模型选择器
            modelSelect.innerHTML = '<option value="">选择模型</option>';
            
            if (selectedManufacturer) {
                // 获取选中厂商的所有模型
                const models = this.modelsData.filter(model => model.manufacturer === selectedManufacturer);
                
                // 填充模型选择器
                models.forEach(model => {
                    const option = document.createElement('option');
                    option.value = model.id;
                    option.textContent = model.name;
                    modelSelect.appendChild(option);
                });
                
                modelSelect.disabled = false;
            } else {
                modelSelect.disabled = true;
            }
        });

        // 添加模型选择事件监听
        modelSelect.addEventListener('change', (event) => {
            const selectedModelId = event.target.value;
            if (selectedModelId) {
                const selectedModel = this.modelsData.find(model => model.id === selectedModelId);
                if (selectedModel) {
                    chat.setModel(selectedModel);
                    // 更新模型信息显示
                    const modelInfo = document.getElementById('modelInfo');
                    if (modelInfo) {
                        modelInfo.textContent = `已选择: ${selectedModel.name}`;
                    }
                }
            }
        });
    },

    // 初始化模板选择器
    initializeTemplateSelectors() {
        if (!this.templateTypes) {
            console.error('Template types not initialized');
            return;
        }
        debugger;

        const templateTypeSelect = document.getElementById('templateTypeSelect');
        const templateSubtypeSelect = document.getElementById('templateSubtypeSelect');
        const templateContent = document.getElementById('templateContent');
        
        if (!templateTypeSelect || !templateSubtypeSelect || !templateContent) {
            console.error('Template elements not found');
            return;
        }
        
        // 初始化模板类型选择器
        templateTypeSelect.innerHTML = '<option value="">选择模板类型</option>';
        Object.entries(this.templateTypes).forEach(([typeKey, typeData]) => {
            const option = document.createElement('option');
            option.value = typeKey;
            option.textContent = typeData.name;
            templateTypeSelect.appendChild(option);
        });
        
        // 监听模板类型变化
        templateTypeSelect.addEventListener('change', (e) => {
            const typeKey = e.target.value;
            this.updateTemplateSubtypes(typeKey);
        });
        
        // 监听模板子类型变化
        templateSubtypeSelect.addEventListener('change', (e) => {
            const typeKey = templateTypeSelect.value;
            const subtypeKey = e.target.value;
            this.updateTemplateContent(typeKey, subtypeKey);
        });
    },

    // 更新模板子类型
    updateTemplateSubtypes(typeKey) {
        const templateSubtypeSelect = document.getElementById('templateSubtypeSelect');
        const templateContent = document.getElementById('templateContent');
        
        if (!templateSubtypeSelect || !templateContent) {
            console.error('Template elements not found');
            return;
        }
        
        templateSubtypeSelect.innerHTML = '<option value="">选择模板子类型</option>';
        templateContent.value = '';
        
        if (!typeKey || !this.templateTypes[typeKey]) return;
        
        const subtypes = this.templateTypes[typeKey].subtypes;
        subtypes.forEach((subtype, index) => {
            const option = document.createElement('option');
            option.value = index;
            option.textContent = subtype.name;
            templateSubtypeSelect.appendChild(option);
        });
    },

    // 更新模板内容
    updateTemplateContent(typeKey, subtypeKey) {
        const templateContent = document.getElementById('templateContent');
        
        if (!templateContent) {
            console.error('Template content element not found');
            return;
        }
        
        if (!typeKey || !subtypeKey || !this.templateTypes[typeKey]) {
            templateContent.value = '';
            return;
        }
        
        const subtypes = this.templateTypes[typeKey].subtypes;
        const template = subtypes[subtypeKey];
        if (template) {
            templateContent.value = template.content || '';
            
            // 通知chat模块模板已更新
            if (chat && typeof chat.setTemplate === 'function') {
                chat.setTemplate(template.content);
            }
        }
    }
};

// 初始化应用
document.addEventListener('DOMContentLoaded', () => app.init());
