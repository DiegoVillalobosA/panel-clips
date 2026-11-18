#!/usr/bin/env python3
"""Lee estadisticas publicas del canal (YouTube Data API) y sube panel.json a GitHub Pages.
Uso: python3 actualizar.py   (ejecutar desde la carpeta del repo del panel)
Clave: ~/tools/claves.env con una linea YT_API_KEY=... (la clave no se sube a ningun lado)."""
import json, os, subprocess, urllib.request, datetime
CANAL = "UC8pSHR5ccHJT31LVpWXVeQg"
SHORTS = ["FHrw8XSPrDA", "jq_b7-tSSKs", "2VjRiH67ygk", "GxaJVDJp60k"]
def clave():
    for l in open(os.path.expanduser("~/tools/claves.env")):
        k, _, v = l.strip().partition("=")
        if k.replace("export ", "") in ("YT_API_KEY", "YOUTUBE_API_KEY"): return v.strip('"\'')
    raise SystemExit("Falta YT_API_KEY en ~/tools/claves.env")
def api(rec, **p):
    p["key"] = clave()
    q = "&".join(f"{k}={v}" for k, v in p.items())
    return json.load(urllib.request.urlopen(f"https://www.googleapis.com/youtube/v3/{rec}?{q}"))
c = api("channels", part="statistics", id=CANAL)["items"][0]["statistics"]
v = api("videos", part="snippet,statistics", id=",".join(SHORTS))["items"]
out = {
  "actualizado": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="minutes"),
  "suscriptores": int(c.get("subscriberCount", 0)),
  "vistas": int(c.get("viewCount", 0)),
  "videos": int(c.get("videoCount", 0)),
  "shorts": [{"id": x["id"], "titulo": x["snippet"]["title"],
              "vistas": int(x["statistics"].get("viewCount", 0)),
              "likes": int(x["statistics"].get("likeCount", 0)),
              "comentarios": int(x["statistics"].get("commentCount", 0))} for x in v],
}
json.dump(out, open("panel.json", "w"), ensure_ascii=False, indent=1)
subprocess.run(["git", "add", "panel.json"], check=True)
if subprocess.run(["git", "diff", "--cached", "--quiet"]).returncode:
    subprocess.run(["git", "commit", "-m", "Actualizar estadisticas"], check=True)
    subprocess.run(["git", "push"], check=True)
print("Listo:", out["suscriptores"], "subs,", out["vistas"], "vistas")
