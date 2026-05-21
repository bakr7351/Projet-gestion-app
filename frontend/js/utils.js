function showAlert(el, message, type = "error") {
 el.textContent = message;
 el.className = `alert alert-${type} show`;
}
function hideAlert(el) {
 el.className = "alert";
}
function showFieldError(inputEl, errorEl, message) {
 inputEl.classList.add("error");
 errorEl.textContent = message;
 errorEl.classList.add("show");
}
function clearFieldError(inputEl, errorEl) {
 inputEl.classList.remove("error");
 errorEl.classList.remove("show");
}
function setLoading(btn, spinnerEl, loading) {
 btn.disabled = loading;
 spinnerEl.classList.toggle("show", loading);
}
function statusBadge(statut) {
 const labels = {
 actif: "Actif", non_verifie: "Non vérifié",
 desactive: "Désactivé", banni: "Banni",
 };
 return `<span class="badge badge-${statut}">${labels[statut] || statut}</span>`;
}
function roleBadge(role) {
 return `<span class="badge badge-${role}">${role === "admin" ? "Admin" : "Utilisateur"}</span>`;
}
function formatDate(iso) {
 if (!iso) return "—";
 return new Date(iso).toLocaleString("fr-FR", { dateStyle: "short", timeStyle: "short" });
}
function requireAuth(loginPath) {
 if (!localStorage.getItem("access_token")) {
 window.location.href = "/user/login.html";
 }
}
function requireAdmin(loginPath) {
 if (!localStorage.getItem("access_token")) {
 window.location.href = "/user/login.html";
 return;
 }
 if (localStorage.getItem("user_role") !== "admin") {
 window.location.href = "/user/dashboard.html";
 }
}
function decodeJWT(token) {
 try {
 const payload = token.split(".")[1];
 return JSON.parse(atob(payload));
 } catch {
 return null;
 }
}