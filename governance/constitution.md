# The AI-First Constitution

Ten articles that do not bend. Everything else in this repository — policies,
skills, hooks, workflows, thresholds — is negotiable through the process in
[GOVERNANCE.md](../GOVERNANCE.md). These are not.

A constitution that could be amended to make today's build pass would not be a
constitution. If an article genuinely blocks legitimate work, that is a signal to
re-examine the work, not to edit the article.

---

## Article 1 — No feature without a specification

No production code for a new feature may be created without a corresponding
specification.

The specification exists before the code, not as documentation written
afterwards to justify what was built. "We will write the spec after" means there
was no specification; it means there was a reconstruction.

*Enforced by:* `scripts/check-pr-spec-link.py`, `specification-gate.yml`,
`PreToolUse` hook.

---

## Article 2 — Specification before prompt

The implementation prompt is **derived from** a reviewed specification. It does
not replace it.

A prompt is an instruction to a machine. A specification is an agreement between
people about what should exist and why. Collapsing the two loses the agreement
and keeps only the instruction — which is exactly the failure mode that makes
generated codebases unmaintainable.

*Enforced by:* `scripts/validate-prompts.py` (a prompt without a `spec_id` is
invalid), `/spdd-generate`.

---

## Article 3 — The prompt is a versioned artifact

Every prompt used for a meaningful implementation must be versioned, carry an
identifier, point to a specification, declare its constraints, declare its stop
conditions, declare its verifications, and keep a change log.

A prompt that produced production code and then vanished from history makes that
code unexplainable. If the prompt mattered enough to generate the system, it
matters enough to review and to keep.

*Enforced by:* `schemas/prompt-reasons.schema.json`, `scripts/validate-prompts.py`.

---

## Article 4 — Dependencies point inward

Domain and application must not depend on frameworks, databases, transports or
adapters.

This is the one architectural rule from which most of the others follow. A
domain that imports a web framework cannot be tested in milliseconds, cannot be
reused, and cannot outlive the framework's next major version.

*Enforced by:* ArchUnit, Import Linter, `architecture-gate.yml`, and negative
fixtures proving the controls actually fire.

---

## Article 5 — Architecture is executable

Every architectural rule that matters must have an automated check.

A rule enforced only by reviewer memory is not a rule; it is a preference that
decays with the first deadline, the first new joiner, or the first tired
reviewer. If a rule cannot be expressed as a check, either express it better or
stop calling it a rule.

*Enforced by:* the architecture policy requires a non-empty `enforced_by` for
every rule; `scripts/validate-architecture-policy.py` fails otherwise.

---

## Article 6 — AI does not approve alone

An AI analysis may find problems and produce recommendations. It must never be
the sole mechanism authorising a merge.

Probabilistic review is a genuinely useful second opinion. It is a poor final
authority, because it is confidently wrong in ways that are hard to predict and
easy to accept. Deterministic gates block; AI advises.

*Enforced by:* `ai-review.yml` is non-blocking by construction; the branch
ruleset requires human approval. Rationale in
[ADR-0005](../docs/decisions/ADR-0005-ai-review-is-not-the-only-gate.md).

---

## Article 7 — Evidence before completion

A change may be declared complete only when evidence exists for: compilation,
tests, lint, typing, architecture, security, acceptance criteria and
traceability.

Evidence means a recorded command and its recorded, real result. A summary
saying "all tests pass" is not evidence. `NOT_EXECUTED` with a reason is
acceptable and honest; a fabricated `PASS` is a governance failure regardless of
whether the code happened to be correct.

*Enforced by:* `schemas/evidence.schema.json` (a `SKIPPED` or `NOT_EXECUTED`
entry must carry a reason), `Stop` hook, `/close-spec`.

---

## Article 8 — Divergence corrects intent first

When code, specification and prompt diverge, the team decides which intent is
valid and updates the intent artifacts **before** generating a new
implementation.

The reflex is to patch the code, because the code is what is failing. That
silently makes the specification a lie, and every future decision is then made
against a document nobody trusts. Fix the intent, then regenerate.

*Enforced by:* `/review-change` reports specification divergence; the pull
request template requires acknowledging it.

---

## Article 9 — Exceptions are explicit

Every deliberate violation of an architectural rule must have an ADR, a
justification, a review deadline and a named owner.

Exceptions are legitimate. Engineering is full of situations where the right
answer is "not now". What is not legitimate is the *undocumented* exception,
which is indistinguishable from a bug, and the *permanent* exception, which is
just a deleted rule wearing a disguise.

No exception is permanent by default. Maximum duration: 90 days.

*Enforced by:* [`architecture-exceptions.md`](architecture-exceptions.md),
CODEOWNERS review, `validate-repository.yml`.

---

## Article 10 — Security and privacy

No prompt, log, workflow or example may expose a secret, token, password,
personal datum, real banking datum, confidential information, or unauthorised
proprietary content.

This applies to the *process artifacts* as much as to the code. A specification
pasted from a real incident, a prompt containing a production connection string,
a workflow echoing a token into a log — each leaks as effectively as a committed
credential.

The `Create PIX Payment` example is educational: no real bank integration, no
real endpoint, no real personal or banking data. It must stay that way.

*Enforced by:* gitleaks, `PreToolUse` secret-pattern guard, `security.yml`,
CODEOWNERS review.

---

## Amendment

Articles are amended only by a pull request that:

1. links a specification of type `architecture-change`;
2. carries an ADR explaining what changed and why the previous article failed;
3. is approved by CODEOWNERS;
4. passes every gate without exception.

An article may not be amended to unblock an in-flight change. Ship the change
under a documented, expiring exception first, then argue the amendment on its own
merits, separately.
