/* Growth & Lead Intelligence Platform - frontend SPA.
   No build step required: plain JS + Tailwind CDN + Chart.js CDN so the
   whole app can be opened/served without npm/network access. Every
   number rendered here comes from a live API call - see api.js. */

const State = {
  user: JSON.parse(localStorage.getItem("user") || "null"),
  currentDatasetId: localStorage.getItem("current_dataset_id") || null,
  sidebarWidth: Number(localStorage.getItem("sidebar_width")) || 252,
  sidebarResizeHandler: null,
  charts: {},
};

function setUser(user) {
  State.user = user;
  localStorage.setItem("user", JSON.stringify(user));
}

function activityStorageKey() {
  return `growth_intel_activity_${State.user?.id || State.user?.email || "guest"}`;
}

function logActivity(message) {
  if (!State.user) return;
  const key = activityStorageKey();
  let activity = [];
  try {
    activity = JSON.parse(localStorage.getItem(key) || "[]");
  } catch (error) {
    console.error("Could not read recent activity.", error);
  }
  activity.unshift({ message, timestamp: new Date().toISOString() });
  localStorage.setItem(key, JSON.stringify(activity.slice(0, 30)));
}

function setCurrentDataset(id) {
  if (id && id !== State.currentDatasetId) {
    const selected = document.querySelector("#dataset-picker option:checked")?.textContent.trim();
    logActivity(`Selected dataset${selected ? `: ${selected}` : ""}`);
  }
  State.currentDatasetId = id;
  localStorage.setItem("current_dataset_id", id || "");
}

function getNumberLocale() {
  return window.GrowthI18n?.getLocale() || "en-US";
}

function toast(message, type = "info") {
  const el = document.createElement("div");
  el.className = `toast ${type}`;
  el.textContent = message;
  document.body.appendChild(el);
  setTimeout(() => el.remove(), 4000);
}

function fmtNum(v, digits = 0) {
  if (v === null || v === undefined || Number.isNaN(v)) return "—";
  return Number(v).toLocaleString(getNumberLocale(), { maximumFractionDigits: digits });
}
function fmtMoney(v) {
  if (v === null || v === undefined) return "—";
  return "$" + Number(v).toLocaleString(getNumberLocale(), { maximumFractionDigits: 0 });
}
function fmtPct(v) {
  if (v === null || v === undefined) return "—";
  return Number(v).toLocaleString(getNumberLocale(), { maximumFractionDigits: 1 }) + "%";
}

/* ---------------------------- Router ---------------------------- */
const Router = {
  routes: {},
  register(name, renderFn, { requiresAuth = true } = {}) {
    this.routes[name] = { renderFn, requiresAuth };
  },
  go(name, params = {}) {
    location.hash = `#${name}${params.id ? "/" + params.id : ""}`;
  },
  async render() {
    const hash = location.hash.replace("#", "") || (State.user ? "dashboard" : "login");
    const [name, id] = hash.split("/");
    const route = this.routes[name] || this.routes["dashboard"];

    if (route.requiresAuth && !State.user) {
      location.hash = "#login";
      return;
    }
    if (!route.requiresAuth && State.user && (name === "login" || name === "register")) {
      location.hash = "#dashboard";
      return;
    }

    const app = document.getElementById("app");
    if (route.requiresAuth) {
      app.innerHTML = Shell(name);
      setupSidebarResizer(app.querySelector(".app-shell"));
      const outlet = document.getElementById("outlet");
      outlet.innerHTML = `<div class="flex justify-center py-24"><div class="spinner"></div></div>`;
      try {
        await route.renderFn(outlet, id);
      } catch (err) {
        outlet.innerHTML = ErrorState(err.message);
      }
    } else {
      app.innerHTML = `<div id="outlet"></div>`;
      await route.renderFn(document.getElementById("outlet"), id);
    }
    window.GrowthI18n?.translate(app);
  },
};
window.addEventListener("hashchange", () => Router.render());

/* ---------------------------- Shell (nav) ---------------------------- */
function Shell(active) {
  const activeLabel = {
    dashboard: "Overview",
    upload: "Upload dataset",
    explorer: "Data explorer",
    funnel: "Funnel analytics",
    segments: "Lead segmentation",
    kpis: "KPI analytics",
    insights: "AI insights",
    chat: "AI analyst",
    experiments: "Experiments",
    reports: "Reports",
    settings: "Settings",
  }[active] || "Workspace";
  const nav = [
    ["dashboard", "Dashboard", "◫"],
    ["upload", "Upload dataset", "↥"],
    ["explorer", "Data explorer", "⌕"],
    ["funnel", "Funnel analytics", "▽"],
    ["segments", "Lead segments", "◈"],
    ["kpis", "KPI analytics", "↗"],
    ["insights", "AI insights", "✳"],
    ["chat", "Ask AI analyst", "◌"],
    ["experiments", "Experiments", "⌘"],
    ["reports", "Reports", "▤"],
    ["settings", "Settings", "⚙"],
  ];
  return `
  <div class="app-shell" style="--sidebar-width: ${State.sidebarWidth}px">
    <aside class="app-sidebar">
      <a href="#dashboard" class="brand-lockup">
        <span class="brand-mark">g</span>
        <span><span class="brand-name">growth<span class="brand-name-accent">intel</span></span>
        <span class="brand-caption">${escapeHtml(State.user?.organization_name || "Growth workspace")}</span></span>
      </a>
      <div class="nav-caption">WORKSPACE</div>
      <nav class="app-nav">
        ${nav.slice(0, 6).map(([key, label, icon]) => `
          <a href="#${key}" class="nav-link ${active === key ? "active" : ""}">
            <span class="nav-icon">${icon}</span><span>${label}</span>
          </a>`).join("")}
      </nav>
      <div class="nav-caption nav-caption-tools">TOOLS</div>
      <nav class="app-nav">
        ${nav.slice(6, 10).map(([key, label, icon]) => `
          <a href="#${key}" class="nav-link ${active === key ? "active" : ""}">
            <span class="nav-icon">${icon}</span><span>${label}</span>
          </a>`).join("")}
      </nav>
      <div class="sidebar-spacer"></div>
      <div class="sidebar-bottom">
        <a href="#settings" class="nav-link ${active === "settings" ? "active" : ""}">
          <span class="nav-icon">⚙</span><span>Settings</span>
        </a>
        <button onclick="Actions.logout()" class="nav-link logout-link">
          <span class="nav-icon">↪</span><span>Log out</span>
        </button>
        <div class="sidebar-user">
          <span class="user-avatar">${escapeHtml((State.user?.full_name || State.user?.email || "U").slice(0, 1).toUpperCase())}</span>
          <span class="user-details"><strong>${escapeHtml(State.user?.full_name || "Workspace user")}</strong><small>${escapeHtml(State.user?.email || "")}</small></span>
        </div>
      </div>
    </aside>
    <div class="sidebar-resizer" role="separator" aria-orientation="vertical" aria-label="Resize navigation panel" tabindex="0"></div>
    <div class="app-main">
      <header class="mobile-header">
        <a href="#dashboard" class="mobile-brand"><span class="brand-mark">g</span><span>growth<span class="brand-name-accent">intel</span></span></a>
        <select aria-label="Navigate" onchange="Router.go(this.value)">
          ${nav.map(([key, label]) => `<option value="${key}" ${active === key ? "selected" : ""}>${label}</option>`).join("")}
        </select>
        <button onclick="Actions.logout()" class="mobile-logout" aria-label="Log out">Log out</button>
      </header>
      <header class="desktop-topbar">
        <div class="topbar-page">${activeLabel}</div>
        <div class="topbar-right"><span class="live-indicator"></span> Live workspace <span class="topbar-divider"></span><span class="topbar-date">${new Date().toLocaleDateString(getNumberLocale(), { month: "short", day: "numeric", year: "numeric" })}</span></div>
      </header>
      <main class="app-content">
        <div id="outlet"></div>
      </main>
    </div>
  </div>`;
}

function setupSidebarResizer(shell) {
  if (State.sidebarResizeHandler) {
    window.removeEventListener("resize", State.sidebarResizeHandler);
  }
  if (!shell) return;

  const resizer = shell.querySelector(".sidebar-resizer");
  const minWidth = 190;
  const maxWidth = () => Math.max(minWidth, Math.min(420, shell.clientWidth - 370));
  let width = Math.min(Math.max(State.sidebarWidth, minWidth), maxWidth());

  const applyWidth = (nextWidth, persist = false) => {
    width = Math.min(Math.max(nextWidth, minWidth), maxWidth());
    shell.style.setProperty("--sidebar-width", `${width}px`);
    resizer.setAttribute("aria-valuemin", String(minWidth));
    resizer.setAttribute("aria-valuemax", String(maxWidth()));
    resizer.setAttribute("aria-valuenow", String(Math.round(width)));
    if (persist) {
      State.sidebarWidth = width;
      localStorage.setItem("sidebar_width", String(Math.round(width)));
    }
  };

  resizer.addEventListener("pointerdown", (event) => {
    if (event.button !== 0) return;
    event.preventDefault();
    resizer.setPointerCapture(event.pointerId);
  });
  resizer.addEventListener("pointermove", (event) => {
    if (resizer.hasPointerCapture(event.pointerId)) {
      applyWidth(event.clientX - shell.getBoundingClientRect().left);
    }
  });
  resizer.addEventListener("pointerup", (event) => {
    if (resizer.hasPointerCapture(event.pointerId)) {
      resizer.releasePointerCapture(event.pointerId);
      applyWidth(width, true);
    }
  });
  resizer.addEventListener("pointercancel", () => applyWidth(width, true));
  resizer.addEventListener("keydown", (event) => {
    const step = event.shiftKey ? 32 : 12;
    if (event.key === "ArrowLeft") applyWidth(width - step, true);
    else if (event.key === "ArrowRight") applyWidth(width + step, true);
    else if (event.key === "Home") applyWidth(minWidth, true);
    else if (event.key === "End") applyWidth(maxWidth(), true);
    else return;
    event.preventDefault();
  });

  State.sidebarResizeHandler = () => applyWidth(width);
  window.addEventListener("resize", State.sidebarResizeHandler);
  applyWidth(width);
}

function ErrorState(message) {
  return `<div class="card p-8 text-center">
    <div class="text-3xl mb-2">⚠️</div>
    <div class="font-semibold text-slate-800 mb-1">Something went wrong</div>
    <div class="text-sm text-slate-500">${escapeHtml(message)}</div>
  </div>`;
}
function EmptyState(title, subtitle, cta) {
  return `<div class="card p-12 text-center">
    <div class="text-3xl mb-2">📭</div>
    <div class="font-semibold text-slate-800 mb-1">${title}</div>
    <div class="text-sm text-slate-500 mb-4">${subtitle}</div>
    ${cta || ""}
  </div>`;
}
function escapeHtml(str) {
  const div = document.createElement("div");
  div.textContent = str ?? "";
  return div.innerHTML;
}

/* ---------------------------- Actions ---------------------------- */
const Actions = {
  logout() {
    logActivity("Signed out");
    Api.setToken(null);
    setUser(null);
    setCurrentDataset(null);
    Router.go("login");
  },
};

/* ---------------------------- Auth Pages ---------------------------- */
function LoginPage(outlet) {
  outlet.innerHTML = `
  <div class="auth-page">
    <section class="auth-story">
      <a href="#login" class="auth-brand"><span class="brand-mark">g</span><span>growth<span>intel</span></span></a>
      <div class="auth-story-copy">
        <div class="auth-eyebrow"><span></span> YOUR NEXT GROWTH CHAPTER</div>
        <h1>Turn your data<br />into <span>momentum.</span></h1>
        <p>One clear view of your leads, performance, and what to do next. Make confident moves with the whole picture in focus.</p>
        <div class="auth-benefits">
          <div><span class="benefit-icon">↗</span><span><strong>See what’s working</strong><small>Get a sharper view of performance</small></span></div>
          <div><span class="benefit-icon">◈</span><span><strong>Find your next opportunity</strong><small>Turn insights into action</small></span></div>
        </div>
      </div>
      <div class="auth-preview" aria-hidden="true">
        <div class="preview-topline"><span><i></i> GROWTH PULSE</span><span class="preview-period">YOUR WORKSPACE</span></div>
        <div class="preview-title">Progress, at a glance</div>
        <div class="preview-subtitle">Your data. A clearer direction.</div>
        <div class="preview-chart">
          <div class="preview-y-axis"><span></span><span></span><span></span><span></span></div>
          <svg viewBox="0 0 480 118" preserveAspectRatio="none">
            <defs><linearGradient id="preview-fill" x1="0" x2="0" y1="0" y2="1"><stop offset="0%" stop-color="#9f8cff" stop-opacity=".34"/><stop offset="100%" stop-color="#9f8cff" stop-opacity="0"/></linearGradient></defs>
            <path d="M0 96 C34 87 47 91 78 73 S130 81 160 57 S211 68 244 48 S297 58 328 35 S380 44 411 22 S456 29 480 8 L480 118 L0 118 Z" fill="url(#preview-fill)"/>
            <path d="M0 96 C34 87 47 91 78 73 S130 81 160 57 S211 68 244 48 S297 58 328 35 S380 44 411 22 S456 29 480 8" fill="none" stroke="#a999ff" stroke-width="3" vector-effect="non-scaling-stroke"/>
            <circle cx="411" cy="22" r="5" fill="#fff" stroke="#a999ff" stroke-width="3" vector-effect="non-scaling-stroke"/>
          </svg>
        </div>
        <div class="preview-footer"><span>From first signal</span><span>To your next big move <b>↗</b></span></div>
      </div>
      <div class="auth-story-footer"><span>BUILT FOR THE CURIOUS AND AMBITIOUS</span><span>Make every insight count.</span></div>
    </section>
    <section class="auth-form-side">
      <div class="auth-form-wrap">
        <div class="auth-mobile-brand"><span class="brand-mark">g</span><span>growth<span>intel</span></span></div>
        <div class="auth-form-heading">
          <span class="auth-welcome-mark">✳</span>
          <div class="auth-form-kicker">WELCOME BACK</div>
          <h2>Good to see you.</h2>
          <p>Sign in to pick up where your next chapter begins.</p>
        </div>
        <form id="login-form" class="auth-login-form">
          <div class="auth-field">
            <label for="login-email">Work email</label>
            <input id="login-email" required type="email" name="email" autocomplete="email" placeholder="you@company.com" />
          </div>
          <div class="auth-field">
            <label for="login-password">Password</label>
            <input id="login-password" required type="password" name="password" autocomplete="current-password" placeholder="Enter your password" />
          </div>
          <button class="btn-primary auth-submit" type="submit">Sign in <span>→</span></button>
        </form>
        <button id="show-otp-login" class="auth-mode-toggle" type="button">Sign in with an email code</button>
        <div id="otp-login-panel" class="auth-otp-panel" hidden>
          <p>We’ll email you a one-time sign-in code.</p>
          <div class="auth-field">
            <label for="otp-login-email">Work email</label>
            <input id="otp-login-email" type="email" autocomplete="email" placeholder="you@company.com" required />
          </div>
          <button id="send-login-otp" class="btn-primary auth-submit" type="button">Send sign-in code <span>→</span></button>
          <form id="otp-verify-form" class="auth-login-form" hidden>
            <div class="auth-field">
              <label for="otp-login-code">Email code</label>
              <input id="otp-login-code" type="text" inputmode="numeric" autocomplete="one-time-code" pattern="[0-9]{6}" maxlength="6" placeholder="Enter 6-digit code" required />
            </div>
            <button id="verify-login-otp" class="btn-primary auth-submit" type="submit">Verify code &amp; sign in <span>→</span></button>
          </form>
          <div id="otp-login-message" class="auth-otp-message" role="status" aria-live="polite"></div>
          <button id="back-to-password-login" class="auth-mode-toggle" type="button">Use password instead</button>
        </div>
        <div class="auth-signup">New to Growth Intel? <a href="#register">Create your workspace <span>→</span></a></div>
        <div class="auth-secure"><span>◇</span> Your workspace is private and secure</div>
      </div>
      <div class="auth-copyright">© ${new Date().getFullYear()} Growth Intel <span>·</span> A clearer path to growth</div>
    </section>
  </div>`;

  document.getElementById("login-form").addEventListener("submit", async (e) => {
    e.preventDefault();
    const fd = new FormData(e.target);
    try {
      const res = await Api.login({ email: fd.get("email"), password: fd.get("password") });
      Api.setToken(res.access_token);
      setUser(res.user);
      logActivity("Signed in");
      Router.go("dashboard");
    } catch (err) {
      toast(err.message, "error");
    }
  });

  const passwordForm = document.getElementById("login-form");
  const otpPanel = document.getElementById("otp-login-panel");
  const otpEmail = document.getElementById("otp-login-email");
  const otpMessage = document.getElementById("otp-login-message");
  const otpSendButton = document.getElementById("send-login-otp");

  document.getElementById("show-otp-login").addEventListener("click", () => {
    otpEmail.value = document.getElementById("login-email").value;
    passwordForm.hidden = true;
    document.getElementById("show-otp-login").hidden = true;
    otpPanel.hidden = false;
    otpEmail.focus();
  });
  document.getElementById("back-to-password-login").addEventListener("click", () => {
    otpPanel.hidden = true;
    passwordForm.hidden = false;
    document.getElementById("show-otp-login").hidden = false;
  });
  otpSendButton.addEventListener("click", async () => {
    if (!otpEmail.reportValidity()) return;
    otpSendButton.disabled = true;
    otpSendButton.textContent = "Sending code…";
    otpMessage.textContent = "";
    try {
      const result = await Api.requestLoginOTP(otpEmail.value.trim());
      document.getElementById("otp-verify-form").hidden = false;
      otpMessage.textContent = result.detail;
      document.getElementById("otp-login-code").focus();
    } catch (err) {
      otpMessage.textContent = err.message;
    } finally {
      otpSendButton.disabled = false;
      otpSendButton.innerHTML = "Send another code <span>→</span>";
    }
  });
  document.getElementById("otp-verify-form").addEventListener("submit", async (e) => {
    e.preventDefault();
    const verifyButton = document.getElementById("verify-login-otp");
    verifyButton.disabled = true;
    otpMessage.textContent = "";
    try {
      const res = await Api.verifyLoginOTP(otpEmail.value.trim(), document.getElementById("otp-login-code").value);
      Api.setToken(res.access_token);
      setUser(res.user);
      logActivity("Signed in with email code");
      Router.go("dashboard");
    } catch (err) {
      otpMessage.textContent = err.message;
      verifyButton.disabled = false;
    }
  });
}

function RegisterPage(outlet) {
  outlet.innerHTML = `
  <div class="min-h-screen flex items-center justify-center bg-slate-50 px-4">
    <div class="card p-8 w-full max-w-md">
      <div class="text-2xl font-bold mb-1">Create your workspace</div>
      <div class="text-sm text-slate-500 mb-6">Start analyzing your growth data in minutes</div>
      <form id="register-form" class="space-y-4">
        <div>
          <label class="text-sm font-medium">Organization name</label>
          <input required name="organization_name" class="w-full mt-1 border rounded-lg px-3 py-2" placeholder="Acme Inc" />
        </div>
        <div>
          <label class="text-sm font-medium">Full name</label>
          <input required name="full_name" class="w-full mt-1 border rounded-lg px-3 py-2" placeholder="Jane Doe" />
        </div>
        <div>
          <label class="text-sm font-medium">Email</label>
          <input required type="email" name="email" id="register-email" autocomplete="email" class="w-full mt-1 border rounded-lg px-3 py-2" placeholder="you@company.com" />
        </div>
        <button id="send-registration-code" class="btn-secondary w-full" type="button">Send verification code</button>
        <div id="registration-code-section" class="auth-field" hidden>
          <label for="registration-code">Email verification code</label>
          <input id="registration-code" type="text" inputmode="numeric" autocomplete="one-time-code" pattern="[0-9]{6}" maxlength="6" class="w-full mt-1 border rounded-lg px-3 py-2" placeholder="Enter the 6-digit code" disabled />
          <small class="auth-registration-hint">Enter the code we sent to your email before creating your workspace.</small>
          <button id="verify-registration-code" class="btn-secondary w-full mt-2" type="button" disabled>Verify code</button>
        </div>
        <div>
          <label class="text-sm font-medium">Password</label>
          <input required minlength="8" type="password" name="password" class="w-full mt-1 border rounded-lg px-3 py-2" placeholder="At least 8 characters" />
        </div>
        <button id="create-account-button" class="btn-primary w-full" type="submit" disabled>Create Account</button>
        <div id="registration-message" class="auth-otp-message" role="status" aria-live="polite"></div>
      </form>
      <div class="text-sm text-slate-500 mt-4 text-center">
        Already have an account? <a href="#login" class="text-indigo-600 font-medium">Sign in</a>
      </div>
    </div>
  </div>`;

  const registerForm = document.getElementById("register-form");
  const registrationEmail = document.getElementById("register-email");
  const registrationCode = document.getElementById("registration-code");
  const registrationSection = document.getElementById("registration-code-section");
  const registrationMessage = document.getElementById("registration-message");
  const sendCodeButton = document.getElementById("send-registration-code");
  const verifyCodeButton = document.getElementById("verify-registration-code");
  const createAccountButton = document.getElementById("create-account-button");
  let verifiedEmail = "";

  registrationEmail.addEventListener("input", () => {
    if (verifiedEmail && registrationEmail.value.trim().toLowerCase() !== verifiedEmail) {
      verifiedEmail = "";
      registrationSection.hidden = true;
      registrationCode.disabled = true;
      registrationCode.required = false;
      registrationCode.value = "";
      verifyCodeButton.disabled = true;
      createAccountButton.disabled = true;
      registrationMessage.textContent = "Email changed. Verify the new address before creating your workspace.";
    }
  });

  sendCodeButton.addEventListener("click", async () => {
    if (!registrationEmail.reportValidity()) return;
    sendCodeButton.disabled = true;
    sendCodeButton.textContent = "Sending verification code…";
    registrationMessage.textContent = "";
    try {
      const result = await Api.requestRegistrationOTP(registrationEmail.value.trim());
      verifiedEmail = registrationEmail.value.trim().toLowerCase();
      registrationCode.disabled = false;
      registrationCode.required = true;
      registrationSection.hidden = false;
      registrationCode.value = "";
      verifyCodeButton.disabled = true;
      createAccountButton.disabled = true;
      registrationMessage.textContent = result.detail;
      registrationCode.focus();
    } catch (err) {
      registrationMessage.textContent = err.message;
    } finally {
      sendCodeButton.disabled = false;
      sendCodeButton.textContent = "Send verification code";
    }
  });

  registrationCode.addEventListener("input", () => {
    createAccountButton.disabled = true;
    verifyCodeButton.disabled = !/^\d{6}$/.test(registrationCode.value) || !verifiedEmail;
  });

  verifyCodeButton.addEventListener("click", async () => {
    if (!verifiedEmail || registrationEmail.value.trim().toLowerCase() !== verifiedEmail) {
      registrationMessage.textContent = "Send a new code to the email address entered above.";
      return;
    }
    verifyCodeButton.disabled = true;
    verifyCodeButton.textContent = "Verifying code…";
    registrationMessage.textContent = "";
    try {
      const result = await Api.verifyRegistrationOTP(verifiedEmail, registrationCode.value);
      createAccountButton.disabled = false;
      registrationMessage.textContent = result.detail;
    } catch (err) {
      registrationMessage.textContent = err.message;
      verifyCodeButton.disabled = registrationCode.value.length !== 6;
    } finally {
      verifyCodeButton.textContent = "Verify code";
    }
  });

  registerForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    if (!verifiedEmail || registrationEmail.value.trim().toLowerCase() !== verifiedEmail) {
      registrationMessage.textContent = "Verify your email before creating your workspace.";
      return;
    }
    const fd = new FormData(e.target);
    createAccountButton.disabled = true;
    createAccountButton.textContent = "Creating workspace…";
    registrationMessage.textContent = "";
    try {
      const res = await Api.register({
        organization_name: fd.get("organization_name"),
        full_name: fd.get("full_name"),
        email: fd.get("email"),
        password: fd.get("password"),
      });
      Api.setToken(res.access_token);
      setUser(res.user);
      logActivity("Created a workspace");
      Router.go("dashboard");
    } catch (err) {
      registrationMessage.textContent = err.message;
      createAccountButton.disabled = false;
      createAccountButton.textContent = "Create Account";
    }
  });
}

/* ---------------------------- Dataset Picker (shared) ---------------------------- */
async function DatasetPickerBar(container, onChange) {
  const datasets = await Api.listDatasets();
  const analyzed = datasets.filter((d) => d.status === "analyzed");
  if (!analyzed.some((dataset) => dataset.id === State.currentDatasetId)) {
    setCurrentDataset(analyzed[0]?.id || null);
  }

  const bar = document.createElement("div");
  bar.className = "flex items-center gap-3 mb-6 flex-wrap";
  bar.innerHTML = `
    ${analyzed.length ? `
      <label class="text-sm font-medium text-slate-600" for="dataset-picker">Analyzed dataset:</label>
      <select id="dataset-picker" class="border rounded-lg px-3 py-2 text-sm min-w-[240px]">
        ${analyzed.map((d) => `<option value="${d.id}" ${d.id === State.currentDatasetId ? "selected" : ""}>
          ${escapeHtml(d.filename)} (${fmtNum(d.row_count)} rows)
        </option>`).join("")}
      </select>` : `
      <div class="dataset-picker-empty">
        <span>No analyzed datasets are available yet.</span>
        <a href="#upload" class="btn-primary">${datasets.length ? "Continue dataset analysis" : "Upload your first dataset"} <span>→</span></a>
      </div>`}
  `;
  container.appendChild(bar);
  const select = bar.querySelector("#dataset-picker");
  if (select) {
    select.addEventListener("change", () => {
      setCurrentDataset(select.value);
      onChange(select.value);
    });
  }
  return { datasets, selectedId: State.currentDatasetId };
}

/* ---------------------------- Dashboard ---------------------------- */
async function DashboardPage(outlet) {
  outlet.innerHTML = `<div class="dashboard-intro">
    <div><div class="eyebrow"><span class="eyebrow-line"></span> GROWTH OVERVIEW</div>
      <h1>Know your numbers.<br><span>Grow with confidence.</span></h1>
      <p>Your latest performance, funnel health, and opportunities — all in one place.</p>
    </div>
    <a href="#upload" class="btn-primary intro-action"><span>＋</span> Add dataset</a>
  </div><div id="picker-slot"></div><div id="dashboard-body"></div>`;
  const pickerSlot = document.getElementById("picker-slot");
  const { datasets, selectedId } = await DatasetPickerBar(pickerSlot, (id) => renderDashboardBody(id));
  await renderDashboardBody(selectedId, datasets);
}

async function renderDashboardBody(datasetId, datasets) {
  const body = document.getElementById("dashboard-body");
  if (!datasetId) {
    body.innerHTML = EmptyState("No analyzed dataset selected", "Upload a CSV/XLSX file and run analysis to see your dashboard.",
      `<a href="#upload" class="btn-primary">Upload Dataset</a>`);
    return;
  }
  body.innerHTML = `<div class="flex justify-center py-16"><div class="spinner"></div></div>`;

  try {
    const [kpiResp, funnelResp, trendsResp, anomaliesResp, segResp] = await Promise.all([
      Api.getKpis(datasetId),
      Api.getFunnel(datasetId),
      Api.getTrends(datasetId, 30),
      Api.getAnomalies(datasetId, 90),
      Api.getSegments(datasetId),
    ]);
    const kpi = Object.fromEntries(kpiResp.kpis.map((k) => [k.metric, k.value]));

    body.innerHTML = `
      <div class="section-heading"><div><h2>Performance at a glance</h2><p>A clear snapshot of your selected dataset</p></div><span class="dataset-live-pill"><span class="live-indicator"></span> Live data</span></div>
      <div class="grid grid-cols-2 lg:grid-cols-5 gap-4 mb-6">
        ${KpiCard("Total Leads", fmtNum(kpi.leads))}
        ${KpiCard("Overall Conversion", fmtPct(kpi.overall_conversion))}
        ${KpiCard("Revenue", fmtMoney(kpi.revenue))}
        ${KpiCard("Activation Rate", fmtPct(kpi.activation_rate), `Activated ${fmtNum(kpi.activations)} of ${fmtNum(kpi.signups)} signups`)}
        ${KpiCard("Trial → Payment", fmtPct(kpi.trial_conversion), `Paid ${fmtNum(kpi.payments)} of ${fmtNum(kpi.trials)} trials`)}
      </div>

      <div class="grid lg:grid-cols-3 gap-5 mb-6">
        <div class="card chart-card lg:col-span-2">
          <div class="chart-heading"><div><span class="chart-kicker">CONVERSION</span><div class="font-semibold">Funnel performance</div></div><span class="chart-icon">▽</span></div>
          <canvas id="funnelChart" height="140"></canvas>
        </div>
        <div class="card chart-card">
          <div class="chart-heading"><div><span class="chart-kicker">AUDIENCE</span><div class="font-semibold">Segment mix</div></div><span class="chart-icon chart-icon-purple">◈</span></div>
          <canvas id="segmentChart" height="180"></canvas>
        </div>
      </div>

      <div class="section-heading trend-section-heading"><div><h2>Trends over time</h2><p>See where momentum is building</p></div></div>
      <div class="grid lg:grid-cols-2 gap-5 mb-6">
        <div class="card chart-card">
          <div class="chart-heading"><div><span class="chart-kicker">REVENUE</span><div class="font-semibold">Revenue trend <span class="muted-period">· latest 30 days</span></div></div><span class="chart-icon chart-icon-green">$</span></div>
          <div class="trend-metric-row"><div class="trend-total" id="revenue-trend-total"></div><div class="trend-change" id="revenue-trend-change"></div></div>
          <canvas id="revenueTrendChart" height="140"></canvas>
        </div>
        <div class="card chart-card">
          <div class="chart-heading"><div><span class="chart-kicker">ACQUISITION</span><div class="font-semibold">Lead trend <span class="muted-period">· latest 30 days</span></div></div><span class="chart-icon chart-icon-blue">↗</span></div>
          <div class="trend-metric-row"><div class="trend-total" id="leads-trend-total"></div><div class="trend-change" id="leads-trend-change"></div></div>
          <canvas id="leadsTrendChart" height="140"></canvas>
        </div>
      </div>
      <div id="trend-data-guidance" class="trend-data-guidance" hidden></div>

      <div class="section-heading trend-section-heading"><div><h2>Signals &amp; opportunities</h2><p>Useful next steps from your latest data</p></div></div>
      <div class="grid lg:grid-cols-2 gap-5">
        <div class="card insight-card">
          <div class="insight-title"><span class="insight-spark">✳</span><div><span class="chart-kicker">YOUR AI ANALYST</span><div class="font-semibold">Growth insights</div></div></div>
          <div id="ai-preview" class="text-sm text-slate-600">
            <a href="#insights" class="insight-link">Generate AI insights <span>→</span></a>
          </div>
        </div>
        <div class="card insight-card">
          <div class="insight-title"><span class="alert-mark">!</span><div><span class="chart-kicker">ANOMALY MONITOR</span><div class="font-semibold">Worth a closer look</div></div></div>
          <div id="alerts-list" class="space-y-2 text-sm"></div>
        </div>
      </div>
    `;

    renderFunnelChart("funnelChart", funnelResp.stages);
    renderSegmentChart("segmentChart", segResp.segments);
    const revSeries = trendsResp.series.find((s) => s.metric === "revenue");
    const leadsSeries = trendsResp.series.find((s) => s.metric === "leads");
    renderTrendChart("revenueTrendChart", revSeries, "#4f46e5", "revenue-trend-total", "revenue-trend-change", "payment_date");
    renderTrendChart("leadsTrendChart", leadsSeries, "#0891b2", "leads-trend-total", "leads-trend-change", "signup_date");
    if (!revSeries?.points.length && !leadsSeries?.points.length) {
      const guidance = document.getElementById("trend-data-guidance");
      guidance.hidden = false;
      guidance.innerHTML = `<span class="trend-guidance-icon">i</span><span><strong>Time-series needs date data.</strong> This dataset has no mapped signup or payment dates, so there are no real daily trends to plot. Map <code>signup_date</code> for leads and <code>payment_date</code> for revenue during upload, or choose a dated dataset such as <strong>sample_data.csv</strong>.</span>`;
    }

    const alertsList = document.getElementById("alerts-list");
    if (anomaliesResp.anomalies.length === 0) {
      alertsList.innerHTML = `<div class="text-slate-400">No anomalies detected in the last 90 days. ✅</div>`;
    } else {
      alertsList.innerHTML = anomaliesResp.anomalies.slice(0, 4).map((a) => `
        <div class="p-2 rounded-lg ${a.severity === "high" ? "bg-red-50 text-red-700" : "bg-amber-50 text-amber-700"}">
          <span class="font-medium">${escapeHtml(a.metric)}</span> on ${a.date}: ${a.change_pct > 0 ? "+" : ""}${a.change_pct}%
        </div>
      `).join("");
    }

    try {
      const latest = await Api.getLatestInsights(datasetId);
      document.getElementById("ai-preview").innerHTML = `
        <p class="mb-2">${escapeHtml(latest.executive_summary)}</p>
        <a href="#insights" class="text-indigo-600 font-medium text-sm">View full insights →</a>
      `;
    } catch (_) { /* no insights generated yet - link stays as-is */ }

  } catch (err) {
    body.innerHTML = ErrorState(err.message);
  }
}

function KpiCard(label, value, footnote = "Current dataset") {
  const icon = { "Total Leads": "↗", "Overall Conversion": "%", Revenue: "$", "Activation Rate": "✳", "Trial → Payment": "→" }[label] || "·";
  return `<div class="card p-4">
    <div class="metric-topline"><span class="metric-label">${label}</span><span class="metric-icon">${icon}</span></div>
    <div class="metric-value">${value}</div>
    <div class="metric-footnote"><span class="metric-footnote-dot"></span> ${footnote}</div>
  </div>`;
}

function renderFunnelChart(canvasId, stages) {
  const ctx = document.getElementById(canvasId);
  if (State.charts[canvasId]) State.charts[canvasId].destroy();
  State.charts[canvasId] = new Chart(ctx, {
    type: "bar",
    data: {
      labels: stages.map((s) => window.GrowthI18n.translateText(s.name)),
      datasets: [{ label: window.GrowthI18n.translateText("Users"), data: stages.map((s) => s.user_count), backgroundColor: "#4f46e5" }],
    },
    options: { indexAxis: "y", plugins: { legend: { display: false } }, scales: { x: { beginAtZero: true } } },
  });
}

function renderSegmentChart(canvasId, segments) {
  const ctx = document.getElementById(canvasId);
  if (State.charts[canvasId]) State.charts[canvasId].destroy();
  const palette = ["#4f46e5", "#0891b2", "#16a34a", "#d97706", "#dc2626", "#7c3aed", "#0284c7", "#65a30d"];
  State.charts[canvasId] = new Chart(ctx, {
    type: "doughnut",
    data: {
      labels: segments.map((s) => s.name),
      datasets: [{ data: segments.map((s) => s.size), backgroundColor: segments.map((_, i) => palette[i % palette.length]) }],
    },
    options: { plugins: { legend: { position: "bottom", labels: { boxWidth: 10, font: { size: 10 } } } } },
  });
}

function renderLineChart(canvasId, series, color) {
  const ctx = document.getElementById(canvasId);
  if (State.charts[canvasId]) State.charts[canvasId].destroy();
  if (!series || series.points.length === 0) {
    ctx.getContext("2d").font = "13px sans-serif";
    ctx.getContext("2d").fillText(window.GrowthI18n.translateText("Not enough data yet"), 10, 20);
    return;
  }
  State.charts[canvasId] = new Chart(ctx, {
    type: "line",
    data: {
      labels: series.points.map((p) => p.period),
      datasets: [{ data: series.points.map((p) => p.value), borderColor: color, backgroundColor: color + "22", fill: true, tension: 0.3, pointRadius: 2 }],
    },
    options: { plugins: { legend: { display: false } }, scales: { x: { ticks: { maxTicksLimit: 6 } } } },
  });
}

function renderTrendChart(canvasId, series, color, totalId, changeId, requiredDate) {
  const total = document.getElementById(totalId);
  const change = document.getElementById(changeId);
  if (!series || series.points.length === 0) {
    total.textContent = "—";
    change.textContent = "No date data";
    change.classList.add("trend-change-empty");
    const canvas = document.getElementById(canvasId);
    canvas.replaceWith(Object.assign(document.createElement("div"), {
      className: "trend-empty-state",
      innerHTML: `<span>⌁</span><strong>No dated records available</strong><small>Map <code>${requiredDate}</code> to see this trend.</small>`,
    }));
    return;
  }

  total.textContent = canvasId === "revenueTrendChart"
    ? fmtMoney(series.current_period_total)
    : fmtNum(series.current_period_total);
  if (series.pct_change === null) {
    change.textContent = "No previous-period comparison";
    change.classList.add("trend-change-neutral");
  } else {
    const direction = series.pct_change > 0 ? "up" : series.pct_change < 0 ? "down" : "flat";
    change.textContent = `${series.pct_change > 0 ? "+" : ""}${fmtPct(series.pct_change)} vs prior 30 days`;
    change.classList.add(`trend-change-${direction}`);
  }
  renderLineChart(canvasId, series, color);
}

/* ---------------------------- Upload Page ---------------------------- */
function UploadPage(outlet) {
  outlet.innerHTML = `
    <h1 class="text-xl font-bold mb-4">Upload Dataset</h1>
    <div class="card p-6" id="upload-card">
      <p class="text-sm text-slate-500 mb-4">Upload a CSV or Excel file with lead/customer data. We'll auto-detect columns, flag data-quality issues, and let you confirm the mapping before analysis.</p>
      <input type="file" id="file-input" accept=".csv,.xlsx,.xls" class="block w-full text-sm border rounded-lg p-2" />
      <button id="upload-btn" class="btn-primary mt-4" disabled>Upload &amp; Preview</button>
    </div>
    <div id="preview-area" class="mt-6"></div>
  `;
  const fileInput = document.getElementById("file-input");
  const uploadBtn = document.getElementById("upload-btn");
  fileInput.addEventListener("change", () => { uploadBtn.disabled = !fileInput.files.length; });

  uploadBtn.addEventListener("click", async () => {
    const file = fileInput.files[0];
    if (!file) return;
    uploadBtn.disabled = true;
    uploadBtn.textContent = "Uploading…";
    try {
      const preview = await Api.uploadDataset(file);
      logActivity(`Uploaded dataset: ${file.name}`);
      renderMappingPreview(preview);
      toast("File uploaded. Review the column mapping below.", "success");
    } catch (err) {
      toast(err.message, "error");
    } finally {
      uploadBtn.disabled = false;
      uploadBtn.textContent = "Upload & Preview";
    }
  });
}

const CANONICAL_FIELDS = [
  "", "lead_id", "customer_id", "name", "email", "signup_date", "source", "campaign",
  "industry", "country", "company_size", "product", "plan", "trial_start",
  "activation_date", "payment_date", "revenue", "engagement_score",
  "number_of_sessions", "pages_viewed", "emails_opened", "support_tickets", "churn", "status",
];

function renderMappingPreview(preview) {
  const area = document.getElementById("preview-area");
  const missingPct = preview.missing_value_pct;
  area.innerHTML = `
    <div class="card p-6 mb-6">
      <div class="font-semibold mb-3">Data Quality Preview</div>
      <div class="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
        <div><div class="text-slate-500">Total Rows</div><div class="text-lg font-bold">${fmtNum(preview.total_rows)}</div></div>
        <div><div class="text-slate-500">Columns</div><div class="text-lg font-bold">${preview.columns.length}</div></div>
        <div><div class="text-slate-500">Duplicate Rows</div><div class="text-lg font-bold">${fmtNum(preview.duplicate_row_count)}</div></div>
        <div><div class="text-slate-500">Auto-mapped Columns</div><div class="text-lg font-bold">${Object.values(preview.suggested_mapping).filter(Boolean).length}/${preview.columns.length}</div></div>
      </div>
    </div>

    <div class="card p-6 mb-6">
      <div class="mapping-heading">
        <div>
          <div class="font-semibold">Confirm Column Mapping</div>
          <p>Match each source column to the field it represents. Suggested matches are preselected.</p>
        </div>
        <button id="increase-mapping-font" class="mapping-font-button" type="button" aria-label="Increase mapping text size">
          <span aria-hidden="true">A↑</span> Increase text
        </button>
      </div>
      <div class="mapping-progress" role="group" aria-label="Mapping progress">
        <div class="mapping-progress-track"><span id="mapping-progress-bar"></span></div>
        <span id="mapping-count" aria-live="polite"></span>
      </div>
      <div class="overflow-x-auto">
        <table class="w-full mapping-table">
          <thead><tr class="text-left text-slate-500 border-b">
            <th class="py-2 pr-4">Source Column</th><th class="py-2 pr-4">Detected Type</th><th class="py-2 pr-4">Missing</th><th class="py-2">Map To</th>
          </tr></thead>
          <tbody id="mapping-rows">
            ${preview.columns.map((col) => `
              <tr class="border-b last:border-0">
                <td class="py-3 pr-4 font-medium">${escapeHtml(col)}</td>
                <td class="py-2 pr-4 text-slate-500">${preview.detected_dtypes[col] || "-"}</td>
                <td class="py-2 pr-4 text-slate-500">${missingPct[col] ?? 0}%</td>
                <td class="py-2">
                  <div class="mapping-target">
                    <span class="mapping-arrow" aria-hidden="true">→</span>
                    <select data-col="${escapeHtml(col)}" aria-label="Map ${escapeHtml(col)} to a field" class="mapping-select border rounded">
                    ${CANONICAL_FIELDS.map((f) => `<option value="${f}" ${preview.suggested_mapping[col] === f ? "selected" : ""}>${f || "(unmapped)"}</option>`).join("")}
                    </select>
                  </div>
                </td>
              </tr>`).join("")}
          </tbody>
        </table>
      </div>
      <button id="confirm-mapping-btn" class="btn-primary mt-4">Confirm Mapping &amp; Run Analysis</button>
    </div>

    <div class="card p-6">
      <div class="font-semibold mb-3">Sample Rows</div>
      <div class="overflow-x-auto">
        <table class="w-full text-xs">
          <thead><tr class="text-left text-slate-500 border-b">${preview.columns.map((c) => `<th class="py-1 pr-4">${escapeHtml(c)}</th>`).join("")}</tr></thead>
          <tbody>
            ${preview.sample_rows.map((row) => `<tr class="border-b last:border-0">${preview.columns.map((c) => `<td class="py-1 pr-4">${escapeHtml(row[c] ?? "")}</td>`).join("")}</tr>`).join("")}
          </tbody>
        </table>
      </div>
    </div>
  `;

  const mappingSelects = [...area.querySelectorAll(".mapping-select")];
  const mappingCount = area.querySelector("#mapping-count");
  const mappingProgressBar = area.querySelector("#mapping-progress-bar");
  const updateMappingProgress = () => {
    const mapped = mappingSelects.filter((select) => select.value).length;
    const total = mappingSelects.length;
    mappingCount.textContent = `${mapped} of ${total} columns mapped${mapped < total ? ` · ${total - mapped} unmapped` : ""}`;
    mappingProgressBar.style.width = `${total ? (mapped / total) * 100 : 0}%`;
  };
  mappingSelects.forEach((select) => select.addEventListener("change", updateMappingProgress));
  updateMappingProgress();

  const mappingTable = area.querySelector(".mapping-table");
  const fontButton = area.querySelector("#increase-mapping-font");
  let mappingFontSize = 15;
  fontButton.addEventListener("click", () => {
    mappingFontSize = Math.min(mappingFontSize + 2, 23);
    mappingTable.style.setProperty("--mapping-font-size", `${mappingFontSize}px`);
    if (mappingFontSize === 23) fontButton.disabled = true;
  });

  document.getElementById("confirm-mapping-btn").addEventListener("click", async (e) => {
    const btn = e.target;
    const mapping = {};
    document.querySelectorAll(".mapping-select").forEach((sel) => {
      if (sel.value) mapping[sel.dataset.col] = sel.value;
    });
    btn.disabled = true;
    btn.textContent = "Running analysis…";
    try {
      await Api.confirmMapping(preview.dataset_id, mapping);
      const run = await Api.startAnalysis(preview.dataset_id);
      await pollAnalysis(run.id);
      logActivity(`Completed dataset analysis: ${preview.filename || "uploaded dataset"}`);
      setCurrentDataset(preview.dataset_id);
      toast("Analysis complete! Redirecting to dashboard…", "success");
      Router.go("dashboard");
    } catch (err) {
      toast(err.message, "error");
      btn.disabled = false;
      btn.textContent = "Confirm Mapping & Run Analysis";
    }
  });
}

async function pollAnalysis(runId) {
  for (let i = 0; i < 60; i++) {
    const status = await Api.getAnalysisStatus(runId);
    if (status.status === "completed") return status;
    if (status.status === "failed") throw new Error(status.error_message || "Analysis failed.");
    await new Promise((r) => setTimeout(r, 800));
  }
  throw new Error("Analysis is taking longer than expected. Check back in a moment.");
}

/* ---------------------------- Data Explorer ---------------------------- */
async function ExplorerPage(outlet) {
  outlet.innerHTML = `<div id="picker-slot"></div><div id="explorer-body"></div>`;
  const { selectedId } = await DatasetPickerBar(document.getElementById("picker-slot"), (id) => renderExplorer(id, 1, ""));
  await renderExplorer(selectedId, 1, "");
}

async function renderExplorer(datasetId, page, search) {
  const body = document.getElementById("explorer-body");
  if (!datasetId) { body.innerHTML = EmptyState("No dataset selected", "Upload and analyze a dataset first."); return; }
  body.innerHTML = `<div class="flex justify-center py-16"><div class="spinner"></div></div>`;
  try {
    const data = await Api.getDatasetRows(datasetId, page, 25, search);
    const cols = data.rows.length ? Object.keys(data.rows[0]).filter((c) => !["id", "organization_id", "dataset_id", "created_at", "updated_at"].includes(c)) : [];
    const totalPages = Math.max(1, Math.ceil(data.total / data.page_size));

    body.innerHTML = `
      <div class="card p-4 mb-4 flex flex-wrap gap-3 items-center justify-between">
        <input id="search-box" value="${escapeHtml(search)}" placeholder="Search by name or email…" class="border rounded-lg px-3 py-2 text-sm w-64" />
        <div class="text-sm text-slate-500">${fmtNum(data.total)} rows total</div>
      </div>
      <div class="card overflow-x-auto">
        <table class="w-full text-xs">
          <thead><tr class="text-left text-slate-500 border-b bg-slate-50">${cols.map((c) => `<th class="py-2 px-3">${c}</th>`).join("")}</tr></thead>
          <tbody>
            ${data.rows.length === 0 ? `<tr><td colspan="${cols.length}" class="text-center py-8 text-slate-400">No rows found</td></tr>` :
              data.rows.map((r) => `<tr class="border-b last:border-0 hover:bg-slate-50">${cols.map((c) => `<td class="py-2 px-3">${escapeHtml(formatCell(r[c]))}</td>`).join("")}</tr>`).join("")}
          </tbody>
        </table>
      </div>
      <div class="flex justify-between items-center mt-4 text-sm">
        <button class="btn-secondary" ${page <= 1 ? "disabled" : ""} id="prev-page">← Previous</button>
        <div>Page ${page} of ${totalPages}</div>
        <button class="btn-secondary" ${page >= totalPages ? "disabled" : ""} id="next-page">Next →</button>
      </div>
    `;
    document.getElementById("search-box").addEventListener("keydown", (e) => {
      if (e.key === "Enter") renderExplorer(datasetId, 1, e.target.value);
    });
    document.getElementById("prev-page")?.addEventListener("click", () => renderExplorer(datasetId, page - 1, search));
    document.getElementById("next-page")?.addEventListener("click", () => renderExplorer(datasetId, page + 1, search));
  } catch (err) {
    body.innerHTML = ErrorState(err.message);
  }
}
function formatCell(v) {
  if (v === null || v === undefined) return "";
  if (typeof v === "boolean") return v ? "Yes" : "No";
  return v;
}

/* ---------------------------- Funnel Page ---------------------------- */
async function FunnelPage(outlet) {
  outlet.innerHTML = `<div class="dashboard-intro">
    <div><div class="eyebrow"><span class="eyebrow-line"></span> CONVERSION JOURNEY</div>
      <h1>Funnel <span>analytics.</span></h1>
      <p>See how leads move from first touch to payment, and where they drop off.</p>
    </div>
  </div><div id="picker-slot"></div><div id="funnel-body"></div>`;
  const { selectedId } = await DatasetPickerBar(document.getElementById("picker-slot"), (id) => renderFunnelPage(id));
  await renderFunnelPage(selectedId);
}
async function renderFunnelPage(datasetId) {
  const body = document.getElementById("funnel-body");
  if (!datasetId) { body.innerHTML = EmptyState("No dataset selected", "Upload and analyze a dataset first."); return; }
  body.innerHTML = `<div class="flex justify-center py-16"><div class="spinner"></div></div>`;
  try {
    const funnel = await Api.getFunnel(datasetId);
    const conversionStages = funnel.stages.slice(2);
    const hasStageActivity = conversionStages.some((stage) => stage.user_count > 0);
    body.innerHTML = `
      <div class="section-heading"><div><h2>Your conversion journey</h2><p>${fmtNum(funnel.stages[0]?.user_count || 0)} records tracked through each stage</p></div>
        <span class="dataset-live-pill"><span class="live-indicator"></span> Live data</span>
      </div>
      ${!hasStageActivity ? `
        <div class="funnel-guidance">
          <div class="funnel-guidance-icon">↗</div>
          <div><strong>Your funnel is waiting for stage data</strong>
            <p>This dataset has records, but no signup, trial, activation, or payment dates. Map the relevant date columns to these fields during upload to see your conversion journey.</p>
            <div class="funnel-required-fields"><span>signup_date</span><span>trial_start</span><span>activation_date</span><span>payment_date</span></div>
          </div>
          <a href="#upload" class="btn-primary">Upload or map data <span>→</span></a>
        </div>` : ""}
      <div class="card chart-card funnel-chart-card">
        <div class="chart-heading"><div><span class="chart-kicker">STAGE-BY-STAGE</span><div class="font-semibold">Conversion funnel</div></div><span class="chart-icon">▽</span></div>
        ${!hasStageActivity ? `<div class="funnel-chart-empty"><span>↗</span><strong>No conversion stages to plot yet</strong><small>Once signup or later-stage dates are mapped, your funnel will appear here.</small></div>` : `<canvas id="funnelChartBig" height="110"></canvas>`}
      </div>
      ${funnel.biggest_drop_off ? `
        <div class="card p-4 mb-6 bg-amber-50 border-amber-200 text-amber-800 text-sm">
          <strong>Biggest drop-off:</strong> ${funnel.biggest_drop_off.from_stage} → ${funnel.biggest_drop_off.to_stage}
          at ${fmtPct(funnel.biggest_drop_off.drop_off_from_previous)}
        </div>` : ""}
      <div class="card overflow-x-auto">
        <table class="w-full text-sm">
          <thead><tr class="text-left text-slate-500 border-b"><th class="py-2 px-3">Stage</th><th class="py-2 px-3">Users</th><th class="py-2 px-3">Conv. from Previous</th><th class="py-2 px-3">Drop-off</th><th class="py-2 px-3">Conv. from Start</th></tr></thead>
          <tbody>
            ${funnel.stages.map((s) => `<tr class="border-b last:border-0">
              <td class="py-2 px-3 font-medium">${s.name}</td>
              <td class="py-2 px-3">${fmtNum(s.user_count)}</td>
              <td class="py-2 px-3">${fmtPct(s.conversion_from_previous)}</td>
              <td class="py-2 px-3">${fmtPct(s.drop_off_from_previous)}</td>
              <td class="py-2 px-3">${fmtPct(s.conversion_from_start)}</td>
            </tr>`).join("")}
          </tbody>
        </table>
      </div>
    `;
    if (hasStageActivity) renderFunnelChart("funnelChartBig", funnel.stages);
  } catch (err) { body.innerHTML = ErrorState(err.message); }
}

/* ---------------------------- Segments Page ---------------------------- */
async function SegmentsPage(outlet) {
  outlet.innerHTML = `<div id="picker-slot"></div><div id="segments-body"></div>`;
  const { selectedId } = await DatasetPickerBar(document.getElementById("picker-slot"), (id) => renderSegmentsPage(id));
  await renderSegmentsPage(selectedId);
}
async function renderSegmentsPage(datasetId) {
  const body = document.getElementById("segments-body");
  if (!datasetId) { body.innerHTML = EmptyState("No dataset selected", "Upload and analyze a dataset first."); return; }
  body.innerHTML = `<div class="flex justify-center py-16"><div class="spinner"></div></div>`;
  try {
    const data = await Api.getSegments(datasetId);
    body.innerHTML = `
      <div class="grid md:grid-cols-2 gap-4">
        ${data.segments.map((s) => `
          <div class="card p-5">
            <div class="flex justify-between items-start mb-2">
              <div class="font-semibold">${escapeHtml(s.name)}</div>
              <div class="text-xs px-2 py-1 rounded-full bg-indigo-50 text-indigo-700">${fmtNum(s.size)} leads</div>
            </div>
            <div class="grid grid-cols-3 gap-2 text-sm mt-3">
              <div><div class="text-slate-500 text-xs">Conversion</div><div class="font-bold">${fmtPct(s.conversion_rate)}</div></div>
              <div><div class="text-slate-500 text-xs">Total Revenue</div><div class="font-bold">${fmtMoney(s.total_revenue)}</div></div>
              <div><div class="text-slate-500 text-xs">Avg Engagement</div><div class="font-bold">${s.avg_engagement !== null ? fmtPct(s.avg_engagement * 100) : "—"}</div></div>
            </div>
            <div class="text-xs text-slate-500 mt-3">Top source: ${escapeHtml(s.characteristics?.top_source || "—")} · ${s.characteristics?.pct_of_total ?? 0}% of total</div>
          </div>
        `).join("")}
      </div>
    `;
  } catch (err) { body.innerHTML = ErrorState(err.message); }
}

/* ---------------------------- KPI Analytics Page ---------------------------- */
async function KpisPage(outlet) {
  outlet.innerHTML = `<div id="picker-slot"></div><div id="kpi-filters" class="mb-4"></div><div id="kpi-body"></div>`;
  const { selectedId } = await DatasetPickerBar(document.getElementById("picker-slot"), (id) => renderKpiPage(id));
  document.getElementById("kpi-filters").innerHTML = `
    <div class="card p-4 flex flex-wrap gap-3 items-end">
      <div><label class="text-xs text-slate-500 block mb-1">Source</label><input id="f-source" class="border rounded px-2 py-1 text-sm" placeholder="e.g. google" /></div>
      <div><label class="text-xs text-slate-500 block mb-1">Plan</label><input id="f-plan" class="border rounded px-2 py-1 text-sm" placeholder="e.g. Pro" /></div>
      <div><label class="text-xs text-slate-500 block mb-1">Country</label><input id="f-country" class="border rounded px-2 py-1 text-sm" /></div>
      <button id="apply-filters" class="btn-primary">Apply Filters</button>
      <button id="clear-filters" class="btn-secondary">Clear</button>
    </div>`;
  document.getElementById("apply-filters").addEventListener("click", () => renderKpiPage(State.currentDatasetId, {
    source: document.getElementById("f-source").value, plan: document.getElementById("f-plan").value, country: document.getElementById("f-country").value,
  }));
  document.getElementById("clear-filters").addEventListener("click", () => {
    ["f-source", "f-plan", "f-country"].forEach((id) => document.getElementById(id).value = "");
    renderKpiPage(State.currentDatasetId, {});
  });
  await renderKpiPage(selectedId, {});
}
async function renderKpiPage(datasetId, filters) {
  const body = document.getElementById("kpi-body");
  if (!datasetId) { body.innerHTML = EmptyState("No dataset selected", "Upload and analyze a dataset first."); return; }
  body.innerHTML = `<div class="flex justify-center py-16"><div class="spinner"></div></div>`;
  try {
    const cleanFilters = Object.fromEntries(Object.entries(filters || {}).filter(([, v]) => v));
    const data = await Api.getKpis(datasetId, cleanFilters);
    body.innerHTML = `<div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4">
      ${data.kpis.map((k) => `<div class="card p-4"><div class="text-xs text-slate-500 mb-1">${k.label}</div><div class="text-xl font-bold">${formatKpiValue(k.metric, k.value)}</div></div>`).join("")}
    </div>`;
  } catch (err) { body.innerHTML = ErrorState(err.message); }
}
function formatKpiValue(metric, value) {
  if (value === null || value === undefined) return "—";
  if (metric === "revenue" || metric === "avg_revenue_per_customer") return fmtMoney(value);
  if (metric.includes("rate") || metric.includes("conversion")) return fmtPct(value);
  return fmtNum(value, 1);
}

/* ---------------------------- AI Insights Page ---------------------------- */
async function InsightsPage(outlet) {
  outlet.innerHTML = `<div id="picker-slot"></div><div id="insights-body"></div>`;
  const { selectedId } = await DatasetPickerBar(document.getElementById("picker-slot"), (id) => renderInsightsPage(id));
  await renderInsightsPage(selectedId);
}
async function renderInsightsPage(datasetId) {
  const body = document.getElementById("insights-body");
  if (!datasetId) { body.innerHTML = EmptyState("No dataset selected", "Upload and analyze a dataset first."); return; }

  body.innerHTML = `<div class="card p-6 mb-4 flex items-center justify-between">
    <div class="text-sm text-slate-500">Generate fresh AI-powered insights from the current analysis, or view the most recent ones.</div>
    <button id="gen-insights-btn" class="btn-primary whitespace-nowrap">✨ Generate Insights</button>
  </div><div id="insights-content"></div>`;

  document.getElementById("gen-insights-btn").addEventListener("click", async (e) => {
    e.target.disabled = true;
    e.target.textContent = "Thinking…";
    try {
      const result = await Api.generateInsights(datasetId);
      logActivity("Generated AI insights");
      renderInsightsContent(result);
    } catch (err) {
      toast(err.message, "error");
    } finally {
      e.target.disabled = false;
      e.target.textContent = "✨ Generate Insights";
    }
  });

  try {
    const latest = await Api.getLatestInsights(datasetId);
    renderInsightsContent(latest);
  } catch (_) {
    document.getElementById("insights-content").innerHTML = EmptyState("No insights yet", "Click 'Generate Insights' to get an AI-powered analysis of this dataset.");
  }
}
function renderInsightsContent(data) {
  const content = document.getElementById("insights-content");
  const sourceBadge = data.source === "llm"
    ? `<span class="text-xs px-2 py-1 rounded-full bg-emerald-50 text-emerald-700">LLM-generated</span>`
    : `<span class="text-xs px-2 py-1 rounded-full bg-slate-100 text-slate-600">Rule-based (no LLM key configured)</span>`;

  content.innerHTML = `
    <div class="card p-6 mb-4">
      <div class="flex justify-between items-start mb-2"><div class="font-semibold">Executive Summary</div>${sourceBadge}</div>
      <p class="text-sm text-slate-700">${escapeHtml(data.executive_summary)}</p>
    </div>
    <div class="grid md:grid-cols-2 gap-4 mb-4">
      ${InsightList("Key Findings", data.key_findings, "📌")}
      ${InsightList("Problems", data.problems, "🚩")}
      ${InsightList("Opportunities", data.opportunities, "💡")}
      ${InsightList("Recommended Actions", data.recommended_actions, "✅")}
    </div>
    <div class="card p-6">
      <div class="font-semibold mb-3">🧪 Experiment Ideas</div>
      <div class="space-y-3">
        ${data.experiment_ideas.map((exp) => `
          <div class="border rounded-lg p-3 text-sm">
            <div><strong>Hypothesis:</strong> ${escapeHtml(exp.hypothesis)}</div>
            <div><strong>Experiment:</strong> ${escapeHtml(exp.experiment)}</div>
            <div class="text-slate-500 mt-1">Metric: ${escapeHtml(exp.metric)} · Expected: ${escapeHtml(exp.expected_direction)}</div>
            <button class="btn-secondary mt-2 text-xs" onclick='Actions.createExperimentFromIdea(${JSON.stringify(exp).replace(/'/g, "&apos;")})'>Add to Experiments</button>
          </div>
        `).join("")}
      </div>
    </div>
  `;
}
function InsightList(title, items, icon) {
  return `<div class="card p-5">
    <div class="font-semibold mb-2">${icon} ${title}</div>
    <ul class="text-sm text-slate-700 space-y-1.5 list-disc list-inside">
      ${(items || []).map((i) => `<li>${escapeHtml(i)}</li>`).join("") || `<li class="text-slate-400">Insufficient data to determine this.</li>`}
    </ul>
  </div>`;
}
Actions.createExperimentFromIdea = async (exp) => {
  try {
    await Api.createExperiment({
      name: exp.hypothesis.slice(0, 80),
      hypothesis: exp.hypothesis,
      proposed_change: exp.experiment,
      primary_kpi: exp.metric,
      expected_impact: exp.expected_direction,
      dataset_id: State.currentDatasetId,
    });
    logActivity("Created an experiment from an AI idea");
    toast("Added to Experiments.", "success");
  } catch (err) { toast(err.message, "error"); }
};

/* ---------------------------- Ask AI Analyst (Chat) ---------------------------- */
async function ChatPage(outlet) {
  outlet.innerHTML = `<div id="picker-slot"></div>
    <div class="card p-0 flex flex-col h-[65vh]">
      <div id="chat-messages" class="flex-1 overflow-y-auto p-5 space-y-4"></div>
      <form id="chat-form" class="border-t p-3 flex gap-2">
        <input id="chat-input" class="flex-1 border rounded-lg px-3 py-2 text-sm" placeholder="Ask about your business data, e.g. 'Why did conversion decrease?'" />
        <button class="btn-primary" type="submit">Ask</button>
      </form>
    </div>`;
  const { selectedId } = await DatasetPickerBar(document.getElementById("picker-slot"), () => {});
  const messages = document.getElementById("chat-messages");

  const examples = ["Which lead source performs best?", "Where is the biggest funnel drop-off?", "Give me the top growth opportunities.", "What should we test next?"];
  messages.innerHTML = `<div class="text-sm text-slate-500">Try asking:</div>
    <div class="flex flex-wrap gap-2">${examples.map((q) => `<button class="btn-secondary text-xs example-q">${q}</button>`).join("")}</div>`;
  messages.querySelectorAll(".example-q").forEach((btn) => btn.addEventListener("click", () => {
    document.getElementById("chat-input").value = btn.textContent;
    document.getElementById("chat-form").dispatchEvent(new Event("submit"));
  }));

  document.getElementById("chat-form").addEventListener("submit", async (e) => {
    e.preventDefault();
    const input = document.getElementById("chat-input");
    const question = input.value.trim();
    if (!question || !State.currentDatasetId) return;
    appendChatBubble(question, "user");
    input.value = "";
    const loadingId = appendChatBubble("Thinking…", "assistant", true);
    try {
      const res = await Api.chat(State.currentDatasetId, question);
      document.getElementById(loadingId).remove();
      appendChatBubble(res.answer, "assistant", false, res.source, res.tool_used);
    } catch (err) {
      document.getElementById(loadingId).remove();
      appendChatBubble(err.message, "assistant");
    }
  });
}
function appendChatBubble(text, role, loading = false, source, toolUsed) {
  const id = `bubble-${Date.now()}-${Math.random().toString(36).slice(2)}`;
  const messages = document.getElementById("chat-messages");
  const div = document.createElement("div");
  div.id = id;
  div.className = `flex ${role === "user" ? "justify-end" : "justify-start"}`;
  const badge = source && !loading ? `<div class="text-[10px] text-slate-400 mt-1">${source === "llm" ? "LLM" : "Rule-based"}${toolUsed ? " · " + toolUsed : ""}</div>` : "";
  div.innerHTML = `<div class="max-w-[75%] ${role === "user" ? "bg-indigo-600 text-white" : "bg-slate-100 text-slate-800"} rounded-2xl px-4 py-2 text-sm ${loading ? "italic opacity-70" : ""}">
    ${escapeHtml(text)}${badge}
  </div>`;
  messages.appendChild(div);
  messages.scrollTop = messages.scrollHeight;
  return id;
}

/* ---------------------------- Experiments Page ---------------------------- */
async function ExperimentsPage(outlet) {
  outlet.innerHTML = `
    <div class="flex justify-between items-center mb-4">
      <h1 class="text-xl font-bold">Experiments</h1>
      <button id="new-exp-btn" class="btn-primary">+ New Experiment</button>
    </div>
    <div id="exp-form-slot"></div>
    <div id="exp-list" class="grid md:grid-cols-2 gap-4"></div>
  `;
  document.getElementById("new-exp-btn").addEventListener("click", () => renderExperimentForm());
  await loadExperiments();
}
function renderExperimentForm(existing) {
  const slot = document.getElementById("exp-form-slot");
  slot.innerHTML = `
    <div class="card p-5 mb-6">
      <div class="font-semibold mb-3">${existing ? "Edit" : "New"} Experiment</div>
      <form id="exp-form" class="grid md:grid-cols-2 gap-3 text-sm">
        <input required name="name" placeholder="Experiment name" class="border rounded px-3 py-2 md:col-span-2" value="${escapeHtml(existing?.name || "")}" />
        <textarea name="problem" placeholder="Problem" class="border rounded px-3 py-2 md:col-span-2">${escapeHtml(existing?.problem || "")}</textarea>
        <textarea name="hypothesis" placeholder="Hypothesis" class="border rounded px-3 py-2 md:col-span-2">${escapeHtml(existing?.hypothesis || "")}</textarea>
        <input name="target_segment" placeholder="Target segment" class="border rounded px-3 py-2" value="${escapeHtml(existing?.target_segment || "")}" />
        <input name="proposed_change" placeholder="Proposed change" class="border rounded px-3 py-2" value="${escapeHtml(existing?.proposed_change || "")}" />
        <input name="primary_kpi" placeholder="Primary KPI" class="border rounded px-3 py-2" value="${escapeHtml(existing?.primary_kpi || "")}" />
        <input name="secondary_kpi" placeholder="Secondary KPI" class="border rounded px-3 py-2" value="${escapeHtml(existing?.secondary_kpi || "")}" />
        <input name="expected_impact" placeholder="Expected impact" class="border rounded px-3 py-2" value="${escapeHtml(existing?.expected_impact || "")}" />
        <select name="priority" class="border rounded px-3 py-2">
          ${["low", "medium", "high"].map((p) => `<option ${existing?.priority === p ? "selected" : ""}>${p}</option>`).join("")}
        </select>
        <input name="success_criteria" placeholder="Success criteria" class="border rounded px-3 py-2 md:col-span-2" value="${escapeHtml(existing?.success_criteria || "")}" />
        <div class="md:col-span-2 flex gap-2">
          <button class="btn-primary" type="submit">${existing ? "Save Changes" : "Create Experiment"}</button>
          <button type="button" id="cancel-exp" class="btn-secondary">Cancel</button>
        </div>
      </form>
    </div>`;
  document.getElementById("cancel-exp").addEventListener("click", () => { slot.innerHTML = ""; });
  document.getElementById("exp-form").addEventListener("submit", async (e) => {
    e.preventDefault();
    const fd = new FormData(e.target);
    const payload = Object.fromEntries(fd.entries());
    try {
      if (existing) await Api.updateExperiment(existing.id, payload);
      else await Api.createExperiment({ ...payload, dataset_id: State.currentDatasetId });
      logActivity(existing ? `Updated experiment: ${payload.name}` : `Created experiment: ${payload.name}`);
      slot.innerHTML = "";
      toast("Saved.", "success");
      await loadExperiments();
    } catch (err) { toast(err.message, "error"); }
  });
}
async function loadExperiments() {
  const list = document.getElementById("exp-list");
  list.innerHTML = `<div class="flex justify-center py-16 col-span-2"><div class="spinner"></div></div>`;
  try {
    const experiments = await Api.listExperiments();
    if (!experiments.length) {
      list.innerHTML = EmptyState("No experiments yet", "Create one manually, or generate ideas from AI Insights.", `<a href="#insights" class="btn-primary">Go to AI Insights</a>`);
      return;
    }
    const statusColors = { proposed: "bg-slate-100 text-slate-600", planned: "bg-blue-50 text-blue-700", running: "bg-amber-50 text-amber-700", completed: "bg-emerald-50 text-emerald-700" };
    list.innerHTML = experiments.map((exp) => `
      <div class="card p-5">
        <div class="flex justify-between items-start mb-2">
          <div class="font-semibold">${escapeHtml(exp.name)}</div>
          <span class="text-xs px-2 py-1 rounded-full ${statusColors[exp.status] || ""}">${exp.status}</span>
        </div>
        <div class="text-sm text-slate-600 space-y-1">
          ${exp.hypothesis ? `<div><strong>Hypothesis:</strong> ${escapeHtml(exp.hypothesis)}</div>` : ""}
          ${exp.primary_kpi ? `<div><strong>Primary KPI:</strong> ${escapeHtml(exp.primary_kpi)}</div>` : ""}
          <div><strong>Priority:</strong> ${exp.priority}</div>
        </div>
        <div class="flex gap-2 mt-3">
          <select data-id="${exp.id}" class="status-select border rounded px-2 py-1 text-xs">
            ${["proposed", "planned", "running", "completed"].map((s) => `<option ${exp.status === s ? "selected" : ""}>${s}</option>`).join("")}
          </select>
          <button data-id="${exp.id}" class="edit-exp btn-secondary text-xs">Edit</button>
          <button data-id="${exp.id}" class="delete-exp btn-secondary text-xs text-red-600">Delete</button>
        </div>
      </div>
    `).join("");

    list.querySelectorAll(".status-select").forEach((sel) => sel.addEventListener("change", async () => {
      try { await Api.updateExperiment(sel.dataset.id, { status: sel.value }); toast("Status updated.", "success"); await loadExperiments(); }
      catch (err) { toast(err.message, "error"); }
    }));
    list.querySelectorAll(".edit-exp").forEach((btn) => btn.addEventListener("click", () => {
      const exp = experiments.find((x) => x.id === btn.dataset.id);
      renderExperimentForm(exp);
      window.scrollTo({ top: 0, behavior: "smooth" });
    }));
    list.querySelectorAll(".delete-exp").forEach((btn) => btn.addEventListener("click", async () => {
      if (!confirm("Delete this experiment?")) return;
      try { await Api.deleteExperiment(btn.dataset.id); await loadExperiments(); } catch (err) { toast(err.message, "error"); }
    }));
  } catch (err) { list.innerHTML = ErrorState(err.message); }
}

/* ---------------------------- Reports Page ---------------------------- */
async function ReportsPage(outlet) {
  outlet.innerHTML = `<div id="picker-slot"></div>
    <div class="flex justify-between items-center my-4">
      <h1 class="text-xl font-bold">Reports</h1>
      <button id="gen-report-btn" class="btn-primary">Generate Report</button>
    </div>
    <div id="reports-list"></div>`;
  const { selectedId } = await DatasetPickerBar(document.getElementById("picker-slot"), () => {});
  document.getElementById("gen-report-btn").addEventListener("click", async (e) => {
    if (!State.currentDatasetId) { toast("Select an analyzed dataset first.", "error"); return; }
    e.target.disabled = true;
    e.target.textContent = "Generating…";
    try {
      await Api.createReport(State.currentDatasetId);
      logActivity("Generated a report");
      toast("Report generated.", "success");
      await loadReports();
    } catch (err) { toast(err.message, "error"); }
    finally { e.target.disabled = false; e.target.textContent = "Generate Report"; }
  });
  await loadReports();
}
async function loadReports() {
  const list = document.getElementById("reports-list");
  list.innerHTML = `<div class="flex justify-center py-16"><div class="spinner"></div></div>`;
  try {
    const reports = await Api.listReports();
    if (!reports.length) { list.innerHTML = EmptyState("No reports yet", "Generate a report to get an exportable summary of KPIs, funnel, segments, and AI insights."); return; }
    list.innerHTML = `<div class="space-y-3">${reports.map((r) => `
      <div class="card p-4 flex justify-between items-center flex-wrap gap-2">
        <div>
          <div class="font-semibold">${escapeHtml(r.title)}</div>
          <div class="text-xs text-slate-500">${r.content?.generated_at ? new Date(r.content.generated_at).toLocaleString() : ""}</div>
        </div>
        <div class="flex gap-2">
          <button class="btn-secondary text-xs export-btn" data-id="${r.id}" data-fmt="csv" data-name="${escapeHtml(r.title)}">Export CSV</button>
          <button class="btn-secondary text-xs export-btn" data-id="${r.id}" data-fmt="xlsx" data-name="${escapeHtml(r.title)}">Export Excel</button>
          <button class="btn-secondary text-xs export-btn" data-id="${r.id}" data-fmt="pdf" data-name="${escapeHtml(r.title)}">Export PDF</button>
        </div>
      </div>`).join("")}</div>`;
    list.querySelectorAll(".export-btn").forEach((btn) => btn.addEventListener("click", () => downloadReportExport(btn.dataset.id, btn.dataset.fmt, btn.dataset.name)));
  } catch (err) { list.innerHTML = ErrorState(err.message); }
}

async function downloadReportExport(reportId, format, title) {
  try {
    const blob = await Api.exportReport(reportId, format);
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `${title || "report"}.${format}`;
    document.body.appendChild(a);
    a.click();
    a.remove();
    URL.revokeObjectURL(url);
  } catch (err) {
    toast(err.message || "Export failed.", "error");
  }
}

/* ---------------------------- Settings Page ---------------------------- */
function SettingsPage(outlet) {
  const savedLanguage = localStorage.getItem("growth_intel_language") || "en";
  const backendDocsUrl = API_BASE
    ? `${API_BASE}/docs`
    : `${window.location.protocol}//${window.location.hostname}:8000/docs`;
  let activity = [];
  try {
    activity = JSON.parse(localStorage.getItem(activityStorageKey()) || "[]");
  } catch (error) {
    console.error("Could not read recent activity.", error);
  }
  const languageNames = Object.fromEntries(["en", "hi", "es", "fr"].map((code) => [code, window.GrowthI18n.getLanguageName(code)]));
  outlet.innerHTML = `
    <div class="dashboard-intro">
      <div><div class="eyebrow"><span class="eyebrow-line"></span> YOUR WORKSPACE</div>
        <h1>Settings &amp; <span>preferences.</span></h1>
        <p>Manage account security, activity, and how your workspace is displayed.</p>
      </div>
    </div>
    <div class="settings-layout">
      <section class="card settings-card">
        <div class="settings-section-heading"><span class="settings-section-icon">◉</span><div><h2>Account details</h2><p>Your profile and workspace information</p></div></div>
        <div class="settings-profile">
          <span class="settings-profile-avatar">${escapeHtml((State.user?.full_name || State.user?.email || "U").slice(0, 1).toUpperCase())}</span>
          <div><strong>${escapeHtml(State.user?.full_name || "Workspace user")}</strong><span>${escapeHtml(State.user?.organization_name || "Your workspace")}</span></div>
          <span class="settings-role">${escapeHtml(State.user?.role || "member")}</span>
        </div>
        <div class="settings-detail-list">
          <div><span>Email address</span><strong>${escapeHtml(State.user?.email || "")}</strong></div>
          <div><span>Organization</span><strong>${escapeHtml(State.user?.organization_name || "—")}</strong></div>
          <div><span>API connection</span><strong>${escapeHtml(API_BASE || `${window.location.origin} (same origin)`)}</strong></div>
        </div>
      </section>

      <section class="card settings-card">
        <button class="settings-security-toggle" type="button" aria-expanded="false" aria-controls="settings-security-content">
          <span class="settings-section-icon settings-icon-purple">◇</span>
          <span class="settings-security-copy"><span>Password &amp; security</span><small>Change your password to keep your account secure</small></span>
          <span class="settings-security-chevron" aria-hidden="true">⌄</span>
        </button>
        <div class="settings-security-content" id="settings-security-content" hidden>
          <form id="change-password-form" class="settings-password-form">
            <label>Current password<input required type="password" name="current_password" autocomplete="current-password" minlength="1" maxlength="128" /></label>
            <label>New password<input required type="password" name="new_password" autocomplete="new-password" minlength="8" maxlength="128" placeholder="At least 8 characters" /></label>
            <label>Confirm new password<input required type="password" name="confirm_password" autocomplete="new-password" minlength="8" maxlength="128" placeholder="Enter your new password again" /></label>
            <div class="settings-form-footer"><span>Use at least 8 characters.</span><button class="btn-primary" type="submit">Update password <span>→</span></button></div>
          </form>
        </div>
      </section>

      <section class="card settings-card">
        <div class="settings-section-heading"><span class="settings-section-icon settings-icon-blue">◷</span><div><h2>Past activity</h2><p>Recent activity saved in this browser for your account</p></div></div>
        ${activity.length ? `<div class="activity-list">${activity.slice(0, 10).map((item) => `
          <div class="activity-item"><span class="activity-dot"></span><div><strong>${escapeHtml(item.message)}</strong><time>${escapeHtml(new Date(item.timestamp).toLocaleString(getNumberLocale(), { dateStyle: "medium", timeStyle: "short" }))}</time></div></div>
        `).join("")}</div>` : `<div class="settings-empty-activity"><span>◷</span><div><strong>No activity recorded yet</strong><p>Sign-ins, dataset uploads, and key actions will appear here.</p></div></div>`}
        <div class="settings-local-note">Activity is stored locally in this browser and is not shared with other devices.</div>
      </section>

      <section class="card settings-card">
        <div class="settings-section-heading"><span class="settings-section-icon settings-icon-green">文</span><div><h2>Language &amp; region</h2><p>Choose how dates and numbers are formatted</p></div></div>
        <label class="settings-language-field" for="settings-language">Formatting preference
          <select id="settings-language">
            ${Object.entries(languageNames).map(([code, name]) => `<option value="${code}" ${savedLanguage === code ? "selected" : ""}>${name}</option>`).join("")}
          </select>
        </label>
        <div class="settings-local-note">The selected language changes the entire interface, including pages, controls, and messages.</div>
      </section>

      <section class="card settings-card settings-support-card">
        <div class="settings-section-heading"><span class="settings-section-icon settings-icon-amber">?</span><div><h2>Help &amp; support</h2><p>Find guidance or get help with your workspace</p></div></div>
        <div class="support-options">
          <a href="${escapeHtml(backendDocsUrl)}" target="_blank" rel="noopener noreferrer"><span class="support-option-icon">▤</span><span><strong>API documentation</strong><small>Browse available backend endpoints</small></span><b>↗</b></a>
          <div><span class="support-option-icon">◈</span><span><strong>Having trouble with a dataset?</strong><small>Check that the file has headers and map the relevant columns before running analysis.</small></span></div>
          <div><span class="support-option-icon">✳</span><span><strong>Need account help?</strong><small>Contact your workspace administrator for access or organization support.</small></span></div>
        </div>
      </section>
    </div>
  `;

  const securityToggle = document.querySelector(".settings-security-toggle");
  const securityContent = document.getElementById("settings-security-content");
  securityToggle.addEventListener("click", () => {
    const isExpanded = securityToggle.getAttribute("aria-expanded") === "true";
    securityToggle.setAttribute("aria-expanded", String(!isExpanded));
    securityContent.hidden = isExpanded;
    securityToggle.querySelector(".settings-security-chevron").textContent = isExpanded ? "⌄" : "⌃";
    if (!isExpanded) {
      securityContent.querySelector('input[name="current_password"]').focus();
    }
  });

  document.getElementById("change-password-form").addEventListener("submit", async (event) => {
    event.preventDefault();
    const form = event.currentTarget;
    const data = new FormData(form);
    const newPassword = data.get("new_password");
    if (newPassword !== data.get("confirm_password")) {
      toast("The new passwords do not match.", "error");
      return;
    }
    const button = form.querySelector('button[type="submit"]');
    button.disabled = true;
    try {
      await Api.changePassword({
        current_password: data.get("current_password"),
        new_password: newPassword,
      });
      form.reset();
      logActivity("Changed account password");
      toast("Your password was updated.", "success");
    } catch (err) {
      toast(err.message, "error");
    } finally {
      button.disabled = false;
    }
  });

  document.getElementById("settings-language").addEventListener("change", (event) => {
    window.GrowthI18n.setLanguage(event.target.value);
    logActivity("Changed app language");
    Router.render().then(() => toast("App language updated.", "success"));
  });
}

/* ---------------------------- Route registration ---------------------------- */
Router.register("login", LoginPage, { requiresAuth: false });
Router.register("register", RegisterPage, { requiresAuth: false });
Router.register("dashboard", DashboardPage);
Router.register("upload", UploadPage);
Router.register("explorer", ExplorerPage);
Router.register("funnel", FunnelPage);
Router.register("segments", SegmentsPage);
Router.register("kpis", KpisPage);
Router.register("insights", InsightsPage);
Router.register("chat", ChatPage);
Router.register("experiments", ExperimentsPage);
Router.register("reports", ReportsPage);
Router.register("settings", SettingsPage);

Router.render();
