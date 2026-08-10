# Outreach Copy Playbook

The working spec behind `build_outreach.py`, `outreach_full.csv` and
`outreach_send_ready.csv`.

Source of truth is **Master Outreach Copy Instruction**. This document records how
that instruction was turned into something repeatable across 4,821 rows, every guard
added along the way, and the judgment calls that were mine rather than the
instruction's. Those are marked **[my call]** so you can overrule them.

Every example and count below is taken from the shipping file, not from memory.

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

`Prospect Research JSON` is empty across the entire export — every row literally
contains the string `Response`. Nothing is drawn from it.

Job title is **never** used as an opener. Title-based copy is the exact thing the
instruction forbids, and it is what made the first pass read as filler.

---

## 3. Signal tiers

Matching stops at the first hit, so the strongest available signal always wins.
Openers below are real lines from the file.

### Tier A — the person said or did something public

| Signal | n | Requires | Live example |
|---|---:|---|---|
| `profile` | 1,111 | first-party statements on their LinkedIn profile | "Looks like forecasting and the CRM side of things take up a good part of your week." |
| `spoke` | 120 | podcast / interview / webinar / panel / keynote + their name | "Was listening to the podcast you did about forecasting." |
| `cert` | 57 | Salesforce admin certification | "Saw you handle the Salesforce admin side yourself at Fora Financial." |
| `casestudy` | 24 | "case study" **and** a quote word **and** their name | "Came across a case study with your comments in it." |
| `authored` | 19 | published + blog/article/byline, **and no profile word** | "Was reading the piece you wrote about forecasting and pipeline." |

### Tier B — something happened to them

| Signal | n | Live example |
|---|---:|---|
| `newrole` | 672 | "I read that you moved into revenue operations at Nasdaq." |
| `promotion` | 277 | "I read that you took on a wider remit at TransUnion recently." |

### Tier C — something happened to the company

| Signal | n | Live example |
|---|---:|---|
| `sf_integration` | 420 | "Looks like Salesforce is tied fairly closely into how Blackhawk Network runs." |
| `sf_sor` | 178 | "Looks like Salesforce is the system of record across Alegeus." |
| `hiring` | 129 | "Looks like InvoiceCloud has been adding reps lately." |
| `funding` | 56 | "I read that Cohere Health raised a $90M Series C." |
| `acq_target` | 23 | "I read that Juniper was acquired." |
| `acq_buyer` | 5 | "I read that SoundHound has been buying up other businesses." |

### Tier D — nothing → **HOLD**

Plus 9 hand-written rows carried through verbatim.

---

## 4. Guards

Every guard exists because it produced a wrong email in testing. None are theoretical.

| Guard | Catches | The real failure it stopped |
|---|---|---|
| **Negation** | Absence read as presence | *"**No** first-party quotes… **nor** a case study"* became "Was reading a case study you were quoted in." |
| **Unverified** | Research that flags itself | *"(UNVERIFIED, not opened)"* became "Was listening to a webinar you did." |
| **Attribution** | Company facts read as personal | An **AWS** case study about Condé Nast became "a case study you were quoted in." |
| **Profile ≠ published** | LinkedIn About text called an article | *"self-authored summary language"* became "Was reading the piece you wrote." |
| **Prior role** | Topics from a job they left | *"forecasting… among his responsibilities in **prior role**"* — dropped. |
| **Corp doc** | Earnings/job reqs read as the person speaking | An earnings release "explicitly highlights…" became a personal quote. |
| **Direction** | Who acquired whom | Used only when the brief is unambiguous. All 23 `acq_target` rows manually verified. |
| **Not-a-raise** | Acquisitions, funds, AUM read as raises | HPE's **$14B acquisition of** Juniper became "Juniper raised $14B". A $3.25B hyperscale **fund** and $7.3B of **AUM** became raises too. Funding fell 92 → 56. |
| **Recency** | "Recently" asserted without a date | A Genesys move **50 months** old was called "not long back". See §8. |
| **Ambiguous pronoun** | Two candidates for "it" | *"**PayPal** is tied into **Salesforce**… **it's** the first place anyone looks"* — 118 rows. |

---

## 5. HOLD rules

A row is held when **any** applies. Actual counts:

| n | Reason |
|---:|---|
| 1,298 | **No concrete signal** — only generic title copy would be possible |
| 348 | Role or company flagged **stale** in the research |
| 59 | No work email |
| 9 | No company name |
| 6 | First name unusable for a greeting — initials (`M`, `O`) or junk (`Üöä`) |

The first rule is the big one. Those 1,298 rows are exactly what produced
*"Was reading a bit about the revenue operations side of things at Siteminder"* — an
opener that references nothing. HOLD rose from 358 to 1,721 when that rule landed.

HOLD rows ship with **blank copy and a reason in `notes`**, never with filler.

---

## 6. Status meanings

| Status | n | Meaning |
|---|---:|---|
| `SEND-READY` | 2,142 | Tier A or B signal, or funding. Personal and specific. |
| `REVIEW` | 958 | Tier C only. Accurate, but about the company, not the person. |
| `HOLD` | 1,721 | Blank copy + a reason. |

`outreach_send_ready.csv` = **2,024 rows**: SEND-READY with no `data_flag`.

**[my call]** `funding` counts as SEND-READY though it's a company fact — a fresh
raise is specific, dated, and changes the reader's week. Move it to REVIEW if you
want every SEND-READY row to be personal.

**[my call]** A `profile` signal with no nameable topic drops to REVIEW, because
"Looks like you've spent a lot of your career around revenue operations" is too close
to the title copy we're avoiding.

---

## 7. Sentence 2 — the rule that fixed readability

Sentence 2 must state a **plain consequence the problem can then contradict**. It must
not restate the signal, and it must not be abstract.

The turn works when S2 sets an expectation and the problem breaks it:

> Looks like Salesforce is the system of record across Alegeus. **That probably means
> it's the first place anyone looks to see where a deal stands.**
>
> **But even then, a call can happen on Monday and reach the Salesforce record days
> later, if at all.**

### Banned outright

All of these were live in an earlier draft and are now blocked by automated check:

- "the older story" · "land nowhere useful" · "something older"
- "the full deal picture" · "where the picture usually goes wrong"
- "what the pipeline should look like" · "a wider angle"
- a dangling `there` / `here` — *"your own view of how deals move **there**"* (there where?)
- a pronoun with two possible antecedents

---

## 8. Recency is a factual claim

"Recently" / "not long back" is checkable by the reader, so it is only used when the
research carries a date inside **18 months**. Undated evidence drops the wording too,
since nothing supports it.

This was a real error, not a hypothetical: 376 rows now carry softened wording,
including a Genesys row where the move was **50 months** old and an acquisition that
closed in **Feb 2021** being described as accounts "changing hands right now".

Affected rows explain themselves in `notes` — *"event is 34 months old — opener avoids
claiming it was recent"*.

Sentence 2 is gated the same way: "you're still building your own picture" is only
used when the move really was recent.

---

## 9. Problem lines

One concrete idea, and **both halves always stated** — where the update actually sits,
*and* what the CRM shows.

| Theme | Example |
|---|---|
| forecast | "But even then, one missing buyer update can make a deal look different from what's actually happening." |
| pipeline | "But even then, the latest buyer update can still sit in email while Salesforce shows an older version of the deal." |
| crm | "But even then, an email or meeting can sit in someone's inbox instead of the record it belongs to." |
| account | "But even then, the latest customer update can sit in email while Salesforce shows an older version of the account." |

Dropping either half is what made a draft read as unclear: *"an update that never made
it into Salesforce can make a deal look safer than it is"* leaves the reader to work
out where the update *is*.

---

## 10. Theme routing

Theme drives subject, bullets and help line together, so the three always agree.

| Signal | Theme | Subject |
|---|---|---|
| promotion, newrole, hiring | forecast | `forecast context` |
| spoke, authored, profile, funding | pipeline | `pipeline context` |
| casestudy, cert, sf_integration, sf_sor | crm | `crm context` |
| acq_target, acq_buyer | account | `account context` |

### Bullets — always exactly three, always *what changed → where risk is → what next*

- **forecast** — what changed since the last forecast update / which deals are losing buyer activity / what the rep has committed to do next
- **pipeline** — what changed since the last buyer conversation / which deals are starting to lose momentum / what the rep has committed to do next
- **crm** — what changed since the last buyer conversation / which deals are missing recent activity / what the rep has committed to do next
- **account** — what changed since the last customer update / which accounts may be starting to slow / what the next owner needs to do

### Team label by function

`Enablement` → enablement teams · `Partner/Channel` → account teams · `SalesOps` →
Sales Ops teams · `Analytics/Data` → revenue teams · everything else → RevOps teams.

The noun follows the label: "account teams" are told we flag **accounts**, not deals.

---

## 11. How-we-help line

Two capabilities maximum, plain English, never feature names. Normal hyphen, never an
em dash. Product name stays out — the video explains the product.

> That's what we've been helping RevOps teams with - making sure emails and meetings
> land on the right Salesforce records, and flagging deals that may be starting to slow.

---

## 12. CTA

Identical on every row, by instruction:

> Can I share a 2-minute video showing how we approach this, just so you can compare
> it with your current setup?

No meetings, no 15 minutes, no demo, no calendar link.

---

## 13. Salesforce confidence

When the research doesn't confirm Salesforce, copy says "the CRM" instead —
**1,947 rows**. Two grammatical forms are tracked:

- noun — "…while **the CRM** shows an older version"
- attributive — "…the right **CRM** records" (not "the right the CRM records")

---

## 14. Names and companies

- **First name**: first token only. `Andrew James Smith` → `Andrew`.
- **Company**: shortest name an employee would type. Strips `Inc / LLC / Ltd /
  Corporation`, parentheticals, trailing descriptors.
- **Truncation repair**: when the source name is shorter than the domain suggests, the
  fuller name is recovered from the brief **only if it matches the domain exactly**.
  `Cohere` + `coherehealth.com` → **Cohere Health** — important, because Cohere is a
  different, well-known company. Same fix yields Janus Henderson, Cars Commerce.
  A recovered name can never re-add a legal suffix (`foxcorporation.com` stays `Fox`).
- **Casing repair**: the export mangles names — `Gep` → **GEP**, `Bwh` → **BWH**,
  `Gbg` → **GBG**, `Global pay` → **Global Pay**, `Dun` → **Dun & Bradstreet**.

---

## 15. Data quality flags

`data_flag` is a warning, not a verdict — filter on it before loading a sender.

| n | Flag |
|---:|---|
| 236 | Email domain doesn't match the company site — usually a stale address from a previous employer. Christina Catchpole is confirmed at Nasdaq but her address is `@swisslog.com`. |
| 20 | Same surname on the same domain — 10 people reachable at two addresses, e.g. `cglastetter@` and `christopher.glastetter@insightglobal.com`. |

**[my call]** Domain mismatches are flagged, not held, because some are legitimate
subsidiaries (`bhnetwork.com` for Blackhawk Network, `visa.com` for CardinalCommerce).
Both duplicate copies are excluded from the mailable subset so nobody is emailed twice.

---

## 16. Quality assurance

### Automated — ~25 rules, run on every build

**Structure** — exactly 3 bullets · subject present · no empty fields on live rows ·
greeting matches first name · HOLD rows blank with a reason.

**Facts** — no "recently" without a date inside 18 months · no dollar figure restated
as a raise unless it is one.

**Language** — no banned CTA wording · no banned openers ("I noticed", "Given your
role") · no forced praise · no gendered pronouns · no banned vague phrases · no
dangling `there`/`here` · subject-verb agreement on compound topics ("forecasting and
pipeline **take** up") · no sentence over 26 words.

**Formatting** — no em/en dashes · no double spaces · no doubled articles · no `a`/`an`
disagreement · no template leakage · encoding clean.

**Data** — no legal suffix in company · company ≤ 3 words · first name usable · row
count and order preserved · no duplicate addresses.

### Manual — exhaustive, not sampled

4,821 rows are built from only **243 distinct sentences** (134 opener templates, 42
second sentences, 26 problem lines, 36 help lines, 5 bullet sets). All 243 were printed
and read. That review is what caught the ambiguous pronoun and the account-team
mismatch — neither was reachable by any automated rule.

Current readability: **avg sentence 14.8 words, longest 25**.

---

## 17. Known limits

1. **The research is trusted as given.** Nothing is verified against the live web. The
   guards catch internal contradictions only. If a brief is wrong, the email inherits it.
2. **`profile` is the largest signal at 1,111 rows** and the weakest of the personal
   tiers — it says what someone focuses on, not something they did. This is the quality
   ceiling, not a defect.
3. **No quotes are ever invented.** 1,274 rows have first-party material flagged in
   `notes`, with the source sentence in `signal_evidence`. Dropping their actual words
   into the opener is a human job — that is the gap between these and the hand-written
   Mike Ogden email.
4. **Repetition within a signal type.** 672 rows share the `newrole` pattern. Openers
   are 2,055 distinct across 3,100 live rows, but two `newrole` rows will read as
   siblings.
5. **`REVIEW` rows are honest but impersonal.** They pass on accuracy, not warmth.

---

## 18. Output columns

`first_name` · `company` · `email` · `status` · `signal_type` · `subject` ·
`greeting` · `opener` · `problem` · `point_1` · `point_2` · `point_3` ·
`how_we_help` · `cta` · `signoff` · `full_email` · `notes` · `data_flag` ·
`signal_evidence`

`full_email` is the assembled, ready-to-send version. `signal_evidence` is the exact
sentence from the research the opener was built on — so any row can be audited against
its source in one glance.

---

## 19. Rebuilding

```
python3 build_outreach.py
```

Reads the source export, writes `outreach_full.csv`. Deterministic: same input always
gives the same output, so a rebuild after a research refresh is one command.

---

## 20. The standard

Not "is this grammatically correct?" but:

> If I had one chance to email this person, would I actually send this?

If no — HOLD it.
