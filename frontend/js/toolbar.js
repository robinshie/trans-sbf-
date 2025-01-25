// toolbar.js
export const toolbar = {
    /**
     * 打开单个网页
     * @param {string} url - 要打开的网页地址
     * @param {string} target - 打开方式 (_blank: 新标签页, _self: 当前标签页)
     * @param {string} features - 窗口特性 (如: "width=800,height=600")
     */
    openSinglePage(url, target = '_blank', features = '') {
      if (!url) {
        console.error('URL 不能为空');
        return;
      }
      window.open(url, target, features);
    },
  
    /**
     * 打开多个网页
     * @param {string[]} urls - 要打开的网页地址数组
     * @param {string} target - 打开方式 (_blank: 新标签页, _self: 当前标签页)
     * @param {string} features - 窗口特性 (如: "width=800,height=600")
     */
    openMultiplePages(urls, target = '_blank', features = '') {
      debugger;
      if (!Array.isArray(urls) || urls.length === 0) {
        console.error('URLs 必须是非空数组');
        return;
      }
  
      urls.forEach((url) => {
        if (url) {
          window.open(url, target, features);
        } else {
          console.warn('忽略空 URL');
        }
      });
    },
  
    /**
     * 延迟打开网页
     * @param {string[]} urls - 要打开的网页地址数组
     * @param {number} delay - 每个页面之间的延迟时间 (单位：毫秒)
     * @param {string} target - 打开方式 (_blank: 新标签页, _self: 当前标签页)
     * @param {string} features - 窗口特性 (如: "width=800,height=600")
     */
    openPagesWithDelay(urls, delay = 1000, target = '_blank', features = '') {
      if (!Array.isArray(urls) || urls.length === 0) {
        console.error('URLs 必须是非空数组');
        return;
      }
  
      let index = 0;
  
      const interval = setInterval(() => {
        if (index >= urls.length) {
          clearInterval(interval);
        } else {
          this.openSinglePage(urls[index], target, features);
          index++;
        }
      }, delay);
    }
  };
  