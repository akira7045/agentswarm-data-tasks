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
    r"risky|dangerous|inert|synthetic|local|offline)\b"
)
_INERT = re.compile(
    r"\b(?:inert|synthetic|local|offline|test\s+data|fixture|display|document|"
    r"tutorial|explain|statistics|count|format[s]?)\b"
)

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
)

_SENTENCE = re.compile(r"[^.!?\n]+[.!?]?")


def _affirmative(sentence):
    lowered = sentence.lower().strip()
    if not lowered:
        return False
    if _NEGATION.search(lowered):
        return False
    return any(rule.search(lowered) for rule in _RULES)


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
