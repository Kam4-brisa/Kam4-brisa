"""Gera uma cobrinha que percorre o gráfico de contribuições e cresce a cada dia com commit que come."""
import json, os, sys, urllib.request

USER = os.environ.get("GH_USER", "Kam4-brisa")
QUERY = """query($u:String!){user(login:$u){contributionsCollection{contributionCalendar{
weeks{contributionDays{contributionCount weekday}}}}}}"""

THEMES = {
    "github-snake.svg": dict(empty="#ebedf0", lv=["#a7f3d0", "#34d399", "#059669", "#065f46"], snake="#3f3f46", head="#059669"),
    "github-snake-dark.svg": dict(empty="#18181b", lv=["#064e3b", "#047857", "#10b981", "#34d399"], snake="#d4d4d8", head="#34d399"),
}
CELL, GAP, STEP = 12, 3, 0.07  # px, px, segundos por casa
PAUSE = 2.5  # segundos parada no fim, com a cobra inteira


def fetch():
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": QUERY, "variables": {"u": USER}}).encode(),
        headers={"Authorization": f"bearer {os.environ['GITHUB_TOKEN']}"},
    )
    data = json.load(urllib.request.urlopen(req))
    weeks = data["data"]["user"]["contributionsCollection"]["contributionCalendar"]["weeks"]
    return [[(d["weekday"], d["contributionCount"]) for d in w["contributionDays"]] for w in weeks]


def level(c, mx):
    if c == 0:
        return -1
    return min(3, int(4 * c / (mx + 1)))


def build(weeks, t):
    mx = max((c for w in weeks for _, c in w), default=1) or 1
    # percurso em zigue-zague: coluna descendo, próxima subindo
    path = []
    for x, w in enumerate(weeks):
        days = sorted(w)
        if x % 2:
            days = days[::-1]
        path += [(x, d, c) for d, c in days]
    n = len(path)
    T = n * STEP + PAUSE
    px = lambda v: 4 + v * (CELL + GAP)
    W, H = px(len(weeks)) + 4, px(7) + 4

    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">']
    out.append(f'<rect width="{W}" height="{H}" fill="none"/>')
    eats = []
    for i, (x, y, c) in enumerate(path):
        lv = level(c, mx)
        out.append(f'<rect x="{px(x)}" y="{px(y)}" width="{CELL}" height="{CELL}" rx="3" fill="{t["empty"]}"/>')
        if lv >= 0:
            k = i * STEP / T
            out.append(
                f'<rect x="{px(x)}" y="{px(y)}" width="{CELL}" height="{CELL}" rx="3" fill="{t["lv"][lv]}">'
                f'<animate attributeName="opacity" values="1;1;0;0" keyTimes="0;{k:.5f};{k:.5f};1" dur="{T:.2f}s" repeatCount="indefinite"/></rect>'
            )
            eats.append(i)

    pts = " ".join(f"{px(x) + CELL / 2},{px(y) + CELL / 2}" for x, y, _ in path)
    out.append(f'<path id="p" d="M{pts.replace(" ", " L")}" fill="none"/>')
    run = (n - 1) * STEP / T  # fração do ciclo em movimento
    kp = f'keyPoints="0;1;1" keyTimes="0;{run:.5f};1" calcMode="linear"'

    # cauda: segmento j nasce quando a cabeça come a j-ésima comida e segue j casas atrás
    for j in reversed(range(1, len(eats) + 1)):
        born = eats[j - 1] * STEP / T
        s = CELL - 4
        out.append(
            f'<rect x="{-s / 2}" y="{-s / 2}" width="{s}" height="{s}" rx="3" fill="{t["snake"]}" opacity="0">'
            f'<animate attributeName="opacity" values="0;0;1;1" keyTimes="0;{born:.5f};{born:.5f};1" dur="{T:.2f}s" repeatCount="indefinite"/>'
            f'<animateMotion dur="{T:.2f}s" begin="{j * STEP:.2f}s" repeatCount="indefinite" {kp}><mpath href="#p"/></animateMotion></rect>'
        )
    out.append(
        f'<rect x="{-CELL / 2}" y="{-CELL / 2}" width="{CELL}" height="{CELL}" rx="4" fill="{t["head"]}">'
        f'<animateMotion dur="{T:.2f}s" repeatCount="indefinite" {kp}><mpath href="#p"/></animateMotion></rect>'
    )
    out.append("</svg>")
    return "\n".join(out)


if __name__ == "__main__":
    weeks = fetch()
    os.makedirs("dist", exist_ok=True)
    for name, t in THEMES.items():
        open(os.path.join("dist", name), "w").write(build(weeks, t))
    print("ok", sum(1 for w in weeks for _, c in w if c), "dias com contribuição")
