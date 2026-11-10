"""Advisory rule-based classifier for scam-like task listings; see SPEC.md.

The rules look for an *affirmative instruction* to perform a risky action:
sync/run a payload from an untrusted bare host, reveal key material, pay an
unlock/deposit/verification fee, hand over a payout wallet, or disable safety
protections. Safety framing (Warning:/Security guide:/Scam report:/Do not ...),
negations ("never", "refuse", "no downloads") and inert/quoted context suppress
a match when no later affirmative instruction overrides it.
"""
import re

_SAFETY_TITLE_PREFIXES = (
    "warning:",
    "security guide:",
    "scam report:",
    "do not ",
    "don't ",
)

_NEGATION = re.compile(
    r"\b(?:never|do\s+not|don't|refuse|refused|avoid|without|no\s+"
    r"(?:downloads?|payment|payout|account|submissions?|wallet|fee)|must\s+remain|"
    r"should\s+stay|stay\s+enabled|not\s+(?:requested|needed|required|execute[sd]?)|"
    r"risky|dangerous)\b"
)
_INERT = re.compile(
    r"\b(?:inert|synthetic|local|offline|test\s+data|fixture|display|document|"
    r"tutorial|explain|statistics|count|format[s]?)\b"
)

# Sentences that *report on* language rather than issue it: verbs of framing
# ("says", "meaning", "instruction") plus quoted payloads. A risky clause that
# appears inside quotes is being discussed, not instructed.
_REPORTING = re.compile(
    r"\b(?:says?|reads?|writes?|warn(?:s|ings?)|message|text|label(?:led)?|"
    r"instruction|\bphrases?\b(?=\s+(?:such|like|reads?|says?))|quote[sd]?|wording|tells?\s+(?:users|contributors)|"
    r"asked|explain(?:s|ing)?|describe[sd]?|document(?:s|ing)?|tutorial|"
    r"shows?\s+why|demonstrat\w*|example)\b"
)
_QUOTED = re.compile(r"\"[^\"]*\"|'[^']*'|\u201c[^\u201d]*\u201d|`[^`]*`")

_RULES = (
    # Key material exposure.
    re.compile(r"\b(?:reveal|share|upload|provide|send|post|submit|include|disclose)\b"
               r"[^.]{0,60}\b(?:seed\s+phrase|private\s+key|secret\s+key|recovery\s+phrase)\b"),
    re.compile(r"\b(?:seed\s+phrase|private\s+key|recovery\s+phrase)\b[^.]{0,40}"
               r"\b(?:to\s+prove|for\s+(?:inspection|verification)|in\s+the\s+form|before)\b"),
    # Payout / wallet address harvesting.
    re.compile(r"\b(?:comment|post|reply|submit|include|provide|send|share)\b[^.]{0,40}"
               r"\b(?:payout|wallet)(?:\s+address|\s+in\s+the\s+claim|\s+wallet)?\b"),
    re.compile(r"\b(?:post|reply|include|provide|send|submit)\b[^.]{0,30}"
               r"<wallet-placeholder>"),
    re.compile(r"\bwallet\s+address\s+for\s+(?:release|reward|payment)\b"),
    # Payment traps: unlock/deposit/verification fee.
    re.compile(r"\b(?:pay|send|transfer|submit|make)\b[^.]{0,40}"
               r"\b(?:a\s+|an\s+|the\s+)?(?:verification|unlock|deposit|processing|"
               r"activation|release)\s+fee\b"),
    re.compile(r"\bpay\s+a\s+(?:verification|deposit|unlock)\b"),
    re.compile(r"\b(?:send|transfer|pay)\b[^.]{0,25}\bdeposit\b[^.]{0,25}"
               r"\b(?:to\s+(?:start|unlock|receive|release)|before)\b"),
    # Unsafe execution / untrusted host payload.
    re.compile(r"\b(?:run|execute|download|fetch|sync(?:hronise|hronize)?|install|synchronise|synchronize)\b"
               r"[^.]{0,60}<bare-host>"),
    re.compile(r"\b<bare-host>\b[^.]{0,40}\b(?:before|to\s+become|to\s+qualify|payload|shards?)\b"),
    re.compile(r"\bcurl\b[^.\n]{0,40}\|\s*(?:sh|bash)\b"),
    # Disabling safety.
    re.compile(r"\b(?:disable|turn\s+off|switch\s+off|bypass)\b[^.]{0,40}"
               r"\b(?:safety|security|sandbox|protections?|checks?)\b"),
    # Explicit compliance that follows a quoted payload ("comply to get paid",
    # "do it to qualify"), i.e. the listener is told to obey the quoted text.
    re.compile(r"\b(?:comply|obey|follow\s+it|do\s+(?:it|so|this|that))\b"
               r"[^.]{0,30}\b(?:to\s+(?:get|receive|claim|qualify|unlock|be\s+paid)|before)\b"),
)

_SENTENCE = re.compile(
    r"(?:[^.!?\n\"]|\"[^\"]*\")+[.!?]?", re.S
)


def _strip_quoted(text):
    """Blank out quoted spans, keeping their length-free content removed."""
    return _QUOTED.sub(" ", text)


def _split_clauses(text):
    """Split a sentence on quotes and clause separators, keeping quoted spans."""
    parts = re.split(r"(\"[^\"]*\"|'[^']*'|\u201c[^\u201d]*\u201d|`[^`]*`)", text)
    clauses = []
    for part in parts:
        if not part:
            continue
        if _QUOTED.fullmatch(part):
            clauses.append(part)
        else:
            clauses.extend(c for c in re.split(r"[;:,]", part) if c.strip())
    return clauses


def _affirmative(sentence):
    lowered = sentence.lower().strip()
    if not lowered:
        return False
    clauses = _split_clauses(lowered)
    reporting = any(_REPORTING.search(c) for c in clauses)
    for clause in clauses:
        if _QUOTED.fullmatch(clause):
            continue
        if _NEGATION.search(clause):
            continue
        if _REPORTING.search(clause):
            continue
        if any(rule.search(clause) for rule in _RULES):
            return True
    if reporting:
        return False
    # A bare quoted instruction without reporting framing still counts.
    unquoted = _strip_quoted(lowered)
    if unquoted != lowered and any(rule.search(unquoted) for rule in _RULES):
        return True
    return False


def flag(title, body):
    if not isinstance(title, str) or not isinstance(body, str):
        raise TypeError("title and body must be str")
    title_l = " ".join(title.split()).lower()
    if title_l.startswith(_SAFETY_TITLE_PREFIXES):
        return False

    title_risky = any(rule.search(title_l) for rule in _RULES) and not _NEGATION.search(title_l)
    for sentence in _SENTENCE.findall(" ".join(body.split()).lower()):
        if _affirmative(sentence):
            return True
    if title_risky and not _INERT.search(" ".join(body.split()).lower()):
        return True
    return False
