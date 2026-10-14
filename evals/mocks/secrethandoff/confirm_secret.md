---
expect:
  name: string
  code: string
---

{{input.name}} is ready. Use it with http_request by writing {{secret:{{input.name}}}} in a header, the URL query, or the body.
