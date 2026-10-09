"""Compte, pour chaque langage, le nombre de dépôts où il est le langage principal,
puis met à jour la section entre <!--LANGS:START--> et <!--LANGS:END--> du README."""
import json
import os
import re
import urllib.request
from collections import Counter

USER = os.environ["GH_USER"]
TOKEN = os.environ.get("GITHUB_TOKEN")
TOP_N = 8  # nombre de langages affichés


def fetch_repos():
    repos, page = [], 1
    while True:
        headers = {"Accept": "application/vnd.github+json"}
        if TOKEN:
            headers["Authorization"] = f"Bearer {TOKEN}"
        url = f"https://api.github.com/users/{USER}/repos?per_page=100&page={page}&type=owner"
        with urllib.request.urlopen(urllib.request.Request(url, headers=headers)) as r:
            data = json.load(r)
        if not data:
            return repos
        repos += data
        page += 1


repos = [r for r in fetch_repos() if not r["fork"] and r["name"] != USER]
counts = Counter(r["language"] for r in repos if r["language"])
total = sum(counts.values())
top = counts.most_common(TOP_N)
biggest = top[0][1] if top else 1

lines = ["| Langage | Projets | |", "|---|---:|---|"]
for lang, n in top:
    bar = "█" * max(1, round(10 * n / biggest))
    lines.append(f"| {lang} | {n} ({round(100 * n / total)} %) | {bar} |")

stars = sum(r["stargazers_count"] for r in repos)
lines.append("")
lines.append(f"{len(repos)} projets publics · ⭐ {stars} étoiles au total")
block = "\n".join(lines)

with open("README.md", encoding="utf-8") as f:
    readme = f.read()
readme = re.sub(
    r"(<!--LANGS:START-->).*?(<!--LANGS:END-->)",
    lambda m: f"{m.group(1)}\n{block}\n{m.group(2)}",
    readme,
    flags=re.DOTALL,
)
with open("README.md", "w", encoding="utf-8") as f:
    f.write(readme)
