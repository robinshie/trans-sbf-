// 日志工具模块
export const logger = {
    error: (message, error) => {
        console.error(`[Error] ${message}`, error);
    },
    warn: (message, data) => {
        console.warn(`[Warning] ${message}`, data);
    },
    info: (message, data) => {
        console.info(`[Info] ${message}`, data);
    },
    debug: (message, data) => {
        console.debug(`[Debug] ${message}`, data);
    }
};
