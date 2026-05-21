class NotificationManager {
 constructor() {
 this.container = null;
 this.notifications = new Map();
 this.init();
 }
 init() {
 this.container = document.createElement('div');
 this.container.className = 'notification-container';
 this.container.innerHTML = `
 <style>
 .notification-container {
 position: fixed;
 top: 20px;
 right: 20px;
 z-index: 99999;
 pointer-events: none;
 }
 .notification {
 background: #ffffff !important;
 border: 1px solid #e2e8f0 !important;
 border-radius: 10px;
 padding: 16px 20px;
 margin-bottom: 12px;
 min-width: 320px;
 max-width: 420px;
 box-shadow: 0 8px 30px rgba(0, 0, 0, 0.18) !important;
 pointer-events: auto;
 transform: translateX(120%);
 opacity: 0;
 transition: all 0.35s cubic-bezier(0.4, 0, 0.2, 1);
 position: relative;
 overflow: hidden;
 font-family: 'Segoe UI', system-ui, sans-serif;
 }
 [data-theme="dark"] .notification {
 background: #1e1b4b !important;
 border-color: #3730a3 !important;
 box-shadow: 0 8px 30px rgba(0, 0, 0, 0.55) !important;
 }
 .notification.show {
 transform: translateX(0);
 opacity: 1;
 }
 .notification.hide {
 transform: translateX(120%);
 opacity: 0;
 }
 .notification::before {
 content: '';
 position: absolute;
 left: 0;
 top: 0;
 bottom: 0;
 width: 4px;
 }
 .notification.success::before { background: #10b981; }
 .notification.error::before { background: #ef4444; }
 .notification.warning::before { background: #f59e0b; }
 .notification.info::before { background: #3b82f6; }
 .notification-header {
 display: flex;
 align-items: center;
 justify-content: space-between;
 margin-bottom: 6px;
 }
 .notification-title {
 font-weight: 700;
 font-size: 14px;
 color: #1e293b;
 display: flex;
 align-items: center;
 gap: 8px;
 }
 [data-theme="dark"] .notification-title {
 color: #e2e8f0;
 }
 .notification-icon {
 font-size: 16px;
 }
 .notification-close {
 background: none;
 border: none;
 color: #94a3b8;
 cursor: pointer;
 padding: 2px 6px;
 border-radius: 4px;
 font-size: 14px;
 line-height: 1;
 transition: background-color 0.2s, color 0.2s;
 }
 .notification-close:hover {
 background: #f1f5f9;
 color: #1e293b;
 }
 [data-theme="dark"] .notification-close:hover {
 background: #2d2a5e;
 color: #e2e8f0;
 }
 .notification-message {
 color: #64748b;
 font-size: 13px;
 line-height: 1.5;
 }
 [data-theme="dark"] .notification-message {
 color: #a5b4fc;
 }
 .notification-progress {
 position: absolute;
 bottom: 0;
 left: 0;
 height: 3px;
 transition: width linear;
 }
 .notification.success .notification-progress { background: #10b981; }
 .notification.error .notification-progress { background: #ef4444; }
 .notification.warning .notification-progress { background: #f59e0b; }
 .notification.info .notification-progress { background: #3b82f6; }
 @media (max-width: 480px) {
 .notification-container {
 left: 16px;
 right: 16px;
 top: 16px;
 }
 .notification {
 min-width: auto;
 max-width: none;
 }
 }
 </style>
 `;
 document.body.appendChild(this.container);
 }
 show(message, type = 'info', options = {}) {
 const {
 title = this.getDefaultTitle(type),
 duration = 5000,
 persistent = false,
 actions = [],
 icon = null
 } = options;
 const id = Date.now() + Math.random();
 const notification = this.createNotification(id, title, message, type, actions, icon);
 this.container.appendChild(notification);
 this.notifications.set(id, { element: notification, timer: null });
 requestAnimationFrame(() => {
 notification.classList.add('show');
 });
 if (!persistent && duration > 0) {
 const progressBar = notification.querySelector('.notification-progress');
 if (progressBar) {
 progressBar.style.width = '100%';
 progressBar.style.transitionDuration = duration + 'ms';
 requestAnimationFrame(() => {
 progressBar.style.width = '0%';
 });
 }
 const timer = setTimeout(() => {
 this.hide(id);
 }, duration);
 this.notifications.get(id).timer = timer;
 }
 return id;
 }
 createNotification(id, title, message, type, actions, customIcon) {
 const notification = document.createElement('div');
 notification.className = `notification ${type}`;
 notification.dataset.id = id;
 const icon = customIcon || this.getIcon(type);
 notification.innerHTML = `
 <div class="notification-header">
 <div class="notification-title">
 <span class="notification-icon">${icon}</span>
 ${title}
 </div>
 <button class="notification-close" onclick="notifications.hide(${id})">
 ✕
 </button>
 </div>
 <div class="notification-message">${message}</div>
 ${actions.length > 0 ? this.createActions(actions, id) : ''}
 <div class="notification-progress"></div>
 `;
 return notification;
 }
 createActions(actions, notificationId) {
 const actionsHtml = actions.map(action => `
 <button 
 class="btn-secondary" 
 style="margin-right: 8px; margin-top: 8px; padding: 4px 12px; font-size: 12px;"
 onclick="${action.handler}; notifications.hide(${notificationId})"
 >
 ${action.label}
 </button>
 `).join('');
 return `<div style="margin-top: 12px;">${actionsHtml}</div>`;
 }
 hide(id) {
 const notification = this.notifications.get(id);
 if (!notification) return;
 if (notification.timer) {
 clearTimeout(notification.timer);
 }
 notification.element.classList.remove('show');
 notification.element.classList.add('hide');
 setTimeout(() => {
 if (notification.element.parentNode) {
 notification.element.parentNode.removeChild(notification.element);
 }
 this.notifications.delete(id);
 }, 300);
 }
 hideAll() {
 this.notifications.forEach((_, id) => this.hide(id));
 }
 getIcon(type) {
 const icons = {
 success: '✓',
 error: '✕',
 warning: '⚠',
 info: 'ℹ'
 };
 return icons[type] || icons.info;
 }
 getDefaultTitle(type) {
 const titles = {
 success: 'Succès',
 error: 'Erreur',
 warning: 'Attention',
 info: 'Information'
 };
 return titles[type] || titles.info;
 }
 success(message, options = {}) {
 return this.show(message, 'success', options);
 }
 error(message, options = {}) {
 return this.show(message, 'error', options);
 }
 warning(message, options = {}) {
 return this.show(message, 'warning', options);
 }
 info(message, options = {}) {
 return this.show(message, 'info', options);
 }
}
const notifications = new NotificationManager();
function showAlert(element, message, type = 'info') {
 if (element) {
 element.style.display = 'none';
 }
 notifications.show(message, type);
}
if (typeof module !== 'undefined' && module.exports) {
 module.exports = { NotificationManager, notifications };
}