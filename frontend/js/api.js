const API_BASE = "http://127.0.0.1:5000/api";
function getToken() {
 return localStorage.getItem("access_token");
}
function setToken(token) {
 localStorage.setItem("access_token", token);
}
function clearToken() {
 localStorage.removeItem("access_token");
 localStorage.removeItem("user_role");
}
async function apiFetch(endpoint, options = {}) {
 const token = getToken();
 const headers = { "Content-Type": "application/json", ...(options.headers || {}) };
 if (token) headers["Authorization"] = `Bearer ${token}`;
 const res = await fetch(`${API_BASE}${endpoint}`, { ...options, headers });
 const data = await res.json().catch(() => ({}));
 if (res.status === 401) {
 clearToken();
 window.location.href = "/user/login.html";
 return;
 }
 return { ok: res.ok, status: res.status, data };
}
const Auth = {
 signup: (payload) => apiFetch("/auth/signup", { method: "POST", body: JSON.stringify(payload) }),
 login: (payload) => apiFetch("/auth/login", { method: "POST", body: JSON.stringify(payload) }),
 verifyEmail: (token) => apiFetch("/auth/verify-email", { method: "POST", body: JSON.stringify({ token }) }),
 resendVerification: (email) => apiFetch("/auth/resend-verification", { method: "POST", body: JSON.stringify({ email }) }),
 forgotPassword: (email) => apiFetch("/auth/forgot-password", { method: "POST", body: JSON.stringify({ email }) }),
 resetPassword: (token, password) => apiFetch("/auth/reset-password", { method: "POST", body: JSON.stringify({ token, password }) }),
};
const UserAPI = {
 dashboard: () => apiFetch("/user/dashboard"),
 getProfile: () => apiFetch("/user/profile"),
 updateProfile: (payload) => apiFetch("/user/profile", { method: "PUT", body: JSON.stringify(payload) }),
 changePassword: (payload) => apiFetch("/user/change-password", { method: "PUT", body: JSON.stringify(payload) }),
 loginHistory: () => apiFetch("/user/login-history"),
 history: () => apiFetch("/user/history"),
 logoutAll: () => apiFetch("/user/logout-all", { method: "POST" }),
};
const AdminAPI = {
 dashboard: () => apiFetch("/admin/dashboard"),
 systemMetrics: () => apiFetch("/admin/system-metrics"),
 listUsers: (search = "") => apiFetch(`/admin/users?search=${encodeURIComponent(search)}`),
 getUser: (id) => apiFetch(`/admin/users/${id}`),
 updateStatus: (id, statut) => apiFetch(`/admin/users/${id}/status`, { method: "PUT", body: JSON.stringify({ statut }) }),
 promote: (id) => apiFetch(`/admin/users/${id}/promote`, { method: "PUT" }),
 deleteUser: (id) => apiFetch(`/admin/users/${id}`, { method: "DELETE" }),
 notify: (id, content) => apiFetch(`/admin/users/${id}/notify`, { method: "POST", body: JSON.stringify({ content }) }),
 auditLog: () => apiFetch("/admin/audit-log"),
 archive: () => apiFetch("/admin/archive"),
 ipRecords: () => apiFetch("/admin/ip-records"),
 banIP: (ip) => apiFetch("/admin/ip/ban", { method: "POST", body: JSON.stringify({ ip }) }),
};
const CalculationsAPI = {
 absorption: (payload) => apiFetch("/calculations/absorption", { method: "POST", body: JSON.stringify(payload) }),
 desorption: (payload) => apiFetch("/calculations/desorption", { method: "POST", body: JSON.stringify(payload) }),
 exportAbsorption: (results) => apiFetch("/calculations/export/absorption", { method: "POST", body: JSON.stringify({ results }) }),
 exportDesorption: (results) => apiFetch("/calculations/export/desorption", { method: "POST", body: JSON.stringify({ results }) }),
 history: () => apiFetch("/calculations/history"),
};
async function apiCall(endpoint, method = 'GET', data = null) {
 const token = getToken();
 const headers = { "Content-Type": "application/json" };
 if (token) headers["Authorization"] = `Bearer ${token}`;
 const options = { method, headers };
 if (data && method !== 'GET') {
 options.body = JSON.stringify(data);
 }
 const response = await fetch(`${API_BASE}${endpoint}`, options);
 if (response.status === 401) {
 clearToken();
 window.location.href = "/user/login.html";
 return;
 }
 return await response.json();
}