# Security policy

Please report vulnerabilities **privately** through GitHub:
**[Report a vulnerability](https://github.com/nookverse/gameplay-vertical-short/security/advisories/new)**.
Don't open a public issue. We aim to reply within 7 days.

Relevant areas: shell or ffmpeg command injection through file names, captions or JSON specs, and
anything that reads or writes outside the folders you pass to the tools. The tools make no network
calls; the only download (the optional Kokoro model) is one you run yourself.
