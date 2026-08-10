# Outreach Copy Playbook

The working spec behind `build_outreach.py` and `outreach_full.csv`.

Source of truth is **Master Outreach Copy Instruction**. This document records how
that instruction was turned into something repeatable across 4,821 rows, plus the
judgment calls that were mine rather than the instruction's. Those are marked
**[my call]** so you can overrule them.

---

## 1. Operating principle

One email is one argument:

> real signal → what it probably means → one believable problem → the three things
> that matter → the small part we help with → want to see it?

If any link in that chain cannot be made from the row's own research, the row is
**HOLD**. Weak personalisation is worse than no send.

---

## 2. Where the signal comes from

Only two fields are read: **`Research Brief`** and **`Reasoning`**.

(`Prospect Research JSON` is empty across the whole file — every row literally
contains the string `Response`. Nothing is drawn from it.)

Job title is **never** used as an opener. Title-based copy is the exact thing the
instruction forbids, and it is what made the first pass read as filler.

---

## 3. Signal tiers

Matching stops at the first hit, so the strongest available signal always wins.

### Tier A — the person said or did something public

| Signal | Requires | Opener shape |
|---|---|---|
| `casestudy` | "case study" **and** a quote word **and** their name | "Was reading the case study where you talked about X." |
| `spoke` | podcast / interview / webinar / panel / keynote + name | "Was listening to the podcast you did about X." |
| `authored` | published + blog/article/byline, **and no profile word** | "Was reading the piece you wrote about X." |
| `profile` | first-party statements on their LinkedIn profile | "Looks like X is a big part of your week." |
| `cert` | Salesforce admin certification | "Looks like you hold a Salesforce admin cert…" |

### Tier B — something happened to them

| Signal | Opener shape |
|---|---|
| `promotion` | "Saw you picked up a wider remit at X recently." |
| `newrole` | "Was looking at your move into revenue operations at X." |

### Tier C — something happened to the company

| Signal | Opener shape |
|---|---|
| `funding` | "Saw X raised a $90M Series C." |
| `acq_target` | "Saw X was acquired." |
| `acq_buyer` | "Saw X has been picking up other businesses." |
| `sf_integration` | "Looks like Salesforce is pretty woven into how X works." |
| `sf_sor` | "Looks like Salesforce is the system of record across X." |
| `hiring` | "Saw X has been hiring across the sales side." |

### Tier D — nothing → **HOLD**

---

## 4. Guards (what stops false personalisation)

These exist because each one produced a wrong email in testing.

| Guard | Catches | Real example it killed |
|---|---|---|
| **Negation** | Absence read as presence | *"**No** first-party quotes… **nor** a case study"* was becoming "Was reading a case study you were quoted in." |
| **Unverified** | Research that flags itself | *"(UNVERIFIED, not opened)"* was becoming "Was listening to a webinar you did." |
| **Attribution** | Company facts read as personal | An **AWS** case study about Condé Nast was becoming "a case study you were quoted in." |
| **Profile ≠ published** | LinkedIn About text called an article | *"self-authored summary language"* was becoming "Was reading the piece you wrote." |
| **Prior role** | Stale topics | *"forecasting… among his responsibilities in **prior role**"* — dropped, since it describes a job they left. |
| **Corp doc** | Earnings/job reqs as quotes | An earnings release "explicitly highlights…" was being read as the person speaking. |
| **Direction** | Who acquired whom | Only used when the brief makes direction unambiguous; otherwise skipped. |
| **Amount context** | Investment ≠ funding | Kirkland & Ellis **investing** $500M in AI would have become "raised $500M." Now requires `raised / secured / closed`. |

---

## 5. HOLD rules

A row is held when **any** applies:

1. No work email.
2. First name unusable for a greeting — initials (`M`, `O`) or junk (`Üöä`).
3. No company name.
4. Research flags the role or company as **stale** ("left that role", "no longer at",
   "outdated"). Example: Daren Delaney, listed at CI Eaton Vance, actually at Morgan
   Stanley since 2022.
5. **No concrete signal** — the only possible opener would be generic title copy.

Rule 5 is the big one: it is why HOLD went from 358 to 1,695. Those rows are exactly
the ones that produced *"Was reading a bit about the revenue operations side of
things at Siteminder"* — an opener that references nothing.

---

## 6. Status meanings

| Status | Count | Meaning |
|---|---:|---|
| `SEND-READY` | 2,178 | Tier A or B signal, or funding. Personal and specific. |
| `REVIEW` | 948 | Tier C only. Accurate, but about the company, not the person. |
| `HOLD` | 1,695 | Blank copy + a reason in `notes`. |

**[my call]** `funding` counts as SEND-READY even though it's a company fact — a
fresh raise is specific, dated, and genuinely changes the reader's week. Move it to
REVIEW if you'd rather every SEND-READY row be personal.

**[my call]** A `profile` signal with no nameable topic drops to REVIEW, because
"Looks like you've spent a lot of your career around revenue operations" is close to
the title copy we're trying to avoid.

---

## 7. Sentence 2 — the rule that fixed the readability problem

Sentence 2 must state a **plain consequence that the problem can then contradict**.
It must not restate the signal.

The turn works when S2 ends on an expectation and the problem breaks it:

> Looks like Salesforce is the system of record across Alegeus. **So that's where
> everyone goes to check where a deal stands.**
>
> **But someone has to remember to log every call and email, so a busy week leaves gaps.**

Banned in S2 and the problem line — all were live in an earlier draft:

- "the older story"
- "land nowhere useful"
- "something older"
- "the full deal picture"
- "where the picture usually goes wrong"
- "what the pipeline should look like"
- "a wider angle"

These are enforced by an automated check, not by judgment.

---

## 8. Problem lines

One concrete idea. No two-clause pile-ups. The underlying claim is always the same
human fact: **the newest thing a buyer said is sitting in an inbox, not in the CRM.**

Wording varies by theme:

| Theme | Example |
|---|---|
| forecast | "But by forecast time, a deal can still look fine when the last call with the buyer said otherwise." |
| pipeline | "But the newest thing a buyer said usually sits in someone's email, not in Salesforce." |
| crm | "But someone has to remember to log every call and email, so a busy week leaves gaps." |
| account | "And the next owner only sees what the last one remembered to write down." |

---

## 9. Theme routing

Theme is chosen by signal type, and it drives the subject, bullets, and help line
together — so the three always agree.

| Signal | Theme | Subject |
|---|---|---|
| promotion, newrole, hiring | forecast | `forecast context` |
| spoke, authored, profile, funding | pipeline | `pipeline context` |
| casestudy, cert, sf_integration, sf_sor | crm | `crm context` |
| acq_target, acq_buyer | account | `account context` |

### Bullets per theme

- **forecast** — what changed since the last forecast update / which deals are losing buyer activity / what the rep has committed to do next
- **pipeline** — what changed since the last buyer conversation / which deals are starting to lose momentum / what the rep has committed to do next
- **crm** — what changed since the last buyer conversation / which deals are missing recent activity / what the rep has committed to do next
- **account** — what changed since the last customer update / which accounts may be starting to slow / what the next owner needs to do

Always exactly three. Always `what changed → where risk is → what happens next`.

### Team label by function

`Enablement` → enablement teams · `Partner/Channel` → account teams ·
`SalesOps` → Sales Ops teams · `Analytics/Data` → revenue teams · everything else →
RevOps teams.

---

## 10. How-we-help line

Two capabilities maximum, in plain English, never feature names. Normal hyphen,
never an em dash. Product name stays out — the video explains the product.

> That's what we've been helping RevOps teams with - making sure emails and meetings
> land on the right Salesforce records, and flagging deals that may be starting to slow.

---

## 11. CTA

Identical on every row, by instruction:

> Can I share a 2-minute video showing how we approach this, just so you can compare
> it with your current setup?

No meetings, no 15 minutes, no demo, no calendar link.

---

## 12. Salesforce confidence

When the research says Salesforce is unconfirmed, copy says "the CRM" instead. Two
forms are tracked so grammar holds:

- noun — "…while **the CRM** shows an older version"
- attributive — "…the right **CRM** records" (not "the right the CRM records")

---

## 13. Names and companies

- **First name**: first token only. `Andrew James Smith` → `Andrew`.
- **Company**: shortest name an employee would actually type. Strips `Inc / LLC / Ltd
  / Corporation`, parentheticals, and trailing descriptors.
- **Truncation repair**: when the source name is shorter than the domain suggests, the
  fuller name is recovered from the brief **only if it matches the domain exactly**.
  `Cohere` + `coherehealth.com` → **Cohere Health**. This matters: Cohere is a
  different, well-known company. Same fix gives Janus Henderson, Cars Commerce.
  A recovered name can never re-add a legal suffix (`foxcorporation.com` stays `Fox`).

---

## 14. Data quality flag

`data_flag` marks **236 rows** where the email domain doesn't match the company site —
usually a stale address from a previous employer. Christina Catchpole is confirmed at
Nasdaq but her address is `@swisslog.com`.

**[my call]** Flagged, not held, because some are legitimate subsidiaries
(`bhnetwork.com` for Blackhawk Network, `visa.com` for CardinalCommerce). Filter these
before loading into any sender.

---

## 15. Automated QA

Runs over every row; the build is not accepted with failures.

**Structure** — exactly 3 bullets · subject line present · no empty fields on live
rows · greeting matches first name · HOLD rows carry blank copy and a reason.

**Formatting** — no em/en dashes · no double spaces · no doubled articles
("the the") · no `a`/`an` disagreement · no template leakage (`{}`, `None`) · encoding
clean.

**Language** — no banned CTA wording · no banned openers ("I noticed", "Given your
role") · no forced praise ("impressive", "amazing") · no gendered pronouns in copy ·
no banned vague phrases · no sentence over 26 words.

**Data** — no legal suffix left in company · company name ≤ 3 words · first name
usable.

Current run: clean, except 6 rows containing legitimately accented names (César,
Mélanie, ŌURA).

---

## 16. Known limits

1. **Repetition within a signal type.** 672 rows share the `newrole` pattern. Openers
   are 2,031 distinct across 3,126 live rows, but two `newrole` rows will read as
   siblings. Unavoidable at this volume without hand-writing.
2. **No quotes are ever invented.** Where the research says a first-party quote exists
   (~900 rows), `notes` says so and `signal_evidence` carries the sentence. Dropping
   their actual words in is a human job — that's the gap between these and the
   hand-written Mike Ogden email.
3. **Research is trusted as given.** Nothing is verified against the live web. If the
   brief is wrong, the email inherits it.
4. **`REVIEW` rows are honest but impersonal.** They pass on accuracy, not warmth.

---

## 17. Output columns

`first_name` · `company` · `email` · `status` · `signal_type` · `subject` ·
`greeting` · `opener` · `problem` · `point_1` · `point_2` · `point_3` ·
`how_we_help` · `cta` · `signoff` · `full_email` · `notes` · `data_flag` ·
`signal_evidence`

`full_email` is the assembled, ready-to-send version. `signal_evidence` is the exact
sentence from the research the opener was built on — so any row can be audited
against its source in one glance.

---

## 18. The standard

Not "is this grammatically correct?" but:

> If I had one chance to email this person, would I actually send this?

If no — HOLD it.
