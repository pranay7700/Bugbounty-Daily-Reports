import requests
import datetime
import os
from bs4 import BeautifulSoup

REPORTS_DIR = "reports"
HEADERS = {"User-Agent": "Mozilla/5.0"}

def write_header(date):
    return f"""---
layout: default
parent: Reports
title: {date}
---

# Bug Bounty Report — {date}

"""

# 1. HackerOne Disclosed Reports
def fetch_hackerone():
    url = "https://hackerone.com/hacktivity.json"
    r = requests.get(url, headers=HEADERS)
    reports = r.json().get("reports", [])[:10]
    text = "## HackerOne Disclosed Reports\n"
    for r in reports:
        text += f"- {r['title']} → https://hackerone.com/reports/{r['id']}\n"
    return text + "\n"

# 2. Bugcrowd Disclosed Reports
def fetch_bugcrowd():
    url = "https://bugcrowd.com/disclosures.json?page=1"
    r = requests.get(url, headers=HEADERS).json()
    reports = r["disclosures"][:10]
    text = "## Bugcrowd Disclosed Reports\n"
    for r in reports:
        text += f"- {r['title']} → https://bugcrowd.com{r['url']}\n"
    return text + "\n"

# 3. Medium Writeups Tagged "bug-bounty"
def fetch_medium():
    url = "https://medium.com/tag/bug-bounty/latest"
    r = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(r.text, "html.parser")
    links = soup.find_all("a", href=True)[:10]

    text = "## Medium Bug Bounty Writeups\n"
    for link in links:
        if "medium.com" in link["href"]:
            text += f"- {link.text.strip()} → {link['href']}\n"
    return text + "\n"

# 4. GitHub PoCs for Recently Published CVEs
def fetch_github_pocs():
    query = "CVE+exploit+PoC"
    url = f"https://api.github.com/search/repositories?q={query}&sort=stars&order=desc&per_page=10"
    r = requests.get(url, headers=HEADERS).json()
    items = r.get("items", [])

    text = "## Latest CVE PoCs on GitHub\n"
    for repo in items:
        text += f"- {repo['full_name']} → {repo['html_url']} ⭐ {repo['stargazers_count']}\n"
    return text + "\n"

def main():
    os.makedirs(REPORTS_DIR, exist_ok=True)
    today = datetime.date.today().strftime("%Y-%m-%d")
    filename = f"{REPORTS_DIR}/{today}.md"

    content = write_header(today)
    content += fetch_hackerone()
    content += fetch_bugcrowd()
    content += fetch_medium()
    content += fetch_github_pocs()

    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"✅ Daily report saved → {filename}")

if __name__ == "__main__":
    main()
