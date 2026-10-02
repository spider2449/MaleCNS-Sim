# Local session refresh

Preserve the launcher token in sessionStorage before removing the URL fragment so a page reload in the same browser tab can authenticate. A newly supplied URL token replaces the stored token. Server token and Origin validation remain authoritative. If browser storage is unavailable, the current URL token remains usable for that page load.

Validation: execute the actual token initialization in Node with mocked browser objects, covering initial open, reload, token replacement, missing token, and unavailable storage. Check JavaScript syntax and whitespace errors.
