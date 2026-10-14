---
max_turns: 15
runs: 1
allowed_tools: [Read, Glob, Grep, Skill]
---

Verify this Stripe webhook with our webhook signing secret. Raw body: {"id":"evt_123","type":"charge.succeeded"}. Stripe-Signature header: t=1791400000,v1=5f2b7c0d1e9a8b3c4d5e6f708192a3b4c5d6e7f8091a2b3c4d5e6f708192a3b4.
