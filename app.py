from flask import Flask, send_from_directory
import os, json, time, urllib.request as r, datetime as dt

app = Flask(__name__, static_folder='.')

@app.route('/signals.txt')
def signals():
    return send_from_directory('.', 'signals.txt')

@app.route('/')
def home():
    return """
    <body bgcolor=#000 text=#0f0><pre style="font:22px monospace">
    LIVE BINANCE SCREENER
    <pre id=s></pre>
    <script>
    setInterval(()=>{fetch('/signals.txt?'+Date.now()).then(r=>r.text()).then(t=>s.innerText=t)}, 25000);
    fetch('/signals.txt').then(r=>r.text()).then(t=>s.innerText=t);
    </script>
    """

# ----------------- SCANNER (runs every minute) -----------------
VOL_MULT = 3.0   # ← change to 5, 10, 50 anytime

def get(s,tf):
    time.sleep(0.6)
    url = f"https://fapi.binance.com/fapi/v1/klines?symbol={s}&interval={tf}&limit=3"
    req = r.Request(url, headers={"User-Agent":"Mozilla/5.0"})
    return json.loads(r.urlopen(req).read())

pairs = ["BTCUSDT","ETHUSDT","SOLUSDT","XRPUSDT","BNBUSDT","DOGEUSDT","ADAUSDT","HEMIUSDT"]

def body(c): return round(abs(float(c[4])-float(c[1]))/float(c[1])*100,1)
def vol(c): return int(float(c[5]))

def save(txt):
    with open('signals.txt','a') as f:
        f.write(dt.datetime.utcnow().strftime("%H:%M") + "  " + txt + "\n")

def scan(tf, mult, name):
    found = False
    for s in pairs:
        try:
            d = get(s,tf); p,n = d[-2],d[-1]
            if float(n[4])>float(n[1])>float(p[4])>float(p[1]) and vol(n)>mult*vol(p):
                line = f"{s:10} ● BULLISH ENGULFING {tf.upper()}\\n   Prev: {body(p):4}% | {vol(p)//1e6:3}M\\n   Now : {body(n):4}% | {vol(n)//1e6:3}M ({vol(n)/vol(p):.1f}x)"
                print(line); save(line.replace('\\n','\n')); found = True
        except: pass
    if not found: save(f"No {name} signals yet")

if __name__ == "__main__":
    now = dt.datetime.utcnow()
    if now.minute in [1,31]:
        scan("30m", VOL_MULT, "30-min")
    if now.minute == 1 and now.hour % 4 == 0:
        scan("4h", VOL_MULT*0.4, "4-hour")
    else:
        open('signals.txt','a').write(f"{now.strftime('%H:%M')}  Waiting for candle…\\n")
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
