/* Pure filtering logic, shared by the browser (app.js) and the node test. No dependencies. */
(function (root, factory) {
  if (typeof module === "object" && module.exports) module.exports = factory();
  else root.VBFilter = factory();
})(typeof self !== "undefined" ? self : this, function () {
  function tokens(q) {
    return (q || "").toLowerCase().split(/[^a-z0-9$:._-]+/).filter(Boolean);
  }
  /* q = {text, vuln_class, chain, severity, from, to, hasDetector}  (all optional) */
  function filterEntries(entries, q) {
    const toks = tokens(q.text);
    const out = entries.filter(function (e) {
      if (q.vuln_class && e.vuln_class !== q.vuln_class) return false;
      if (q.chain && e.chains.indexOf(q.chain) === -1) return false;
      if (q.severity && e.severity !== q.severity) return false;
      if (q.from && e.date < q.from) return false;
      if (q.to && e.date > q.to) return false;
      if (q.hasDetector && !e.has_detector) return false;
      for (let i = 0; i < toks.length; i++) if (e.text.indexOf(toks[i]) === -1) return false;
      return true;
    });
    /* newest first; stable tie-break on id */
    out.sort(function (a, b) { return a.date < b.date ? 1 : a.date > b.date ? -1 : a.id < b.id ? -1 : 1; });
    return out;
  }
  return { filterEntries: filterEntries, tokens: tokens };
});
