---
title: Measure before you ship
slug: measure-before-you-ship
date: 2026-11-19
series: Intro
summary: Why this blog exists, who it's for, and the three series it will run.
draft: true
---

I'm Vinícius. I'm a software engineer, and these days most of my work is building AI features and figuring out whether they actually work.

That second part is what this blog is about. Getting a model to produce *something* is easy. Showing that the output is good enough, and staying sure of it as prompts, models and data change, is the actual engineering.

```
idea ──▶ prototype ──▶ [ eval gate ] ──▶ ship
                           │
                           └── fails? ──▶ back to prototype, with a number
```

## Where I'm coming from

- **Industry:** I build evals and the harness around AI features at a startup. I won't write about my employer's internals here, only methods and lessons I can share.
- **Research:** I did an MBA in AI & Big Data at ICMC-USP. My monograph trained a RoBERTa model to predict the CEFR level of English sentences, and that work is now growing into a research proposal.

Both point to the same habit: **don't trust a model you haven't measured**.

## The three series

| Series | What it covers | First post |
| --- | --- | --- |
| **Ship gate** | Evals, quality bars, cost, and when to say no to a feature | [Why I don't ship an AI feature without an eval](/posts/no-eval-no-ship) |
| **Small model, measured** | Fine-tuned small models vs. prompting big ones, with real numbers | [A fine-tuned RoBERTa beat my local LLM, 0.50 to 0.36](/posts/roberta-vs-local-llm) |
| **Decision records** | Architecture choices written up as RFCs, trade-offs included | Coming soon |

## The rule for every post

Each post has to pass three checks before it goes up:

1. **Is there a decision with a trade-off?** If not, it's a tutorial, and there are enough of those already.
2. **Is there a number I measured?** If not, I park it until I've measured something.
3. **Is it free of employer details?** If not, I rewrite it at the method level.

If you're hiring for lead or staff roles that involve AI systems, or you're working on the same problems, I'd like to hear from you. Ways to reach me are on the [About](/about) page.
