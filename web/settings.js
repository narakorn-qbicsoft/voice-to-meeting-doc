// ==================== Settings Modal ====================
const $$ = (id) => document.getElementById(id);
const SETTINGS_FIELDS = [
  "transcribe_provider", "whisper_model", "whisper_device", "whisper_compute_type",
  "summary_provider", "summary_model", "openai_base_url",
  "max_upload_mb", "default_language",
];

const PRESETS = {
  openai: {
    transcribe_provider: "local",
    summary_provider: "openai",
    summary_model: "gpt-4o-mini",
    openai_base_url: "",
  },
  ollama: {
    transcribe_provider: "local",
    summary_provider: "openai",
    summary_model: "gemma3:4b",
    openai_base_url: "http://localhost:11434/v1",
    openai_api_key: "ollama",
  },
  groq: {
    transcribe_provider: "local",
    summary_provider: "openai",
    summary_model: "llama-3.3-70b-versatile",
    openai_base_url: "https://api.groq.com/openai/v1",
  },
  openrouter: {
    transcribe_provider: "local",
    summary_provider: "openai",
    summary_model: "meta-llama/llama-3.3-70b-instruct:free",
    openai_base_url: "https://openrouter.ai/api/v1",
  },
  local: {
    transcribe_provider: "local",
    summary_provider: "none",
    summary_model: "",
    openai_base_url: "",
  },
};

const TOKEN_KEY = "v2d_admin_token";
function getToken() { return localStorage.getItem(TOKEN_KEY) || ""; }
function setToken(t) { if (t) localStorage.setItem(TOKEN_KEY, t); else localStorage.removeItem(TOKEN_KEY); }
function authHeaders() { const t = getToken(); return t ? { "X-Admin-Token": t } : {}; }

// ==================== Provider badge ====================
async function refreshProviderBadge() {
  try {
    const r = await fetch("/api/health");
    const h = await r.json();
    const badge = $$("provider-badge");
    if (!badge) return;
    badge.innerHTML = `
      <span class="badge badge-tx">🗣️ ${h.transcribe_provider}/${h.whisper_model}</span>
      <span class="badge badge-sm">🤖 ${h.summary_provider}${h.summary_provider === "openai" ? " · " + (h.summary_model || "") : ""}</span>
      ${h.auth_required ? '<span class="badge badge-lock">🔒 Admin</span>' : ''}
      <span class="badge badge-ver">v${h.version}</span>
    `;
  } catch (e) { console.error("badge refresh failed", e); }
}

// ==================== Modal Open/Close ====================
function initSettings() {
  const modal = $$("settings-modal");
  const openBtn = $$("open-settings");
  const closeBtn = $$("close-settings");
  if (!modal || !openBtn) {
    console.error("Settings modal elements missing");
    return;
  }

  openBtn.addEventListener("click", openSettings);
  closeBtn.addEventListener("click", closeSettings);
  modal.querySelector(".modal-backdrop").addEventListener("click", closeSettings);
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape" && !modal.classList.contains("hidden")) closeSettings();
  });

  $$("settings-form").addEventListener("submit", saveSettings);
  $$("test-btn").addEventListener("click", testConnection);
  $$("reset-btn").addEventListener("click", resetSettings);

  document.querySelectorAll(".preset").forEach((btn) => {
    btn.addEventListener("click", () => applyPreset(btn));
  });

  refreshProviderBadge();
}

async function openSettings() {
  const modal = $$("settings-modal");
  modal.classList.remove("hidden");
  try {
    const h = await fetch("/api/health").then(r => r.json());
    const authSection = $$("auth-section");
    if (h.auth_required) {
      authSection.classList.remove("hidden");
      $$("admin-token").value = getToken();
    } else {
      authSection.classList.add("hidden");
    }
  } catch (e) {}
  await loadSettings();
}

function closeSettings() {
  $$("settings-modal").classList.add("hidden");
}

// ==================== Load / Save ====================
async function loadSettings() {
  try {
    const r = await fetch("/api/settings", { headers: authHeaders() });
    if (r.status === 401) {
      $$("auth-section").classList.remove("hidden");
      showTestResult(false, "❌ ต้องใส่ Admin Token ก่อน");
      return;
    }
    const data = await r.json();
    const s = data.settings;
    SETTINGS_FIELDS.forEach((k) => {
      const el = $$(k);
      if (el && s[k] != null) el.value = s[k];
    });
    $$("openai_api_key").value = "";
    $$("api-key-status").textContent = s.openai_api_key_set
      ? `🔑 มี key เก็บอยู่: ${s.openai_api_key} (เว้นว่าง = คงค่าเดิม)`
      : "⚠️ ยังไม่มี API Key";
  } catch (e) {
    showTestResult(false, "Load error: " + e.message);
  }
}

async function saveSettings(e) {
  e.preventDefault();
  const t = $$("admin-token").value.trim();
  if (t) setToken(t);

  const patch = collectPatch();
  try {
    const r = await fetch("/api/settings", {
      method: "POST",
      headers: { "Content-Type": "application/json", ...authHeaders() },
      body: JSON.stringify(patch),
    });
    if (!r.ok) throw new Error((await r.json()).detail || r.statusText);
    showTestResult(true, "✅ บันทึกแล้ว — มีผลทันที");
    refreshProviderBadge();
    await loadSettings();
  } catch (err) {
    showTestResult(false, "❌ " + err.message);
  }
}

async function testConnection() {
  showTestResult(null, "⏳ กำลังบันทึก + ทดสอบ...");
  try {
    const patch = collectPatch();
    await fetch("/api/settings", {
      method: "POST",
      headers: { "Content-Type": "application/json", ...authHeaders() },
      body: JSON.stringify(patch),
    });
    const r = await fetch("/api/settings/test", { method: "POST", headers: authHeaders() });
    const data = await r.json();
    showTestResult(data.ok, data.message);
    refreshProviderBadge();
  } catch (e) {
    showTestResult(false, "❌ " + e.message);
  }
}

async function resetSettings() {
  if (!confirm("ลบค่าที่ตั้งใน UI ทั้งหมด แล้วกลับไปใช้ค่าจาก .env?")) return;
  try {
    const r = await fetch("/api/settings/reset", { method: "POST", headers: authHeaders() });
    if (!r.ok) throw new Error((await r.json()).detail || r.statusText);
    showTestResult(true, "↩️ Reset แล้ว");
    await loadSettings();
    refreshProviderBadge();
  } catch (e) {
    showTestResult(false, "❌ " + e.message);
  }
}

function collectPatch() {
  const patch = {};
  SETTINGS_FIELDS.forEach((k) => { patch[k] = $$(k).value; });
  const newKey = $$("openai_api_key").value.trim();
  if (newKey) patch["openai_api_key"] = newKey;
  return patch;
}

function applyPreset(btn) {
  const preset = PRESETS[btn.dataset.preset];
  if (!preset) return;
  Object.entries(preset).forEach(([k, v]) => {
    const el = $$(k);
    if (el) el.value = v;
  });
  showTestResult(null, `🎚️ โหลด preset "${btn.textContent.trim()}" — กรอก API Key (ถ้ายังไม่มี) แล้วกด บันทึก`);
}

function showTestResult(ok, msg) {
  const el = $$("test-result");
  el.classList.remove("hidden", "ok", "fail", "info");
  el.classList.add(ok === true ? "ok" : ok === false ? "fail" : "info");
  el.textContent = msg;
}

// init เมื่อ DOM พร้อม
if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", initSettings);
} else {
  initSettings();
}
