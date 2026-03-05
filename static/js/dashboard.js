/* dashboard.js — CyberShield AI */

// ── Chart.js donut ─────────────────────────────────────────────────────────
const ATTACK_COLORS = {
  Normal:        "#1a7a3a",
  DDoS:          "#c0392b",
  Intrusion:     "#e67e22",
  Malware:       "#9b59b6",
  Phishing:      "#f1c40f",
  SQL_Injection: "#2980b9",
};

let attackChart = null;

function initChart(comptage) {
  const labels = Object.keys(comptage);
  const data   = Object.values(comptage);
  const colors = labels.map(l => ATTACK_COLORS[l] || "#555");

  const ctx = document.getElementById("attackChart");
  if (!ctx) return;

  attackChart = new Chart(ctx, {
    type: "doughnut",
    data: {
      labels,
      datasets: [{
        data,
        backgroundColor: colors,
        borderColor: "#0d1117",
        borderWidth: 2,
      }],
    },
    options: {
      responsive: true,
      plugins: {
        legend: {
          position: "bottom",
          labels: {
            color: "#8b949e",
            font: { size: 11 },
            boxWidth: 12,
          },
        },
      },
    },
  });
}

function updateChart(comptage) {
  if (!attackChart) return;
  const labels = Object.keys(comptage);
  attackChart.data.labels = labels;
  attackChart.data.datasets[0].data   = Object.values(comptage);
  attackChart.data.datasets[0].backgroundColor = labels.map(l => ATTACK_COLORS[l] || "#555");
  attackChart.update();
}

// ── Real-time simulation ───────────────────────────────────────────────────
function simulerAttaque() {
  const statusEl = document.getElementById("simulate-status");
  if (statusEl) statusEl.textContent = "Simulation en cours…";

  fetch("/api/simulate")
    .then(r => r.json())
    .then(data => {
      if (!data.success) return;
      mettreAJourUI(data.stats, data.entry);
      if (statusEl) {
        statusEl.textContent = `✅ ${data.entry.type_attaque} détecté (${data.entry.confiance}%)`;
        setTimeout(() => { statusEl.textContent = ""; }, 4000);
      }
    })
    .catch(() => {
      if (statusEl) statusEl.textContent = "❌ Erreur de simulation";
    });
}

// ── Auto-refresh every 5 s ─────────────────────────────────────────────────
function mettreAJourStats() {
  fetch("/api/stats")
    .then(r => r.json())
    .then(data => mettreAJourUI(data, null))
    .catch(() => {});
}

function mettreAJourUI(stats, newEntry) {
  // Stats cards
  const setEl = (id, val) => { const el = document.getElementById(id); if (el) el.textContent = val; };
  setEl("stat-total",    stats.nb_detections);
  setEl("stat-attaques", stats.nb_attaques);
  setEl("stat-accuracy", stats.accuracy + "%");
  setEl("stat-normal",   stats.nb_normal);

  // Chart
  if (stats.comptage) updateChart(stats.comptage);

  // Table — only update if there are recent entries
  if (stats.recentes && stats.recentes.length > 0) {
    const tbody = document.getElementById("recent-tbody");
    if (!tbody) return;
    tbody.innerHTML = "";
    stats.recentes.forEach(e => {
      const tr = document.createElement("tr");
      if (newEntry && e.datetime === newEntry.datetime) {
        tr.classList.add("table-active");
      }
      tr.innerHTML = `
        <td><small>${e.datetime}</small></td>
        <td><span class="badge attack-badge-${e.badge}">${e.type_attaque}</span></td>
        <td><small>${e.criticite}</small></td>
        <td><code>${e.ip}</code></td>
        <td>
          <div class="progress" style="height:8px;width:70px;">
            <div class="progress-bar bg-cyan" style="width:${e.confiance}%"></div>
          </div>
          <small>${e.confiance}%</small>
        </td>`;
      tbody.appendChild(tr);
    });
  }
}

// ── Init ───────────────────────────────────────────────────────────────────
let statsIntervalId = null;

document.addEventListener("DOMContentLoaded", () => {
  if (typeof initialComptage !== "undefined") {
    initChart(initialComptage);
  }
  statsIntervalId = setInterval(mettreAJourStats, 5000);
});

window.addEventListener("beforeunload", () => {
  if (statsIntervalId !== null) {
    clearInterval(statsIntervalId);
    statsIntervalId = null;
  }
});
