# Lab Notes: DOM-Based XSS via `document.write()` — Search Tracking Feature

## Overview

This lab demonstrates a **DOM-based Cross-Site Scripting (XSS)** vulnerability. Unlike stored or reflected XSS, DOM-based XSS never touches the server — the entire vulnerable data flow (source → sink) happens client-side, inside the browser's JavaScript.

---

## The Vulnerable Code

```javascript
<script>
    function trackSearch(query) {
        document.write('<img src="/resources/images/tracker.gif?searchTerms='+query+'">');
    }
    var query = (new URLSearchParams(window.location.search)).get('search');
    if(query) {
        trackSearch(query);
    }
</script>
```

## What This Code Is Supposed to Do

This is a simple analytics tracker. When a user searches for something on the site, the site wants to log what was searched. It does this by:

1. Reading the search term from the page's URL.
2. Building a fake tiny tracking image tag, embedding the search term into that image's URL as a query parameter.
3. Writing that `<img>` tag into the page using `document.write()`.
4. The browser then requests that image URL, which lets the analytics server log the search term (since the term shows up in the image request).

This is a legacy, "cheap" analytics pattern — no framework, just raw string concatenation into HTML.

---

## Function-by-Function Breakdown

### `window.location.search`
Returns the query string portion of the current URL (everything after `?`). For example, on:
```
https://example.com/?search=shoes
```
`window.location.search` returns `"?search=shoes"`.

### `new URLSearchParams(window.location.search)`
Parses that query string into a usable object, letting you extract individual parameters by name instead of manually splitting strings.

### `.get('search')`
Pulls out the value of the `search` parameter specifically. In the example above, this returns `"shoes"`.

### `if(query) { trackSearch(query); }`
If a `search` parameter was present in the URL, call `trackSearch()` with it.

### `trackSearch(query)`
Takes the raw search term and concatenates it directly into an HTML string, then hands that string to `document.write()`.

### `document.write(...)`
Injects the given string directly into the page as **live HTML** — no filtering, no escaping. Whatever text is passed in is parsed as real markup by the browser.

---

## Source and Sink

| Role | Code | Why |
|---|---|---|
| **Source** | `window.location.search` | Where attacker-controlled data enters. Anyone can craft a URL with any value in the `search` parameter and send it to a victim as a link. |
| **Sink** | `document.write()` | Where that data ends up. This function writes raw HTML into the page with zero sanitization — the most dangerous kind of sink. |

**The vulnerability exists because untrusted data flows straight from the source to the sink with nothing in between to clean or escape it.**

---

## Why This Is Exploitable

Normal use:
```
?search=shoes
```
produces:
```html
<img src="/resources/images/tracker.gif?searchTerms=shoes">
```
Harmless — `shoes` is just text sitting inside an attribute value.

But since `query` is inserted raw, an attacker can inject characters that have special meaning in HTML (`"`, `<`, `>`) to break out of the intended context.

---

## Building the Payload — Step by Step

**Goal:** escape out of the `src="..."` attribute AND out of the `<img>` tag itself, so we can inject a brand-new, real HTML element.

### Step 1 — Escape the attribute
Injecting a `"` closes the `src="..."` attribute value early.

### Step 2 — Escape the tag
A `"` alone isn't enough — you're still inside the `<img ...>` tag boundary. Adding a `>` closes the tag itself, returning the browser's parser to the top level of the document, where it will recognize new tags as real elements.

### Step 3 — Inject the real payload
Now that we're fully outside both the attribute and the tag, anything we add is parsed as genuine HTML — including `<script>` tags.

### Final Payload
```
"><script>alert(1)</script>
```

### Resulting HTML
```html
<img src="/resources/images/tracker.gif?searchTerms="><script>alert(1)</script>">
```

Parsed by the browser as:
1. `<img src="...searchTerms=">` — a (broken) but complete, closed `<img>` tag.
2. `<script>alert(1)</script>` — a brand-new, valid, executable script tag.
3. `">` — leftover stray text, harmless.

---

## Key Concept: Two Nested Boundaries

Every injection into an HTML attribute involves escaping **two separate containers**:

1. **Attribute boundary** (`"..."`) — closed with a matching quote.
2. **Tag boundary** (`<...>`) — closed with `>`.

Closing the quote alone only frees you from the attribute — you're still trapped inside the tag itself. You must close both to reach the "top level" of the page where new tags are actually parsed as real elements.

---

## Mental Model for Future Labs

Every XSS payload answers two questions:
1. **How do I escape whatever context I'm currently stuck inside?** (attribute, tag, string, comment, etc. — depends on where the injection lands)
2. **What malicious payload do I inject once I'm free?**

## General Rule of Thumb

Any time user-controlled input (URL parameters, form fields, cookies, headers) flows into a sink that renders raw HTML/JS — `document.write()`, `innerHTML`, `eval()`, `setTimeout()` with a string, etc. — without proper encoding/sanitization, that's a DOM XSS red flag worth testing.
