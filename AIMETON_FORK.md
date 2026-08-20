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

Current P0 assessment after the first live calibration: **strong research substrate, not yet production-grade probabilistic verifier**.

The verifier is treated as a probabilistic semantic verification layer inside the wider AIMETON Verification Mesh. It must not override deterministic tests, evidence/provenance failures, policy prohibitions, OCC-49 restrictions, or mandatory HITL gates.

Invariant: **Verifier != Truth.**

## Local P0 delta

The current branch carries a local fix and regression coverage for upstream issue #14 (`select()` discards the ring pass when no cache path is given), plus AIMETON-only fail-closed guards that distinguish:

1. valid score evidence from the upstream fallback value `0.5`; and
2. a genuinely non-degenerate probabilistic A-T distribution from a singleton score-token point estimate.

Key commits:

- `9ec4775f778220164862fc80047560e0b3b09690` — preserve ring-pass scores without cache.
- `10a7ac733e0af5d4768e7863db6eaad186f508aa` — deterministic no-cache regression test.
- `6210d63717ef016bd7527c0897a3305836180a2a` — move public-fork regression to an isolated GitHub-hosted runner; no Marketplace actions.
- `1c68693179a8c2ac506d2988aeeec6fe334cbec9` — add fail-closed AIMETON score-evidence guard.
- `92a817a71f900e61fcc682fc9c55eb9b5551010a` — regression coverage for missing/partial/logprob/text score evidence.
- `9cabf17e3644778893666b864aec924e740006ba` — run the full AIMETON verifier P0 regression suite.
- `54841440731ac91017c35f39218fea61d5bffd33` — add fail-closed non-degenerate score-distribution support guard.
- `7202846ca049d19d72db7885fba2f5de6d732ef8` — regress singleton A-T support, literal-only scores, duplicate case variants, and an immutable minimum support floor of two distinct score values.

Upstream issue #14 was still OPEN when checked on 2026-08-20. Before rebasing or promoting this branch, re-check upstream and prefer the upstream fix when equivalent and adequately regression-tested.

## Live Golden-5 finding

The first AIMETON live calibration attempt against RouterAI / `openai/gpt-4o-mini` deliberately failed closed in Site Auditor run `32416294981` rather than manufacturing missing probabilistic evidence.

Observed provider facts:

- provider attempts: `144`;
- provider successes: `144`;
- responses with logprobs: `96` / `96` expected score responses;
- accepted non-degenerate score-distribution events: `86` / `96`;
- prompt tokens: `173,932`;
- completion tokens: `14,409`;
- estimated cost: `3.487929 RUB`.

The ten rejected responses were not HTTP/provider failures. They exposed a semantic extraction limitation: generic `top_logprobs=20` can contain only one A-T score alternative at a score position because non-score tokens consume the remaining top-logprob slots. Upstream-compatible `extract_score()` accepts any non-empty A-T support and renormalizes a singleton to a point estimate. AIMETON therefore must not equate `logprobs present` with `probabilistic distribution measured`.

P0 scientific floor: every required score tag must expose at least **two distinct A-T score values** before AIMETON treats the event as a probabilistic semantic-verifier measurement. This is a minimum validity floor, not proof of good calibration. Future work should prefer constrained score-token decoding/prefill where the backend supports it, then measure calibration quality rather than merely support count.

## What is already strong

- Pairwise comparison is a better primitive for trajectory selection than a single free-form judge score.
- Probabilistic Pivot Tournament reduces comparison cost from full O(N²) while retaining multiple directed comparisons.
- Ring-direction / repeated slot swapping gives a concrete mechanism for reducing A/B position bias.
- The 20-token ordinal scale creates a useful fine-grained semantic signal when the backend actually exposes sufficient score-token support.
- Token accounting, caching, bounded concurrency and backend abstraction are useful production foundations.
- The fork has already demonstrated that it can fail closed around upstream compatibility fallbacks without corrupting the clean upstream mirror.

## What remains weak or unproven

- Generic OpenAI-compatible `top_logprobs=20` does **not** guarantee coverage of the 20 score letters; the first live run produced 10/96 singleton score supports.
- Renormalizing only the visible A-T mass can be badly overconfident when most probability mass is on tokens outside the score alphabet.
- Literal-text fallback is evidence of a chosen score, not a probability distribution.
- The 20-letter scale has not yet been calibrated against AIMETON hard/evidence/human outcomes; ordinal spacing is assumed linear by `extract_score`.
- Model/provider dependence, calibration drift, criterion correlation, and false-accept/false-reject rates are not yet measured.
- `on_error="tie"` is convenient for general library use but is not acceptable as an AIMETON release-authority fallback; AIMETON callers must remain fail-closed.

## Verified CI evidence

The AIMETON runner inventory currently uses repository-scoped self-hosted runners. Because this fork is public, the P0 regression workflow intentionally uses a fresh standard GitHub-hosted Linux runner instead of exposing an AIMETON self-hosted host to public-repository workflow risk. The workflow does not use `actions/checkout`, `actions/setup-python`, or other Marketplace actions; it materializes the exact SHA with git and runs Python's standard-library `unittest`.

Confirmed historical runs:

- Run `32398652273`: exact head `6210d63717ef016bd7527c0897a3305836180a2a`; no-cache ring-pass regression passed.
- Run `32398812463`: exact head `9cabf17e3644778893666b864aec924e740006ba`; full P0 regression suite passed.
- Run `32398924670`: exact head `0000bd7700f0d3199e68ed401ac47669e8453a81`; P0 regression passed.

The distribution-support guard added after the Golden-5 finding must also pass exact-head CI before any repeat live calibration.

## Acceptance before AIMETON use

Required before promotion beyond P0:

1. Keep local regression tests green on every AIMETON branch change.
2. Keep fail-closed coverage for silent flat-score / missing / singleton score evidence and live backend logprob capability probing before any model is trusted.
3. Pin an immutable upstream/fork commit for every experiment.
4. Calibrate on AIMETON-owned data against hard/evidence/human outcomes.
5. Measure false accept / false reject, calibration, latency, and cost.
6. Prove semantic verifier output cannot bypass hard, evidence, policy, release, or HITL gates.
7. No paid model calls without an explicit authorized budget and secret.

## Cross-repository tracking

- Architecture: `Dimar4713/aimeton-architecture#123`
- First product calibration target: `Dimar4713/AIMETON_site_auditor#783`

This file records factual fork state. Normative system architecture remains in `aimeton-architecture`; deployment/runtime facts belong in `aimeton-infrastructure`; product-specific calibration evidence belongs in the executing repository.
