# Lab Notes: DOM-Based XSS via `innerHTML` — Search Message Display

## Overview

This lab demonstrates another **DOM-based Cross-Site Scripting (XSS)** vulnerability — but with a different sink than `document.write()`. This one uses `innerHTML`, which behaves differently and requires a different exploitation technique.

---

## The Vulnerable Code

```javascript
function doSearchQuery(query) {
    document.getElementById('searchMessage').innerHTML = query;
}
var query = (new URLSearchParams(window.location.search)).get('search');
if(query) {
    doSearchQuery(query);
}
```

---

## What This Code Does (Plain English)

The page has a little message box on it, something like:
```html
<div id="searchMessage"></div>
```

The idea is: when you search for something, the site shows a "You searched for: ___" style message by placing your search term inside that box.

### Step by step:

1. **Reads the search term from the URL.**
   ```javascript
   var query = (new URLSearchParams(window.location.search)).get('search');
   ```
   If the URL is `https://example.com/?search=shoes`, then `query` becomes `"shoes"`.

2. **Inserts that term into the page.**
   ```javascript
   document.getElementById('searchMessage').innerHTML = query;
   ```
   This finds the box with `id="searchMessage"` and sets its contents to whatever `query` is.

Normal result:
```html
<div id="searchMessage">shoes</div>
```

---

## Source and Sink

| Role | Code | Why |
|---|---|---|
| **Source** | `URLSearchParams(window.location.search).get('search')` | Reads attacker-controlled data straight from the URL. Anyone can change what comes after `?search=`. |
| **Sink** | `.innerHTML = query` | Inserts the value as **real HTML**, not just plain text. The browser builds actual elements out of it. |

---

## Why `innerHTML` Is Dangerous

`innerHTML` doesn't just display text — it **parses and builds real HTML elements** from whatever string it's given.

### Example: injecting a harmless tag

URL:
```
?search=<b>hello</b>
```

Result:
```html
<div id="searchMessage"><b>hello</b></div>
```

The word "hello" appears **bold** on the page — proving the browser treated `<b>` as a real tag, not plain text.

This proves attacker-supplied HTML gets built into the live page.

---

## The Exploit: Triggering JavaScript

Since HTML tags get built for real, some tags can execute JavaScript automatically — no click needed. A classic payload:

```html
<img src=x onerror=alert(1)>
```

### How it works:
- `<img src=x ...>` — tries to load an image file called `x`
- There is no real file called `x`, so the image **fails to load**
- `onerror=alert(1)` — runs `alert(1)` automatically when the image fails
- `alert(1)` pops up a box on screen — the standard proof-of-concept for "I can run JavaScript here"

### Full exploit URL:
```
https://your-lab-id.web-security-academy.net/?search=<img src=x onerror=alert(1)>
```

---

## Important Catch: `<script>` Tags Don't Work Here

You might expect this to work:
```
?search=<script>alert(1)</script>
```

**It won't fire.** Browsers have a built-in safety rule: **scripts inserted via `innerHTML` are never executed.** The `<script>` element gets created in the DOM, but its code is deliberately inert.

This is different from `document.write()` (used in a previous lab), which **does** execute injected `<script>` tags — because `document.write()` writes into the page while it's still actively being parsed, whereas `innerHTML` modifies an already-loaded page afterward, and browsers block script execution in that scenario specifically.

### Practical takeaway:
When the sink is `innerHTML`, don't bother with `<script>` payloads — use tags with **built-in event handlers** instead:

| Payload | How it fires |
|---|---|
| `<img src=x onerror=alert(1)>` | Fires when the broken image fails to load |
| `<svg onload=alert(1)>` | Fires as soon as the SVG element loads |
| `<input onfocus=alert(1) autofocus>` | Fires automatically due to `autofocus` attribute |
| `<body onload=alert(1)>` | Fires on body load (situational, may not work mid-page) |

`<img src=x onerror=alert(1)>` and `<svg onload=alert(1)>` are the most commonly used since they fire immediately and reliably, without needing user interaction.

---

## Comparison: `document.write()` vs `innerHTML` Sinks

| | `document.write()` | `innerHTML` |
|---|---|---|
| Executes injected `<script>` tags? | ✅ Yes | ❌ No |
| Needs event-handler payloads? | Not necessarily | ✅ Yes, typically required |
| Injection context | Often inside an existing attribute/tag (may need to break out with `">`) | Often full element content (no breakout needed) |
| Example working payload | `"><script>alert(1)</script>` | `<img src=x onerror=alert(1)>` |

---

## Summary Table

| Question | Answer |
|---|---|
| Where does the dangerous input come from? | The URL, after `?search=` |
| Where does it end up? | Inside a page element, via `innerHTML` |
| What's the danger? | `innerHTML` builds real HTML elements from that text, not just plain words |
| Why can't I just use `<script>`? | Browsers block script execution when inserted via `innerHTML` |
| What do I use instead? | A tag with a built-in event, like `<img src=x onerror=alert(1)>` |

---

## General Rule of Thumb

When testing a sink for XSS:
1. Try a harmless tag first (`<b>test</b>`) to confirm HTML is being rendered, not escaped.
2. If confirmed, try `<script>alert(1)</script>` — if it doesn't fire, the sink likely blocks scripts (common with `innerHTML`).
3. Fall back to event-handler-based payloads (`onerror`, `onload`, `onfocus`, etc.) — these work across almost all HTML-rendering sinks.
