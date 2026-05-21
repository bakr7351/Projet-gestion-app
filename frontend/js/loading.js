class LoadingManager {
 constructor() {
 this.loadingStates = new Map();
 this.init();
 }
 init() {
 const style = document.createElement('style');
 style.textContent = `
 .skeleton {
 background: linear-gradient(90deg, var(--skeleton-base) 25%, var(--skeleton-highlight) 50%, var(--skeleton-base) 75%);
 background-size: 200% 100%;
 animation: skeleton-loading 1.5s infinite;
 border-radius: 4px;
 }
 :root {
 --skeleton-base: #f3f4f6;
 --skeleton-highlight: #e5e7eb;
 }
 [data-theme="dark"] {
 --skeleton-base: #374151;
 --skeleton-highlight: #4b5563;
 }
 @keyframes skeleton-loading {
 0% { background-position: 200% 0; }
 100% { background-position: -200% 0; }
 }
 .skeleton-text {
 height: 1em;
 margin: 0.25em 0;
 }
 .skeleton-text.large { height: 1.5em; }
 .skeleton-text.small { height: 0.75em; }
 .skeleton-avatar {
 width: 40px;
 height: 40px;
 border-radius: 50%;
 }
 .skeleton-avatar.large {
 width: 60px;
 height: 60px;
 }
 .skeleton-button {
 height: 36px;
 width: 100px;
 border-radius: 6px;
 }
 .skeleton-card {
 height: 120px;
 border-radius: 8px;
 margin: 8px 0;
 }
 .skeleton-table-row {
 height: 48px;
 margin: 4px 0;
 border-radius: 4px;
 }
 .loading-overlay {
 position: absolute;
 top: 0;
 left: 0;
 right: 0;
 bottom: 0;
 background: rgba(255, 255, 255, 0.8);
 display: flex;
 align-items: center;
 justify-content: center;
 z-index: 100;
 border-radius: inherit;
 }
 [data-theme="dark"] .loading-overlay {
 background: rgba(0, 0, 0, 0.6);
 }
 .loading-spinner {
 width: 32px;
 height: 32px;
 border: 3px solid var(--border);
 border-top-color: var(--primary);
 border-radius: 50%;
 animation: spin 1s linear infinite;
 }
 .loading-dots {
 display: flex;
 gap: 4px;
 }
 .loading-dot {
 width: 8px;
 height: 8px;
 background: var(--primary);
 border-radius: 50%;
 animation: loading-bounce 1.4s infinite ease-in-out;
 }
 .loading-dot:nth-child(1) { animation-delay: -0.32s; }
 .loading-dot:nth-child(2) { animation-delay: -0.16s; }
 @keyframes loading-bounce {
 0%, 80%, 100% { transform: scale(0); }
 40% { transform: scale(1); }
 }
 .fade-in {
 animation: fadeIn 0.3s ease-out;
 }
 @keyframes fadeIn {
 from { opacity: 0; transform: translateY(10px); }
 to { opacity: 1; transform: translateY(0); }
 }
 `;
 document.head.appendChild(style);
 }
 showLoading(element, type = 'spinner') {
 if (!element) return;
 const loadingId = Date.now() + Math.random();
 this.loadingStates.set(loadingId, {
 element,
 originalContent: element.innerHTML,
 originalPosition: element.style.position
 });
 if (!element.style.position || element.style.position === 'static') {
 element.style.position = 'relative';
 }
 const overlay = document.createElement('div');
 overlay.className = 'loading-overlay';
 overlay.dataset.loadingId = loadingId;
 if (type === 'spinner') {
 overlay.innerHTML = '<div class="loading-spinner"></div>';
 } else if (type === 'dots') {
 overlay.innerHTML = `
 <div class="loading-dots">
 <div class="loading-dot"></div>
 <div class="loading-dot"></div>
 <div class="loading-dot"></div>
 </div>
 `;
 }
 element.appendChild(overlay);
 return loadingId;
 }
 hideLoading(loadingId) {
 const state = this.loadingStates.get(loadingId);
 if (!state) return;
 const overlay = state.element.querySelector(`[data-loading-id="${loadingId}"]`);
 if (overlay) {
 overlay.remove();
 }
 state.element.style.position = state.originalPosition;
 this.loadingStates.delete(loadingId);
 }
 createTableSkeleton(container, rowCount = 5) {
 const skeletonHtml = Array(rowCount).fill(0).map(() => 
 '<div class="skeleton skeleton-table-row"></div>'
 ).join('');
 container.innerHTML = skeletonHtml;
 }
 createCardSkeleton(container, cardCount = 3) {
 const skeletonHtml = Array(cardCount).fill(0).map(() => `
 <div class="skeleton skeleton-card"></div>
 `).join('');
 container.innerHTML = skeletonHtml;
 }
 createUserListSkeleton(container, userCount = 8) {
 const skeletonHtml = Array(userCount).fill(0).map(() => `
 <div style="display: flex; align-items: center; padding: 12px; border-bottom: 1px solid var(--border);">
 <div class="skeleton skeleton-avatar" style="margin-right: 12px;"></div>
 <div style="flex: 1;">
 <div class="skeleton skeleton-text" style="width: 60%; margin-bottom: 8px;"></div>
 <div class="skeleton skeleton-text small" style="width: 40%;"></div>
 </div>
 <div class="skeleton skeleton-button"></div>
 </div>
 `).join('');
 container.innerHTML = skeletonHtml;
 }
 createStatsSkeleton(container) {
 const skeletonHtml = `
 <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 16px;">
 ${Array(4).fill(0).map(() => `
 <div style="padding: 20px; border: 1px solid var(--border); border-radius: 8px;">
 <div class="skeleton skeleton-text large" style="width: 80%; margin-bottom: 12px;"></div>
 <div class="skeleton skeleton-text" style="width: 40%;"></div>
 </div>
 `).join('')}
 </div>
 `;
 container.innerHTML = skeletonHtml;
 }
 replaceWithAnimation(element, newContent) {
 element.style.opacity = '0';
 element.style.transform = 'translateY(10px)';
 setTimeout(() => {
 element.innerHTML = newContent;
 element.style.opacity = '1';
 element.style.transform = 'translateY(0)';
 element.style.transition = 'opacity 0.3s ease, transform 0.3s ease';
 }, 150);
 }
 setButtonLoading(button, loading = true) {
 if (!button) return;
 if (loading) {
 button.dataset.originalText = button.textContent;
 button.innerHTML = `
 <div class="loading-dots">
 <div class="loading-dot"></div>
 <div class="loading-dot"></div>
 <div class="loading-dot"></div>
 </div>
 `;
 button.disabled = true;
 } else {
 button.textContent = button.dataset.originalText || button.textContent;
 button.disabled = false;
 delete button.dataset.originalText;
 }
 }
}
const loading = new LoadingManager();
function showLoading(element, type = 'spinner') {
 return loading.showLoading(element, type);
}
function hideLoading(loadingId) {
 loading.hideLoading(loadingId);
}
if (typeof module !== 'undefined' && module.exports) {
 module.exports = { LoadingManager, loading };
}