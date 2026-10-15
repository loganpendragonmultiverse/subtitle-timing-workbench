# Security

No network, telemetry, account, persistent cache or media access. Only explicitly selected subtitle and plan files are read. Reports contain timing evidence; review plans bind source bytes and output bytes using SHA-256. All output paths use exclusive creation, so original and existing files cannot be overwritten.

This is a timing workbench, not a full WebVTT specification validator or subtitle editor. WebVTT NOTE/STYLE/REGION blocks are preserved without semantic validation. No media playback, translation, per-cue editing, automatic correction, or alignment to audio. Character speed excludes whitespace and markup and counts Unicode code points, not visual graphemes; it is review evidence, not a universal readability rule. Inputs are limited to 5 MB, 20,000 cues and 100,000 overlap pairs; timestamps after shifts must remain within 00..99 hours.

Do not post private files or exploitable security details in a public issue. Use GitHub private vulnerability reporting when enabled; if unavailable, contact the maintainer through the organization profile before sharing details. Only this candidate line is currently under review; no supported public release exists yet.
