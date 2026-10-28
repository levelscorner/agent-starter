---
name: web-quality
description: Use when building or reviewing a web page or web app front end, for speed budgets, loading, motion, security headers and the screen widths to test.
---

# Web quality

Hard numbers for front-end work. For how a page should look, use the antislop skills. Adapted in our own words from the web rules in [everything-claude-code](https://github.com/affaan-m/everything-claude-code) (MIT).

## Speed targets

| Measure | Target |
|---|---|
| Largest content shown (LCP) | under 2.5 s |
| Response to a tap or click (INP) | under 200 ms |
| Layout jumping (CLS) | under 0.1 |
| First content shown (FCP) | under 1.5 s |
| Main thread blocked (TBT) | under 200 ms |

## Size budgets (gzipped)

| Page | JavaScript | CSS |
|---|---|---|
| Landing page | under 150 KB | under 30 KB |
| App page | under 300 KB | under 50 KB |
| Small site | under 80 KB | under 15 KB |

## Loading

- Every image has a width and height. Only the hero image loads eagerly with high priority; the rest load lazily.
- Prefer AVIF or WebP. Never ship an image far bigger than it is shown.
- At most two font families. Use `font-display: swap`. Preload only the one critical weight.
- Load heavy libraries only when needed (dynamic import). Third-party scripts load async or deferred.

## Motion

- Animate only `transform`, `opacity`, `clip-path`, and `filter` sparingly. Never animate width, height, top, left, margin, padding or font size.
- Respect reduced-motion settings.
- Use an IntersectionObserver instead of scroll handlers.

## Structure

- Use the semantic element (`header`, `nav`, `main`, `section`, `footer`) before a `div`.
- Colors, type sizes, spacing and durations live in CSS variables, not repeated values.
- Organize files by feature, not by file type.

## Security headers

- A Content Security Policy with a per-request nonce for scripts, not `unsafe-inline`.
- `Strict-Transport-Security`, `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, a strict `Referrer-Policy`, and a `Permissions-Policy` that turns off camera, microphone and location unless needed.

## Test at these widths

320, 375, 768, 1024, 1440 and 1920 pixels. No sideways scrolling at any of them. If the site has light and dark themes, check both. Check keyboard use and contrast every time.
