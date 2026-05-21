class PaginationManager {
 constructor() {
 this.instances = new Map();
 this.init();
 }
 init() {
 const style = document.createElement('style');
 style.textContent = `
 .pagination-container {
 display: flex;
 align-items: center;
 justify-content: space-between;
 padding: 16px 0;
 border-top: 1px solid var(--border, #e2e8f0);
 margin-top: 16px;
 }
 .pagination-info {
 color: var(--text-muted, #64748b);
 font-size: 14px;
 }
 .pagination-controls {
 display: flex;
 align-items: center;
 gap: 8px;
 }
 .pagination-btn {
 padding: 8px 12px;
 border: 1px solid var(--border, #e2e8f0);
 background: var(--surface, #ffffff);
 color: var(--text, #1e293b);
 border-radius: 6px;
 cursor: pointer;
 font-size: 14px;
 transition: all 0.2s ease;
 min-width: 40px;
 text-align: center;
 }
 .pagination-btn:hover:not(:disabled) {
 background: var(--hover, #f1f5f9);
 border-color: var(--primary, #6366f1);
 }
 .pagination-btn:disabled {
 opacity: 0.5;
 cursor: not-allowed;
 }
 .pagination-btn.active {
 background: var(--primary, #6366f1);
 color: white;
 border-color: var(--primary, #6366f1);
 }
 .pagination-ellipsis {
 padding: 8px 4px;
 color: var(--text-muted, #64748b);
 }
 .pagination-size-selector {
 display: flex;
 align-items: center;
 gap: 8px;
 margin-left: 16px;
 }
 .pagination-size-select {
 padding: 6px 8px;
 border: 1px solid var(--border, #e2e8f0);
 border-radius: 4px;
 background: var(--surface, #ffffff);
 color: var(--text, #1e293b);
 font-size: 14px;
 }
 @media (max-width: 640px) {
 .pagination-container {
 flex-direction: column;
 gap: 12px;
 align-items: stretch;
 }
 .pagination-controls {
 justify-content: center;
 }
 .pagination-size-selector {
 justify-content: center;
 margin-left: 0;
 }
 }
 [data-theme="dark"] .pagination-btn {
 background: var(--surface, #1e1b4b);
 border-color: var(--border, #3730a3);
 color: var(--text, #e2e8f0);
 }
 [data-theme="dark"] .pagination-btn:hover:not(:disabled) {
 background: var(--hover, #2d2a5e);
 }
 [data-theme="dark"] .pagination-size-select {
 background: var(--surface, #1e1b4b);
 border-color: var(--border, #3730a3);
 color: var(--text, #e2e8f0);
 }
 `;
 document.head.appendChild(style);
 }
 create(containerId, options = {}) {
 const {
 pageSize = 10,
 pageSizeOptions = [5, 10, 25, 50, 100],
 showSizeSelector = true,
 showInfo = true,
 maxVisiblePages = 5,
 onPageChange = () => {},
 onPageSizeChange = () => {}
 } = options;
 const instance = {
 containerId,
 currentPage: 1,
 pageSize,
 totalItems: 0,
 totalPages: 0,
 pageSizeOptions,
 showSizeSelector,
 showInfo,
 maxVisiblePages,
 onPageChange,
 onPageSizeChange
 };
 this.instances.set(containerId, instance);
 return instance;
 }
 update(containerId, totalItems, currentPage = null) {
 const instance = this.instances.get(containerId);
 if (!instance) return;
 instance.totalItems = totalItems;
 instance.totalPages = Math.ceil(totalItems / instance.pageSize);
 if (currentPage !== null) {
 instance.currentPage = Math.max(1, Math.min(currentPage, instance.totalPages));
 }
 this.render(containerId);
 }
 render(containerId) {
 const instance = this.instances.get(containerId);
 if (!instance) return;
 const container = document.getElementById(containerId);
 if (!container) return;
 const { currentPage, pageSize, totalItems, totalPages } = instance;
 const startItem = (currentPage - 1) * pageSize + 1;
 const endItem = Math.min(currentPage * pageSize, totalItems);
 container.innerHTML = `
 <div class="pagination-container">
 ${instance.showInfo ? `
 <div class="pagination-info">
 Affichage de ${startItem} à ${endItem} sur ${totalItems} éléments
 </div>
 ` : '<div></div>'}
 <div style="display: flex; align-items: center;">
 <div class="pagination-controls">
 ${this.renderPageButtons(instance)}
 </div>
 ${instance.showSizeSelector ? `
 <div class="pagination-size-selector">
 <span style="font-size: 14px; color: var(--text-muted);">Afficher:</span>
 <select class="pagination-size-select" onchange="pagination.changePageSize('${containerId}', this.value)">
 ${instance.pageSizeOptions.map(size => 
 `<option value="${size}" ${size === pageSize ? 'selected' : ''}>${size}</option>`
 ).join('')}
 </select>
 </div>
 ` : ''}
 </div>
 </div>
 `;
 }
 renderPageButtons(instance) {
 const { currentPage, totalPages, maxVisiblePages } = instance;
 if (totalPages <= 1) return '';
 let buttons = [];
 buttons.push(`
 <button class="pagination-btn" ${currentPage === 1 ? 'disabled' : ''} 
 onclick="pagination.goToPage('${instance.containerId}', ${currentPage - 1})">
 ‹
 </button>
 `);
 let startPage = Math.max(1, currentPage - Math.floor(maxVisiblePages / 2));
 let endPage = Math.min(totalPages, startPage + maxVisiblePages - 1);
 if (endPage - startPage + 1 < maxVisiblePages) {
 startPage = Math.max(1, endPage - maxVisiblePages + 1);
 }
 if (startPage > 1) {
 buttons.push(`
 <button class="pagination-btn" onclick="pagination.goToPage('${instance.containerId}', 1)">1</button>
 `);
 if (startPage > 2) {
 buttons.push('<span class="pagination-ellipsis">…</span>');
 }
 }
 for (let i = startPage; i <= endPage; i++) {
 buttons.push(`
 <button class="pagination-btn ${i === currentPage ? 'active' : ''}" 
 onclick="pagination.goToPage('${instance.containerId}', ${i})">
 ${i}
 </button>
 `);
 }
 if (endPage < totalPages) {
 if (endPage < totalPages - 1) {
 buttons.push('<span class="pagination-ellipsis">…</span>');
 }
 buttons.push(`
 <button class="pagination-btn" onclick="pagination.goToPage('${instance.containerId}', ${totalPages})">
 ${totalPages}
 </button>
 `);
 }
 buttons.push(`
 <button class="pagination-btn" ${currentPage === totalPages ? 'disabled' : ''} 
 onclick="pagination.goToPage('${instance.containerId}', ${currentPage + 1})">
 ›
 </button>
 `);
 return buttons.join('');
 }
 goToPage(containerId, page) {
 const instance = this.instances.get(containerId);
 if (!instance) return;
 const newPage = Math.max(1, Math.min(page, instance.totalPages));
 if (newPage === instance.currentPage) return;
 instance.currentPage = newPage;
 this.render(containerId);
 instance.onPageChange(newPage, instance.pageSize);
 }
 changePageSize(containerId, newSize) {
 const instance = this.instances.get(containerId);
 if (!instance) return;
 const oldSize = instance.pageSize;
 instance.pageSize = parseInt(newSize);
 const currentFirstItem = (instance.currentPage - 1) * oldSize + 1;
 instance.currentPage = Math.ceil(currentFirstItem / instance.pageSize);
 instance.totalPages = Math.ceil(instance.totalItems / instance.pageSize);
 instance.currentPage = Math.max(1, Math.min(instance.currentPage, instance.totalPages));
 this.render(containerId);
 instance.onPageSizeChange(instance.currentPage, instance.pageSize);
 }
 getCurrentPage(containerId) {
 const instance = this.instances.get(containerId);
 return instance ? instance.currentPage : 1;
 }
 getPageSize(containerId) {
 const instance = this.instances.get(containerId);
 return instance ? instance.pageSize : 10;
 }
 destroy(containerId) {
 this.instances.delete(containerId);
 const container = document.getElementById(containerId);
 if (container) {
 container.innerHTML = '';
 }
 }
}
const pagination = new PaginationManager();
if (typeof module !== 'undefined' && module.exports) {
 module.exports = { PaginationManager, pagination };
}