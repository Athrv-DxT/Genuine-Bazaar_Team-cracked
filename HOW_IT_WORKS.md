# How Retail Cortex Works - Automatic Alert System

## 🎯 Overview

Retail Cortex automatically monitors weather, trends, festivals, and events to alert you about demand spikes for your products. Here's how it works:

---

## 🌧️ Automatic Rain Detection for Umbrellas

### How It Works:

1. **Every 30 minutes**, the system:
   - Checks weather forecast for your city
   - Looks for rain predicted in next 3-6 hours
   - If rain probability > 70% → **ALERT TRIGGERED!**

2. **If you track "umbrella" keyword:**
   - You get immediate alert: "Rain in 3 hours - Stock up on umbrellas!"
   - Shows predicted impact (revenue opportunity)
   - High priority alert

3. **If you DON'T track "umbrella" yet:**
   - System suggests: "Rain predicted - Consider adding 'umbrella' to your keywords!"
   - Helps you discover new opportunities

### Example Alert:
```
🌧️ Rain Alert: Umbrella Demand Spike Expected
Rain predicted in 3 hours (85% probability). 
Expected spike in umbrella demand. Stock up now!

Predicted Impact: ₹42K
Confidence: 85%
```

---

## 📊 Data Sources

### 1. Weather Data (OpenWeatherMap)
- **What it provides:** Current weather + 5-day forecast
- **How we use it:**
  - Rain probability for next 24 hours
  - Temperature spikes
  - Weather conditions
- **Update frequency:** Every 30 minutes
- **Cost:** FREE (60 calls/min)

### 2. Search Trends (Google Trends)
- **What it provides:** Search interest scores (0-100)
- **How we use it:**
  - Detect trending keywords
  - Identify demand spikes
  - Social media trend detection
- **Update frequency:** Real-time when generating alerts
- **Cost:** FREE (no API key needed)

### 3. Festivals/Holidays (Calendarific)
- **What it provides:** Upcoming holidays and festivals
- **How we use it:**
  - Diwali, Holi, Christmas, etc.
  - Festival-related product alerts
  - Promotion timing windows
- **Update frequency:** Daily
- **Cost:** FREE (1,000 requests/month)

---

## 🔄 Automatic Alert Generation

### Background Job (Runs Every 30 Minutes)

```python
1. Get all active users
2. For each user:
   a. Check weather for their city
   b. Check their tracked keywords
   c. Detect demand peaks:
      - Rain → Umbrella alerts
      - Hot weather → Cold drink alerts
      - Trending keywords → Social trend alerts
      - Upcoming festivals → Festival alerts
   d. Find promotion windows:
      - Sentiment peaks
      - Festival priming days
      - High footfall hours
3. Create alerts in database
4. Users see alerts on dashboard
```

### Manual Trigger
- Click "Generate New Alerts" button
- Immediately checks for new opportunities
- Useful for testing or on-demand checks

---

## 🎯 Alert Types

### 1. Weather Opportunities
- **Rain alerts:** Umbrella, raincoat, waterproof items
- **Hot weather:** Cold drinks, ice cream, fans, AC
- **Cold weather:** Sweaters, heaters, winter wear

### 2. Social Trends
- **Trending keywords:** High search interest detected
- **Social media spikes:** Viral product mentions

### 3. Festival Boosts
- **Diwali:** Lights, candles, sweets, gifts
- **Holi:** Colors, water guns, clothes
- **Christmas:** Gifts, decorations, toys

### 4. Promotion Timing
- **Sentiment peaks:** Best time to run promotions
- **Festival priming:** 3-7 days before festival
- **High footfall:** Peak shopping hours

### 5. Competitor Opportunities
- **Stockouts:** Competitor out of stock
- **Inactivity windows:** Less competition

---

## 📈 How to Use It

### Step 1: Set Up API Keys
1. Get OpenWeatherMap API key (FREE)
2. Get Calendarific API key (FREE)
3. Add to `.env` file
4. Restart backend

### Step 2: Configure Your Account
1. Register/Login
2. Set your location (city, state)
3. Select market categories (electronics, clothes, etc.)

### Step 3: Add Keywords
1. Go to "Keywords" page
2. Add products you sell:
   - "umbrella"
   - "cold drink"
   - "ice cream"
   - "sweater"
   - etc.

### Step 4: Get Automatic Alerts
1. System checks every 30 minutes
2. Alerts appear on dashboard
3. Click "Generate New Alerts" for immediate check

---

## 🔍 Example Scenarios

### Scenario 1: Rain Alert
```
Time: 2:00 PM
Weather: Rain predicted at 5:00 PM (85% probability)
User tracks: "umbrella"

Alert Created:
"🌧️ Rain Alert: Umbrella Demand Spike Expected
Rain predicted in 3 hours (85% probability).
Expected spike in umbrella demand. Stock up now!"

Action: User increases umbrella stock, boosts visibility
Result: Sells 3x more umbrellas than usual
```

### Scenario 2: Festival Alert
```
Time: 10 days before Diwali
User tracks: "lights", "candles"

Alert Created:
"🎆 Diwali: Lights Demand Boost
Diwali is coming up in 10 days.
Expected boost in lights demand. Stock and promote now!"

Action: User stocks up on lights, runs promotion
Result: Captures festival demand spike
```

### Scenario 3: Trend Alert
```
Time: Keyword "skincare" trending on Google
User tracks: "skincare"

Alert Created:
"📈 Trending: Skincare on Social Media
Skincare is trending (score: 78/100).
Capitalize on this trend by increasing visibility!"

Action: User boosts skincare product visibility
Result: Higher conversion rate during trend
```

---

## ⚙️ Configuration

### Alert Check Interval
- Default: Every 30 minutes
- Configurable in `app/config.py`
- Change `alert_check_interval_minutes`

### Weather Forecast Window
- Default: 24 hours ahead
- Checks for rain in next 3-6 hours
- Configurable in `demand_detector.py`

### Rain Threshold
- Default: 70% probability
- Only alerts if rain_prob > 0.7
- Configurable in `_check_weather_demand()`

---

## 🚀 Best Practices

1. **Add relevant keywords:** The more keywords, the more alerts
2. **Set accurate location:** Weather alerts depend on your city
3. **Check alerts regularly:** Act on opportunities quickly
4. **Use API keys:** Without keys, some features won't work
5. **Monitor trends:** Add trending keywords to your list

---

## 📊 Monitoring

- Check dashboard for new alerts
- Filter alerts by type/priority
- View predicted impact scores
- Track which alerts you acted on

---

## 🆘 Troubleshooting

**No rain alerts?**
- Check OpenWeatherMap API key
- Verify city location
- Add "umbrella" keyword
- Check if rain is actually predicted

**No trend alerts?**
- Google Trends works automatically
- Keyword might not be trending
- Try different keywords

**Alerts not generating?**
- Check backend logs
- Verify API keys are set
- Check scheduler is running
- Try manual "Generate Alerts" button

---

## 💡 Tips

1. **Start with weather alerts:** Easiest to set up and most reliable
2. **Add seasonal keywords:** Umbrella (monsoon), sweater (winter), etc.
3. **Monitor festivals:** Add festival-related keywords before major festivals
4. **Act quickly:** Alerts are time-sensitive
5. **Track results:** See which alerts led to sales

---

**The system works automatically once set up! Just add your keywords and let it monitor for opportunities 24/7.**


