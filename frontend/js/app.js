import { api } from './api.js';
import { ui } from './ui.js';
import { theme } from './theme.js';
import { chat } from './chat.js';
import { fileHandler } from './fileHandler.js';

// 应用主模块
export const app = {
    // 全局状态
    modelsData: null,
    state: {
        currentTemplate: null,
        globalTemplates: [
            {
                type: 'prompts',
                name: 'prompts',
                subtypes: [
                    { type: 'system', name: 'system' },
                    { type: 'query', name: 'query' },
                    { type: 'followup', name: 'followup' }
                ]
            },
            {
                type: 'academic',
                name: 'academic',
                subtypes: [
                    { type: 'context', name: 'context' },
                    { type: 'value', name: 'value' },
                    { type: 'validation', name: 'validation' }
                ]
            }
        ]
    },

    // UI元素引用
    elements: {
        templateTypeSelect: null,
        templateSubtypeSelect: null
    },

    // 初始化应用
    async init() {
        try {
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
          
                this.initializeElements();
                // 初始化文件处理模块
                fileHandler.init(chat);
                await this.initTemplates();
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

    initializeElements() {
        const elements = [
            'templateTypeSelect',
            'templateSubtypeSelect',
            'templateContent'
        ];

        elements.forEach(id => {
            this.elements[id] = document.getElementById(id);
            if (!this.elements[id]) {
                throw new Error(`Required element not found: ${id}`);
            }
        });
    },

    // 初始化模板
    async initTemplates() {
        // 模板选择事件
        // 修改bindEvents方法中的模板选择事件
        this.elements.templateTypeSelect.addEventListener('change', (e) => {
            this.state.currentTemplate = e.target.value;
            this.updateSubtemplateSelectors(); // 更新子模板
            this.setTemplate(e.target.value);
        });

        this.elements.templateSubtypeSelect.addEventListener('change', (e) => {
            if (e.target.value) {
                const currentType = this.state.currentTemplate;
                const subtype = e.target.value;
                this.setTemplate(`${currentType}.${subtype}`); // 组合完整的模板标识符
               
            }
        });
        await this.fetchTemplates()
        this.updateTemplateSelectors();
        this.updateSubtemplateSelectors();
        this.updateTemplateContent();
    },
    
    // 获取模板的独立函数
    async fetchTemplates() {
        try {
            const templates = await api.getPromptTemplates();
            this.state.globalTemplates = templates; // 更新全局变量
            return templates;
        } catch (error) {
            logger.error('Failed to fetch templates:', error);
            return this.state.globalTemplates;
        }
    },
    // 更新子模板选择器
    updateSubtemplateSelectors() {
        try {
            this.elements.templateSubtypeSelect.innerHTML = '';

            const subtemplates = this.state.globalTemplates.find(template => 
                template.type === this.state.currentTemplate)?.subtypes || [];
            subtemplates.forEach(template => {
                const option = document.createElement('option');
                option.value = template.name;
                option.textContent = template.name;
                this.elements.templateSubtypeSelect.appendChild(option);
            });
            chat.setDefaultTemplate(this.state.currentTemplate);
        } catch (error) {
            logger.error('Failed to update subtemplate selectors:', error);
            ui.showNotification('更新模板子类型失败', 'error');
        }
    },
    // 更新模板选择器
    updateTemplateSelectors() {
            this.elements.templateTypeSelect.innerHTML = '';
            this.state.globalTemplates.forEach(template => {
                const option = document.createElement('option');
                option.value = template.type;
                option.textContent = template.name;
                this.elements.templateTypeSelect.appendChild(option);
            });
    
            if (this.state.globalTemplates.length > 0) {
                this.state.currentTemplate = this.state.globalTemplates[0].type;
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
       // 更新模板内容
    updateTemplateContent() {
        try {
            // 从globalTemplates中获取当前选中的模板和子模板
            const currentTemplate = this.state.globalTemplates.find(
                template => template.type === this.state.currentTemplate
            );
            
            if (currentTemplate && currentTemplate.subtypes) {
                const currentSubtype = currentTemplate.subtypes.find(
                    subtype => subtype.name === this.elements.templateSubtypeSelect.value
                );
                
                if (currentSubtype) {
                    this.elements.templateContent.value = currentSubtype.content || '';
                }
            }
        } catch (error) {
            logger.error('Failed to update template content:', error);
            ui.showNotification('更新模板内容失败', 'error');
        }
    },
    // 设置模板
    setTemplate(template) {
        try {
            this.updateTemplateContent();
            logger.info('Template set to:', template);
        } catch (error) {
            logger.error('Failed to set template:', error);
            ui.showNotification('设置模板失败', 'error');
        }
    },
};

// 初始化应用
document.addEventListener('DOMContentLoaded', () => app.init());
