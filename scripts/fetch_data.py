#!/usr/bin/env python3
"""Pull profile data from GitHub's GraphQL API into data/snapshot.json.

Standard library only, on purpose: this runs nightly in Actions and a
dependency that breaks upstream would take the profile down with it.

Two things here exist to stop the workflow committing meaningless diffs
every night, both of which cost real time to find:

1. The contribution window is pinned to whole UTC days. Left alone,
   contributionsCollection measures "the past year" from the instant of the
   request, so two runs a few minutes apart bucket days into different weeks
   and shift every chart by a fraction of a pixel.

2. Repositories are filtered to public, non-fork, owner-affiliated. A
   personal token sees private repos and the workflow's token does not, so
   without this the language split depends on who ran the script.

If the API call fails, the previous snapshot is kept and marked stale rather
than overwritten with a half-response. See main().
"""

import datetime as dt
import json
import os
import sys
import urllib.error
import urllib.request

API = "https://api.github.com/graphql"
ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
SNAPSHOT = os.path.join(ROOT, "data", "snapshot.json")

PROFILE = """
query($login:String!, $from:DateTime!, $to:DateTime!, $cursor:String) {
  user(login:$login) {
    login
    name
    createdAt
    followers { totalCount }
    repositories(first: 100, after: $cursor, isFork: false, privacy: PUBLIC,
                 ownerAffiliations: OWNER,
                 orderBy: {field: PUSHED_AT, direction: DESC}) {
      totalCount
      pageInfo { hasNextPage endCursor }
      nodes {
        name
        description
        pushedAt
        stargazerCount
        primaryLanguage { name }
        languages(first: 12, orderBy: {field: SIZE, direction: DESC}) {
          edges { size node { name } }
        }
      }
    }
    window: contributionsCollection(from: $from, to: $to) {
      restrictedContributionsCount
      totalCommitContributions
      totalPullRequestContributions
      totalIssueContributions
      totalPullRequestReviewContributions
      contributionCalendar {
        totalContributions
        weeks { contributionDays { date contributionCount } }
      }
    }
  }
}
"""

YEAR_FIELD = """
    y%(year)d: contributionsCollection(from: "%(from)s", to: "%(to)s") {
      contributionCalendar {
        totalContributions
        weeks { contributionDays { date contributionCount } }
      }
    }
"""


def query(body, variables, token):
    payload = json.dumps({"query": body, "variables": variables}).encode()
    req = urllib.request.Request(
        API, data=payload,
        headers={
            "Authorization": f"bearer {token}",
            "Content-Type": "application/json",
            "User-Agent": "advait27-profile-generator",
        },
    )
    with urllib.request.urlopen(req, timeout=45) as resp:
        out = json.loads(resp.read().decode())
    if "errors" in out:
        raise RuntimeError(json.dumps(out["errors"])[:600])
    if not out.get("data", {}).get("user"):
        raise RuntimeError("no user in response")
    return out["data"]


def utc_window(today, days=365):
    """Whole-UTC-day window ending today. See the module docstring."""
    start = today - dt.timedelta(days=days - 1)
    return (f"{start.isoformat()}T00:00:00Z", f"{today.isoformat()}T23:59:59Z")


def calendar_days(collection):
    out = []
    for week in collection["contributionCalendar"]["weeks"]:
        for day in week["contributionDays"]:
            out.append([day["date"], day["contributionCount"]])
    out.sort()
    return out


def streaks(days, today):
    """Current and longest run of consecutive days with any contribution.

    `days` is [[iso_date, count], ...] ascending and gapless.

    Today counts only if it has activity: a streak is not broken at 09:00 by
    a day that still has fifteen hours left in it, so a zero on the final day
    is skipped rather than treated as a break.
    """
    best = cur = 0
    best_range = cur_range = (None, None)
    for date, count in days:
        if count > 0:
            cur += 1
            cur_range = (date if cur == 1 else cur_range[0], date)
            if cur > best:
                best, best_range = cur, cur_range
        elif date != today.isoformat():
            cur, cur_range = 0, (None, None)
    return {
        "current": cur,
        "current_from": cur_range[0],
        "current_to": cur_range[1],
        "longest": best,
        "longest_from": best_range[0],
        "longest_to": best_range[1],
    }


def collect(login, token, today):
    frm, to = utc_window(today)

    # Repositories paginate; contributions do not. Ask for both on the first
    # page, then keep paging repos only.
    data = query(PROFILE, {"login": login, "from": frm, "to": to, "cursor": None}, token)
    user = data["user"]
    repos = list(user["repositories"]["nodes"])
    page = user["repositories"]["pageInfo"]
    while page["hasNextPage"]:
        more = query(PROFILE, {"login": login, "from": frm, "to": to,
                               "cursor": page["endCursor"]}, token)
        repos.extend(more["user"]["repositories"]["nodes"])
        page = more["user"]["repositories"]["pageInfo"]

    # All-time history, one aliased collection per calendar year. A single
    # contributionsCollection covers at most a year.
    first_year = int(user["createdAt"][:4])
    fields = []
    for year in range(first_year, today.year + 1):
        start = dt.date(year, 1, 1)
        end = min(dt.date(year, 12, 31), today)
        fields.append(YEAR_FIELD % {
            "year": year,
            "from": f"{start.isoformat()}T00:00:00Z",
            "to": f"{end.isoformat()}T23:59:59Z",
        })
    history = query(
        "query($login:String!){ user(login:$login){" + "".join(fields) + "}}",
        {"login": login}, token,
    )["user"]

    all_days = []
    for year in range(first_year, today.year + 1):
        all_days.extend(calendar_days(history[f"y{year}"]))
    all_days.sort()
    # Clamp to the account's own lifetime. The per-year queries start at 1
    # January of the signup year, so without this the "since" date reads as
    # January of a year the account did not yet exist in.
    created = user["createdAt"][:10]
    all_days = [d for d in all_days if created <= d[0] <= today.isoformat()]

    window = user["window"]
    window_days = calendar_days(window)

    # Language totals. Both views are kept because they disagree sharply and
    # the disagreement is the point: notebooks embed base64 cell outputs in
    # their JSON, so Linguist counts rendered plots as authored bytes.
    by_bytes, by_repo = {}, {}
    stars = 0
    for repo in repos:
        stars += repo["stargazerCount"]
        for edge in repo["languages"]["edges"]:
            by_bytes[edge["node"]["name"]] = by_bytes.get(edge["node"]["name"], 0) + edge["size"]
        primary = (repo["primaryLanguage"] or {}).get("name")
        if primary:
            by_repo[primary] = by_repo.get(primary, 0) + 1

    def ranked(mapping):
        # Sort by value desc, then name asc: ties must not reorder between runs.
        return [[k, v] for k, v in sorted(mapping.items(), key=lambda kv: (-kv[1], kv[0]))]

    recent = [
        {
            "name": r["name"],
            "description": (r["description"] or "").strip(),
            "language": (r["primaryLanguage"] or {}).get("name") or "",
            "pushed": r["pushedAt"][:10],
            "stars": r["stargazerCount"],
        }
        for r in sorted(repos, key=lambda r: (r["pushedAt"], r["name"]), reverse=True)[:5]
    ]

    return {
        "schema": 1,
        "generated": today.isoformat(),
        "stale": False,
        "login": user["login"],
        "name": user["name"] or user["login"],
        "created": user["createdAt"][:10],
        "followers": user["followers"]["totalCount"],
        "window": {
            "from": frm[:10],
            "to": to[:10],
            "days": window_days,
            "total": window["contributionCalendar"]["totalContributions"],
            "commits": window["totalCommitContributions"],
            "prs": window["totalPullRequestContributions"],
            "issues": window["totalIssueContributions"],
            "reviews": window["totalPullRequestReviewContributions"],
            "restricted": window["restrictedContributionsCount"],
        },
        # A token that cannot see private contributions reports zero
        # restricted contributions, and the calendar total drops with it.
        # Recorded so the chart can say "public contributions" instead of
        # quietly understating the year. See the workflow's token choice.
        "private_hidden": window["restrictedContributionsCount"] == 0,
        "streak": dict(
            streaks(all_days, today),
            all_time=sum(c for _, c in all_days),
            active_days=sum(1 for _, c in all_days if c > 0),
            since=all_days[0][0] if all_days else today.isoformat(),
        ),
        "langs": {
            "by_repo": ranked(by_repo),
            "by_bytes": ranked(by_bytes),
            "repo_count": len(repos),
        },
        "repos": {"total": len(repos), "stars": stars, "recent": recent},
    }


def write(snapshot):
    os.makedirs(os.path.dirname(SNAPSHOT), exist_ok=True)
    with open(SNAPSHOT, "w") as fh:
        json.dump(snapshot, fh, indent=2, sort_keys=True, ensure_ascii=False)
        fh.write("\n")


def main():
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    login = os.environ.get("GH_LOGIN")
    if not token or not login:
        sys.exit("GITHUB_TOKEN and GH_LOGIN must be set")

    today = dt.datetime.now(dt.timezone.utc).date()
    try:
        write(collect(login, token, today))
        print(f"snapshot written for {login} @ {today}")
    except (urllib.error.URLError, RuntimeError, KeyError, TimeoutError) as exc:
        # Keep the last good snapshot rather than shipping a broken page. The
        # job exits clean so a transient API failure does not turn the repo
        # red, but the staleness is recorded and rendered.
        if not os.path.exists(SNAPSHOT):
            sys.exit(f"fetch failed and no previous snapshot exists: {exc}")
        with open(SNAPSHOT) as fh:
            previous = json.load(fh)
        previous["stale"] = True
        write(previous)
        print(f"::warning::fetch failed ({exc}); kept snapshot "
              f"from {previous.get('generated')}")


if __name__ == "__main__":
    main()
