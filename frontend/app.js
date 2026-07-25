"use strict";

const $ = (sel) => document.querySelector(sel);
const statusEl = $("#status");
const resultsEl = $("#results");

// ---- tab switching ----
document.querySelectorAll(".tab").forEach((tab) => {
  tab.addEventListener("click", () => {
    document.querySelectorAll(".tab").forEach((t) => t.classList.remove("active"));
    document.querySelectorAll(".panel").forEach((p) => p.classList.remove("active"));
    tab.classList.add("active");
    $("#panel-" + tab.dataset.mode).classList.add("active");
    resultsEl.innerHTML = "";
    statusEl.textContent = "";
  });
});

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

function reviewHtml(r) {
  return `
    <div class="review">
      <div><span class="rating">${esc(r.rating || "No rating")}</span>
        — <span class="pub">${esc(r.publisher || r.publisherSite || "Unknown publisher")}</span></div>
      ${r.title ? `<div>${esc(r.title)}</div>` : ""}
      ${r.url ? `<a href="${esc(r.url)}" target="_blank" rel="noopener">Read the fact-check →</a>` : ""}
    </div>`;
}

function claimBlockHtml({ claimText, verdict, results, timestamp }) {
  const reviews = results.length
    ? results.map(reviewHtml).join("")
    : `<div class="review"><span class="pub">No published fact-check found for this claim.</span></div>`;
  const ts = timestamp != null ? `<span class="claim-meta">⏱ ${fmtTime(timestamp)}</span>` : "";
  return `
    <div class="claim-block">
      <div class="claim-text">${esc(claimText)}</div>
      <div class="claim-meta">
        <span class="badge ${esc(verdict)}">${esc(verdict)}</span> ${ts}
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
$("#btn-claim").addEventListener("click", async () => {
  const query = $("#claim-input").value.trim();
  if (!query) return;
  resultsEl.innerHTML = "";
  statusEl.textContent = "Searching fact-checks…";
  try {
    const data = await postJSON("/api/verify/claim", { query });
    statusEl.textContent = `${data.count} published fact-check(s) found.`;
    resultsEl.innerHTML = claimBlockHtml({
      claimText: query,
      verdict: data.verdict,
      results: data.results,
    });
  } catch (err) {
    statusEl.textContent = "⚠ " + err.message;
  }
});

// ---- link mode ----
$("#btn-link").addEventListener("click", async () => {
  const url = $("#link-input").value.trim();
  if (!url) return;
  resultsEl.innerHTML = "";
  statusEl.textContent = "Fetching captions and extracting claims…";
  try {
    const data = await postJSON("/api/verify/link", { url });
    statusEl.textContent = `${data.claimsFound} check-worthy claim(s) extracted from video ${data.videoId}.`;
    resultsEl.innerHTML = data.claims
      .map((c) => claimBlockHtml({
        claimText: c.claim,
        verdict: c.verdict,
        results: c.results,
        timestamp: c.timestamp,
      }))
      .join("");
  } catch (err) {
    statusEl.textContent = "⚠ " + err.message;
  }
});
