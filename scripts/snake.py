"""Cobrinha que vai atrás de cada dia com contribuição e cresce a cada um que come."""
import json, os, urllib.request
from collections import deque

USER = os.environ.get("GH_USER", "Kam4-brisa")
QUERY = """query($u:String!){user(login:$u){contributionsCollection{contributionCalendar{
weeks{contributionDays{contributionCount weekday}}}}}}"""
THEMES = {
    "github-snake.svg": dict(empty="#ebedf0", lv=["#a7f3d0", "#6ee7b7", "#34d399", "#059669"], snake="#18181b"),
    "github-snake-dark.svg": dict(empty="#161618", lv=["#064e3b", "#047857", "#059669", "#10b981"], snake="#ecfdf5"),
}
CELL, GAP = 11, 4
U = CELL + GAP
STEP = 0.09        # segundos por casa
BASE = 1.2 * U     # tamanho inicial
GROW = 0.35 * U    # quanto cresce por dia comido
PAUSE = 2.0


def fetch():
    req = urllib.request.Request("https://api.github.com/graphql",
        data=json.dumps({"query": QUERY, "variables": {"u": USER}}).encode(),
        headers={"Authorization": f"bearer {os.environ['GITHUB_TOKEN']}"})
    weeks = json.load(urllib.request.urlopen(req))["data"]["user"]["contributionsCollection"]["contributionCalendar"]["weeks"]
    return {(x, d["weekday"]): d["contributionCount"] for x, w in enumerate(weeks) for d in w["contributionDays"]}, len(weeks)


def route(grid, ncols):
    """Do canto esquerdo, vai sempre até o dia com contribuição mais próximo (BFS)."""
    food = {k for k, c in grid.items() if c}
    pos, path = (-1, 3), [(-1, 3)]
    while food:
        prev, q = {pos: None}, deque([pos])
        while q:
            c = q.popleft()
            if c in food:
                break
            for dx, dy in ((1, 0), (0, 1), (0, -1), (-1, 0)):
                n = (c[0] + dx, c[1] + dy)
                if -1 <= n[0] <= ncols and 0 <= n[1] < 7 and n not in prev:
                    prev[n] = c; q.append(n)
        seg = []
        while c != pos:
            seg.append(c); c = prev[c]
        path += seg[::-1]; pos = path[-1]; food.discard(pos)
    path += [(x, pos[1]) for x in range(pos[0] + 1, ncols + 3)]  # sai pela direita
    return path


def build(grid, ncols, t):
    mx = max(grid.values()) or 1
    path = route(grid, ncols)
    n = len(path)
    T = (n - 1) * STEP + PAUSE
    run = (n - 1) * STEP / T
    cx = lambda p: 4 + p[0] * U + CELL / 2 + U
    cy = lambda p: 4 + p[1] * U + CELL / 2
    W, H = 8 + (ncols + 2) * U, 8 + 7 * U

    eaten_at, seen = {}, set()
    lengths = []
    L = BASE
    for k, p in enumerate(path):
        if grid.get(p) and p not in seen:
            seen.add(p); eaten_at[p] = k; L += GROW
        lengths.append(L)

    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W:.0f}" height="{H:.0f}" viewBox="0 0 {W:.0f} {H:.0f}">',
           '<style>@media (prefers-reduced-motion: reduce){animate,animateMotion{display:none}}</style>']
    for (x, y), c in grid.items():
        r = f'x="{cx((x, y)) - CELL / 2}" y="{cy((x, y)) - CELL / 2}" width="{CELL}" height="{CELL}" rx="2.5"'
        out.append(f'<rect {r} fill="{t["empty"]}"/>')
        if c:
            lv = min(3, int(4 * c / (mx + 1)))
            k = eaten_at[(x, y)] * STEP / T
            out.append(f'<rect {r} fill="{t["lv"][lv]}"><animate attributeName="opacity" values="1;1;0;0;1" '
                       f'keyTimes="0;{k:.5f};{k + .004:.5f};.995;1" dur="{T:.2f}s" repeatCount="indefinite"/></rect>')

    d = "M" + " L".join(f"{cx(p):.1f},{cy(p):.1f}" for p in path)
    kt = ";".join(f"{k * STEP / T:.5f}" for k in range(n)) + ";1"
    dash = ";".join(f"{l:.1f} 99999" for l in lengths) + f";{lengths[-1]:.1f} 99999"
    off = ";".join(f"{lengths[k] - k * U:.1f}" for k in range(n)) + f";{lengths[-1] - (n - 1) * U:.1f}"
    out.append(f'<path d="{d}" fill="none" stroke="{t["snake"]}" stroke-width="8" stroke-linecap="round" stroke-linejoin="round" '
               f'stroke-dasharray="{BASE:.1f} 99999" stroke-dashoffset="{BASE:.1f}">'
               f'<animate attributeName="stroke-dasharray" values="{dash}" keyTimes="{kt}" dur="{T:.2f}s" repeatCount="indefinite"/>'
               f'<animate attributeName="stroke-dashoffset" values="{off}" keyTimes="{kt}" dur="{T:.2f}s" repeatCount="indefinite"/></path>')
    out.append("</svg>")
    return "\n".join(out)


if __name__ == "__main__":
    grid, ncols = fetch()
    os.makedirs("dist", exist_ok=True)
    for name, t in THEMES.items():
        open(os.path.join("dist", name), "w").write(build(grid, ncols, t))
    print("ok")
