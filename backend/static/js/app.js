(function () {
    "use strict";

    function escapeHtml(s) {
        if (s == null) return "";
        const d = document.createElement("div");
        d.textContent = s;
        return d.innerHTML;
    }

    function showToast(message, type) {
        const root = document.getElementById("toastRoot");
        if (!root) return;
        const el = document.createElement("div");
        el.className = "toast " + (type === "error" ? "err" : type === "ok" ? "ok" : "info");
        el.textContent = message;
        root.appendChild(el);
        setTimeout(function () {
            el.remove();
        }, 4200);
    }

    function formatInsights(ins) {
        if (ins == null || ins === "") return "—";
        if (typeof ins === "string") {
            try {
                var o = JSON.parse(ins);
                return JSON.stringify(o, null, 2);
            } catch (e) {
                return ins;
            }
        }
        if (typeof ins === "object") return JSON.stringify(ins, null, 2);
        return String(ins);
    }

    function riskBadgeClass(risk) {
        var r = (risk || "low").toString().toLowerCase();
        if (r === "none") r = "low";
        var cap = r.charAt(0).toUpperCase() + r.slice(1);
        return "risk-badge risk-" + cap;
    }

    /* Live clock + connection dot */
    function startLiveClock() {
        var clock = document.getElementById("liveClock");
        if (!clock) return;
        function tick() {
            clock.textContent = new Date().toLocaleString(undefined, {
                weekday: "short",
                hour: "2-digit",
                minute: "2-digit",
                second: "2-digit",
            });
        }
        tick();
        setInterval(tick, 1000);
    }

    function setConnLive(on) {
        var dot = document.getElementById("liveDot");
        var label = document.getElementById("connStatus");
        if (dot) dot.classList.toggle("idle", !on);
        if (label) label.textContent = on ? "Live" : "Idle";
    }

    var navToggle = document.getElementById("navToggle");
    var navLinks = document.getElementById("navLinks");
    if (navToggle && navLinks) {
        navToggle.addEventListener("click", function () {
            navLinks.classList.toggle("open");
        });
    }

    startLiveClock();

    /* Auth */
    var loginForm = document.getElementById("loginForm");
    if (loginForm) {
        loginForm.addEventListener("submit", async function (e) {
            e.preventDefault();
            var email = document.getElementById("loginEmail").value;
            var password = document.getElementById("loginPassword").value;
            var err = document.getElementById("loginError");
            var params = new URLSearchParams();
            params.append("username", email);
            params.append("password", password);
            try {
                var res = await fetch("/login", {
                    method: "POST",
                    headers: { "Content-Type": "application/x-www-form-urlencoded" },
                    body: params,
                });
                var data = await res.json().catch(function () { return {}; });
                if (!res.ok) {
                    err.innerText = data.detail || "Login failed.";
                    err.classList.remove("hidden");
                    return;
                }
                showToast("Signed in.", "ok");
                window.location.href = "/dashboard";
            } catch (error) {
                err.innerText = "Network error.";
                err.classList.remove("hidden");
            }
        });
    }

    var signupForm = document.getElementById("signupForm");
    if (signupForm) {
        signupForm.addEventListener("submit", async function (e) {
            e.preventDefault();
            var name = document.getElementById("signupName").value;
            var email = document.getElementById("signupEmail").value;
            var password = document.getElementById("signupPassword").value;
            var err = document.getElementById("signupError");
            try {
                var res = await fetch("/signup", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ name: name, email: email, password: password }),
                });
                var data = await res.json().catch(function () { return {}; });
                if (!res.ok) {
                    err.innerText = data.detail || "Signup failed.";
                    err.classList.remove("hidden");
                    return;
                }
                showToast("Account created. Please log in.", "ok");
                window.location.href = "/login";
            } catch (error) {
                err.innerText = "Network error.";
                err.classList.remove("hidden");
            }
        });
    }

    var logoutBtn = document.getElementById("logoutBtn");
    if (logoutBtn) {
        logoutBtn.addEventListener("click", async function (e) {
            e.preventDefault();
            await fetch("/logout");
            showToast("Logged out.", "info");
            window.location.href = "/login";
        });
    }

    /* Upload */
    var uploadForm = document.getElementById("uploadForm");
    if (uploadForm) {
        uploadForm.addEventListener("submit", async function (e) {
            e.preventDefault();
            var zipInput = document.getElementById("zipInput");
            var mediaInput = document.getElementById("mediaInput");
            var textEl = document.getElementById("textInput");
            var zipFile = zipInput && zipInput.files[0];
            var mediaFile = mediaInput && mediaInput.files[0];
            var textVal = textEl ? textEl.value.trim() : "";

            if (!zipFile && !mediaFile && !textVal) {
                showToast("Choose a file or enter text.", "error");
                return;
            }

            var loader = document.getElementById("loader");
            var loaderText = document.getElementById("loaderText");
            if (loader) loader.classList.remove("hidden");
            if (loaderText) loaderText.textContent = "Running pipeline…";

            var formData = new FormData();
            var endpoint = "/api/analyze";
            if (zipFile) {
                formData.append("file", zipFile);
                endpoint = "/api/analyze-zip";
            } else {
                if (mediaFile) formData.append("file", mediaFile);
                if (textVal) formData.append("text", textVal);
            }

            setConnLive(false);
            try {
                var res = await fetch(endpoint, { method: "POST", body: formData });
                var raw = await res.text();
                var json = null;
                try {
                    json = JSON.parse(raw);
                } catch (parseErr) {
                    json = null;
                }
                if (!res.ok) {
                    var detail = json && json.detail ? (Array.isArray(json.detail) ? json.detail.map(function (d) { return d.msg || d; }).join(" ") : json.detail) : raw.slice(0, 200);
                    showToast("Analysis failed: " + detail, "error");
                    return;
                }
                showToast("Analysis complete. Loading Intelligence Hub...", "ok");
                // Immediately transition user to their populated dashboard
                window.location.href = "/dashboard";
            } catch (error) {
                console.error(error);
                showToast("Network error during analysis.", "error");
            } finally {
                if (loader) loader.classList.add("hidden");
                setConnLive(true);
            }
        });
    }

    /* Dashboard */
    var currentChart = null;
    var dashboardPollTimer = null;

    async function fetchDashboardData() {
        var loading = document.getElementById("dashboard-loading");
        try {
            var res = await fetch("/api/dashboard/stats");
            if (res.status === 401) {
                window.location.href = "/login";
                return;
            }
            var data = await res.json();

            var root = document.getElementById("dashboard-container");
            if (root) root.classList.remove("hidden");
            if (loading) loading.classList.add("hidden");

            var s = data.summary || {};
            var elC = document.getElementById("stat-comments");
            var elL = document.getElementById("stat-likes");
            var elA = document.getElementById("stat-activity");
            var elW = document.getElementById("stat-wellbeing");
            if (elC) elC.textContent = s.total_comments != null ? s.total_comments : 0;
            if (elL) elL.textContent = s.total_likes != null ? s.total_likes : 0;
            var activity =
                s.total_activity != null
                    ? s.total_activity
                    : s.total_posts != null
                      ? s.total_posts
                      : (Number(s.total_messages || 0) + Number(s.total_urls || 0));
            if (elA) elA.textContent = activity;
            var wb = data.analysis && data.analysis.wellbeing_score;
            if (elW) elW.textContent = wb != null && !isNaN(Number(wb)) ? Number(wb).toFixed(2) : "—";

            var risk = (data.analysis && data.analysis.risk_level) || "low";
            var badge = document.getElementById("risk-badge");
            if (badge) {
                badge.className = riskBadgeClass(risk);
                badge.textContent = risk + " risk";
            }

            var insightEl = document.getElementById("insight-text");
            if (insightEl) {
                insightEl.textContent = formatInsights(data.analysis && data.analysis.insights);
            }
            var recs = document.getElementById("recs-text");
            if (recs) recs.textContent = (data.analysis && data.analysis.recommendations) || "—";

            function fillMessages(items) {
                var ul = document.getElementById("messages-list");
                if (!ul) return;
                ul.innerHTML = "";
                if (!items || !items.length) {
                    ul.innerHTML = "<li>No messages yet.</li>";
                    return;
                }
                items.forEach(function (m) {
                    var li = document.createElement("li");
                    var t = m.message_text || "";
                    li.appendChild(document.createTextNode(t.length > 220 ? t.slice(0, 220) + "…" : t));
                    var sm = document.createElement("div");
                    sm.className = "text-muted text-sm";
                    sm.style.marginTop = "0.35rem";
                    sm.textContent = (m.message_type || "") + (m.timestamp ? " · " + m.timestamp : "");
                    li.appendChild(sm);
                    ul.appendChild(li);
                });
            }

            function fillInteractions(items) {
                var ul = document.getElementById("interactions-list");
                if (!ul) return;
                ul.innerHTML = "";
                if (!items || !items.length) {
                    ul.innerHTML = "<li>No engagement rows yet.</li>";
                    return;
                }
                items.forEach(function (i) {
                    var li = document.createElement("li");
                    li.innerHTML =
                        "<strong>" +
                        escapeHtml(i.type || "") +
                        "</strong> " +
                        escapeHtml(i.text || "") +
                        '<div class="text-muted text-sm" style="margin-top:0.25rem">' +
                        escapeHtml(i.timestamp || "") +
                        "</div>";
                    ul.appendChild(li);
                });
            }

            fillMessages(data.messages);
            fillInteractions(data.interactions);

            var ctx = document.getElementById("sentimentChart");
            if (ctx && window.Chart) {
                var c2d = ctx.getContext("2d");
                if (currentChart) currentChart.destroy();
                var sent = ((data.analysis && data.analysis.sentiment) || "neutral").toLowerCase();
                var dist = [0, 1, 0];
                if (sent === "positive") dist = [1, 0, 0];
                else if (sent === "negative") dist = [0, 0, 1];
                currentChart = new Chart(c2d, {
                    type: "doughnut",
                    data: {
                        labels: ["Positive", "Neutral", "Negative"],
                        datasets: [
                            {
                                data: dist,
                                backgroundColor: ["#34d399", "#64748b", "#f87171"],
                                borderWidth: 0,
                            },
                        ],
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {
                            legend: {
                                position: "bottom",
                                labels: { color: "#e2e8f0", font: { family: "DM Sans" } },
                            },
                        },
                    },
                });
            }
            setConnLive(true);
        } catch (err) {
            console.error("Dashboard load error", err);
            setConnLive(false);
            if (loading) loading.textContent = "Could not load dashboard.";
        }
    }

    function startDashboardPoll() {
        if (dashboardPollTimer) clearInterval(dashboardPollTimer);
        dashboardPollTimer = setInterval(fetchDashboardData, 12000);
    }

    if (document.getElementById("dashboard-container")) {
        fetchDashboardData().then(function () {
            startDashboardPoll();
        });
    }

    /* Insights / live feed */
    var insightsPollTimer = null;

    async function fetchInsightsFeed() {
        var loading = document.getElementById("insights-loading");
        try {
            var res = await fetch("/api/dashboard/stats");
            if (res.status === 401) {
                window.location.href = "/login";
                return;
            }
            var data = await res.json();
            var container = document.getElementById("insights-container");
            if (container) container.classList.remove("hidden");
            if (loading) loading.classList.add("hidden");

            var sync = document.getElementById("feedLastSync");
            if (sync) sync.textContent = "Updated " + new Date().toLocaleTimeString();

            var tl = document.getElementById("timeline-list");
            if (tl) {
                tl.innerHTML = "";
                var events = data.timeline || [];
                if (!events.length) {
                    tl.innerHTML = "<li class=\"text-muted\">No timeline events yet. Run an analysis from the Analyze page.</li>";
                } else {
                    events.forEach(function (ev) {
                        var li = document.createElement("li");
                        li.className = "timeline-item";
                        li.innerHTML =
                            '<span class="tl-icon">' +
                            escapeHtml(ev.icon || "•") +
                            '</span><div class="tl-body"><strong>' +
                            escapeHtml(ev.title || "") +
                            "</strong><div>" +
                            escapeHtml((ev.content || "").slice(0, 280)) +
                            (ev.content && ev.content.length > 280 ? "…" : "") +
                            '</div><small>' +
                            escapeHtml(ev.timestamp || "") +
                            "</small></div>";
                        tl.appendChild(li);
                    });
                }
            }

            function fillTags(id, arr) {
                var ul = document.getElementById(id);
                if (!ul) return;
                ul.innerHTML = "";
                var list = arr || [];
                if (!list.length) {
                    ul.innerHTML = "<li class=\"text-muted\">None yet.</li>";
                    return;
                }
                list.forEach(function (x) {
                    var li = document.createElement("li");
                    li.textContent = typeof x === "string" ? x : JSON.stringify(x);
                    ul.appendChild(li);
                });
            }

            fillTags("searches-list", data.searches);
            fillTags("prefs-list", data.preferences);
            setConnLive(true);
        } catch (e) {
            console.error(e);
            setConnLive(false);
            if (loading) loading.textContent = "Could not load feed.";
        }
    }

    if (document.getElementById("insights-container")) {
        fetchInsightsFeed().then(function () {
            insightsPollTimer = setInterval(fetchInsightsFeed, 12000);
        });
    }

    /* Settings */
    var purgeBtn = document.getElementById("purgeDataBtn");
    if (purgeBtn) {
        purgeBtn.addEventListener("click", async function () {
            if (!confirm("Delete all behavioral data for your account? This cannot be undone.")) return;
            try {
                var res = await fetch("/api/account/purge", { method: "POST" });
                var data = await res.json().catch(function () { return {}; });
                if (!res.ok) {
                    showToast(data.detail || "Purge failed.", "error");
                    return;
                }
                showToast(data.message || "Data cleared.", "ok");
                window.location.reload();
            } catch (err) {
                showToast("Request failed.", "error");
            }
        });
    }

    var savePrefsBtn = document.getElementById("savePrefsBtn");
    if (savePrefsBtn) {
        savePrefsBtn.addEventListener("click", function () {
            var sel = document.getElementById("toxicityLevel");
            var late = document.getElementById("lateNightFlag");
            var prefs = {
                toxicity: sel ? sel.value : "balanced",
                lateNight: late ? late.checked : true,
                savedAt: new Date().toISOString(),
            };
            try {
                localStorage.setItem("sentinel_ui_prefs", JSON.stringify(prefs));
                showToast("Preferences saved locally.", "ok");
            } catch (e) {
                showToast("Could not save preferences.", "error");
            }
        });
    }

    /* Restore settings UI from localStorage */
    (function restorePrefs() {
        var sel = document.getElementById("toxicityLevel");
        var late = document.getElementById("lateNightFlag");
        if (!sel && !late) return;
        try {
            var raw = localStorage.getItem("sentinel_ui_prefs");
            if (!raw) return;
            var p = JSON.parse(raw);
            if (sel && p.toxicity) sel.value = p.toxicity;
            if (late && typeof p.lateNight === "boolean") late.checked = p.lateNight;
        } catch (e) {}
    })();
})();
