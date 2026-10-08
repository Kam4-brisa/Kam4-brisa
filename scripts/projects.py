"""Gera assets/projects-{dark,light}.svg: cards dos projetos com borda animada."""
PROJECTS = [
    # (nome, rótulo, descrição, tags, largura em colunas: 2 = linha inteira)
    ("Kana Sprint", "código aberto", "Japonês em sessões de 2 minutos, pensado para quem tem TDAH.", ["JavaScript", "Vite", "Vitest"], 2),
    ("Pumpo", "código privado", "Plataforma web com área do aluno, rotas e painel.", ["Python", "Flask", "Docker"], 1),
    ("Hermetico", "código privado", "Gera sites e landing pages por nicho.", ["Python", "Next.js", "Tailwind"], 1),
]
T = {"dark": dict(bg="#09090b", ln="#27272a", title="#fafafa", fg="#a1a1aa", acc="#34d399", ghost="#18181b"),
     "light": dict(bg="#fafafa", ln="#e4e4e7", title="#18181b", fg="#52525b", acc="#059669", ghost="#f0f0f2")}
W, H, GAP = 1200, 238, 24
SPLIT = 700  # largura do card da esquerda na linha de dois


def card(x, y, w, p, t, delay):
    name, label, desc, tags, _ = p
    open_src = label == "código aberto"
    out = [f'<rect x="{x+1}" y="{y+1}" width="{w-2}" height="{H}" rx="16" fill="{t["bg"]}" stroke="{t["ln"]}"/>']
    if open_src:  # kana grandes ao fundo, só no projeto aberto
        out.append(f'<text x="{x+w-40}" y="{y+200}" text-anchor="end" class="j" font-size="150" font-weight="700" fill="{t["ghost"]}">かな</text>')
    out.append(f'<rect class="bm" style="animation-delay:{delay}s" x="{x+1}" y="{y+1}" width="{w-2}" height="{H}" rx="16" fill="none" stroke="{t["acc"]}" stroke-width="1.5" pathLength="100" stroke-dasharray="10 90"/>')
    out.append(f'<text x="{x+33}" y="{y+70}" class="f" font-size="32" font-weight="700" letter-spacing="-1" fill="{t["title"]}">{name}</text>')
    out.append(f'<text x="{x+w-31}" y="{y+66}" text-anchor="end" class="m" font-size="13" fill="{t["acc"] if open_src else t["fg"]}">{label}</text>')
    out.append(f'<text x="{x+33}" y="{y+112}" class="f" font-size="18" fill="{t["fg"]}">{desc}</text>')
    tx = x + 33
    for tag in tags:
        tw = 25 + 8 * len(tag)
        out.append(f'<rect x="{tx}" y="{y+182}" width="{tw}" height="30" rx="8" fill="{t["bg"]}" stroke="{t["ln"]}"/>'
                   f'<text x="{tx+12}" y="{y+202}" class="m" font-size="13" fill="{t["fg"]}">{tag}</text>')
        tx += tw + 8
    return "".join(out)


for n, t in T.items():
    cards, y, row, delay = [], 0, [], 0
    for p in PROJECTS:
        if p[4] == 2:
            cards.append(card(0, y, W, p, t, delay)); y += H + GAP; delay -= 2
        else:
            row.append(p)
            if len(row) == 2:
                cards.append(card(0, y, SPLIT + 1, row[0], t, delay)); delay -= 2
                cards.append(card(SPLIT + 20, y, W - SPLIT - 20, row[1], t, delay)); delay -= 2
                y += H + GAP; row = []
    total = y - GAP + 2
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{total}" viewBox="0 0 {W} {total}">
<style>
.bm{{animation:b 6s linear infinite}}
@keyframes b{{from{{stroke-dashoffset:100}}to{{stroke-dashoffset:0}}}}
.f{{font-family:ui-sans-serif,-apple-system,"Segoe UI",Helvetica,Arial,sans-serif}}
.m{{font-family:ui-monospace,SFMono-Regular,Consolas,monospace}}
.j{{font-family:"Hiragino Sans","Yu Gothic","Noto Sans JP","Meiryo",sans-serif}}
@media (prefers-reduced-motion: reduce){{*{{animation:none!important}}}}
</style>
{chr(10).join(cards)}
</svg>
'''
    open(f"assets/projects-{n}.svg", "w", encoding="utf8").write(svg)
print("ok")
