---
title: A fine-tuned RoBERTa beat my local LLM, 0.50 to 0.36
slug: roberta-vs-local-llm
date: 2026-11-19
series: Small model, measured
summary: Predicting the CEFR level of English sentences with TF-IDF, a few-shot local LLM and a fine-tuned RoBERTa. The small model won, and here's where it still falls short.
draft: true
---

For my MBA monograph I wanted to answer a practical question: **how hard is a given English sentence for a learner?** The standard yardstick is CEFR, the six levels from A1 (beginner) to C2 (near-native).

If you can score a sentence's level automatically, you can keep generated text at the right difficulty for a student. That's the long-term goal behind this work.

## The setup

```
English sentence
      │
      ▼
┌────────────┬──────────────────┬─────────────────────┐
│  TF-IDF    │ Local LLM        │ RoBERTa-base        │
│  + linear  │ (gemma, few-shot)│ fine-tuned,         │
│  model     │ prompted         │ regression head     │
└────────────┴──────────────────┴─────────────────────┘
      │               │                   │
      └──────── CEFR level (A1 … C2) ─────┘
                      │
                      ▼
          scored with QWK against human labels
```

- **Data:** 1,188 labelled sentences.
- **Metric:** quadratic weighted kappa (QWK). It rewards getting close: predicting B1 when the answer is B2 costs much less than predicting A1. That matches how a level classifier fails in practice.
- **Three contenders:** a classic TF-IDF baseline, a local LLM prompted with a few examples (gemma, running on my own machine), and RoBERTa-base fine-tuned as a regressor.

## Results

| Approach | QWK |
| --- | --- |
| TF-IDF baseline | 0.17 |
| Local LLM, few-shot | 0.36 |
| **Fine-tuned RoBERTa-base** | **0.50** |

The fine-tuned encoder beat prompting by a wide margin, and it runs locally on modest hardware. For a narrow, well-defined task with labelled data, a small specialised model was both better and cheaper than a general model asked nicely.

## The weak spot

0.50 is not state of the art. Published BERT-style results on the full CEFR-SP dataset reach about **0.61 to 0.63**. My model sits about 0.11 below that.

The most likely reason is data. I trained on 1,188 sentences, and the full dataset is much larger. So the honest reading is:

- ✅ The *ranking* of approaches holds: fine-tuning > few-shot prompting > TF-IDF.
- ⚠️ The *absolute number* isn't competitive yet.

The next step is retraining on the full CEFR-SP data and publishing the model and code, so the comparison can be reproduced.

## The engineering takeaway

Before reaching for the biggest model you can call, ask three questions:

1. Is the task narrow enough to fine-tune for?
2. Do you have, or can you get, labelled data?
3. Do you have a metric that reflects how errors actually hurt?

If all three are yes, a small fine-tuned model is worth trying first. And that third question applies to every AI feature, which is the subject of the [Ship gate](/posts/no-eval-no-ship) series.

<!-- TODO before publishing: confirm the exact dataset name/split for the 1,188 sentences, the gemma variant, and link the monograph / model card. -->
