"""Final build: real signal -> connected opener -> believable problem -> 3 points -> help -> CTA.

Fixes over the previous pass:
  * no filler openers. If there is no concrete signal, the row is HOLD.
  * sentence 2 is written to follow the SPECIFIC signal type, not picked from a generic bank.
  * LinkedIn profile text is no longer described as a published article.
  * a company case study is no longer described as quoting the person.
"""
import csv, re, hashlib, sys

sys.path.insert(0, "/tmp/claude-0/-home-user-erics-coldoutboundskills/734106dc-509a-5dda-9288-29244327cfc1/scratchpad")
csv.field_size_limit(10**9)

SRC = "/root/.claude/uploads/734106dc-509a-5dda-9288-29244327cfc1/142ae5d4-Leaders_RevOpsDefaultviewexport1786359479617.csv"
OUT = "/home/user/erics-coldoutboundskills/outreach_full.csv"
HAND = "/home/user/erics-coldoutboundskills/outreach_first10.csv"

CTA = "Can I share a 2-minute video showing how we approach this, just so you can compare it with your current setup?"
SIGNOFF = "Best,\nSijhah"

SENT_SPLIT = re.compile(r'(?<=[.!?])\s+')
def sentences(t):
    return [s.strip() for s in SENT_SPLIT.split(t or "") if s.strip()]

NEG = re.compile(r"(\bno\b|\bnot\b|\bnor\b|\bnone\b|\bwithout\b|\bnever\b|\bunable\b|did ?n[o']t"
                 r"|\babsence\b|\black(?:s|ing)?\b|\bfailed to\b|\bcould ?n[o']t\b"
                 r"|\bunverified\b|\bunconfirmed\b|\bnot opened\b|\bhypothes|\bassum|\bspeculat)", re.I)
def negated(s): return bool(NEG.search(s))

STALE_PAT = re.compile(
    r"(left (?:that|the|his|her|their) role|no longer (?:at|with|in)"
    r"|has since (?:moved|joined|left|departed)|\bdeparted\b|\bstale\b|\boutdated\b|out of date"
    r"|title and company .{0,30}appear|role/company .{0,20}stale"
    r"|now lists .{0,40}(?:advisory|CEO|different))", re.I)
SF_UNCLEAR = re.compile(
    r"(salesforce fit (?:is |= )?(?:assessed as )?unclear"
    r"|no (?:clear |authoritative |explicit )?public (?:confirmation|evidence)"
    r"|salesforce (?:usage|fit)[^.]{0,30}unclear|unclear whether[^.]{0,40}salesforce"
    r"|no explicit public evidence)", re.I)

CORP_DOC = re.compile(r"\b(earnings release|press release|job req|job listing|job posting|10-K|SEC filing|investor)\b", re.I)
PERSONAL_MARK = re.compile(r"\b(LinkedIn|profile|podcast|interview|webinar|panel|keynote|blog|article|post|case study|quote[ds]?|said|describes?|described|authored|wrote|published|certification|certified)\b", re.I)
PROFILE_WORD = re.compile(r"\b(LinkedIn|profile|summary|About section|headline|bio)\b", re.I)

P_CASE = re.compile(r"\bcase study\b", re.I)
P_QUOTEWORD = re.compile(r"\bquot(?:e|es|ed|ing)\b", re.I)
P_SPOKE = re.compile(r"\b(podcast|interview|webinar|panel|keynote|spoke at|fireside)\b", re.I)
P_PUBLISHED = re.compile(r"\b(authored a|wrote a|published a|blog post|byline|article|whitepaper|authored the|blog \()", re.I)
P_BLOGWORD = re.compile(r"\b(blog|article|byline|whitepaper|op-ed)\b", re.I)
P_PROFILE_FP = re.compile(r"\b(first-?party (?:quote|statement|language|signal)s?|explicitly (?:documents|highlights|describes|lists)"
                          r"|profile (?:explicitly )?(?:documents|highlights|describes|contains|lists)"
                          r"|publicly (?:describ|stat|says|said)|self-authored)\b", re.I)
P_CERT = re.compile(r"\bSalesforce (?:Administrator|Admin|certified|certification)\b", re.I)
P_PROMO = re.compile(r"\bpromot(?:ed|ion)\b", re.I)
P_NEW = re.compile(r"\b(recent(?:ly)? job change|fresh(?:ly)? job change|new in (?:role|seat)"
                   r"|recently (?:joined|moved|stepped|started)|joined [A-Z][\w&.\- ]{1,30} (?:as|in)\b"
                   r"|stepped into|moved into|started (?:as|in) )", re.I)

RAISED = re.compile(r"\b(raised|secured|closed)\b[^.]{0,60}?(\$\s?\d[\d.,]*\s?(?:M|B|million|billion)|Series\s+[A-F])", re.I)
SERIES_LOOSE = re.compile(r"\b(raised|closed|secured)[^.]{0,40}\bSeries\s+([A-F])\b", re.I)
SERIES_ONLY = re.compile(r"\bSeries\s+([A-F])\b[^.]{0,40}\b(funding|round|raise|investment)\b", re.I)
MONEY = re.compile(r"\$\s?\d[\d.,]*\s?(?:M|B|million|billion)\b", re.I)
SF_INT = re.compile(r"\b(AppExchange|native Salesforce (?:plugin|integration|app)|Salesforce (?:plugin|integration|connector)"
                    r"|integrates? with Salesforce|lists a Salesforce integration|Salesforce Commerce Cloud)\b", re.I)
SF_SOR = re.compile(r"\b(uses Salesforce|runs (?:its .{0,20})?on Salesforce|Salesforce tenant|Salesforce as (?:its|the)"
                    r"|system[- ]of[- ]record|confirmed Salesforce (?:stack|shop)|mandate[sd]? Salesforce|require[sd]? Salesforce)\b", re.I)
HIRING = re.compile(r"\b(quota-carrying hiring|hiring|scaling (?:the )?(?:GTM|sales|team)|headcount growth"
                    r"|expanding the (?:sales|GTM) team|GTM expansion)\b", re.I)

# Controlled topic vocabulary. Free-text extraction produced mangled clause
# fragments ("forecasting and GTM reporting among his responsibilities in prior
# role"), so topics are matched against known phrases and rendered cleanly.
TOPIC_VOCAB = [
    (re.compile(r"\bforecast(?:ing|s)?\b", re.I),                      "forecasting"),
    (re.compile(r"\bpipeline\b", re.I),                                 "pipeline"),
    (re.compile(r"\battribution\b", re.I),                              "attribution"),
    (re.compile(r"\bterritor(?:y|ies)\b|\bquota\b", re.I),              "territory and quota planning"),
    (re.compile(r"\bcompensation\b|\bcomp plan", re.I),                 "comp"),
    (re.compile(r"\benablement\b", re.I),                               "enablement"),
    (re.compile(r"\b(?:revenue |sales )?reporting\b|\banalytics\b", re.I), "revenue reporting"),
    (re.compile(r"\bautomation\b", re.I),                               "automation"),
    (re.compile(r"\bGTM strategy\b|\bgo-to-market strategy\b", re.I),   "GTM strategy"),
    (re.compile(r"\bdata quality\b|\bdata hygiene\b|\bclean data\b", re.I), "data quality"),
    (re.compile(r"\b(?:tech |sales )?stack\b|\btooling\b", re.I),       "the tooling side"),
    (re.compile(r"\bSalesforce\b|\bCRM\b", re.I),                       "the CRM side of things"),
    (re.compile(r"\bdeal desk\b", re.I),                                "deal desk"),
    (re.compile(r"\bchurn\b|\bretention\b", re.I),                      "retention"),
]
# Never build an opener off a topic drawn from a sentence about a PRIOR role.
PRIOR_ROLE = re.compile(r"\b(prior role|previous role|former(?:ly)?|before (?:joining|moving)|earlier in (?:his|her|their) career|past role)\b", re.I)


def topic_from(sent):
    """Return at most two clean topics joined naturally, or ''. Two-item rule."""
    if PRIOR_ROLE.search(sent):
        return ""
    found = []
    for pat, label in TOPIC_VOCAB:
        if pat.search(sent) and label not in found:
            found.append(label)
        if len(found) == 2:
            break
    if not found:
        return ""
    return found[0] if len(found) == 1 else f"{found[0]} and {found[1]}"


LEGAL = {"inc","inc.","llc","l.l.c.","ltd","ltd.","plc","corp","corp.","corporation","co","co.",
         "incorporated","gmbh","s.a.","sa","ag","srl","bv","b.v.","pty","limited","lp","llp","sas","nv","n.v.","oy","ab","spa","kk"}
def clean_company(name):
    n = (name or "").strip()
    if not n: return ""
    n = re.split(r"\s*[,(]\s*", n)[0]
    n = re.sub(r"\s*[-–—|]\s*(?:a|an|the)\s+.*$", "", n, flags=re.I)
    words = [w for w in n.split() if w]
    while words and words[-1].lower().strip(".,") in LEGAL:
        words.pop()
    if len(words) > 2 and words[-1].lower() in {"group","holdings","holding","company","services","solutions","technologies","international","global","partners","systems"}:
        words = words[:-1]
    if len(words) > 3:
        words = words[:2]
    return " ".join(words) if words else n

GENERIC_MAIL = {"gmail.com","yahoo.com","hotmail.com","outlook.com","icloud.com","aol.com"}

def domain_core(d):
    d = (d or "").strip().lower()
    d = re.sub(r"^https?://", "", d).replace("www.", "").split("/")[0]
    p = d.split(".")
    return p[0] if p and p[0] else ""


def resolve_company(raw, website, brief):
    """Recover a truncated company name using the website + research brief.

    The source lists 'Cohere' for coherehealth.com; naming the wrong company in
    the opener is worse than saying nothing, so upgrade only when the brief
    actually uses the longer name AND it matches the domain exactly.
    """
    base = clean_company(raw)
    sc = domain_core(website)
    flat = re.sub(r"[^a-z0-9]", "", base.lower())
    if not (base and sc and flat and sc.startswith(flat) and len(sc) > len(flat) + 2):
        return base
    m = re.search(rf"\b{re.escape(base)}\s+([A-Z][A-Za-z]+)\b", brief)
    if m:
        tail = m.group(1)
        # never re-add a legal/entity suffix we just stripped (foxcorporation.com)
        if tail.lower().strip(".") in LEGAL or tail.lower() in {
                "group", "holdings", "holding", "company", "international", "global"}:
            return base
        cand = f"{base} {tail}"
        if re.sub(r"[^a-z0-9]", "", cand.lower()) == sc:
            return cand
    return base


def email_domain_flag(email, website):
    """Warn when the work email domain does not line up with the company site."""
    if not email or "@" not in email or not website:
        return ""
    dom = email.split("@")[1].lower()
    if dom in GENERIC_MAIL:
        return "personal email domain - verify"
    dc, sc = domain_core(dom), domain_core(website)
    if dc and sc and dc != sc and dc not in sc and sc not in dc:
        return f"email domain ({dom}) does not match company site ({website}) - verify the address is current"
    return ""


def clean_first(name):
    n = (name or "").strip()
    if not n: return ""
    return re.split(r"[\s,._-]+", n)[0].strip(".,").strip()

def pick(key, salt, opts):
    h = int(hashlib.md5((key + "|" + salt).encode()).hexdigest(), 16)
    return opts[h % len(opts)]

# No value may start with "the" - templates supply their own article
# ("the {remit} seat" would otherwise render "the the Salesforce side seat").
REMIT = {"General RevOps":"revenue operations","Strategy/Planning/GTM":"GTM planning","Analytics/Data":"revenue analytics",
         "Enablement":"enablement","Systems/SF/CRM":"Salesforce and systems","SalesOps":"sales operations",
         "Program/PMO":"revenue programs","Partner/Channel":"partner and channel","DealDesk/Comp":"deal desk and comp",
         "MarketingOps":"marketing operations"}
def team_for(func, cat):
    if func == "Enablement": return "enablement teams"
    if func == "Partner/Channel": return "account teams"
    if func == "SalesOps" or cat == "Sales Operations": return "Sales Ops teams"
    if func == "Analytics/Data": return "revenue teams"
    return "RevOps teams"

POINTS = {
 "forecast":  ["what changed since the last forecast update","which deals are losing buyer activity","what the rep has committed to do next"],
 "pipeline":  ["what changed since the last buyer conversation","which deals are starting to lose momentum","what the rep has committed to do next"],
 "crm":       ["what changed since the last buyer conversation","which deals are missing recent activity","what the rep has committed to do next"],
 "account":   ["what changed since the last customer update","which accounts may be starting to slow","what the next owner needs to do"],
 "enablement":["what changed since the last buyer conversation","which deals are starting to slow","what the rep has committed to do next"],
}
SUBJECT = {"forecast":"forecast context","pipeline":"pipeline context","crm":"crm context",
           "account":"account context","enablement":"deal context"}
def help_line(theme, team, crm_n, crm_a):
    """crm_n = noun form ('Salesforce' / 'the CRM'); crm_a = attributive ('Salesforce' / 'CRM')."""
    return {
 "forecast":  f"That's what we've been helping {team} with - keeping the latest emails and meetings in {crm_n}, and making forecast changes easier to explain.",
 "pipeline":  f"That's what we've been helping {team} with - making sure emails and meetings land on the right {crm_a} records, and flagging deals that may be starting to slow.",
 "crm":       f"That's what we've been helping {team} with - making sure emails and meetings land on the right {crm_a} records on their own, and keeping the activity history complete.",
 "account":   f"That's what we've been helping {team} with - making sure emails and meetings land on the right {crm_a} records, and flagging accounts that may be starting to slow.",
 "enablement":f"That's what we've been helping {team} with - keeping the latest deal activity in {crm_n}, and giving the team a clearer view of what each rep should do next.",
    }[theme]

def problem_line(theme, crm_n, crm_a, key):
    return pick(key, "prob", {
 "forecast": ["And by forecast time, one buyer update sitting in email can make a deal look better than it really is.",
              "And by forecast time, one missing buyer update can make a deal look different from what's actually happening.",
              f"And by forecast time, a buyer update stuck in someone's inbox can leave {crm_n} showing the older story."],
 "pipeline": [f"But even then, the newest buyer update can sit in someone's inbox while {crm_n} shows an older version of the deal.",
              f"But even then, one buyer update can sit in email while {crm_n} shows an older picture of the deal.",
              f"But even then, the last real conversation can stay in email while {crm_n} shows something older."],
 "crm":      ["But even then, an email or meeting can still miss the record it belongs to.",
              f"But even with a tidy setup, the latest email or meeting can miss the {crm_a} record it belongs to.",
              f"But even then, the newest buyer update can land nowhere useful while {crm_n} shows an older version of the deal."],
 "account":  [f"But in that kind of move, the latest customer update can sit in email while {crm_n} shows an older version of the account.",
              f"But even then, one customer update can sit in email while {crm_n} shows an older picture of the account.",
              f"But even then, what was last agreed with a customer can stay in email while {crm_n} shows something older."],
 "enablement":[f"But even with a strong process, one buyer update can sit in email while {crm_n} shows an older version of the deal.",
               f"But even with good habits, the latest buyer update can sit in a rep's inbox while {crm_n} shows an older picture.",
               f"But even then, what a buyer last said can stay in email while {crm_n} shows something older."],
    }[theme])


def person_sent(s, first, last):
    if negated(s) or CORP_DOC.search(s) or not PERSONAL_MARK.search(s):
        return False
    low = s.lower()
    if first and len(first) > 2 and first.lower() in low: return True
    if last and len(last) > 2 and last.lower() in low: return True
    return bool(re.search(r"\b(the subject|the prospect)\b", low))


def extract(row):
    brief = row.get("Research Brief") or ""
    reason = row.get("Reasoning") or ""
    text = brief + " " + reason
    first, last = (row.get("first_name") or "").strip(), (row.get("last_name") or "").strip()
    company_raw = (row.get("company_name") or "").strip()
    res = {"kind": None, "evidence": "", "extra": {}, "stale": bool(STALE_PAT.search(text)),
           "sf_unclear": bool(SF_UNCLEAR.search(text)) or ("salesforce" not in text.lower()),
           "has_quote": False}
    sents = sentences(brief) + sentences(reason)
    clean = [s for s in sents if not negated(s)]

    # Tier A - genuine public artifact by/about this person
    for s in sents:
        if person_sent(s, first, last) and P_CASE.search(s) and P_QUOTEWORD.search(s):
            res.update(kind="casestudy", evidence=s, has_quote=True); return res
    for s in sents:
        if person_sent(s, first, last) and P_SPOKE.search(s):
            m = re.search(r"\b(podcast|interview|webinar|panel|keynote)\b", s, re.I)
            res.update(kind="spoke", evidence=s, has_quote=True,
                       extra={"medium": m.group(1).lower() if m else "interview",
                              "topic": topic_from(s)}); return res
    for s in sents:
        if person_sent(s, first, last) and P_PUBLISHED.search(s) and P_BLOGWORD.search(s) \
           and not PROFILE_WORD.search(s):
            res.update(kind="authored", evidence=s, has_quote=True, extra={"topic": topic_from(s)}); return res
    for s in sents:
        if person_sent(s, first, last) and P_PROFILE_FP.search(s):
            res.update(kind="profile", evidence=s, has_quote=True, extra={"topic": topic_from(s)}); return res
    for s in sents:
        if person_sent(s, first, last) and P_CERT.search(s):
            res.update(kind="cert", evidence=s); return res

    # Tier B - personal event
    for kind, pat in [("promotion", P_PROMO), ("newrole", P_NEW)]:
        for s in sents:
            if negated(s) or not pat.search(s): continue
            low = s.lower()
            if (first and first.lower() in low) or (last and last.lower() in low) \
               or re.search(r"\b(the subject|the prospect)\b", low):
                res.update(kind=kind, evidence=s); return res

    # Tier C - company fact
    for s in clean:
        if RAISED.search(s) or SERIES_LOOSE.search(s) or SERIES_ONLY.search(s):
            amt, ser = MONEY.search(s), re.search(r"\bSeries\s+([A-F])\b", s)
            res.update(kind="funding", evidence=s,
                       extra={"amount": re.sub(r"\s+","",amt.group(0)).upper().replace("MILLION","M").replace("BILLION","B") if amt else "",
                              "series": ser.group(1) if ser else ""}); return res
    cw = [w for w in re.split(r"[\s,]+", company_raw) if len(w) > 3][:1]
    if cw:
        c = re.escape(cw[0])
        tgt = re.compile(rf"\b{c}\b[^.]{{0,40}}\bwas acquired\b|\bacquisition of [^.]{{0,20}}\b{c}\b", re.I)
        buy = re.compile(rf"\b{c}\b[^.]{{0,40}}\bacquired\b(?! by)", re.I)
        for s in clean:
            if tgt.search(s): res.update(kind="acq_target", evidence=s); return res
        for s in clean:
            if buy.search(s): res.update(kind="acq_buyer", evidence=s); return res
    for s in clean:
        if SF_INT.search(s): res.update(kind="sf_integration", evidence=s); return res
    for s in clean:
        if SF_SOR.search(s): res.update(kind="sf_sor", evidence=s); return res
    for s in clean:
        if HIRING.search(s): res.update(kind="hiring", evidence=s); return res
    return res


def art(word):
    return "an" if word[:1].lower() in "aeiou" else "a"


def build_opener(kind, extra, first, company, remit, key, crm_n):
    """Return (sentence1, sentence2, theme). Sentence 2 must follow from sentence 1."""
    topic = (extra or {}).get("topic", "")
    if kind == "promotion":
        s1 = pick(key, "s1", [f"Saw you picked up a wider remit at {company} recently.",
                              f"Looks like you moved up into a bigger {remit} remit at {company}.",
                              f"Saw you've taken on more of the {remit} side at {company}.",
                              f"Looks like your patch at {company} got quite a bit bigger recently."])
        s2 = pick(key, "s2", ["That probably means more of the number sits with you now than it used to.",
                              "That probably means you're still shaping how the whole pipeline picture comes together.",
                              "More of the forecast probably lands on your desk now.",
                              "That probably means you're seeing deals from a wider angle than before."])
        return s1, s2, "forecast"
    if kind == "newrole":
        s1 = pick(key, "s1", [f"Looks like you stepped into the {remit} seat at {company} fairly recently.",
                              f"Was looking at your move into {remit} at {company}.",
                              f"Looks like you're still fairly new into the {remit} seat at {company}.",
                              f"Saw you moved across into {remit} at {company} not too long ago."])
        s2 = pick(key, "s2", ["You're probably still building your own view of how deals really move here.",
                              "That probably means you're still shaping how the pipeline and forecast come together.",
                              "You've probably spent a fair bit of that time working out where the numbers come from.",
                              "That probably means you're still deciding what the pipeline should look like."])
        return s1, s2, "forecast"
    if kind == "spoke":
        med = (extra or {}).get("medium", "interview")
        s1 = f"Was listening to the {med} you did about {topic}." if topic else \
             pick(key, "s1", [f"Was listening to {art(med)} {med} you did.",
                              f"Came across {art(med)} {med} you took part in."])
        s2 = pick(key, "s2", ["That probably means how deals actually run is something you've thought about a lot.",
                              "That probably means you spend a lot of time close to how deals really move.",
                              "You've probably got clear views on where the process tends to break."])
        return s1, s2, "pipeline"
    if kind == "authored":
        s1 = f"Was reading the piece you wrote about {topic}." if topic else \
             pick(key, "s1", ["Was reading a piece you'd written.",
                              "Came across something you'd published."])
        s2 = pick(key, "s2", ["That probably means how deals actually run is something you've thought about a lot.",
                              "You've probably got a clear view of where the process tends to break."])
        return s1, s2, "pipeline"
    if kind == "casestudy":
        s1 = f"Was reading the case study where you talked about {topic}." if topic else \
             pick(key, "s1", ["Was reading a case study you were quoted in.",
                              "Came across a case study with your comments in it."])
        s2 = pick(key, "s2", [f"That probably means {crm_n} is already central to how the team works.",
                              f"That probably means the team already leans on {crm_n} for most of the day to day."])
        return s1, s2, "crm"
    if kind == "profile":
        vb = "are" if " and " in topic else "is"
        s1 = f"Looks like {topic} {vb} a big part of what you focus on." if topic else \
             pick(key, "s1", [f"Looks like you've spent a lot of your career around {remit}.",
                              f"Looks like {remit} has been your patch for a while now."])
        s2 = pick(key, "s2", ["That probably means you notice pretty quickly when the numbers stop matching reality.",
                              "That probably gives you a close view of how deals are really moving.",
                              "You've probably got a good feel for where the picture usually goes wrong."])
        return s1, s2, "pipeline"
    if kind == "cert":
        s1 = pick(key, "s1", [f"Looks like you hold a Salesforce admin cert on top of running {remit} at {company}.",
                              f"Saw you've got the Salesforce admin side covered yourself at {company}."])
        s2 = pick(key, "s2", ["That probably means you know exactly how clean or messy the data really is.",
                              "That probably means you see the gaps in the records before anyone else does."])
        return s1, s2, "crm"
    if kind == "funding":
        amt, ser = (extra or {}).get("amount", ""), (extra or {}).get("series", "")
        if amt and ser: what = f"raised {art(amt[1:2] or 'x')} {amt} Series {ser}".replace("raised a $", "raised a $")
        elif amt:       what = f"raised {amt}"
        elif ser:       what = f"raised a Series {ser}"
        else:           what = "closed a new round"
        if amt and ser: what = f"raised a {amt} Series {ser}"
        s1 = f"Saw {company} {what}."
        s2 = pick(key, "s2", ["That probably means the team is growing quicker than the process behind it.",
                              "That probably means headcount is going up faster than the tooling around it.",
                              "That probably means a lot more deals are moving than a year ago."])
        return s1, s2, "pipeline"
    if kind == "acq_target":
        s1 = f"Saw {company} was acquired."
        s2 = pick(key, "s2", ["That probably means a lot of accounts and systems are being pulled into one view.",
                              "That probably means a fair bit of the book is changing hands right now."])
        return s1, s2, "account"
    if kind == "acq_buyer":
        s1 = f"Saw {company} has been picking up other businesses."
        s2 = pick(key, "s2", ["That probably means a lot of accounts and systems are being pulled into one view.",
                              "That probably means new books of business keep landing on the team."])
        return s1, s2, "account"
    if kind == "sf_integration":
        # Kept deliberately soft: the research confirms a Salesforce tie-in, not
        # always that the company built it into its own product.
        s1 = pick(key, "s1", [f"Looks like Salesforce is pretty woven into how {company} works.",
                              f"Looks like {company} is tied into Salesforce fairly closely."])
        s2 = pick(key, "s2", ["That probably means most of the day to day already runs through it.",
                              "That probably means it's where the sales team actually lives."])
        return s1, s2, "crm"
    if kind == "sf_sor":
        s1 = pick(key, "s1", [f"Looks like Salesforce is the system of record across {company}.",
                              f"Looks like {company} runs the go-to-market side on Salesforce."])
        s2 = pick(key, "s2", ["That probably means most of the day to day already runs through it.",
                              "That probably means the team leans on it for the full deal picture."])
        return s1, s2, "crm"
    if kind == "hiring":
        s1 = pick(key, "s1", [f"Saw {company} has been hiring across the go-to-market side.",
                              f"Looks like {company} has been adding to the sales side lately."])
        s2 = pick(key, "s2", ["That probably means more reps and more deals to keep track of.",
                              "That probably means the pipeline is getting busier than it used to be."])
        return s1, s2, "forecast"
    return None, None, None


def full_email(r):
    if not r["opener"]:
        return ""
    return "\n".join([f"Subject: {r['subject']}", "", r["greeting"], "", r["opener"], "", r["problem"], "",
                      "So, usually, there are three things the team needs to know:", "",
                      f"- {r['point_1']}", f"- {r['point_2']}", f"- {r['point_3']}", "",
                      r["how_we_help"], "", r["cta"], "", r["signoff"]])

STRONG = {"casestudy", "spoke", "authored", "profile", "cert", "promotion", "newrole", "funding"}

cols = ["first_name","company","email","status","signal_type","subject","greeting","opener","problem",
        "point_1","point_2","point_3","how_we_help","cta","signoff","full_email","notes","data_flag","signal_evidence"]

hand = {}
with open(HAND, encoding="utf-8") as f:
    for row in csv.DictReader(f):
        hand[row["email"]] = row

rows = list(csv.DictReader(open(SRC, encoding="utf-8")))
out, stats, kinds = [], {}, {}
for r in rows:
    email = (r.get("WorkEmail") or "").strip()
    first = clean_first(r.get("first_name"))
    company = resolve_company(r.get("company_name"), r.get("website"),
                              (r.get("Research Brief") or "") + " " + (r.get("Reasoning") or ""))
    dflag = email_domain_flag(email, r.get("website"))
    func = (r.get("function") or "").strip()
    cat = (r.get("category") or "").strip()
    remit = REMIT.get(func, "revenue operations")
    e = extract(r)
    crm_n = "the CRM" if e["sf_unclear"] else "Salesforce"   # noun:  "...while the CRM shows..."
    crm_a = "CRM" if e["sf_unclear"] else "Salesforce"       # attr:  "...the right CRM records..."
    notes = []

    if email in hand:
        rec = {k: hand[email].get(k, "") for k in cols if k in hand[email]}
        rec.setdefault("signal_type", "hand-written")
        rec["signal_evidence"] = ""
        rec = {k: rec.get(k, "") for k in cols}
        rec["signal_type"] = "hand-written"
        rec["data_flag"] = dflag
        if rec["status"] == "HOLD-recommended":
            rec["status"] = "REVIEW"   # keep the status vocabulary to 3 values
        rec["full_email"] = full_email(rec)
        stats[rec["status"]] = stats.get(rec["status"], 0) + 1
        kinds["hand-written"] = kinds.get("hand-written", 0) + 1
        out.append(rec); continue

    if not email:
        status, kind = "HOLD", None; notes.append("no work email on file")
    elif len(first) < 2 or not re.search(r"[A-Za-z]", first):
        # initials ("M", "O") or junk ("Üöä") cannot produce a real greeting
        status, kind = "HOLD", None; notes.append("first name unusable for a greeting - check the source record")
    elif not company:
        status, kind = "HOLD", None; notes.append("no company name on file")
    elif e["stale"]:
        status, kind = "HOLD", None; notes.append("research flags the role or company as stale/outdated - re-verify before sending")
    elif e["kind"] is None:
        status, kind = "HOLD", None; notes.append("no concrete signal in the research - only generic title/role copy would be possible")
    else:
        kind = e["kind"]
        status = "SEND-READY" if kind in STRONG else "REVIEW"
        if kind == "profile" and not e["extra"].get("topic"):
            # stated-expertise signal with no nameable topic reads close to
            # generic title copy, so it does not go out unreviewed
            status = "REVIEW"
            notes.append("profile signal but no specific topic found - opener leans generic")
        elif status == "REVIEW":
            notes.append("company-level signal only - opener is real but not personal")

    if status == "HOLD":
        rec = dict(first_name=first, company=company, email=email, status=status, signal_type="",
                   subject="", greeting="", opener="", problem="", point_1="", point_2="", point_3="",
                   how_we_help="", cta="", signoff="", full_email="", notes="; ".join(notes),
                   data_flag=dflag, signal_evidence=e["evidence"][:300])
        stats[status] = stats.get(status, 0) + 1
        kinds["HOLD"] = kinds.get("HOLD", 0) + 1
        out.append(rec); continue

    key = email
    s1, s2, theme = build_opener(kind, e["extra"], first, company, remit, key, crm_n)
    team = team_for(func, cat)
    p1, p2, p3 = POINTS[theme]
    if e["has_quote"]:
        notes.append("first-party material exists - worth dropping their actual words into the opener")
    if e["sf_unclear"]:
        notes.append('Salesforce not confirmed - used generic "CRM"')

    rec = dict(first_name=first, company=company, email=email, status=status, signal_type=kind,
               subject=SUBJECT[theme], greeting=f"Hi {first},", opener=f"{s1} {s2}",
               problem=problem_line(theme, crm_n, crm_a, key), point_1=p1, point_2=p2, point_3=p3,
               how_we_help=help_line(theme, team, crm_n, crm_a), cta=CTA, signoff=SIGNOFF,
               full_email="", notes="; ".join(notes), data_flag=dflag,
               signal_evidence=e["evidence"][:300])
    rec["full_email"] = full_email(rec)
    stats[status] = stats.get(status, 0) + 1
    kinds[kind] = kinds.get(kind, 0) + 1
    out.append(rec)

with open(OUT, "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=cols, quoting=csv.QUOTE_ALL)
    w.writeheader()
    for rec in out:
        w.writerow(rec)

print("wrote", OUT, "rows:", len(out))
print("status:", stats)
print("signals:", dict(sorted(kinds.items(), key=lambda x: -x[1])))
