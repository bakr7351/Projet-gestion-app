class FilterManager {
 constructor() {
 this.instances = new Map();
 this.init();
 }
 init() {
 const style = document.createElement('style');
 style.textContent = `
 .filter-container {
 background: var(--surface, #ffffff);
 border: 1px solid var(--border, #e2e8f0);
 border-radius: 8px;
 padding: 16px;
 margin-bottom: 16px;
 }
 .filter-row {
 display: flex;
 gap: 12px;
 align-items: center;
 flex-wrap: wrap;
 margin-bottom: 12px;
 }
 .filter-row:last-child {
 margin-bottom: 0;
 }
 .filter-group {
 display: flex;
 flex-direction: column;
 gap: 4px;
 min-width: 120px;
 }
 .filter-label {
 font-size: 12px;
 font-weight: 500;
 color: var(--text-muted, #64748b);
 text-transform: uppercase;
 letter-spacing: 0.05em;
 }
 .filter-input {
 padding: 8px 12px;
 border: 1px solid var(--border, #e2e8f0);
 border-radius: 6px;
 font-size: 14px;
 background: var(--input-bg, #f8fafc);
 color: var(--text, #1e293b);
 transition: border-color 0.2s ease;
 }
 .filter-input:focus {
 outline: none;
 border-color: var(--primary, #6366f1);
 box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
 }
 .filter-search {
 flex: 1;
 min-width: 200px;
 }
 .filter-select {
 min-width: 120px;
 }
 .filter-actions {
 display: flex;
 gap: 8px;
 align-items: flex-end;
 }
 .filter-btn {
 padding: 8px 16px;
 border: 1px solid var(--border, #e2e8f0);
 border-radius: 6px;
 font-size: 14px;
 cursor: pointer;
 transition: all 0.2s ease;
 background: var(--surface, #ffffff);
 color: var(--text, #1e293b);
 }
 .filter-btn-primary {
 background: var(--primary, #6366f1);
 color: white;
 border-color: var(--primary, #6366f1);
 }
 .filter-btn-primary:hover {
 background: var(--primary-hover, #4f46e5);
 }
 .filter-btn-secondary:hover {
 background: var(--hover, #f1f5f9);
 }
 .filter-tags {
 display: flex;
 gap: 8px;
 flex-wrap: wrap;
 margin-top: 8px;
 }
 .filter-tag {
 display: inline-flex;
 align-items: center;
 gap: 6px;
 padding: 4px 8px;
 background: var(--primary-light, #e0e7ff);
 color: var(--primary, #6366f1);
 border-radius: 4px;
 font-size: 12px;
 font-weight: 500;
 }
 .filter-tag-remove {
 cursor: pointer;
 font-weight: bold;
 opacity: 0.7;
 transition: opacity 0.2s ease;
 }
 .filter-tag-remove:hover {
 opacity: 1;
 }
 .filter-results-count {
 font-size: 14px;
 color: var(--text-muted, #64748b);
 margin-top: 8px;
 }
 @media (max-width: 768px) {
 .filter-row {
 flex-direction: column;
 align-items: stretch;
 }
 .filter-group {
 min-width: auto;
 }
 .filter-search {
 min-width: auto;
 }
 .filter-actions {
 justify-content: stretch;
 }
 .filter-btn {
 flex: 1;
 }
 }
 [data-theme="dark"] .filter-container {
 background: var(--surface, #1e1b4b);
 border-color: var(--border, #3730a3);
 }
 [data-theme="dark"] .filter-input {
 background: var(--input-bg, #2d2a5e);
 border-color: var(--border, #3730a3);
 color: var(--text, #e2e8f0);
 }
 [data-theme="dark"] .filter-btn {
 background: var(--surface, #1e1b4b);
 border-color: var(--border, #3730a3);
 color: var(--text, #e2e8f0);
 }
 [data-theme="dark"] .filter-btn-secondary:hover {
 background: var(--hover, #2d2a5e);
 }
 `;
 document.head.appendChild(style);
 }
 create(containerId, options = {}) {
 const {
 searchPlaceholder = 'Rechercher...',
 filters = [],
 onFilterChange = () => {},
 debounceMs = 300,
 showResultsCount = true
 } = options;
 const instance = {
 containerId,
 searchPlaceholder,
 filters,
 onFilterChange,
 debounceMs,
 showResultsCount,
 currentFilters: {},
 searchTimeout: null,
 resultsCount: 0
 };
 this.instances.set(containerId, instance);
 this.render(containerId);
 return instance;
 }
 render(containerId) {
 const instance = this.instances.get(containerId);
 if (!instance) return;
 const container = document.getElementById(containerId);
 if (!container) return;
 container.innerHTML = `
 <div class="filter-container">
 <div class="filter-row">
 <div class="filter-group filter-search">
 <label class="filter-label">Recherche</label>
 <input 
 type="text" 
 class="filter-input" 
 placeholder="${instance.searchPlaceholder}"
 oninput="filters.handleSearchInput('${containerId}', this.value)"
 />
 </div>
 ${instance.filters.map(filter => this.renderFilter(containerId, filter)).join('')}
 <div class="filter-actions">
 <button class="filter-btn filter-btn-secondary" onclick="filters.clearAll('${containerId}')">
 Effacer
 </button>
 <button class="filter-btn filter-btn-primary" onclick="filters.applyFilters('${containerId}')">
 Appliquer
 </button>
 </div>
 </div>
 <div class="filter-tags" id="${containerId}-tags"></div>
 ${instance.showResultsCount ? `
 <div class="filter-results-count" id="${containerId}-count">
 Aucun résultat
 </div>
 ` : ''}
 </div>
 `;
 this.updateTags(containerId);
 }
 renderFilter(containerId, filter) {
 const { type, key, label, options = [], placeholder = '' } = filter;
 if (type === 'select') {
 return `
 <div class="filter-group">
 <label class="filter-label">${label}</label>
 <select class="filter-input filter-select" onchange="filters.handleFilterChange('${containerId}', '${key}', this.value)">
 <option value="">Tous</option>
 ${options.map(option => `
 <option value="${option.value}">${option.label}</option>
 `).join('')}
 </select>
 </div>
 `;
 }
 if (type === 'date') {
 return `
 <div class="filter-group">
 <label class="filter-label">${label}</label>
 <input 
 type="date" 
 class="filter-input" 
 onchange="filters.handleFilterChange('${containerId}', '${key}', this.value)"
 />
 </div>
 `;
 }
 if (type === 'text') {
 return `
 <div class="filter-group">
 <label class="filter-label">${label}</label>
 <input 
 type="text" 
 class="filter-input" 
 placeholder="${placeholder}"
 oninput="filters.handleFilterChange('${containerId}', '${key}', this.value)"
 />
 </div>
 `;
 }
 return '';
 }
 handleSearchInput(containerId, value) {
 const instance = this.instances.get(containerId);
 if (!instance) return;
 if (instance.searchTimeout) {
 clearTimeout(instance.searchTimeout);
 }
 instance.searchTimeout = setTimeout(() => {
 instance.currentFilters.search = value.trim();
 this.updateTags(containerId);
 instance.onFilterChange(this.getActiveFilters(containerId));
 }, instance.debounceMs);
 }
 handleFilterChange(containerId, key, value) {
 const instance = this.instances.get(containerId);
 if (!instance) return;
 if (value === '' || value === null || value === undefined) {
 delete instance.currentFilters[key];
 } else {
 instance.currentFilters[key] = value;
 }
 this.updateTags(containerId);
 }
 applyFilters(containerId) {
 const instance = this.instances.get(containerId);
 if (!instance) return;
 instance.onFilterChange(this.getActiveFilters(containerId));
 }
 clearAll(containerId) {
 const instance = this.instances.get(containerId);
 if (!instance) return;
 instance.currentFilters = {};
 const container = document.getElementById(containerId);
 if (container) {
 const inputs = container.querySelectorAll('.filter-input');
 inputs.forEach(input => {
 if (input.type === 'text' || input.type === 'date') {
 input.value = '';
 } else if (input.tagName === 'SELECT') {
 input.selectedIndex = 0;
 }
 });
 }
 this.updateTags(containerId);
 instance.onFilterChange(this.getActiveFilters(containerId));
 }
 updateTags(containerId) {
 const instance = this.instances.get(containerId);
 if (!instance) return;
 const tagsContainer = document.getElementById(`${containerId}-tags`);
 if (!tagsContainer) return;
 const tags = [];
 Object.entries(instance.currentFilters).forEach(([key, value]) => {
 if (!value) return;
 let label = key;
 let displayValue = value;
 const filterDef = instance.filters.find(f => f.key === key);
 if (filterDef) {
 label = filterDef.label;
 if (filterDef.type === 'select') {
 const option = filterDef.options.find(o => o.value === value);
 if (option) {
 displayValue = option.label;
 }
 }
 }
 if (key === 'search') {
 label = 'Recherche';
 }
 tags.push(`
 <div class="filter-tag">
 ${label}: ${displayValue}
 <span class="filter-tag-remove" onclick="filters.removeFilter('${containerId}', '${key}')">×</span>
 </div>
 `);
 });
 tagsContainer.innerHTML = tags.join('');
 }
 removeFilter(containerId, key) {
 const instance = this.instances.get(containerId);
 if (!instance) return;
 delete instance.currentFilters[key];
 const container = document.getElementById(containerId);
 if (container) {
 const input = container.querySelector(`[onchange*="${key}"], [oninput*="${key}"]`);
 if (input) {
 if (input.type === 'text' || input.type === 'date') {
 input.value = '';
 } else if (input.tagName === 'SELECT') {
 input.selectedIndex = 0;
 }
 }
 }
 this.updateTags(containerId);
 instance.onFilterChange(this.getActiveFilters(containerId));
 }
 getActiveFilters(containerId) {
 const instance = this.instances.get(containerId);
 return instance ? { ...instance.currentFilters } : {};
 }
 updateResultsCount(containerId, count) {
 const instance = this.instances.get(containerId);
 if (!instance) return;
 instance.resultsCount = count;
 const countElement = document.getElementById(`${containerId}-count`);
 if (countElement) {
 if (count === 0) {
 countElement.textContent = 'Aucun résultat';
 } else if (count === 1) {
 countElement.textContent = '1 résultat trouvé';
 } else {
 countElement.textContent = `${count} résultats trouvés`;
 }
 }
 }
 destroy(containerId) {
 const instance = this.instances.get(containerId);
 if (instance && instance.searchTimeout) {
 clearTimeout(instance.searchTimeout);
 }
 this.instances.delete(containerId);
 const container = document.getElementById(containerId);
 if (container) {
 container.innerHTML = '';
 }
 }
}
const filters = new FilterManager();
if (typeof module !== 'undefined' && module.exports) {
 module.exports = { FilterManager, filters };
}