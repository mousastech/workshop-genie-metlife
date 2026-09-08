# MetLife — AI/BI + Genie Enablement Workshop | Session Overview


**Date:** September 17, 2026 · **Time:** 9:00 AM – 2:00 PM (BRT) · **Duration:** 5 hours (4h content + 1h break) · **Format:** Instructor-led, hands-on

---

## About this session

This hands-on workshop introduces MetLife's business and data teams to **Databricks AI/BI** — self-service dashboards and **Genie**, the natural-language interface that lets anyone ask questions of governed data in plain language and get trusted answers back as tables, charts, and SQL.

Rather than slides, participants work directly in a live Databricks workspace against a realistic **insurance dataset** (Life & Pension policies, premiums, claims, fraud signals, and broker/channel distribution). By the end, each participant will have built a dashboard and run a full analytical conversation in Genie against MetLife-shaped data.

The session is designed for a **mixed audience** of business analysts and data practitioners. No prior Databricks experience is required; basic familiarity with insurance concepts (policies, premiums, claims) is helpful.

---

## What participants will be able to do

- Navigate the Databricks Data Intelligence Platform and understand where AI/BI and Genie fit.
- Build and share an **AI/BI dashboard** with filters and visualizations — no code required.
- Ask business questions in natural language through **Genie** and validate the generated SQL.
- Understand what makes a Genie answer *trustworthy*: curated instructions, business synonyms, table relationships, certified example queries, and a governed semantic layer (Metric Views, Domain, glossary) — the building blocks of **Genie Ontology**.
- Apply all of the above to three **MetLife use cases**: claims & fraud, distribution performance, and premium persistence.

---

## Agenda at a glance

| Time | Block | Focus |
|------|-------|-------|
| 09:00 – 09:30 | 1. Opening & the AI/BI vision for insurance | Why conversational analytics; platform tour |
| 09:30 – 10:30 | 2. AI/BI Dashboards (hands-on) | Build your first dashboard |
| 10:30 – 11:30 | 3. Genie — first conversation (hands-on) | Natural-language analytics on insurance data |
| 11:30 – 12:30 | Break / Lunch | — |
| 12:30 – 13:30 | 4. Genie deep dive — curation, semantic layer & Ontology (hands-on) | Instructions, synonyms, Metric Views, Domain, glossary, certified SQL |
| 13:30 – 13:50 | 5. MetLife use-case lab | Fraud, distribution & persistence |
| 13:50 – 14:00 | 6. Wrap-up & adoption path | Next steps, Q&A |

---

## Key topics covered in each training block

### Block 1 — Opening & the AI/BI vision for insurance (09:00–09:30)
- The shift from report backlogs to **self-service, conversational analytics**.
- Where AI/BI Dashboards and Genie sit on the Databricks Data Intelligence Platform, and how Unity Catalog governance keeps answers safe.
- Tour of the workshop dataset: the insurance data model participants will use all day.

### Block 2 — AI/BI Dashboards, hands-on (09:30–10:30)
- Anatomy of an AI/BI dashboard: datasets, visualizations, and filters.
- Building charts from a dataset (KPIs, bar/line, tables) with no SQL.
- Cross-filtering, period selectors, and layout for an executive-ready view.
- Publishing and sharing a dashboard with the team.

### Block 3 — Genie, first conversation, hands-on (10:30–11:30)
- What Genie is and how it translates natural language into governed SQL.
- Running a first set of business questions and reading the answer, the chart, and the generated SQL.
- Follow-up questions and iterative refinement ("break it down by region", "only active policies").
- Recognizing a good answer vs. one that needs clarification.

### Block 4 — Genie deep dive: curation, semantic layer & Ontology, hands-on (12:30–13:30)
- Why curation matters: turning a generic space into a **trusted domain agent**.
- Business **instructions** and **synonyms** (e.g., "premium", "claim ratio", "persistence").
- **Table relationships (joins)** so multi-table questions work reliably.
- **Governed semantic layer**: **Metric Views** for canonical metrics (loss ratio, delinquency, persistence, fraud rate), a **Domain** (Unity Catalog tags) and a certified **business glossary**.
- **Genie Ontology**: how these governed assets — plus auto-inferred context from dashboards and queries — form the account-level "business map" that grounds Genie's answers.
- **Certified example SQL** and sample questions that steer Genie toward correct patterns; validating improvements by re-asking questions that previously failed.

### Block 5 — MetLife use-case lab (13:30–13:50)
- **Claims & fraud:** claim volumes, average settlement time, and fraud-suspicion signals.
- **Distribution:** broker and channel performance vs. targets.
- **Premium persistence:** delinquency and retention across regions and channels.

### Block 6 — Wrap-up & adoption path (13:50–14:00)
- From workshop to production: how to bring MetLife's own data into Genie.
- Governance, sharing, and rollout considerations.
- Open Q&A.

---

## Prerequisites & logistics

- **Access:** each participant needs a Databricks workspace login (provided ahead of the session) and a laptop with a modern browser.
- **No installation** is required — everything runs in the browser.
- **Dataset & Genie space** are pre-provisioned; participants start asking questions from minute one.
- Recommended group size for a hands-on format: up to ~25 participants.

*Prepared by the Databricks team for MetLife. The workshop uses a synthetic, MetLife-shaped insurance dataset created for training purposes only.*
