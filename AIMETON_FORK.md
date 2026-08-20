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

The current branch carries a local fix and regression coverage for upstream issue #14 (`select()` discards the ring pass when no cache path is given).

Local commits:

- `9ec4775f778220164862fc80047560e0b3b09690` — preserve ring-pass scores without cache.
- `10a7ac733e0af5d4768e7863db6eaad186f508aa` — add deterministic no-cache regression test requiring no paid API and no secret.

Upstream issue #14 was still OPEN when this record was written on 2026-08-20. Before rebasing or promoting this branch, re-check upstream and prefer the upstream fix when equivalent and adequately regression-tested.

## Acceptance before AIMETON use

Required before promotion beyond P0:

1. Execute local regression tests in an authorized AIMETON runtime/runner.
2. Add guard coverage for silent flat-score / 0.5 collapse and backend logprob capability.
3. Pin an immutable upstream/fork commit for every experiment.
4. Calibrate on AIMETON-owned data against hard/evidence/human outcomes.
5. Measure false accept / false reject, calibration, latency, and cost.
6. Prove semantic verifier output cannot bypass hard, evidence, policy, release, or HITL gates.
7. No paid model calls without an explicit authorized budget and secret.

## Cross-repository tracking

- Architecture: `Dimar4713/aimeton-architecture#123`
- First product calibration target: `Dimar4713/AIMETON_site_auditor#783`

This file records factual fork state. Normative system architecture remains in `aimeton-architecture`; deployment/runtime facts belong in `aimeton-infrastructure`; product-specific calibration evidence belongs in the executing repository.
