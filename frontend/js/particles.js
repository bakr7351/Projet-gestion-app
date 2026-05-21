(function () {
 const wrapper = document.createElement("div");
 wrapper.id = "wave-bg";
 wrapper.innerHTML = `
 <svg class="wave wave-1" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1440 320" preserveAspectRatio="none">
 <path fill="rgba(255,255,255,0.06)" d="
 M0,160 C180,220 360,80 540,160 C720,240 900,80 1080,160 C1260,240 1350,120 1440,160 L1440,320 L0,320 Z
 "/>
 </svg>
 <svg class="wave wave-2" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1440 320" preserveAspectRatio="none">
 <path fill="rgba(255,255,255,0.04)" d="
 M0,200 C200,120 400,260 600,200 C800,140 1000,260 1200,200 C1320,160 1380,220 1440,200 L1440,320 L0,320 Z
 "/>
 </svg>
 <svg class="wave wave-3" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1440 320" preserveAspectRatio="none">
 <path fill="rgba(255,255,255,0.03)" d="
 M0,240 C240,180 480,300 720,240 C960,180 1200,300 1440,240 L1440,320 L0,320 Z
 "/>
 </svg>
 <svg class="wave wave-top-1" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1440 320" preserveAspectRatio="none">
 <path fill="rgba(255,255,255,0.04)" d="
 M0,80 C360,160 720,0 1080,80 C1260,120 1380,60 1440,80 L1440,0 L0,0 Z
 "/>
 </svg>
 `;
 document.body.prepend(wrapper);
 const style = document.createElement("style");
 style.textContent = `
 #wave-bg {
 position: fixed;
 inset: 0;
 pointer-events: none;
 z-index: 0;
 overflow: hidden;
 }
 .wave {
 position: absolute;
 width: 200%;
 height: 180px;
 bottom: 0;
 left: 0;
 }
 .wave-top-1 {
 position: absolute;
 width: 200%;
 height: 120px;
 top: 0;
 left: 0;
 }
 .wave-1 {
 animation: waveMove 10s linear infinite;
 bottom: 0;
 }
 .wave-2 {
 animation: waveMove 14s linear infinite reverse;
 bottom: 20px;
 }
 .wave-3 {
 animation: waveMove 18s linear infinite;
 bottom: 40px;
 }
 .wave-top-1 {
 animation: waveMove 12s linear infinite reverse;
 }
 @keyframes waveMove {
 0% { transform: translateX(0); }
 100% { transform: translateX(-50%); }
 }
 .bubble {
 position: absolute;
 border-radius: 50%;
 background: rgba(255,255,255,0.07);
 animation: bubbleRise linear infinite;
 pointer-events: none;
 }
 @keyframes bubbleRise {
 0% { transform: translateY(0) scale(1); opacity: 0; }
 10% { opacity: 1; }
 90% { opacity: .6; }
 100% { transform: translateY(-100vh) scale(1.3); opacity: 0; }
 }
 `;
 document.head.appendChild(style);
 function spawnBubbles() {
 const container = document.getElementById("wave-bg");
 for (let i = 0; i < 18; i++) {
 const b = document.createElement("div");
 b.className = "bubble";
 const size = Math.random() * 40 + 10;
 b.style.cssText = `
 width: ${size}px;
 height: ${size}px;
 left: ${Math.random() * 100}%;
 bottom: ${Math.random() * 20}%;
 animation-duration: ${Math.random() * 12 + 8}s;
 animation-delay: ${Math.random() * 10}s;
 `;
 container.appendChild(b);
 }
 }
 spawnBubbles();
})();