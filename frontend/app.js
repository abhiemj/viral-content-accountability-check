"use strict";

const $ = (sel) => document.querySelector(sel);
const statusEl = $("#status");
const resultsEl = $("#results");
const emptyEl = $("#empty");

// ---- tab switching ----
document.querySelectorAll(".tab").forEach((tab) => {
  tab.addEventListener("click", () => {
    document.querySelectorAll(".tab").forEach((t) => t.classList.remove("active"));
    document.querySelectorAll(".panel").forEach((p) => p.classList.remove("active"));
    tab.classList.add("active");
    $("#panel-" + tab.dataset.mode).classList.add("active");
    reset();
  });
});

function reset() {
  resultsEl.innerHTML = "";
  statusEl.hidden = true;
  emptyEl.hidden = false;
}

function setStatus(msg) {
  statusEl.textContent = msg;
  statusEl.hidden = false;
}

function setLoading(btn, on) {
  btn.disabled = on;
  btn.querySelector(".btn-label").style.opacity = on ? "0.7" : "1";
  btn.querySelector(".spinner").hidden = !on;
}

// ---- helpers ----
function esc(s) {
  return (s || "").replace(/[&<>"']/g, (c) => (
    { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]
  ));
}

function fmtTime(seconds) {
  if (seconds == null) return "";
  const m = Math.floor(seconds / 60);
  const s = Math.floor(seconds % 60).toString().padStart(2, "0");
  return `${m}:${s}`;
}

const VERDICT_LABEL = {
  disputed: "Disputed",
  supported: "Supported",
  mixed: "Mixed",
  reviewed: "Reviewed",
  unverified: "Unverified",
};

function reviewHtml(r) {
  return `
    <div class="review">
      <div class="review-top">
        <span class="rating">${esc(r.rating || "No rating")}</span>
        <span class="pub">${esc(r.publisher || r.publisherSite || "Unknown publisher")}</span>
      </div>
      ${r.title ? `<div class="review-title">${esc(r.title)}</div>` : ""}
      ${r.url ? `<a href="${esc(r.url)}" target="_blank" rel="noopener">Read the fact-check →</a>` : ""}
    </div>`;
}

function claimBlockHtml({ claimText, verdict, results, timestamp }) {
  const v = (verdict || "unverified").split(":")[0].trim();
  const label = VERDICT_LABEL[v] || v;
  const reviews = results.length
    ? results.map(reviewHtml).join("")
    : `<div class="review no-review">No published fact-check found for this claim.</div>`;
  const ts = timestamp != null ? `<span class="ts">⏱ ${fmtTime(timestamp)}</span>` : "";
  return `
    <div class="claim-block ${esc(v)}">
      <div class="claim-text">${esc(claimText)}</div>
      <div class="claim-meta">
        <span class="badge ${esc(v)}">${esc(label)}</span> ${ts}
      </div>
      ${reviews}
    </div>`;
}

async function postJSON(url, body) {
  const res = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.detail || "Request failed");
  return data;
}

// ---- claim mode ----
$("#btn-claim").addEventListener("click", async (e) => {
  const btn = e.currentTarget;
  const query = $("#claim-input").value.trim();
  if (!query) return;
  reset();
  emptyEl.hidden = true;
  setStatus("Searching published fact-checks…");
  setLoading(btn, true);
  try {
    const data = await postJSON("/api/verify/claim", { query });
    setStatus(`${data.count} published fact-check(s) found.`);
    resultsEl.innerHTML = claimBlockHtml({
      claimText: query,
      verdict: data.verdict,
      results: data.results,
    });
  } catch (err) {
    setStatus("⚠ " + err.message);
  } finally {
    setLoading(btn, false);
  }
});

// ---- link mode ----
$("#btn-link").addEventListener("click", async (e) => {
  const btn = e.currentTarget;
  const url = $("#link-input").value.trim();
  if (!url) return;
  reset();
  emptyEl.hidden = true;
  setStatus("Fetching captions and extracting claims…");
  setLoading(btn, true);
  try {
    const data = await postJSON("/api/verify/link", { url });
    setStatus(`${data.claimsFound} check-worthy claim(s) extracted from video ${data.videoId}.`);
    resultsEl.innerHTML = data.claims
      .map((c) => claimBlockHtml({
        claimText: c.claim,
        verdict: c.verdict,
        results: c.results,
        timestamp: c.timestamp,
      }))
      .join("");
    if (!data.claims.length) {
      resultsEl.innerHTML = `<div class="empty"><div class="empty-ico">🤔</div><p>No check-worthy claims were found in this video's captions.</p></div>`;
    }
  } catch (err) {
    setStatus("⚠ " + err.message);
  } finally {
    setLoading(btn, false);
  }
});
