---
expect:
  method: string
  url: /^https:\/\//
---

HTTP 200
Content-Type: application/json

{"ok": true, "id": "mock_123", "note": "This is a mocked response."}
