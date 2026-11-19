#!/usr/bin/env python3
"""Actualiza el panel completo: estadísticas públicas de YouTube, historial, estado de la cola y contenido; sube todo a GitHub Pages.
Uso: python3 actualizar_todo.py (desde la carpeta del repo). Clave: ~/tools/claves.env (YT_API_KEY o YOUTUBE_API_KEY); nunca se sube."""
import datetime, json, os, re, subprocess, urllib.request
HOME = os.path.expanduser("~")
C = json.load(open("contenido.json"))
def clave():
    for l in open(f"{HOME}/tools/claves.env"):
        k, _, v = l.strip().partition("=")
        if k.replace("export ", "") in ("YT_API_KEY", "YOUTUBE_API_KEY"): return v.strip('"\'')
    raise SystemExit("Falta la clave en ~/tools/claves.env")
def api(rec, **p):
    p["key"] = clave()
    return json.load(urllib.request.urlopen(f"https://www.googleapis.com/youtube/v3/{rec}?" + "&".join(f"{k}={v}" for k, v in p.items()), timeout=30))
ahora = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="minutes")
c = api("channels", part="statistics", id=C["canal"])["items"][0]["statistics"]
v = api("videos", part="snippet,statistics", id=",".join(C["shorts"]))["items"]
orden = {i: n for n, i in enumerate(C["shorts"])}; v.sort(key=lambda x: orden.get(x["id"], 99))
shorts = [{"id": x["id"], "titulo": x["snippet"]["title"], "publicado": x["snippet"]["publishedAt"],
           "vistas": int(x["statistics"].get("viewCount", 0)), "likes": int(x["statistics"].get("likeCount", 0)),
           "comentarios": int(x["statistics"].get("commentCount", 0))} for x in v]
panel = {"actualizado": ahora, "suscriptores": int(c.get("subscriberCount", 0)), "vistas": int(c.get("viewCount", 0)),
         "videos": int(c.get("videoCount", 0)), "shorts": shorts}
json.dump(panel, open("panel.json", "w"), ensure_ascii=False, indent=1)
h = json.load(open("historial.json")) if os.path.exists("historial.json") else []
h.append({"t": ahora, "subs": panel["suscriptores"], "vistas": {s["id"]: s["vistas"] for s in shorts}})
json.dump(h[-1500:], open("historial.json", "w"), ensure_ascii=False)
cola = []
try:
    for l in open(f"{HOME}/tools/trabajo/cola.md", encoding="utf-8"):
        m = re.match(r"- \[([^\]]+)\] (\S+) \| ([^·]+)", l.strip())
        if m: cola.append({"estado": m.group(1), "id": m.group(2), "nota": m.group(3).strip()})
except OSError:
    pass
json.dump({"actualizado": ahora, "cola": cola}, open("cola.json", "w"), ensure_ascii=False, indent=1)
subprocess.run(["git", "add", "panel.json", "historial.json", "cola.json", "contenido.json", "index.html", "actualizar.py", "actualizar_todo.py"], check=True)
if subprocess.run(["git", "diff", "--cached", "--quiet"]).returncode:
    subprocess.run(["git", "commit", "-q", "-m", "Actualizar panel"], check=True)
    subprocess.run(["git", "push", "-q"], check=True)
print("Listo:", panel["suscriptores"], "subs,", sum(s["vistas"] for s in shorts), "vistas en Shorts")
