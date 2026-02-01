import pandas as pd
import requests
import time

# --- मास्टर कॉन्फिगरेशन ---
stock_master = {
    "GC=F": "Gold", "CL=F": "Crude Oil", "BTC-USD": "Bitcoin", "ETH-USD": "Ethereum",
    "RELIANCE.NS": "Reliance", "HDFCBANK.NS": "HDFC Bank", "TCS.NS": "TCS", "TATAMOTORS.NS": "Tata Motors",
    "NVDA": "Nvidia", "AAPL": "Apple", "TSLA": "Tesla", "GOOGL": "Google", "MSFT": "Microsoft",
    "6758.T": "Sony", "7203.T": "Toyota"
}

global_indices = {"^NSEI": "Nifty 50", "^GSPC": "S&P 500", "^N225": "Nikkei 225", "^FTSE": "FTSE 100"}

def get_data(symbol, days="300d"):
    try:
        url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?range={days}&interval=1d"
        headers = {'User-Agent': 'Mozilla/5.0'}
        res = requests.get(url, headers=headers, timeout=15).json()
        result = res['chart']['result'][0]
        df = pd.DataFrame({
            'open': result['indicators']['quote'][0]['open'],
            'high': result['indicators']['quote'][0]['high'],
            'low': result['indicators']['quote'][0]['low'],
            'close': result['indicators']['quote'][0]['close'],
            'volume': result['indicators']['quote'][0]['volume']
        }).dropna()
        return df
    except: return pd.DataFrame()

def analyze_pro(df):
    if len(df) < 200: return None
    curr_p = df['close'].iloc[-1]
    
    # १. RSI
    delta = df['close'].diff()
    up = delta.clip(lower=0).rolling(14).mean()
    down = delta.clip(upper=0).abs().rolling(14).mean()
    rsi = round(100 - (100 / (1 + (up / down).iloc[-1])), 2)
    
    # २. Volume
    avg_vol = df['volume'].tail(20).mean()
    vol_boost = df['volume'].iloc[-1] > (avg_vol * 1.2)
    
    # ३. Levels (Support & Resistance)
    support = round(df['low'].tail(15).min(), 2)
    resistance = round(df['high'].tail(15).max(), 2)
    
    # ४. Stop-Loss (Support च्या थोडं खाली किंवा २% सेफ्टी मार्जिन)
    stop_loss = round(min(support, curr_p * 0.97), 2)
    
    # ५. Trend & Performance
    sma200 = df['close'].rolling(200).mean().iloc[-1]
    trend = "BULLISH" if curr_p > sma200 else "BEARISH"
    is_bullish_candle = curr_p > df['open'].iloc[-1]
    perf_10d = round(((curr_p - df['close'].iloc[-11]) / df['close'].iloc[-11]) * 100, 2) if len(df) > 11 else 0
    
    return {
        'price': round(curr_p, 2), 'rsi': rsi, 'trend': trend, 
        'bullish': is_bullish_candle, 'vol_boost': vol_boost,
        'support': support, 'resistance': resistance, 'stop_loss': stop_loss,
        'perf_10d': f"{perf_10d}%"
    }

def run_ultimate_engine():
    print(f"🌟 राही 'अल्टीमेट' इंजिन V4.0 (PRO) - सक्रिय 🌟\n")
    
    mood_score = 0
    for sym in global_indices.keys():
        df = get_data(sym, "5d")
        if not df.empty and len(df) >= 2:
            if df['close'].iloc[-1] > df['close'].iloc[-2]: mood_score += 1
    market_mood = "🔥 POSITIVE" if mood_score >= 2 else "⚠️ CAUTIOUS"
    
    results = []
    for sym, name in stock_master.items():
        df = get_data(sym)
        data = analyze_pro(df)
        if data:
            score = 0
            if data['rsi'] < 45: score += 1
            if data['trend'] == "BULLISH": score += 1
            if data['bullish']: score += 1
            if data['vol_boost']: score += 1
            if market_mood == "🔥 POSITIVE": score += 1
            results.append({'sym': sym, 'name': name, 'score': score, **data})
        time.sleep(0.1)

    sorted_res = sorted(results, key=lambda x: x['score'], reverse=True)
    print("═"*75 + f"\n🏆 राही '१ १००% परफेक्ट' रिपोर्ट (मूड: {market_mood}) 🏆\n" + "═"*75)

    for i, r in enumerate(sorted_res):
        signal = "🚀 STRONG BUY" if r['score'] >= 4 else "🔎 WATCH" if r['score'] >= 2 else "😴 AVOID"
        print(f"[{i+1}] {r['name']} ({r['sym']}) -> {signal} (Score: {r['score']}/5)")
        print(f"💰 Price: {r['price']} | 🛡️ Stop-Loss: {r['stop_loss']}")
        print(f"🎯 Support: {r['support']} | 🏁 Target: {r['resistance']}")
        print(f"📊 RSI: {r['rsi']} | Trend: {r['trend']} | Vol: {'High 🔥' if r['vol_boost'] else 'Normal'}")
        print("─" * 70)

if __name__ == "__main__":
    run_ultimate_engine()
  
