"""Summarise one task-feed page as a JSON object (see SPEC.md)."""
import json
import math
import re
import sys
from datetime import datetime, timezone

BUCKETS = ("none", "text", "under_10", "at_least_10")
ISO_RE = re.compile(
    r"^(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2}):(\d{2})(\.\d+)?(Z|[+-]\d{2}:\d{2})$"
)


class FeedError(Exception):
    pass


def parse_time(value, label):
    if not isinstance(value, str):
        raise FeedError(f"{label} must be an ISO 8601 string")
    if not ISO_RE.match(value):
        raise FeedError(f"{label} must be a valid ISO 8601 timestamp with timezone")
    text = value[:-1] + "+00:00" if value.endswith("Z") else value
    try:
        dt = datetime.fromisoformat(text)
    except ValueError:
        raise FeedError(f"{label} is not a valid timestamp")
    if dt.tzinfo is None or dt.utcoffset() is None:
        raise FeedError(f"{label} must include a timezone")
    return dt


def bucket_for(bounty):
    if bounty is None:
        return "none"
    if not isinstance(bounty, dict):
        raise FeedError("bounty must be an object or null")
    if "reward" in bounty and not isinstance(bounty["reward"], str):
        raise FeedError("bounty.reward must be a string")
    reward = bounty.get("reward")
    if "amountUsd" in bounty and not isinstance(bounty["amountUsd"], (int, float)):
        raise FeedError("bounty.amountUsd must be a number")
    amount = bounty.get("amountUsd")
    if amount is not None:
        if isinstance(amount, bool) or not isinstance(amount, (int, float)):
            raise FeedError("bounty.amountUsd must be a number")
        if isinstance(amount, int):
            if amount < 0:
                raise FeedError("bounty.amountUsd must be finite and nonnegative")
        else:
            if not math.isfinite(amount) or amount < 0:
                raise FeedError("bounty.amountUsd must be finite and nonnegative")
        if amount == 0:
            if isinstance(reward, str) and reward.strip():
                return "text"
            return "none"
        return "under_10" if amount < 10 else "at_least_10"
    if reward is None:
        return "none"
    return "text" if reward.strip() else "none"


def summarise(feed):
    if not isinstance(feed, dict):
        raise FeedError("feed must be a JSON object")
    items = feed.get("items")
    if not isinstance(items, list):
        raise FeedError("items must be a list")
    if "now" not in feed:
        raise FeedError("now is required")
    now = parse_time(feed["now"], "now")

    total = len(items)
    by_status = {}
    buckets = {name: 0 for name in BUCKETS}
    ages = []
    tag_counts = {}
    seen_ids = set()

    for item in items:
        if not isinstance(item, dict):
            raise FeedError("each item must be an object")
        for field in ("id", "type", "status", "createdAt", "tags"):
            if field not in item:
                raise FeedError(f"item missing required field {field}")

        ident = item["id"]
        if not isinstance(ident, str) or not ident:
            raise FeedError("item id must be a nonempty string")
        if ident in seen_ids:
            raise FeedError(f"duplicate item id {ident!r}")
        seen_ids.add(ident)

        if item["type"] != "task":
            raise FeedError("item type must be 'task'")

        status = item["status"]
        if not isinstance(status, str) or not status:
            raise FeedError("item status must be a nonempty string")
        by_status[status] = by_status.get(status, 0) + 1

        created = parse_time(item["createdAt"], "createdAt")
        age = (now - created).total_seconds() / 3600.0
        ages.append(max(0.0, age))

        tags = item["tags"]
        if not isinstance(tags, list):
            raise FeedError("item tags must be a list")
        normalised = set()
        for tag in tags:
            if not isinstance(tag, str):
                raise FeedError("each tag must be a string")
            normalised_tag = tag.strip().casefold()
            if normalised_tag:
                normalised.add(normalised_tag)
        for tag in normalised:
            tag_counts[tag] = tag_counts.get(tag, 0) + 1

        buckets[bucket_for(item.get("bounty"))] += 1

    if ages:
        ages.sort()
        mid = len(ages) // 2
        median = ages[mid] if len(ages) % 2 else (ages[mid - 1] + ages[mid]) / 2.0
        median = int(median) if median == int(median) else median
    else:
        median = None

    top_tags = [
        {"tag": tag, "count": count}
        for tag, count in sorted(tag_counts.items(), key=lambda pair: (-pair[1], pair[0]))[:5]
    ]

    return {
        "total": total,
        "by_status": by_status,
        "reward_buckets": buckets,
        "median_age_hours": median,
        "top_tags": top_tags,
    }


def main(argv):
    if len(argv) != 2:
        sys.stderr.write("usage: feed_stats.py <feed.json>\n")
        return 2
    try:
        with open(argv[1], "r", encoding="utf-8") as handle:
            feed = json.load(handle)
    except OSError as exc:
        sys.stderr.write(f"cannot read input file: {exc}\n")
        return 2
    except json.JSONDecodeError as exc:
        sys.stderr.write(f"malformed JSON: {exc}\n")
        return 2
    try:
        summary = summarise(feed)
    except FeedError as exc:
        sys.stderr.write(f"invalid input: {exc}\n")
        return 2
    sys.stdout.write(json.dumps(summary, ensure_ascii=False) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
