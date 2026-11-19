---
title: Why I don't ship an AI feature without an eval
slug: no-eval-no-ship
date: 2026-11-19
series: Ship gate
summary: Demos lie. A small, boring eval set is what makes an AI feature safe to change, and it's the first thing I build.
draft: true
---

Every AI feature I've worked on has had the same moment: the demo looks great, and someone asks "can we ship it?"

My answer is always the same question back: **compared to what, measured how?**

## Why demos lie

A demo is a handful of inputs the builder picked, usually after seeing what works. That tells you the feature *can* work, not that it *does* work on the inputs real users will send.

And AI features keep changing underneath you:

```
          your feature
               │
   ┌───────────┼────────────┬──────────────┐
   ▼           ▼            ▼              ▼
 prompt     model        retrieved      user
 edits      upgrades     data shifts    behaviour
   │           │            │              │
   └───────────┴─────┬──────┴──────────────┘
                     ▼
        output quality moves, silently
```

Without an eval, you find out about a regression from a customer.

## The minimum eval I build first

It doesn't need to be fancy. Before shipping, I want:

1. **A fixed set of real-ish cases.** Start with 30 to 100. Include the easy ones, the ugly ones, and the cases you're scared of.
2. **A clear pass/fail or score per case.** Exact match, a rubric, a programmatic check, or an LLM judge that you've spot-checked against humans.
3. **A baseline.** The current behaviour, or the simplest thing that could work. A number means nothing without something to compare it to.
4. **One command to run it.** If it's annoying to run, nobody runs it.

## The gate

```
change (prompt / model / code)
            │
            ▼
      run eval suite
            │
     score ≥ baseline?  ── no ──▶ don't merge; look at the failures
            │
           yes
            │
            ▼
   cost & latency OK?   ── no ──▶ trade-off discussion, with numbers
            │
           yes
            ▼
          ship
```

The gate does two things. It stops regressions, and it changes the conversation. "It feels better" turns into "it went from X to Y on these cases, and it costs Z more per request". That's a conversation a team can make decisions with.

## The trade-off

Evals cost time up front, and a small eval set can give you false confidence if it doesn't look like real traffic. I accept that because:

- the first version takes hours, not weeks;
- every production failure becomes a new case, so the set gets better over time;
- the alternative is shipping blind and paying for it later.

<!-- TODO before publishing: add one concrete, employer-safe example with a real number (e.g. "a prompt change that looked better in the demo dropped the pass rate from X% to Y%"). This post needs a measured number to pass the blog's own rule #2. -->
