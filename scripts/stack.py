"""Gera assets/stack-{dark,light}.svg: duas faixas de logos rolando (marquee). Ícones do Simple Icons."""
import re, urllib.request
ROWS = [
    [("python", "Python"), ("flask", "Flask"), ("postgresql", "PostgreSQL"), ("gunicorn", "Gunicorn"), ("pytest", "pytest"), ("docker", "Docker"), ("linux", "Linux")],
    [("nextdotjs", "Next.js"), ("react", "React"), ("typescript", "TypeScript"), ("javascript", "JavaScript"), ("tailwindcss", "Tailwind"), ("vite", "Vite"), ("framer", "Framer Motion"), ("git", "Git"), ("vercel", "Vercel")],
]
T = {"dark": dict(bg="#09090b", ln="#27272a", fg="#e4e4e7", ic="#a1a1aa"),
     "light": dict(bg="#fafafa", ln="#e4e4e7", fg="#27272a", ic="#52525b")}
paths = {}
for row in ROWS:
    for slug, _ in row:
        svg = urllib.request.urlopen(f"https://cdn.jsdelivr.net/npm/simple-icons@13/icons/{slug}.svg").read().decode()
        paths[slug] = re.search(r' d="([^"]+)"', svg).group(1)

def chips(row, t):
    out, x = [], 0
    for slug, name in row:
        w = 64 + len(name) * 9.4
        out.append(f'<g transform="translate({x:.0f},0)"><rect width="{w:.0f}" height="56" rx="12" fill="{t["bg"]}" stroke="{t["ln"]}"/>'
                   f'<g transform="translate(20,16) scale(1)"><path d="{paths[slug]}" fill="{t["ic"]}" transform="scale(1)"/></g>'
                   f'<text x="52" y="34" class="f" font-size="16" font-weight="500" fill="{t["fg"]}">{name}</text></g>')
        x += w + 12
    return "".join(out), x

for n, t in T.items():
    rows, kf = [], []
    for i, row in enumerate(ROWS):
        body, wid = chips(row, t)
        a, b = (0, -wid) if i == 0 else (-wid, 0)
        kf.append(f"@keyframes k{i}{{from{{transform:translateX({a:.0f}px)}}to{{transform:translateX({b:.0f}px)}}}}.k{i}{{animation:k{i} 45s linear infinite}}")
        rows.append(f'<g transform="translate(0,{24 + i * 76})"><g class="k{i}">'
                    f'{body}<g transform="translate({wid:.0f},0)">{body}</g><g transform="translate({2*wid:.0f},0)">{body}</g></g></g>')
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="180" viewBox="0 0 1200 180">
<style>
.f{{font-family:ui-sans-serif,-apple-system,"Segoe UI",Helvetica,Arial,sans-serif}}
{"".join(kf)}
@media (prefers-reduced-motion: reduce){{*{{animation:none!important}}}}
</style>
<defs><linearGradient id="g"><stop offset="0" stop-color="#000"/><stop offset=".1" stop-color="#fff"/><stop offset=".9" stop-color="#fff"/><stop offset="1" stop-color="#000"/></linearGradient>
<mask id="m"><rect width="1200" height="180" fill="url(#g)"/></mask></defs>
<rect width="1200" height="180" rx="16" fill="{t["bg"]}" stroke="{t["ln"]}"/>
<g mask="url(#m)">{"".join(rows)}</g>
</svg>'''
    open(f"assets/stack-{n}.svg", "w", encoding="utf8").write(svg)
print("ok")
