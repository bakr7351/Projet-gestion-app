class ModalManager {
 constructor() {
 this.activeModals = new Map();
 this.init();
 }
 init() {
 const style = document.createElement('style');
 style.textContent = `
 .modal-overlay {
 position: fixed;
 top: 0;
 left: 0;
 right: 0;
 bottom: 0;
 background: rgba(0, 0, 0, 0.5);
 display: flex;
 align-items: center;
 justify-content: center;
 z-index: 10000;
 opacity: 0;
 transition: opacity 0.3s ease;
 backdrop-filter: blur(4px);
 }
 .modal-overlay.show {
 opacity: 1;
 }
 .modal {
 background: var(--surface, #ffffff);
 border-radius: 12px;
 box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
 max-width: 500px;
 width: 90%;
 max-height: 80vh;
 overflow: hidden;
 transform: scale(0.9) translateY(20px);
 transition: transform 0.3s ease;
 border: 1px solid var(--border, #e2e8f0);
 }
 .modal-overlay.show .modal {
 transform: scale(1) translateY(0);
 }
 .modal-header {
 padding: 24px 24px 0 24px;
 display: flex;
 align-items: center;
 gap: 12px;
 }
 .modal-icon {
 width: 48px;
 height: 48px;
 border-radius: 50%;
 display: flex;
 align-items: center;
 justify-content: center;
 font-size: 24px;
 flex-shrink: 0;
 }
 .modal-icon.success {
 background: #dcfce7;
 color: #16a34a;
 }
 .modal-icon.error {
 background: #fee2e2;
 color: #dc2626;
 }
 .modal-icon.warning {
 background: #fef3c7;
 color: #d97706;
 }
 .modal-icon.info {
 background: #dbeafe;
 color: #2563eb;
 }
 .modal-icon.question {
 background: #f3e8ff;
 color: #9333ea;
 }
 .modal-title {
 font-size: 18px;
 font-weight: 600;
 color: var(--text, #1e293b);
 margin: 0;
 }
 .modal-body {
 padding: 16px 24px 24px 24px;
 }
 .modal-message {
 color: var(--text-muted, #64748b);
 line-height: 1.5;
 margin: 0;
 }
 .modal-input {
 width: 100%;
 padding: 12px;
 border: 1px solid var(--border, #e2e8f0);
 border-radius: 8px;
 font-size: 14px;
 margin-top: 16px;
 background: var(--input-bg, #f8fafc);
 color: var(--text, #1e293b);
 }
 .modal-input:focus {
 outline: none;
 border-color: var(--primary, #6366f1);
 box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
 }
 .modal-actions {
 padding: 0 24px 24px 24px;
 display: flex;
 gap: 12px;
 justify-content: flex-end;
 }
 .modal-btn {
 padding: 10px 20px;
 border-radius: 8px;
 font-size: 14px;
 font-weight: 500;
 cursor: pointer;
 border: none;
 transition: all 0.2s ease;
 min-width: 80px;
 }
 .modal-btn-primary {
 background: var(--primary, #6366f1);
 color: white;
 }
 .modal-btn-primary:hover {
 background: var(--primary-hover, #4f46e5);
 }
 .modal-btn-secondary {
 background: var(--surface-secondary, #f1f5f9);
 color: var(--text, #1e293b);
 border: 1px solid var(--border, #e2e8f0);
 }
 .modal-btn-secondary:hover {
 background: var(--hover, #e2e8f0);
 }
 .modal-btn-danger {
 background: #dc2626;
 color: white;
 }
 .modal-btn-danger:hover {
 background: #b91c1c;
 }
 .modal-btn:disabled {
 opacity: 0.5;
 cursor: not-allowed;
 }
 @media (max-width: 480px) {
 .modal {
 width: 95%;
 margin: 20px;
 }
 .modal-actions {
 flex-direction: column-reverse;
 }
 .modal-btn {
 width: 100%;
 }
 }
 [data-theme="dark"] .modal {
 background: var(--surface, #1e1b4b);
 border-color: var(--border, #3730a3);
 }
 [data-theme="dark"] .modal-title {
 color: var(--text, #e2e8f0);
 }
 [data-theme="dark"] .modal-message {
 color: var(--text-muted, #a5b4fc);
 }
 [data-theme="dark"] .modal-input {
 background: var(--input-bg, #2d2a5e);
 border-color: var(--border, #3730a3);
 color: var(--text, #e2e8f0);
 }
 [data-theme="dark"] .modal-btn-secondary {
 background: var(--surface-secondary, #2d2a5e);
 color: var(--text, #e2e8f0);
 border-color: var(--border, #3730a3);
 }
 `;
 document.head.appendChild(style);
 document.addEventListener('keydown', (e) => {
 if (e.key === 'Escape') {
 this.closeTopModal();
 }
 });
 }
 show(options = {}) {
 const {
 title = 'Confirmation',
 message = '',
 type = 'info', 
 buttons = [{ text: 'OK', primary: true }],
 input = null, 
 closable = true
 } = options;
 return new Promise((resolve) => {
 const modalId = Date.now() + Math.random();
 const overlay = document.createElement('div');
 overlay.className = 'modal-overlay';
 overlay.dataset.modalId = modalId;
 const modal = document.createElement('div');
 modal.className = 'modal';
 const header = document.createElement('div');
 header.className = 'modal-header';
 const icon = document.createElement('div');
 icon.className = `modal-icon ${type}`;
 icon.textContent = this.getIcon(type);
 const titleEl = document.createElement('h3');
 titleEl.className = 'modal-title';
 titleEl.textContent = title;
 header.appendChild(icon);
 header.appendChild(titleEl);
 const body = document.createElement('div');
 body.className = 'modal-body';
 const messageEl = document.createElement('p');
 messageEl.className = 'modal-message';
 messageEl.textContent = message;
 body.appendChild(messageEl);
 let inputEl = null;
 if (input) {
 inputEl = document.createElement('input');
 inputEl.className = 'modal-input';
 inputEl.type = input.type || 'text';
 inputEl.placeholder = input.placeholder || '';
 inputEl.value = input.value || '';
 body.appendChild(inputEl);
 }
 const actions = document.createElement('div');
 actions.className = 'modal-actions';
 buttons.forEach((button, index) => {
 const btn = document.createElement('button');
 btn.className = `modal-btn ${button.primary ? 'modal-btn-primary' : button.danger ? 'modal-btn-danger' : 'modal-btn-secondary'}`;
 btn.textContent = button.text;
 btn.addEventListener('click', () => {
 const result = {
 buttonIndex: index,
 button: button,
 value: inputEl ? inputEl.value : null
 };
 this.close(modalId);
 resolve(result);
 });
 actions.appendChild(btn);
 });
 modal.appendChild(header);
 modal.appendChild(body);
 modal.appendChild(actions);
 overlay.appendChild(modal);
 if (closable) {
 overlay.addEventListener('click', (e) => {
 if (e.target === overlay) {
 this.close(modalId);
 resolve({ buttonIndex: -1, button: null, value: null });
 }
 });
 }
 document.body.appendChild(overlay);
 this.activeModals.set(modalId, { overlay, resolve });
 requestAnimationFrame(() => {
 overlay.classList.add('show');
 });
 if (inputEl) {
 setTimeout(() => inputEl.focus(), 100);
 }
 });
 }
 close(modalId) {
 const modal = this.activeModals.get(modalId);
 if (!modal) return;
 modal.overlay.classList.remove('show');
 setTimeout(() => {
 if (modal.overlay.parentNode) {
 modal.overlay.parentNode.removeChild(modal.overlay);
 }
 this.activeModals.delete(modalId);
 }, 300);
 }
 closeTopModal() {
 const modalIds = Array.from(this.activeModals.keys());
 if (modalIds.length > 0) {
 const topModalId = modalIds[modalIds.length - 1];
 this.close(topModalId);
 const modal = this.activeModals.get(topModalId);
 if (modal && modal.resolve) {
 modal.resolve({ buttonIndex: -1, button: null, value: null });
 }
 }
 }
 getIcon(type) {
 const icons = {
 success: '✓',
 error: '✕',
 warning: '⚠',
 info: 'ℹ',
 question: '?'
 };
 return icons[type] || icons.info;
 }
 confirm(message, title = 'Confirmation') {
 return this.show({
 title,
 message,
 type: 'question',
 buttons: [
 { text: 'Annuler', primary: false },
 { text: 'Confirmer', primary: true }
 ]
 }).then(result => result.buttonIndex === 1);
 }
 alert(message, title = 'Information', type = 'info') {
 return this.show({
 title,
 message,
 type,
 buttons: [{ text: 'OK', primary: true }]
 });
 }
 prompt(message, title = 'Saisie', defaultValue = '') {
 return this.show({
 title,
 message,
 type: 'question',
 input: { type: 'text', value: defaultValue },
 buttons: [
 { text: 'Annuler', primary: false },
 { text: 'OK', primary: true }
 ]
 }).then(result => result.buttonIndex === 1 ? result.value : null);
 }
 confirmDelete(itemName = 'cet élément') {
 return this.show({
 title: 'Supprimer',
 message: `Êtes-vous sûr de vouloir supprimer ${itemName} ? Cette action est irréversible.`,
 type: 'warning',
 buttons: [
 { text: 'Annuler', primary: false },
 { text: 'Supprimer', danger: true }
 ]
 }).then(result => result.buttonIndex === 1);
 }
}
const modals = new ModalManager();
window.confirm = (message) => {
 return modals.confirm(message);
};
window.alert = (message) => {
 return modals.alert(message);
};
window.prompt = (message, defaultValue) => {
 return modals.prompt(message, 'Saisie', defaultValue);
};
if (typeof module !== 'undefined' && module.exports) {
 module.exports = { ModalManager, modals };
}