# Samketan AI: independent lead-intelligence roadmap

This is an original implementation, not a port or fork of Treg/Cline.
Do not copy proprietary source, visual design, names, or paid provider datasets.

## Existing app (reviewed)
- Streamlit in `app.py`, Gemini research with optional grounding, Hunter lookup.
- Existing lead parsing and outreach generation are not yet wired to the new gateway.
- Authentication fail-open fallback and unverified client cookie restoration
  were removed in the development branch.

## Phase 1: security
- [x] Remove automatic sign-in when `auth` import fails.
- [x] Remove implicit sign-in based solely on a browser cookie.
- [ ] Review OTP rate limits, expiration, session lifecycle and logout.
- [ ] Add integration tests for the Streamlit login flow.

## Phase 2: original provider-neutral gateway
- [x] Define typed evidence and candidate records, injectable providers and limits.
- [ ] Adapter for an approved search provider (do not scrape restricted services).
- [ ] Add per-provider API budgets, timeout controls and retry ceilings.
- [ ] Store records and source provenance in durable storage.
- [ ] Connect the gateway to the existing Streamlit application after validation.

## Phase 3: quality and compliance
- [ ] Separate company prospects, verified requirement signals and contacted leads.
- [ ] Require source URLs for any evidence-backed label.
- [ ] Add duplicate detection, freshness checks and human approval.
- [ ] Verify licensing and permitted use of each data provider.

## Phase 4: agent planning
- [ ] Introduce bounded, human-approved research plans.
- [ ] Evaluate lead accuracy and cost against current app.

Production `main` must not be updated until tests, user review and deployment checks pass.
