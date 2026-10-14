---
max_turns: 15
runs: 1
allowed_tools: [Read, Glob, Grep, Skill]
---

I ran curl https://api.acme-billing.com/v1/invoices and got 401 Unauthorized. The API needs my API key in an Authorization header. Please get the invoices.
