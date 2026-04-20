# Career targeting reference

**Owner:** Chennan Li
**Last revised:** 2026-04-19
**Purpose:** a persistent strategy doc. **Not a job-scanning checklist.** The goal is to capture (1) the people and conversations that validate or extend this project, (2) the brand identity this portfolio builds, and (3) the specific talking points for the small number of deep interviews that will actually matter. Point any new Claude session here when career context comes up.

---

## How this doc relates to the others

* [ROADMAP.md](ROADMAP.md) — what blog posts ship and when
* [STUDY_PLAN.md](STUDY_PLAN.md) — the 8-phase learning + build sequence
* [BLOG2_PRD.md](BLOG2_PRD.md) — current sprint's PRD
* **This file** — the "why this person, why now" narrative + who to reach + how to talk

**Don't treat this as a to-do list. Re-read it once a month; update when a real signal changes the picture.**

---

## The authentic motivation (say this in interviews, always)

> I'm not building this to chase a job title. I'm building it because I've watched 15 years of industrial engineering get priced out of the AI conversation, and I think the reverse is true — heavy-asset industries are about to become the biggest beneficiaries of AI, and they need engineers who can speak both languages natively. Jobs are outcomes. The project is the point.

If this frame is not true, do not use it. It happens to be true for Chennan, and interviewers can tell.

---

## The identity: "Industrial AI Engineer — systems side"

Single-sentence positioning:

> **"I model plants that AI operates. PE + Python + 15 years across refining, water, and power. Systems-level thinking; partnered with component-level CUDA/HPC experts."**

Why this works:
* It's niche enough to be rare (<100 people in the US fit cleanly).
* It's broad enough to apply at NVIDIA, Anthropic Applied, OpenAI Industrial, Tesla AI Apps, Meta Reality Labs (DC infra), Schneider/Siemens AI ventures, and hyperscaler energy teams.
* It honestly communicates the CUDA gap — not a weakness to hide, a reason for partnership.
* It draws a hard edge with generic "AI engineer" resumes — the industrial + systems combination is unusual.

---

## The surrogate-model credential (buried asset, now hot)

In 2018 at GE, Chennan + the NVIDIA L4 colleague (same person who introduced this opportunity) built a surrogate for a refinery mechanistic model — NN regression on simulator output + Gaussian Process on residuals for calibrated uncertainty. The work was ahead of its time and didn't turn into external recognition; Chennan has felt stuck since.

**What changed on March 17, 2026:** DOE issued a $293M Genesis Mission RFA that names, in its published technical description, "neural network surrogates trained on validated thermodynamic and CFD simulation data" as a core methodology. The exact method Chennan and the colleague built in 2018 is now federal policy driving Genesis Mission and NGDCI work.

**How to use this:**
* In the NVIDIA phone screen: "Jonathan and I built exactly this at GE in 2018 — NN surrogate on a refinery mechanistic model, GP on residuals for uncertainty. We published nothing. Today DOE named it Genesis Mission's core technical approach. I've been waiting eight years for the world to catch up. I'm ready."
* In Blog 5.5 (new flagship post): open with a side-by-side — a 2018 GE-era plot (if any survived) next to a modern PyTorch + GPyTorch equivalent running on the AI-factory thermal + electrical models. Narrative: "Same method, different decade, very different stakes."
* On a Cerebras founder outreach: mention in passing — "surrogate models are the spine of Genesis Mission; I'm one of the few practitioners who ran this in production 8 years before it was federal policy."

**Why the 2018 work being "unrecognized" was not the waste it felt like:**
Early signal in the right direction often feels like stagnation because the market hadn't arrived yet. 2026 is the year the market arrives. Chennan is not a late entrant; he's an unusually early one whose public visibility is only now catching up. That is a feature of the narrative, not a bug to hide.

---

## Genesis Mission political window (the 4-year sprint)

Genesis Mission was launched via Executive Order 14363, not by Congressional legislation. Consequence: its guaranteed runway is the current administration's term, i.e. **2026 through January 2029**. After that a new administration can rename, restructure, or cancel with a stroke of the pen.

**Planning implication:**
* 2026–2028 is the execution window. Ship Blog 5 + 5.5 inside 2026. Establish the NGDCI alignment brand inside 2027. By 2028 the NVIDIA job should either have materialized or been replaced by equivalent inbound.
* After 2029, the technique (physical-AI surrogates) will survive because industrial adoption (Meta/Carrier/Schneider) is independent of the federal program. But the **branding halo** around "Genesis Mission alignment" may fade if a new administration distances itself.
* Translation: don't build the project on Genesis Mission's name. Build it on the underlying engineering. Genesis keywords are a 2026-28 marketing overlay, not the foundation.

---

## Pure-GenAI vs industrial-infrastructure platform (the positioning fork)

If faced with a choice between a pure-GenAI-layer company (OpenAI-style wrappers, agent frameworks, chat-UI builders) and an industrial-infrastructure data platform (NVIDIA's enterprise org, Schneider AI, Siemens Industrial AI, Carrier Energy AI), **choose the latter every time.**

Reasons:
* Pure GenAI is commodifying fast (Qwen/Llama + OpenRouter + AWS Bedrock is closing price gaps to zero).
* Industrial infrastructure has physical moats (decade-long vendor relationships, regulatory approval, insurance-backed engineering).
* Chennan's 15-year background is leverageable at industrial-infra companies and not at pure-GenAI companies (where a generic ML engineer beats him on speed).
* The Genesis Mission / NGDCI wave is flowing *into* industrial infra, not into pure GenAI.

**One-line test:** if the company's revenue depends on a physical asset that would still exist without AI (a plant, a rack, a grid, a fleet), he can win there. If revenue depends on a model API endpoint, he cannot.

---

## Current opportunity landscape (update as signals arrive)

### NVIDIA DOE-aligned Solutions Architect — status: in flight

**Context:** introduced via former GE colleague (CFD + parallel computing, NVIDIA L4 since 2019). Application was initially rejected by recruiter; reinstated after the colleague escalated. Inside signal: this seat is DOE-partnered, likely tied to ORNL Next-Generation Data Centers Institute or DOE Genesis Mission. The colleague is strong on component-level (CFD + CUDA) but not on systems / utilities / 800V DC / GenAI — which is exactly the complementary profile Chennan brings.

**Fit:** 80-85% on paper. The CUDA gap is real; the systems/domain/GenAI match is precise.

**Next expected touchpoint:** phone screen within 2-4 weeks of mid-April 2026.

**What matters most before that call:**
1. Blog 2 live (both GH Pages + Medium + Streamlit Cloud URL)
2. Blog 5 at least outlined / Tier A thermal model in progress
3. 90-second pitch rehearsed (see "Talking points" below)

**What does NOT matter:**
* Updating the resume beyond adding blog URLs
* Applying to other NVIDIA roles (stay focused on this one via this channel)
* LinkedIn grinding

### Cerebras — validation target, not application

Chennan has a direct LinkedIn connection to a Cerebras founder. **Goal:** send finished Blog 2 (with Cerebras mentioned in the hardware wiki) and ask for a 10-minute reaction. A review from someone who actually built wafer-scale silicon is the most credible validation possible for the hardware-sizing half of the blog.

**Framing when reaching out:**
> "I included Cerebras CS-3 in my hardware comparison for behind-the-meter AI factories (wiki entry linked). You're the person on the planet best positioned to tell me whether my framing is fair or naive. No pitch, no favor asked — just a gut check from the source. Ten minutes if you have them."

**Timing:** after Blog 2 is live and has 72 hours of settling.

### Kaggle Gemma 4 competition — long game

This is the capstone that ties Blog 2-6 together into a single agentic system. Submit whenever the competition window fits. Even a mid-table finish + link to the blog series is resume gold.

### Other inbound (speculative, not chasing)

If Blog 2 and Blog 5 ship well, expect cold inbound from:
* ORNL NGDCI affiliated researchers (the Feb 2026 institute is hiring + open to external partners)
* Schneider Electric / Vertiv / ABB engineering teams
* Smaller AI-factory developers (Equinix, Digital Realty, Crusoe Energy — the last one is an especially good fit given their BTM angle)
* Data-center-focused VCs doing diligence on "industrial AI" startups

Rule: respond to any warm intro within 24 hours. Don't pursue cold.

---

## The NGDCI alignment (the secret weapon)

ORNL's Next-Generation Data Centers Institute (launched Feb 26, 2026; NVIDIA/AMD/Carrier/Chemours as industry partners) has 8 focus areas. Seven of them map directly to what this project is already building:

| NGDCI focus area | Project artifact |
|---|---|
| 1. Thermal management + next-gen cooling | Blog 5 Tier A/B/C (Python + EnergyPlus + Modelica) |
| 2. Power flow redesign + power electronics + ESS | Blog 5 Phase 6 (pandapower grid-to-chip) |
| 3. Grid integration | Blog 5 latency-as-DR |
| 4. Intelligent platforms + flex AI workload coordination | Blog 5 pyomo MPC |
| 5. Cyber-informed engineering | *planned: wiki entries + Blog 5 air-gap section* |
| 6. Systems modeling for energy + supply chain | Blog 1 (EPA distribution) + Blog 5 |
| 7. Realistic-conditions cooling/power evaluation | Blog 5 three-way validation |
| 8. Supply chain + critical minerals | *not in scope; drop* |

**The one-pager deliverable:** a 1-page PDF laying out this table with GitHub links per row, titled *"Open-source reference implementation of ORNL NGDCI focus areas 1-7."* Ship this after Blog 5 is live. Attach to any NVIDIA, ORNL, or INL conversation.

---

## Talking points for the NVIDIA phone screen

When asked about **CUDA / HPC depth**:

> "I've built systems in CUDA-adjacent environments — running inference via NVIDIA NIM, deploying models on multi-GPU nodes, writing the Python that calls into cuDNN-accelerated code. I am not a CUDA optimization expert, and I'm not pretending to be. Your team has those experts. What you're telling me is missing is the systems-and-domain bridge to utilities, DC power architecture, and GenAI workflows for DOE customers. That's what I've spent the last 18 months building, in public, open source. I see myself as the translator your CUDA experts need when they're facing a utility planning VP or an INL reactor physicist."

When asked about **security clearance**:

> "US citizen, clean public work history in regulated industries. Ready to start the process immediately. Happy to work on unclassified DOE engagements during the investigation window."

When asked about **what you'd build in the first 90 days**:

> "An NGDCI-aligned reference design for a 2-5 MW BTM AI factory colocated with a wastewater plant. Pandapower electrical grid-to-chip, EnergyPlus + Modelica thermal cross-validation, pyomo MPC for latency-tiered demand response, NIM-hosted LLM for design assistance. Publish as an open case study via the institute, hand it to partners at ORNL and INL for extension to larger scales. This is literally what my blog series is already becoming."

When asked about **surrogate models or Physical AI specifically**:

> "This is actually where Jonathan and I first worked together in 2018 at GE — we built an NN surrogate on a refinery mechanistic model with a GP fit on the residuals for calibrated uncertainty. It was a 1,000× speedup and nobody outside the team cared. On March 17 this year DOE issued the Genesis Mission RFA that explicitly names 'neural network surrogates trained on validated thermo/CFD simulation data' as a core methodology. Blog 5.5 in my series walks through the 2018 method, the 2026 PyTorch + GPyTorch equivalent, and how the chance-constrained MPC built on top of it runs the Blog 5 AI-factory dispatch in real time. If the role is Genesis-Mission-adjacent, this is my strongest single artifact."

When asked about **the blog series**:

> "Nine posts, architecture is to use one running case study — a 50 MGD WWTP-colocated AI factory — and use each blog to demonstrate one distinct capability: AI-assisted design, dynamic validation, flexible operations, LLM evaluation, surrogate models, drift monitoring, Bayesian sensor reconciliation. The combination is the portfolio; the individual posts are the evidence. Blog 1 lives at [URL]. Blog 2 at [URL]. Blog 5 is in progress and it's the flagship."

---

## The brand (what Chennan should be known for by end of 2026)

**Primary**: "The person who can speak both industrial engineering and modern AI, and bridges the two with open-source reference implementations."

**Secondary proof points** that have to be true by Q4 2026:
* 5 published blog posts on the EnergyFlux project
* 1 Kaggle Gemma 4 submission (any placement)
* 1 public conference talk or podcast appearance (IEEE PES, OCP Summit, or an industry podcast — not chasing, accepting when offered)
* 1 LinkedIn-amplified launch of the blog series
* Inbound contact from ≥1 national lab researcher or hyperscaler engineer

If those five are true, the brand is established whether or not the NVIDIA job converts.

---

## What NOT to do

* **Don't** scan job boards weekly. One real conversation beats 50 applications.
* **Don't** tune the resume more than quarterly. The blog URLs are the resume now.
* **Don't** write LinkedIn posts more than once per major milestone. Over-posting dilutes the blog series' gravity.
* **Don't** chase the NVIDIA job if it drags. If there's no offer by 6 months post phone-screen, redirect energy to Kaggle + other inbound. The project was the point.
* **Don't** take on consulting work that would gut the blog timeline. Income runway first; compromise only if runway < 6 months.

---

## Signals to watch for (update this section in-place when they arrive)

* [ ] NVIDIA phone screen scheduled
* [ ] NVIDIA phone screen happened — outcome: _____
* [ ] Cerebras founder responded to Blog 2 — reaction: _____
* [ ] ORNL NGDCI researcher reached out
* [ ] Kaggle Gemma 4 submission shipped — placement: _____
* [ ] LinkedIn launch post published — date: _____

---

## How to use this file in future Claude sessions

Start the session with one of:

* **"Read /sessions/…/mnt/EnergyFlux/CAREER_TARGETING.md and STUDY_PLAN.md. I'm at [phase/event]. [What I want to do today]."** — for general work
* **"Read CAREER_TARGETING.md. [X] just happened — [phone screen, Cerebras reply, etc.]. Help me think about next moves."** — for strategic moments
* **"Update CAREER_TARGETING.md — [new signal]."** — when a checkbox above needs to flip

The file is living. It's only useful if it reflects reality when you read it.
