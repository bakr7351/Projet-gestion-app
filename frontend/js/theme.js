(function () {
 const STORAGE_KEY = "absorption_theme";
 function getTheme() {
 return localStorage.getItem(STORAGE_KEY) || "light";
 }
 function applyTheme(theme) {
 document.documentElement.setAttribute("data-theme", theme);
 localStorage.setItem(STORAGE_KEY, theme);
 const icon = theme === "dark" ? "☀️" : "🌙";
 document.querySelectorAll(".theme-toggle").forEach(btn => {
 btn.innerHTML = icon;
 btn.title = theme === "dark" ? "Mode clair" : "Mode sombre";
 });
 document.querySelectorAll(".theme-toggle-inline").forEach(btn => {
 btn.innerHTML = icon;
 btn.title = theme === "dark" ? "Mode clair" : "Mode sombre";
 });
 }
 function toggleTheme() {
 applyTheme(getTheme() === "dark" ? "light" : "dark");
 }
 applyTheme(getTheme());
 document.addEventListener("DOMContentLoaded", () => {
 applyTheme(getTheme());
 document.querySelectorAll(".theme-toggle").forEach(btn => {
 if (!btn.getAttribute("onclick")) {
 btn.addEventListener("click", toggleTheme);
 }
 });
 if (!document.querySelector(".topbar") && !document.querySelector(".sidebar") && !document.querySelector(".navbar") && !document.querySelector(".top-bar")) {
 const btn = document.createElement("button");
 btn.className = "theme-toggle";
 btn.addEventListener("click", toggleTheme);
 document.body.appendChild(btn);
 }
 });
 window.toggleTheme = toggleTheme;
 window.applyTheme = applyTheme;
 window.getTheme = getTheme;
})();