# AIMETON fork status

Status: experimental / P0 evaluation fork. This repository is not yet an AIMETON production dependency.

## Provenance

- Upstream: `llm-as-a-verifier/llm-as-a-verifier`
- AIMETON fork: `Dimar4713/llm-as-a-verifier`
- Clean upstream mirror branch: `main`
- AIMETON working branch: `aimeton/verifier-p0`
- Fork baseline SHA: `8db8a114355a9d7fdf9a8d1d5c87f6aeebd18770`
- Baseline date: 2026-08-20

The `main` branch is intended to remain a clean synchronization point with upstream. AIMETON-specific experiments and temporary fixes belong on dedicated branches until an explicit promotion decision is made.

## AIMETON integration status

Architectural decision: ADOPT IDEA / TRIAL IMPLEMENTATION / DO NOT STANDARDIZE UPSTREAM DEPENDENCY YET.

The verifier is treated as a probabilistic semantic verification layer inside the wider AIMETON Verification Mesh. It must not override deterministic tests, evidence/provenance failures, policy prohibitions, OCC-49 restrictions, or mandatory HITL gates.

Invariant: **Verifier != Truth.**

## Local P0 delta

The current branch carries a local fix and regression coverage for upstream issue #14 (`select()` discards the ring pass when no cache path is given), plus an AIMETON-only fail-closed score-evidence guard that distinguishes valid score evidence from the upstream fallback value `0.5`.

Key commits:

- `9ec4775f778220164862fc80047560e0b3b09690` — preserve ring-pass scores without cache.
- `10a7ac733e0af5d4768e7863db6eaad186f508aa` — deterministic no-cache regression test.
- `6210d63717ef016bd7527c0897a3305836180a2a` — move public-fork regression to an isolated GitHub-hosted runner; no Marketplace actions.
- `1c68693179a8c2ac506d2988aeeec6fe334cbec9` — add fail-closed AIMETON score-evidence guard.
- `92a817a71f900e61fcc682fc9c55eb9b5551010a` — regression coverage for missing/partial/logprob/text score evidence.
- `9cabf17e3644778893666b864aec924e740006ba` — run the full AIMETON verifier P0 regression suite.

Upstream issue #14 was still OPEN when checked on 2026-08-20. Before rebasing or promoting this branch, re-check upstream and prefer the upstream fix when equivalent and adequately regression-tested.

## Verified CI evidence

The AIMETON runner inventory currently uses repository-scoped self-hosted runners. Because this fork is public, the P0 regression workflow intentionally uses a fresh standard GitHub-hosted Linux runner instead of exposing an AIMETON self-hosted host to public-repository workflow risk. The workflow does not use `actions/checkout`, `actions/setup-python`, or other Marketplace actions; it materializes the exact SHA with git and runs Python's standard-library `unittest`.

Confirmed runs:

- Run `32398652273`: exact head `6210d63717ef016bd7527c0897a3305836180a2a`; no-cache ring-pass regression passed.
- Run `32398812463`: exact head `9cabf17e3644778893666b864aec924e740006ba`; full P0 regression suite passed.

## Acceptance before AIMETON use

Required before promotion beyond P0:

1. Keep local regression tests green on every AIMETON branch change.
2. Keep fail-closed coverage for silent flat-score / missing score evidence and add live backend logprob capability probing before any model is trusted.
3. Pin an immutable upstream/fork commit for every experiment.
4. Calibrate on AIMETON-owned data against hard/evidence/human outcomes.
5. Measure false accept / false reject, calibration, latency, and cost.
6. Prove semantic verifier output cannot bypass hard, evidence, policy, release, or HITL gates.
7. No paid model calls without an explicit authorized budget and secret.

## Cross-repository tracking

- Architecture: `Dimar4713/aimeton-architecture#123`
- First product calibration target: `Dimar4713/AIMETON_site_auditor#783`

This file records factual fork state. Normative system architecture remains in `aimeton-architecture`; deployment/runtime facts belong in `aimeton-infrastructure`; product-specific calibration evidence belongs in the executing repository.
