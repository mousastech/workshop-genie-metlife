# MetLife — AI/BI + Genie Enablement Workshop | Session Overview


**Date:** September 17, 2026 · **Time:** 11:00 AM – 1:00 PM (BRT) · **Duration:** 2 hours · **Session 2 of 2 — Business User track** · **Format:** Instructor-led, hands-on

> **The day at a glance (two sessions):**
> - **Session 1 · 09:00–11:00 — Databricks for the Technical User (Data Engineering).**
> - **Session 2 · 11:00–13:00 — Databricks for the Business User (this overview): AI/BI + Genie.**

---

## About this session

This hands-on session introduces MetLife's **business teams** to **Databricks AI/BI** — self-service dashboards and **Genie**, the natural-language interface that lets anyone ask questions of governed data in plain language and get trusted answers back as tables and charts.

Rather than slides, participants work directly in a live Databricks workspace against a realistic **insurance dataset** (Life & Pension policies, premiums, claims, fraud signals, and broker/channel distribution). By the end, each participant will have built a dashboard and run an analytical conversation in Genie against MetLife-shaped data.

The session is designed for a **business audience** — analysts and business owners. **No coding is required** and no prior Databricks experience is needed; basic familiarity with insurance concepts (policies, premiums, claims) is helpful.

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
| 11:00 – 11:10 | 1. Opening & the AI/BI vision for insurance | Why conversational analytics; quick platform tour |
| 11:10 – 11:40 | 2. AI/BI Dashboards (hands-on) | Build your first dashboard |
| 11:40 – 12:20 | 3. Genie — natural-language analytics (hands-on) | Ask questions, read the answer |
| 12:20 – 12:45 | 4. Trustworthy Genie — curation & semantic layer | Instructions, synonyms, Metric Views, Domain, glossary |
| 12:45 – 12:55 | 5. MetLife use-case lab | Fraud, distribution & persistence |
| 12:55 – 13:00 | 6. Wrap-up & adoption path | Next steps, Q&A |

---

## Key topics covered in each training block

### Block 1 — Opening & the AI/BI vision for insurance (11:00–11:10)
- The shift from report backlogs to **self-service, conversational analytics**.
- Where AI/BI Dashboards and Genie sit on the Databricks Data Intelligence Platform, and how Unity Catalog governance keeps answers safe.
- Quick tour of the workshop dataset: the insurance data model used throughout.

### Block 2 — AI/BI Dashboards, hands-on (11:10–11:40)
- Anatomy of an AI/BI dashboard: datasets, visualizations, and filters.
- Building charts from a dataset (KPIs, bar/pie, tables) with no SQL.
- Cross-filtering and layout for an executive-ready view; publishing and sharing.

### Block 3 — Genie, natural-language analytics, hands-on (11:40–12:20)
- What Genie is and how it turns plain-language questions into trusted answers.
- Running a set of business questions and reading the answer and the chart.
- Follow-up questions and iterative refinement ("break it down by region", "only active policies").
- Recognizing a good answer vs. one that needs clarification.

### Block 4 — Trustworthy Genie: curation & semantic layer (12:20–12:45)
- Why curation matters: turning a generic space into a **trusted domain agent**.
- Business **instructions** and **synonyms** (e.g., "premium", "claim ratio", "persistence").
- **Governed semantic layer**: **Metric Views** for canonical metrics (loss ratio, delinquency, persistence, fraud rate), a **Domain** (Unity Catalog tags) and a certified **business glossary**.
- **Genie Ontology**: how these governed assets — plus auto-inferred context from dashboards and queries — form the account-level "business map" that grounds Genie's answers.

### Block 5 — MetLife use-case lab (12:45–12:55)
- **Claims & fraud:** claim volumes, average settlement time, and fraud-suspicion signals.
- **Distribution:** broker and channel performance vs. targets.
- **Premium persistence:** delinquency and retention across regions and channels.

### Block 6 — Wrap-up & adoption path (12:55–13:00)
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
