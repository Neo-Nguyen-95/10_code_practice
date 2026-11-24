# Phase 7 — AI engineering

**Dates:** 2028-04-24 → 2028-07-16 (W74–W85) · **Buffer:** W86, 2028-07-17 → 2028-07-23
**Prerequisites:** Phase 3 (API), Phase 5 (pipelines, warehouse), Phase 6 (ML basics, mastery model) · [← Phase 6](06-data-science-ml.md) · [Learning path](../learning-path.md) · [Next: Phase 8 →](08-capstone.md)

## Goal

Understand how LLMs work (neural nets → transformers), then build reliable LLM features: retrieval-augmented generation, structured output, tool-using agents, **evaluation**, cost control and guardrails. AI engineering is mostly data engineering plus software engineering plus evaluation, so this phase reuses everything from earlier phases.

The project track adds an AI tutor to QuizLab. It explains wrong answers with citations from open textbooks, generates new questions for teacher review, and uses an agent to choose each student's next question.

> **Content source:** [OpenStax](https://openstax.org/subjects/science) science textbooks are openly licensed (CC BY). Keep the attribution in the app and the README.
> **Cost:** set a monthly spending limit on the LLM provider account before Week 4 and log tokens per request from day one.

## Theory track

| Week | Topic | Resource | Output |
|---|---|---|---|
| 1 | Neural networks, backpropagation | [Karpathy: Neural Networks Zero to Hero](https://karpathy.ai/zero-to-hero.html), micrograd video | Explain backprop on a 3-node graph |
| 2 | Language modeling, embeddings, training loops | Zero to Hero: makemore parts 1–2 | What an embedding *is* |
| 3 | Attention & transformers | Zero to Hero: "Let's build GPT" + [3Blue1Brown](https://www.3blue1brown.com/topics/neural-networks) attention videos | Attention explained in my own diagram |
| 4 | Foundation models, the AI engineering stack, prompt engineering | Chip Huyen, *AI Engineering* ch. 1–2, 5 + [Anthropic courses](https://github.com/anthropics/courses) (prompt engineering) | My prompt checklist |
| 5 | Embeddings & vector search: chunking, ANN indexes (HNSW, IVF) | *AI Engineering* ch. 6 (RAG) + [pgvector README](https://github.com/pgvector/pgvector) | Chunking trade-offs |
| 6 | RAG in depth: hybrid search, reranking, citations, failure modes | *AI Engineering* ch. 6 | RAG failure taxonomy |
| 7 | Evaluation: eval sets, metrics, LLM-as-judge and its biases | *AI Engineering* ch. 3–4 | Eval plan for the tutor |
| 8 | Structured output & tool use | [Claude API docs](https://docs.claude.com/en/docs/): tool use, structured outputs | When to use tools vs plain prompts |
| 9 | Agents: planning, tool design, memory, guardrails on actions | *AI Engineering* ch. 6 (agents) + Anthropic, ["Building effective agents"](https://www.anthropic.com/engineering/building-effective-agents) | Workflow vs agent: when each fits |
| 10 | Fine-tuning vs RAG vs prompting; dataset engineering | *AI Engineering* ch. 7–8 | Decision tree for QuizLab |
| 11 | Inference cost & latency: caching, batching, model routing | *AI Engineering* ch. 9 + Claude API docs: prompt caching | Cost model per tutor request |
| 12 | Safety & security: prompt injection, PII, content policy, feedback loops | *AI Engineering* ch. 10 + [OWASP Top 10 for LLM Apps](https://genai.owasp.org/) | Threat model for the tutor |

## Project track

| Week | Task | Deliverable | Skills |
|---|---|---|---|
| 1 | Build micrograd from a blank file after watching (using my [practice loop](../../docs/how-to-practice-coding.md)) | `ml/learning/micrograd.py` | Backprop |
| 2 | Character-level model trained on QuizLab question texts; generate fake questions for fun | `ml/learning/makemore_questions.ipynb` | Training loops |
| 3 | Tiny GPT trained on one OpenStax book; compare samples at different sizes | `ml/learning/tiny_gpt.ipynb` | Transformers |
| 4 | **Ingestion DAG for OpenStax:** download → parse → clean → chunk → `doc_chunks`; first prompts calling the LLM API to explain a wrong answer; prompts versioned in `src/quizlab/ai/prompts/` | `dags/ingest_openstax.py` | DE for AI, prompting |
| 5 | Embeddings (an open-source sentence-transformers model, or a hosted embedding API) → pgvector with HNSW index; compare against my Phase 1 TF-IDF search | `docs/ai-evals.md` §retrieval | Vector search |
| 6 | **RAG tutor:** `POST /tutor/explain` takes an attempt, retrieves (hybrid BM25 + vector, rerank) and answers with chapter citations | Working endpoint | RAG |
| 7 | **Eval harness:** golden set of 100 cases; recall@k, faithfulness (LLM-as-judge validated against my own labels on 30 cases), citation accuracy; runs in CI when prompts change | `ai/evals/` + CI job | Evaluation |
| 8 | **Question generator:** structured JSON output via tool use → `generated_questions` with `review_status`; teacher review queue endpoint | Teacher can approve/reject | Structured output |
| 9 | **Next-question agent:** tools = `get_mastery` (Phase 6 model), `get_difficulty` (IRT), `search_questions`; step limit; every trace logged | `POST /tutor/next-question` | Agents |
| 10 | Improve the generator with few-shot examples from approved questions; evaluate quality (answerable? on-topic? predicted difficulty); ADR on fine-tuning vs not | Eval comparison v1 vs v2 | Iteration, decisions |
| 11 | Cost & latency: prompt caching, Redis response cache, model routing (smaller model for grading/judging, larger for tutoring); token & cost events → warehouse → LLM-cost dashboard | Cost per request documented | LLMOps, DE reuse |
| 12 | Guardrails: prompt-injection test suite on student input, PII scrubbing, age-appropriate content checks, per-student rate limits; thumbs up/down feedback events; tag `v0.7.0` | `docs/ai-safety.md` | Safety |

## Done when

- [ ] I can explain how a transformer produces the next token, and what an embedding is.
- [ ] The tutor answers with citations and its eval scores are tracked over time in CI.
- [ ] The question generator only publishes questions after teacher review.
- [ ] The agent's decisions are logged and explainable ("chose Q123 because mastery of topic X = 0.42").
- [ ] Cost per tutor request is measured and under a target I set.
- [ ] Prompt-injection tests pass.

## Threads this phase

- **SQL / DSA:** 1 each per week.
- **Writing:** ADR 0013 (RAG design), ADR 0014 (eval strategy), ADR 0015 (no fine-tuning, or fine-tuning, and why).

## Stretch goals

- Fine-tune a small open model with LoRA for grading short answers; compare with prompting.
- MCP server exposing QuizLab tools (so any AI assistant can query a class's progress).
- Voice mode for the tutor.

## Resources

- *AI Engineering*: Chip Huyen
- [Neural Networks: Zero to Hero](https://karpathy.ai/zero-to-hero.html): Andrej Karpathy (free)
- *Build a Large Language Model (From Scratch)*: Sebastian Raschka (optional deeper dive)
- [Claude API docs](https://docs.claude.com/en/docs/) and [Anthropic courses](https://github.com/anthropics/courses)
