class PaginationManager {
    constructor(options) {
        // 默認配置
        const defaultOptions = {
            // 初始狀態
            initialPage: 1,
            totalPages: 1,
            noDataErrorMessage: "Error: No Data!",

            // DOM 元素選擇器或元素
            elements: {
                container: '#dataContainer',
                list: '#dataList',
                prevButton: '#prevButton',
                nextButton: '#nextButton',
                pageInput: '#pageInput',
                totalPages: '#totalPages',
                resultMesssage: '#resultMesssage'
            },

            // 數據相關函數
            fetchData: async (page) => {
                // 默認的獲取數據邏輯
                return {
                    items: Array(5).fill(null).map((_, index) => ({
                        id: index + 1,
                        title: `Item ${page}-${index + 1}`
                    })),
                    totalPages: 22
                };
            },

            // 自定義渲染函數
            renderItem: (item) => {
                const li = document.createElement('li');
                li.className = 'data-item';
                li.textContent = item.title;
                return li;
            },

            // 自定義加載中顯示
            renderLoading: () => {
                const div = document.createElement('div');
                div.className = 'loading';
                return div;
            },

            // 自定義錯誤顯示
            renderError: (error) => {
                const div = document.createElement('div');
                div.className = 'error';
                div.textContent = error;
                return div;
            },

            // 事件回調
            onPageChange: null,
            onError: null,
            onDataLoaded: null
        };

        // 保存事件處理函數的引用
        this.eventHandlers = {
            prev: null,
            next: null,
            input: null
        };

        // 合併用戶配置和默認配置
        this.options = { ...defaultOptions, ...options };

        // 初始化狀態
        this.currentPage = this.options.initialPage;
        this.totalPages = this.options.totalPages;
        this.isLoading = false;
        this.responseData = null;

        // 初始化 DOM 元素
        this.initializeElements();

        // 綁定事件
        this.bindEvents();

        // 初始加載數據
        this.fetchData(this.currentPage);
    }

    restore(){
        // 初始化 DOM 元素
        this.initializeElements();

        // 綁定事件
        this.bindEvents();

        // 復原並重新render資料
        this.restoreData()
    }

    initializeElements() {
        // 獲取 DOM 元素
        const getElement = (selectorOrElement) => {
            if (typeof selectorOrElement === 'string') {
                return document.querySelector(selectorOrElement);
            }
            return selectorOrElement;
        };

        const { elements } = this.options;
        this.elements = {
            container: getElement(elements.container),
            list: getElement(elements.list),
            prevButton: getElement(elements.prevButton),
            nextButton: getElement(elements.nextButton),
            pageInput: getElement(elements.pageInput),
            totalPages: getElement(elements.totalPages),
            resultMesssage: getElement(elements.resultMesssage),
        };

        // 驗證必要元素是否存在
        Object.entries(this.elements).forEach(([key, element]) => {
            if (!element) {
                throw new Error(`Required element "${key}" not found`);
            }
        });
    }

    bindEvents() {
        // 創建事件處理函數並保存引用
        this.eventHandlers.prev = () => {
            if (this.currentPage > 1) {
                this.currentPage--;
                this.updateUI();
                this.fetchData(this.currentPage);
            }
        };

        this.eventHandlers.next = () => {
            if (this.currentPage < this.totalPages) {
                this.currentPage++;
                this.updateUI();
                this.fetchData(this.currentPage);
            }
        };

        this.eventHandlers.input = (e) => {
            const newPage = parseInt(e.target.value);
            if (newPage >= 1 && newPage <= this.totalPages) {
                this.currentPage = newPage;
                this.fetchData(this.currentPage);
            } else {
                e.target.value = this.currentPage;
            }
        };

        // 添加事件監聽器
        this.elements.prevButton.addEventListener('click', this.eventHandlers.prev);
        this.elements.nextButton.addEventListener('click', this.eventHandlers.next);
        this.elements.pageInput.addEventListener('change', this.eventHandlers.input);
    }

    unbindEvents() {
        // 移除所有事件監聽器
        if (this.eventHandlers.prev) {
            this.elements.prevButton.removeEventListener('click', this.eventHandlers.prev);
        }

        if (this.eventHandlers.next) {
            this.elements.nextButton.removeEventListener('click', this.eventHandlers.next);
        }

        if (this.eventHandlers.input) {
            this.elements.pageInput.removeEventListener('change', this.eventHandlers.input);
        }

        // 清空事件處理函數引用
        this.eventHandlers = {
            prev: null,
            next: null,
            input: null
        };
    }

    // 添加銷毀方法
    destroy() {
        // 解除事件綁定
        this.unbindEvents();

        // 清空數據
        this.elements.list.innerHTML = '';
        this.elements.container.innerHTML = '';

        // 重置狀態
        this.currentPage = 1;
        this.isLoading = false;

        // 清空元素引用
        this.elements = null;
    }

    async fetchData(page) {
        if (this.isLoading) return;

        this.showLoading();
        this.isLoading = true;

        try {
            const result = await this.options.fetchData(page);

            if (result.totalPages) {
                this.totalPages = result.totalPages;
            }

            this.responseData = result;
            this.renderData(result.items, result.total);
            this.updateUI();

            // 調用數據加載完成回調
            if (this.options.onDataLoaded) {
                this.options.onDataLoaded(result);
            }

        } catch (error) {
            this.showError(error.message);

            // 調用錯誤回調
            if (this.options.onError) {
                this.options.onError(error);
            }
        } finally {
            this.isLoading = false;
        }

    }

    async restoreData() {
        if (this.isLoading) return;

        this.showLoading();
        this.isLoading = true;

        try {
            const result = this.responseData;

            if (result.totalPages) {
                this.totalPages = result.totalPages;
            }

            this.responseData = result;
            this.renderData(result.items, result.total);
            this.updateUI();

            // 調用數據加載完成回調
            if (this.options.onDataLoaded) {
                this.options.onDataLoaded(result);
            }

        } catch (error) {
            this.showError(error.message);

            // 調用錯誤回調
            if (this.options.onError) {
                this.options.onError(error);
            }
        } finally {
            this.isLoading = false;
        }

    }

    showLoading() {
        this.elements.resultMesssage.innerHTML = '';
        this.elements.resultMesssage.appendChild(this.options.renderLoading());
    }

    showError(message) {
        this.elements.resultMesssage.innerHTML = '';
        this.elements.resultMesssage.appendChild(this.options.renderError(message));
    }

    showTotalResult(total){
        this.elements.resultMesssage.innerHTML = `${total}個結果`;
    }

    clearError(){
        this.elements.resultMesssage.innerHTML = '';
    }

    renderData(items,total=null) {
        this.clearError();
        this.elements.list.innerHTML = '';
        // this.elements.container.innerHTML = '';
        // this.elements.container.appendChild(this.elements.list);

        if (items.length === 0) {
            this.showError(this.options.noDataErrorMessage);
        }
        if(total){
            this.showTotalResult(total);
        }
        items.forEach(item => {
            this.elements.list.appendChild(this.options.renderItem(item));
        });
    }

    updateUI() {
        this.elements.pageInput.value = this.currentPage;
        this.elements.totalPages.textContent = this.totalPages;
        this.elements.prevButton.disabled = this.currentPage === 1;
        this.elements.nextButton.disabled = this.currentPage === this.totalPages;

        // 調用頁面變更回調
        if (this.options.onPageChange) {
            this.options.onPageChange(this.currentPage);
        }
    }
}