class ExportManager {
 constructor() {
 this.init();
 }
 init() {
 const style = document.createElement('style');
 style.textContent = `
 .export-dropdown {
 position: relative;
 display: inline-block;
 }
 .export-btn {
 padding: 8px 16px;
 background: var(--primary, #6366f1);
 color: white;
 border: none;
 border-radius: 6px;
 cursor: pointer;
 font-size: 14px;
 font-weight: 500;
 display: flex;
 align-items: center;
 gap: 8px;
 transition: background-color 0.2s ease;
 }
 .export-btn:hover {
 background: var(--primary-hover, #4f46e5);
 }
 .export-menu {
 position: absolute;
 top: 100%;
 right: 0;
 background: var(--surface, #ffffff);
 border: 1px solid var(--border, #e2e8f0);
 border-radius: 8px;
 box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
 z-index: 1000;
 min-width: 200px;
 opacity: 0;
 visibility: hidden;
 transform: translateY(-10px);
 transition: all 0.2s ease;
 }
 .export-menu.show {
 opacity: 1;
 visibility: visible;
 transform: translateY(0);
 }
 .export-menu-item {
 padding: 12px 16px;
 cursor: pointer;
 border-bottom: 1px solid var(--border, #e2e8f0);
 transition: background-color 0.2s ease;
 display: flex;
 align-items: center;
 gap: 12px;
 }
 .export-menu-item:last-child {
 border-bottom: none;
 }
 .export-menu-item:hover {
 background: var(--hover, #f1f5f9);
 }
 .export-menu-icon {
 font-size: 16px;
 width: 20px;
 text-align: center;
 }
 .export-menu-content {
 flex: 1;
 }
 .export-menu-title {
 font-weight: 500;
 color: var(--text, #1e293b);
 margin-bottom: 2px;
 }
 .export-menu-desc {
 font-size: 12px;
 color: var(--text-muted, #64748b);
 }
 .export-progress {
 position: fixed;
 top: 20px;
 right: 20px;
 background: var(--surface, #ffffff);
 border: 1px solid var(--border, #e2e8f0);
 border-radius: 8px;
 padding: 16px;
 box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
 z-index: 10000;
 min-width: 300px;
 transform: translateX(100%);
 transition: transform 0.3s ease;
 }
 .export-progress.show {
 transform: translateX(0);
 }
 .export-progress-header {
 display: flex;
 align-items: center;
 gap: 12px;
 margin-bottom: 12px;
 }
 .export-progress-title {
 font-weight: 500;
 color: var(--text, #1e293b);
 }
 .export-progress-bar {
 width: 100%;
 height: 6px;
 background: var(--border, #e2e8f0);
 border-radius: 3px;
 overflow: hidden;
 }
 .export-progress-fill {
 height: 100%;
 background: var(--primary, #6366f1);
 transition: width 0.3s ease;
 }
 [data-theme="dark"] .export-menu {
 background: var(--surface, #1e1b4b);
 border-color: var(--border, #3730a3);
 }
 [data-theme="dark"] .export-menu-item {
 border-color: var(--border, #3730a3);
 }
 [data-theme="dark"] .export-menu-item:hover {
 background: var(--hover, #2d2a5e);
 }
 [data-theme="dark"] .export-progress {
 background: var(--surface, #1e1b4b);
 border-color: var(--border, #3730a3);
 }
 `;
 document.head.appendChild(style);
 document.addEventListener('click', (e) => {
 if (!e.target.closest('.export-dropdown')) {
 this.closeAllDropdowns();
 }
 });
 }
 createExportButton(containerId, options = {}) {
 const {
 data = [],
 filename = 'export',
 columns = [],
 onDataFetch = null,
 formats = ['csv', 'json', 'excel']
 } = options;
 const container = document.getElementById(containerId);
 if (!container) return;
 const dropdownId = `export-dropdown-${Date.now()}`;
 container.innerHTML = `
 <div class="export-dropdown" id="${dropdownId}">
 <button class="export-btn" onclick="exportManager.toggleDropdown('${dropdownId}')">
 📊 Exporter
 <span style="font-size: 12px;">▼</span>
 </button>
 <div class="export-menu" id="${dropdownId}-menu">
 ${formats.includes('csv') ? `
 <div class="export-menu-item" onclick="exportManager.exportData('${dropdownId}', 'csv')">
 <div class="export-menu-icon">📄</div>
 <div class="export-menu-content">
 <div class="export-menu-title">CSV</div>
 <div class="export-menu-desc">Compatible Excel, Google Sheets</div>
 </div>
 </div>
 ` : ''}
 ${formats.includes('json') ? `
 <div class="export-menu-item" onclick="exportManager.exportData('${dropdownId}', 'json')">
 <div class="export-menu-icon">🔧</div>
 <div class="export-menu-content">
 <div class="export-menu-title">JSON</div>
 <div class="export-menu-desc">Format développeur</div>
 </div>
 </div>
 ` : ''}
 ${formats.includes('excel') ? `
 <div class="export-menu-item" onclick="exportManager.exportData('${dropdownId}', 'excel')">
 <div class="export-menu-icon">📊</div>
 <div class="export-menu-content">
 <div class="export-menu-title">Excel</div>
 <div class="export-menu-desc">Fichier .xlsx natif</div>
 </div>
 </div>
 ` : ''}
 </div>
 </div>
 `;
 container.dataset.exportOptions = JSON.stringify({
 data,
 filename,
 columns,
 onDataFetch: onDataFetch ? onDataFetch.toString() : null
 });
 }
 toggleDropdown(dropdownId) {
 this.closeAllDropdowns();
 const menu = document.getElementById(`${dropdownId}-menu`);
 if (menu) {
 menu.classList.toggle('show');
 }
 }
 closeAllDropdowns() {
 document.querySelectorAll('.export-menu').forEach(menu => {
 menu.classList.remove('show');
 });
 }
 async exportData(dropdownId, format) {
 this.closeAllDropdowns();
 const container = document.getElementById(dropdownId).parentElement;
 const options = JSON.parse(container.dataset.exportOptions || '{}');
 let { data, filename, columns, onDataFetch } = options;
 const progressId = this.showProgress(`Exportation ${format.toUpperCase()}...`);
 try {
 if (onDataFetch) {
 const fetchFn = new Function('return ' + onDataFetch)();
 data = await fetchFn();
 }
 this.updateProgress(progressId, 30);
 let blob, mimeType, extension;
 switch (format) {
 case 'csv':
 const csvContent = this.convertToCSV(data, columns);
 blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
 mimeType = 'text/csv';
 extension = 'csv';
 break;
 case 'json':
 const jsonContent = JSON.stringify(data, null, 2);
 blob = new Blob([jsonContent], { type: 'application/json;charset=utf-8;' });
 mimeType = 'application/json';
 extension = 'json';
 break;
 case 'excel':
 blob = await this.convertToExcel(data, columns);
 mimeType = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet';
 extension = 'xlsx';
 break;
 default:
 throw new Error('Format non supporté');
 }
 this.updateProgress(progressId, 80);
 const timestamp = new Date().toISOString().slice(0, 19).replace(/:/g, '-');
 const finalFilename = `${filename}_${timestamp}.${extension}`;
 this.downloadBlob(blob, finalFilename);
 this.updateProgress(progressId, 100);
 setTimeout(() => {
 this.hideProgress(progressId);
 notifications.success(`Export ${format.toUpperCase()} terminé`, {
 title: 'Export réussi'
 });
 }, 500);
 } catch (error) {
 this.hideProgress(progressId);
 notifications.error(`Erreur lors de l'export: ${error.message}`, {
 title: 'Erreur d\'export'
 });
 }
 }
 convertToCSV(data, columns = []) {
 if (!data || data.length === 0) return '';
 if (columns.length === 0) {
 columns = Object.keys(data[0]).map(key => ({ key, label: key }));
 }
 const headers = columns.map(col => this.escapeCSV(col.label)).join(',');
 const rows = data.map(row => {
 return columns.map(col => {
 const value = this.getNestedValue(row, col.key);
 return this.escapeCSV(value);
 }).join(',');
 });
 return [headers, ...rows].join('\n');
 }
 async convertToExcel(data, columns = []) {
 const csvContent = this.convertToCSV(data, columns);
 return new Blob([csvContent], { 
 type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' 
 });
 }
 escapeCSV(value) {
 if (value === null || value === undefined) return '';
 const stringValue = String(value);
 if (stringValue.includes(',') || stringValue.includes('"') || stringValue.includes('\n')) {
 return '"' + stringValue.replace(/"/g, '""') + '"';
 }
 return stringValue;
 }
 getNestedValue(obj, path) {
 return path.split('.').reduce((current, key) => {
 return current && current[key] !== undefined ? current[key] : '';
 }, obj);
 }
 downloadBlob(blob, filename) {
 const url = window.URL.createObjectURL(blob);
 const link = document.createElement('a');
 link.href = url;
 link.download = filename;
 document.body.appendChild(link);
 link.click();
 document.body.removeChild(link);
 window.URL.revokeObjectURL(url);
 }
 showProgress(title) {
 const progressId = Date.now();
 const progressEl = document.createElement('div');
 progressEl.className = 'export-progress';
 progressEl.id = `export-progress-${progressId}`;
 progressEl.innerHTML = `
 <div class="export-progress-header">
 <div class="export-progress-title">${title}</div>
 </div>
 <div class="export-progress-bar">
 <div class="export-progress-fill" style="width: 0%"></div>
 </div>
 `;
 document.body.appendChild(progressEl);
 setTimeout(() => {
 progressEl.classList.add('show');
 }, 100);
 return progressId;
 }
 updateProgress(progressId, percentage) {
 const progressEl = document.getElementById(`export-progress-${progressId}`);
 if (progressEl) {
 const fill = progressEl.querySelector('.export-progress-fill');
 if (fill) {
 fill.style.width = `${percentage}%`;
 }
 }
 }
 hideProgress(progressId) {
 const progressEl = document.getElementById(`export-progress-${progressId}`);
 if (progressEl) {
 progressEl.classList.remove('show');
 setTimeout(() => {
 if (progressEl.parentNode) {
 progressEl.parentNode.removeChild(progressEl);
 }
 }, 300);
 }
 }
}
const exportManager = new ExportManager();
if (typeof module !== 'undefined' && module.exports) {
 module.exports = { ExportManager, exportManager };
}