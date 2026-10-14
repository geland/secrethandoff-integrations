---
expect:
  name: /^[A-Za-z][A-Za-z0-9_]{0,63}$/
  reason: string
  policy.hosts: array
---

{{input.name}} is ready. Sent only to the hosts in the policy you gave. Use it with http_request by writing {{secret:{{input.name}}}} in a header, the URL query, or the body. Use run_with_secret only when a command must read it from its environment.
