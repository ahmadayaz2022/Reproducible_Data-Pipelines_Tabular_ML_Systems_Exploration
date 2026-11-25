# Part C - exploration write-ups (~1 page each, YOUR OWN words, list sources)

## C1 Optimized query system of a social-media feed
Artifact: `exploration/c1_feed_index.py`, output in `outputs/reports/c1_results.txt`. Paste YOUR run's numbers here.
Write about: why "join every followed user's posts at read time" is slow at scale; what an index on (author_id, created_at) changes
(read the EXPLAIN QUERY PLAN lines); fan-out on write vs fan-out on read (when to precompute feeds, e.g. celebrity accounts);
caching; pagination (cursor vs OFFSET); ranking. Sources: <SQLite query planner docs, engineering blogs>.

## C2 GitHub Actions, PR rules, code reviews
Artifacts: `.github/workflows/ci.yml`, `.github/PULL_REQUEST_TEMPLATE.md`, `docs/review_checklist.md`, `.github/CODEOWNERS`.
Write about: triggers (pull_request, push), jobs/steps, secrets, caching; branch protection and required status checks;
CODEOWNERS; what a good review looks like. Push to GitHub and show the workflow running green. Sources: <GitHub docs>.

## C3 Theory of system design
Artifact: glossary of 10 terms, one concrete example each (suggested terms: load balancer, cache, index, sharding, replication,
queue, CAP theorem, SQL vs NoSQL, latency vs throughput, CDN) + a one-paragraph trade-off (e.g. consistency vs availability).
Define each in YOUR words.

## C4 A workflow for system design
Artifact: one-page design doc for a small system you choose, following your workflow step by step
(clarify requirements -> estimate scale -> API -> data model -> high-level design -> deep dive -> bottlenecks/trade-offs -> review).
Record assumptions and numbers at the top of the doc.
