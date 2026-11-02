"""Measure what an AI/automation tool saves, honestly.

Rules this tool enforces:
- at least 5 trials per method, or it refuses to report
- medians, not means, with a bootstrap 90% interval on the time saved
- defects found are reported next to time (faster but worse is not a saving)
- an annual figure is printed only if you give a volume, and is labelled a projection
Standard library only.
"""
import csv
import random
import statistics
import sys

MIN_TRIALS = 5


def load(path):
    with open(path, encoding="utf-8") as fh:
        rows = [r for r in csv.DictReader(fh) if not r["method"].startswith("#")]
    arms = {}
    for r in rows:
        arms.setdefault(r["method"], []).append(
            {"minutes": float(r["minutes"]), "found": int(r["defects_found"]), "planted": int(r["defects_planted"])})
    return arms


def bootstrap_saving(a, b, n=2000, seed=42):
    rnd = random.Random(seed)
    diffs = []
    for _ in range(n):
        sa = [rnd.choice(a) for _ in a]
        sb = [rnd.choice(b) for _ in b]
        diffs.append(statistics.median(sa) - statistics.median(sb))
    diffs.sort()
    return diffs[int(0.05 * n)], diffs[int(0.95 * n)]


def analyse(arms, baseline="manual", candidate="tool"):
    for name in (baseline, candidate):
        if len(arms.get(name, [])) < MIN_TRIALS:
            raise ValueError(f"refusing to report: '{name}' has {len(arms.get(name, []))} trials, need {MIN_TRIALS}")
    a = [t["minutes"] for t in arms[baseline]]
    b = [t["minutes"] for t in arms[candidate]]

    def recall(arm):
        return sum(t["found"] for t in arm) / sum(t["planted"] for t in arm)

    low, high = bootstrap_saving(a, b)
    return {"n": (len(a), len(b)), "median": (statistics.median(a), statistics.median(b)),
            "saving": statistics.median(a) - statistics.median(b), "interval": (low, high),
            "recall": (recall(arms[baseline]), recall(arms[candidate]))}


def main(path, volume=None):
    r = analyse(load(path))
    (ma, mb), (ra, rb) = r["median"], r["recall"]
    print(f"Trials: manual {r['n'][0]}, tool {r['n'][1]}")
    print(f"Median minutes per campaign: manual {ma:.1f}, tool {mb:.1f}")
    print(f"Saved per campaign: {r['saving']:.1f} min (90% interval {r['interval'][0]:.1f} to {r['interval'][1]:.1f})")
    print(f"Planted defects found: manual {ra:.0%}, tool {rb:.0%}")
    if volume:
        lo, hi = (x * volume / 60 for x in r["interval"])
        print(f"PROJECTION, not a measurement: at {volume} campaigns/year, {lo:.0f} to {hi:.0f} hours")
    print("\nNot measured: setup time, false alarms, maintenance, or whether people trust the tool.")


if __name__ == "__main__":
    a = sys.argv[1:]
    main(a[0] if a else "examples/illustrative_trials.csv", int(a[1]) if len(a) > 1 else None)
