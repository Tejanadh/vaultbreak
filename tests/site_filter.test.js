// Run: node tests/site_filter.test.js   (needs build/site/data.json from scripts/build.py)
const assert = require("assert");
const fs = require("fs");
const path = require("path");
const { filterEntries } = require("../site/src/filter.js");

const data = JSON.parse(fs.readFileSync(path.join(__dirname, "..", "build", "site", "data.json"), "utf8"));
const all = data.entries;
assert.ok(all.length >= 15, "expected at least 15 entries");

const ids = (q) => filterEntries(all, q).map((e) => e.id);
assert.strictEqual(filterEntries(all, {}).length, all.length, "no filter returns everything");

// class filter
const re = filterEntries(all, { vuln_class: "reentrancy" });
assert.ok(re.length >= 4 && re.every((e) => e.vuln_class === "reentrancy"), "class filter");
// chain filter
const arb = filterEntries(all, { chain: "arbitrum" });
assert.ok(arb.length >= 3 && arb.every((e) => e.chains.includes("arbitrum")), "chain filter");
// severity filter
assert.ok(filterEntries(all, { severity: "high" }).every((e) => e.severity === "high"), "severity filter");
// date range (inclusive)
const y23 = filterEntries(all, { from: "2023-01-01", to: "2023-12-31" });
assert.ok(y23.length >= 4 && y23.every((e) => e.date.startsWith("2023")), "date range");
// detector filter
const det = filterEntries(all, { hasDetector: true });
assert.ok(det.length >= 5 && det.every((e) => e.has_detector), "has detector filter");
// text search: all tokens must match
assert.ok(ids({ text: "delegatecall" }).includes("VB-2025-0025"), "text finds Bybit by delegatecall");
assert.ok(ids({ text: "read only reentrancy" }).includes("VB-2023-0013"), "text finds Sentiment");
assert.strictEqual(ids({ text: "zzzznotaword" }).length, 0, "no match -> empty");
// combined filters narrow
assert.ok(ids({ vuln_class: "reentrancy", chain: "arbitrum" }).length < re.length, "combined filter narrows");
// ordering newest first
const dates = filterEntries(all, {}).map((e) => e.date);
assert.deepStrictEqual(dates, dates.slice().sort().reverse(), "newest first");
console.log("site filter tests: OK (" + all.length + " entries)");
