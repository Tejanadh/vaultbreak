/* Client-side search and filter over data.json. No framework, no network beyond data.json. */
(function () {
  const $ = (id) => document.getElementById(id);
  const state = {};
  const FIELDS = ["text", "vuln_class", "chain", "severity", "from", "to"];

  function readHash() {
    const p = new URLSearchParams(location.hash.slice(1));
    FIELDS.forEach((f) => { state[f] = p.get(f) || ""; });
    state.hasDetector = p.get("detector") === "1";
  }
  function writeHash() {
    const p = new URLSearchParams();
    FIELDS.forEach((f) => { if (state[f]) p.set(f, state[f]); });
    if (state.hasDetector) p.set("detector", "1");
    history.replaceState(null, "", p.toString() ? "#" + p : location.pathname);
  }
  function fill(sel, items, label) {
    sel.innerHTML = "";
    sel.add(new Option(label, ""));
    items.forEach((i) => sel.add(new Option(i.name || i, i.id || i)));
  }
  function el(tag, cls, text) {
    const n = document.createElement(tag);
    if (cls) n.className = cls;
    if (text !== undefined) n.textContent = text;
    return n;
  }
  function render(data) {
    const res = VBFilter.filterEntries(data.entries, state);
    $("count").textContent = res.length + " of " + data.entries.length + " entries";
    const list = $("results");
    list.innerHTML = "";
    res.forEach((e) => {
      const li = el("li", "card sev-" + e.severity);
      const a = el("a", "title", e.title);
      a.href = "entries/" + e.slug + ".html";
      li.appendChild(a);
      li.appendChild(el("div", "meta", [e.date, e.chains.join(", "), e.class_name, e.severity, e.loss_text,
        e.has_detector ? (e.detector_validated ? "detector: validated" : "detector: draft") : "no detector",
        e.needs_review ? "needs review" : "reviewed"].join(" | ")));
      li.appendChild(el("p", "summary", e.summary.length > 220 ? e.summary.slice(0, 217) + "..." : e.summary));
      list.appendChild(li);
    });
    if (!res.length) list.appendChild(el("li", "empty", "No entries match these filters."));
  }
  fetch("data.json").then((r) => r.json()).then((data) => {
    fill($("vuln_class"), data.options.classes, "All classes");
    fill($("chain"), data.options.chains, "All chains");
    fill($("severity"), data.options.severities, "All severities");
    readHash();
    FIELDS.forEach((f) => { $(f).value = state[f]; });
    $("hasDetector").checked = state.hasDetector;
    const update = () => {
      FIELDS.forEach((f) => { state[f] = $(f).value.trim(); });
      state.hasDetector = $("hasDetector").checked;
      writeHash();
      render(data);
    };
    document.querySelectorAll("#filters input, #filters select").forEach((n) => n.addEventListener("input", update));
    $("reset").addEventListener("click", () => { FIELDS.forEach((f) => { $(f).value = ""; }); $("hasDetector").checked = false; update(); });
    window.addEventListener("hashchange", () => { readHash(); FIELDS.forEach((f) => { $(f).value = state[f]; }); render(data); });
    render(data);
  }).catch((err) => { $("count").textContent = "Could not load data.json (" + err + "). Serve the folder over http."; });
})();
