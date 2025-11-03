from flask import Flask, render_template_string
import json, time, urllib.request as r, datetime as dt, os

app = Flask(__name__)

pairs = ["BTCUSDT","ETHUSDT","SOLUSDT","BNBUSDT","XRPUSDT","DOGEUSDT","ADAUSDT","HEMIUSDT","WIFUSDT","PEPEUSDT","BONKUSDT","FLOKIUSDT","SHIBUSDT","1000RATSUSDT","TURBOUSDT","BRETTUSDT","POPCATUSDT","MEWUSDT","JUPUSDT","PYTHUSDT"]

def get(s, tf):
    time.sleep(0.3)
    url = f"https://fapi.binance.com/fapi/v1/klines?symbol={s}&interval={tf}&limit=3"
    req = r.Request(url, headers={"User-Agent":"Mozilla/5.0"})
    return json.loads(r.urlopen(req).read())

def body(c): return round(abs(float(c[4])-float(c[1]))/float(c[1])*100, 2)
def vol(c): return int(float(c[5]))

@app.route('/')
def home():
    now = dt.datetime.utcnow()
    mins = (30 - now.minute % 30) % 30
    secs = 60 - now.second

    out = "<body bgcolor=#000 text=#0f0 style='font:22px monospace'>"
    out += "<h1>30-MIN SCREENER</h1>"
    out += f"<h2 id=t>Next candle: {mins:02d}:{secs:02d} mm:ss</h2><pre>"
    out += "PAIR       BODY   CURR VOL   PREV VOL   RATIO\n"
    out += "─" * 48 + "\n"

    hits = []
    for s in pairs:
        try:
            d = get(s, "30m")
            cur, pre = d[-2], d[-3]
            if float(cur[4]) > float(cur[1]) and body(cur) >= 2:
                ratio = round(vol(cur)/vol(pre), 2) if vol(pre) else 999
                hits.append((s, body(cur), vol(cur)//1_000_000, vol(pre)//1_000_000, ratio))
        except: pass

    hits.sort(key=lambda x: x[4], reverse=True)
    for p,b,cv,pv,r in hits:
        out += f"{p:10} {b:4}%   {cv:4}M     {pv:4}M     {r:5}x\n"
    if not hits:
        out += "No GREEN ≥2% candle in last 30 min\n"

    out += "\nRefresh every <input id=s value=60 size=2> sec "
    out += "<button onclick='clearInterval(i);i=setInterval(go,s.value*1000);go()'>GO</button>"
    out += "<script>"
    out += "function go(){location.reload()}"
    out += f"let c={{mm:{mins},ss:{secs}}};"
    out += "setInterval(()=>{"
    out += "  if(--c.ss<0){c.ss=59; if(c.mm>0) c.mm--}"
    out += "  t.innerText=`Next candle: ${String(c.mm).padStart(2,'0')}:${String(c.ss).padStart(2,'0')} mm:ss`"
    out += "},1000);"
    out += "let i=setInterval(go,60000);"
    out += "</script></pre></body>"
    return out

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
