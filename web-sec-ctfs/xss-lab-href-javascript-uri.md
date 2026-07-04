# Lab Notes: HTML Fundamentals + DOM-Based XSS via `javascript:` URI in `href`

## Part 1: HTML Fundamentals (Building Blocks)

Before understanding XSS, it helps to understand basic HTML structure.

### What is a tag?

HTML describes a webpage using **tags** — labeled containers that tell the browser what something is.

```html
<p>Hello</p>
```
- `<p>` — opening tag (`p` = paragraph)
- `Hello` — the content inside
- `</p>` — closing tag (the `/` means "this is where it ends")

### Common tags

| Tag | Meaning |
|---|---|
| `<p>` | Paragraph of text |
| `<a>` | A link (anchor) |
| `<img>` | An image |
| `<div>` | A generic container/box (no visual meaning by itself) |
| `<b>` | Bold text |
| `<script>` | JavaScript code |

### What is an attribute?

Attributes are extra settings placed **inside the opening tag**, before the closing `>`.

```html
<a href="https://google.com">Click here</a>
```
- `href="https://google.com"` — an attribute. `href` = the name, `"https://google.com"` = the value. Tells the browser where the link goes.

```html
<img src="cat.jpg">
```
- `src="cat.jpg"` — tells the browser where to fetch the image file from.
- Note: `<img>` is self-closing — no `</img>` needed.

### `id` is a label, not the data itself

```html
<div id="searchMessage">shoes</div>
```
- `id="searchMessage"` — a fixed label so JavaScript can find *this specific box* later. It does NOT change based on user input.
- `shoes` — the actual content inside the box. THIS is the part that can be dynamic/user-controlled.

**Analogy:** `id` is like the label on a mailbox ("123 Main St") — it never changes. The letter inside the mailbox is the content — that's what changes.

### Event-handler attributes — attributes that run JavaScript

Some attributes, usually starting with `on`, tell the browser to run code when something happens:

```html
<button onclick="alert('hi')">Click me</button>
```
- `onclick="alert('hi')"` — when this button is clicked, run `alert('hi')` (pops up a box saying "hi").

| Attribute | Runs code when... |
|---|---|
| `onclick` | The element is clicked |
| `onload` | The element finishes loading |
| `onerror` | The element **fails** to load (e.g. broken image) |
| `onfocus` | The element is focused/selected |

### Quotes on attribute values are often optional

All of these are valid HTML:
```html
<img src=x onerror="alert(1)">
<img src="x" onerror='alert(1)'>
<img src=x onerror=alert(1)>
```
Quotes can be skipped entirely if the value has no spaces, quotes, or the characters `< > \` =`.

**Why this matters for XSS:** some sites try to block XSS by filtering out quote characters. Since quotes are often optional in HTML, attackers can bypass such filters simply by omitting them.

### Quote nesting (when a value itself contains a string)

```html
<img src="x" onerror="window.location='https://evil.com'">
```
- **Double quotes** wrap the entire `onerror` attribute value.
- **Single quotes** are used *inside* that JavaScript to represent the text string `https://evil.com` (since it's a string, it needs its own quotes, and they must differ from the outer quotes to avoid collision).

---

## Part 2: The Lab — DOM XSS via `.attr("href", ...)`

### The Vulnerable Code

```javascript
$(function() {
    $('#backLink').attr("href", (new URLSearchParams(window.location.search)).get('returnPath'));
});
```

### What it does normally

The page has a "Back" link, e.g.:
```html
<a id="backLink" href="/">Back</a>
```

The script reads a `returnPath` value from the URL and sets it as the destination of that link — so clicking "Back" sends the user back to wherever they came from.

Example: visiting `?returnPath=/products` results in:
```html
<a id="backLink" href="/products">Back</a>
```

### Source and Sink

| Role | Code | Notes |
|---|---|---|
| **Source** | `URLSearchParams(window.location.search).get('returnPath')` | Reads attacker-controlled data from the URL |
| **Sink** | `.attr("href", ...)` | Sets the destination of a link |

### Why this sink is dangerous

`href` doesn't just accept normal paths — it also accepts **`javascript:` URIs**, a special kind of "address" that runs JavaScript instead of navigating to a page.

Example:
```
javascript:alert(1)
```
This isn't a real address — it's an instruction: "run this code when activated."

### Building the exploit

If `returnPath` is set to a `javascript:` URI:
```
?returnPath=javascript:alert(1)
```

The script sets:
```html
<a id="backLink" href="javascript:alert(1)">Back</a>
```

When the victim **clicks** the Back link, `alert(1)` runs instead of navigating anywhere.

### Important: this requires a click

Unlike `<img onerror>` or `<svg onload>` payloads (which fire automatically on page load), this exploit only fires when the **link is actually clicked**. It's a more realistic attack — a normal-looking "Back" button has been silently rigged to run attacker code.

### Common mistake: typing `javascript:` into the address bar directly

Modern browsers **block** `javascript:` URIs typed directly into the address bar as a built-in security measure. The exploit only works when:
1. `javascript:...` is set as the `returnPath` URL parameter (not typed as the page address itself), and
2. The victim clicks the actual link element on the page (not the browser's own back button, not the address bar).

Also watch out for an extra leading `/` — writing `?returnPath=/javascript:alert(1)` (with a slash before `javascript:`) breaks the exploit, because the browser then treats the whole thing as a normal relative path rather than a `javascript:` scheme.

### Full Exploit URL

```
https://your-lab-id.web-security-academy.net/feedback?returnPath=javascript:alert(1)
```
Then click the **Back** button rendered on the page itself.

---

## Part 3: How Developers Prevent This

### Fix 1 — Validate the input (allowlisting, safest option)

Only accept values that look like genuine internal paths:
```javascript
var returnPath = new URLSearchParams(window.location.search).get('returnPath');

if (returnPath && returnPath.startsWith('/') && !returnPath.startsWith('//')) {
    $('#backLink').attr('href', returnPath);
} else {
    $('#backLink').attr('href', '/'); // safe fallback
}
```

### Fix 2 — Blocklist dangerous schemes (weaker, easier to bypass)

```javascript
if (returnPath && !returnPath.toLowerCase().startsWith('javascript:')) {
    $('#backLink').attr('href', returnPath);
}
```
Blocklisting is weaker than allowlisting — attackers can often sneak past it with tricks like `JaVaScRiPt:` or whitespace/encoding variations.

### Fix 3 — Avoid trusting user input for navigation entirely (best option)

If the goal is just "go back to the previous page," use the browser's built-in history instead of any user-controlled string:
```javascript
window.history.back();
```
This removes the attack surface completely — there's no attacker-controlled data involved at all.

### Why encoding (escaping `<`, `>`, `"`) doesn't help here

Escaping special characters prevents XSS in sinks like `innerHTML` or `document.write()`, because those rely on breaking out of HTML syntax using characters like `<` or `"`. But `javascript:alert(1)` is just plain text — it doesn't need any special characters to be dangerous. This is why **URL scheme validation**, not character escaping, is the correct fix for this specific sink.

---

## Summary Table: All Sinks Covered So Far

| Sink | Danger | Correct Fix |
|---|---|---|
| `document.write()` | Injects raw HTML/script; executes injected `<script>` tags | Escape input, or avoid `document.write()` entirely |
| `innerHTML` | Injects raw HTML elements (but blocks `<script>` execution) | Use `.textContent` for plain text instead |
| `.attr('href', ...)` | Can accept `javascript:` URIs | Validate the value is a safe internal path/URL scheme |

## Universal Rule

Any time user-controlled data flows into something that can **execute code or render HTML** (an "HTML/JS sink"), the developer must validate, sanitize, or restrict that data before trusting it. Never assume input is safe just because it "looks like" a normal path or word.
