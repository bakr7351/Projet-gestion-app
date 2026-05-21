class WelcomeModal {
 constructor() {
 this.init();
 }
 init() {
 const style = document.createElement('style');
 style.textContent = `
 .welcome-overlay {
 position: fixed;
 inset: 0;
 background: rgba(0, 0, 0, 0.7);
 display: flex;
 align-items: center;
 justify-content: center;
 z-index: 10000;
 opacity: 0;
 transition: opacity 0.3s ease;
 backdrop-filter: blur(4px);
 }
 .welcome-overlay.show {
 opacity: 1;
 }
 .welcome-modal {
 background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
 border-radius: 20px;
 padding: 60px 40px;
 max-width: 500px;
 width: 90%;
 text-align: center;
 box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
 transform: scale(0.8) translateY(30px);
 transition: transform 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
 color: white;
 }
 .welcome-overlay.show .welcome-modal {
 transform: scale(1) translateY(0);
 }
 .welcome-icon {
 font-size: 80px;
 margin-bottom: 20px;
 animation: welcomeBounce 0.6s ease-out 0.2s both;
 }
 @keyframes welcomeBounce {
 0% {
 transform: scale(0) translateY(20px);
 opacity: 0;
 }
 50% {
 transform: scale(1.1);
 }
 100% {
 transform: scale(1) translateY(0);
 opacity: 1;
 }
 }
 .welcome-title {
 font-size: 32px;
 font-weight: 800;
 margin-bottom: 10px;
 animation: fadeInUp 0.6s ease-out 0.3s both;
 }
 .welcome-subtitle {
 font-size: 18px;
 opacity: 0.95;
 margin-bottom: 30px;
 animation: fadeInUp 0.6s ease-out 0.4s both;
 }
 .welcome-user-info {
 background: rgba(255, 255, 255, 0.15);
 border-radius: 12px;
 padding: 20px;
 margin-bottom: 30px;
 backdrop-filter: blur(10px);
 animation: fadeInUp 0.6s ease-out 0.5s both;
 }
 .welcome-user-name {
 font-size: 24px;
 font-weight: 700;
 margin-bottom: 8px;
 }
 .welcome-user-role {
 font-size: 14px;
 opacity: 0.85;
 text-transform: uppercase;
 letter-spacing: 1px;
 }
 .welcome-message {
 font-size: 16px;
 line-height: 1.6;
 margin-bottom: 30px;
 opacity: 0.9;
 animation: fadeInUp 0.6s ease-out 0.6s both;
 }
 .welcome-actions {
 display: flex;
 gap: 12px;
 justify-content: center;
 animation: fadeInUp 0.6s ease-out 0.7s both;
 }
 .welcome-btn {
 padding: 12px 28px;
 border: none;
 border-radius: 8px;
 font-size: 14px;
 font-weight: 600;
 cursor: pointer;
 transition: all 0.3s ease;
 text-decoration: none;
 display: inline-flex;
 align-items: center;
 gap: 8px;
 }
 .welcome-btn-primary {
 background: white;
 color: #667eea;
 flex: 1;
 }
 .welcome-btn-primary:hover {
 transform: translateY(-2px);
 box-shadow: 0 10px 20px rgba(0, 0, 0, 0.2);
 }
 .welcome-btn-secondary {
 background: rgba(255, 255, 255, 0.2);
 color: white;
 border: 2px solid white;
 }
 .welcome-btn-secondary:hover {
 background: rgba(255, 255, 255, 0.3);
 }
 .welcome-progress {
 height: 3px;
 background: rgba(255, 255, 255, 0.3);
 border-radius: 2px;
 margin-top: 20px;
 overflow: hidden;
 }
 .welcome-progress-bar {
 height: 100%;
 background: white;
 animation: progressFill 3s ease-out forwards;
 }
 @keyframes progressFill {
 from {
 width: 0%;
 }
 to {
 width: 100%;
 }
 }
 @keyframes fadeInUp {
 from {
 opacity: 0;
 transform: translateY(20px);
 }
 to {
 opacity: 1;
 transform: translateY(0);
 }
 }
 [data-theme="dark"] .welcome-modal {
 background: linear-gradient(135deg, #1e1b4b 0%, #2d2a5e 100%);
 }
 [data-theme="dark"] .welcome-btn-primary {
 background: #e2e8f0;
 color: #1e1b4b;
 }
 @media (max-width: 480px) {
 .welcome-modal {
 padding: 40px 24px;
 }
 .welcome-title {
 font-size: 24px;
 }
 .welcome-subtitle {
 font-size: 16px;
 }
 .welcome-actions {
 flex-direction: column;
 }
 .welcome-btn {
 width: 100%;
 }
 }
 `;
 document.head.appendChild(style);
 }
 show(userData = {}) {
 const {
 firstName = 'Utilisateur',
 lastName = '',
 role = 'user',
 redirectUrl = '/user/dashboard.html',
 duration = 3000
 } = userData;
 const overlay = document.createElement('div');
 overlay.className = 'welcome-overlay';
 overlay.innerHTML = `
 <div class="welcome-modal">
 <div class="welcome-icon">👋</div>
 <h1 class="welcome-title">Bienvenue !</h1>
 <p class="welcome-subtitle">Connexion réussie</p>
 <div class="welcome-user-info">
 <div class="welcome-user-name">${firstName} ${lastName}</div>
 <div class="welcome-user-role">
 ${role === 'admin' ? '👑 Administrateur' : '👤 Utilisateur'}
 </div>
 </div>
 <p class="welcome-message">
 ${role === 'admin' 
 ? 'Vous avez accès à tous les outils d\'administration. Gérez les utilisateurs, consultez les statistiques et bien plus encore !'
 : 'Vous êtes maintenant connecté. Explorez votre tableau de bord et commencez à utiliser la plateforme !'}
 </p>
 <div class="welcome-actions">
 <button class="welcome-btn welcome-btn-primary" onclick="window.location.href = '${redirectUrl}'">
 Accéder au dashboard →
 </button>
 </div>
 <div class="welcome-progress">
 <div class="welcome-progress-bar"></div>
 </div>
 </div>
 `;
 document.body.appendChild(overlay);
 requestAnimationFrame(() => {
 overlay.classList.add('show');
 });
 setTimeout(() => {
 this.hide(overlay);
 window.location.href = redirectUrl;
 }, duration);
 overlay.addEventListener('click', (e) => {
 if (e.target === overlay) {
 this.hide(overlay);
 window.location.href = redirectUrl;
 }
 });
 return overlay;
 }
 hide(overlay) {
 overlay.classList.remove('show');
 setTimeout(() => {
 if (overlay.parentNode) {
 overlay.parentNode.removeChild(overlay);
 }
 }, 300);
 }
}
const welcome = new WelcomeModal();
if (typeof module !== 'undefined' && module.exports) {
 module.exports = { WelcomeModal, welcome };
}