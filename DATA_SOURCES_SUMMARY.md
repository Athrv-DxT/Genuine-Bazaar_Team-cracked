# 📊 Data Sources Summary - Where We Get Our Data

## ✅ Currently Implemented

### 1. **Weather Data** → OpenWeatherMap API
- **What:** Current weather + 5-day forecast
- **Used for:** Rain alerts, temperature spikes, weather-based demand
- **Cost:** FREE (60 calls/min, 1M/month)
- **Setup:** Get API key from openweathermap.org
- **Status:** ✅ Fully implemented

### 2. **Search Trends** → Google Trends (pytrends)
- **What:** Search interest scores (0-100)
- **Used for:** Trending keywords, social media trends
- **Cost:** FREE (no API key needed)
- **Setup:** Works automatically
- **Status:** ✅ Fully implemented

### 3. **Festivals/Holidays** → Calendarific API
- **What:** Upcoming holidays and festivals
- **Used for:** Festival-related product alerts, promotion timing
- **Cost:** FREE (1,000 requests/month)
- **Setup:** Get API key from calendarific.com
- **Status:** ✅ Fully implemented

---

## 🔄 How Automatic Rain Detection Works

### Step-by-Step Process:

1. **Every 30 minutes**, background job runs:
   ```
   → Get all active users
   → For each user:
      → Get their city location
      → Call OpenWeatherMap API for weather forecast
      → Check if rain predicted in next 3-6 hours
      → If rain_probability > 70%:
         → Check if user tracks "umbrella" keyword
         → If yes: Create HIGH priority alert
         → If no: Suggest adding "umbrella" keyword
   ```

2. **Alert Created:**
   ```
   Title: "🌧️ Rain Alert: Umbrella Demand Spike Expected"
   Message: "Rain predicted in 3 hours (85% probability). 
            Expected spike in umbrella demand. Stock up now!"
   Predicted Impact: ₹42K
   Confidence: 85%
   ```

3. **User Sees Alert:**
   - On dashboard
   - In alerts page
   - Can filter by type/priority

---

## 📈 Data Flow Diagram

```
┌─────────────────┐
│  OpenWeatherMap │
│     API         │
└────────┬────────┘
         │ Weather Forecast
         ▼
┌─────────────────┐
│ Weather Service │
│  (Every 30 min) │
└────────┬────────┘
         │ Processed Data
         ▼
┌─────────────────┐
│ Demand Detector │
│  (Check Rain)   │
└────────┬────────┘
         │ Alerts Generated
         ▼
┌─────────────────┐
│  Alert Database │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  User Dashboard │
│  (See Alerts)   │
└─────────────────┘
```

---

## 🎯 What You Need to Do

### Minimum Setup (Just Rain Alerts):
1. ✅ Get OpenWeatherMap API key (FREE)
2. ✅ Add to `.env` file
3. ✅ Set your city location in account
4. ✅ Add "umbrella" keyword
5. ✅ Done! Alerts work automatically

### Full Setup (All Features):
1. ✅ OpenWeatherMap API key (weather)
2. ✅ Calendarific API key (festivals)
3. ✅ Google Trends (automatic, no key needed)
4. ✅ Optional: Twitter API (social trends)

---

## 💰 Cost Breakdown

| Service | Cost | Limits | Status |
|---------|------|--------|--------|
| OpenWeatherMap | FREE | 60/min, 1M/month | ✅ Required |
| Google Trends | FREE | Unlimited | ✅ Automatic |
| Calendarific | FREE | 1,000/month | ✅ Optional |
| Twitter | FREE | Limited | ⚠️ Optional |

**Total Monthly Cost: $0** 🎉

---

## 🔧 Configuration

### Alert Check Frequency
- Default: Every 30 minutes
- Change in: `app/config.py` → `alert_check_interval_minutes`

### Rain Detection Threshold
- Default: 70% probability
- Change in: `app/services/demand_detector.py` → `_check_weather_demand()`

### Forecast Window
- Default: 24 hours ahead
- Checks: Next 3-6 hours for rain alerts
- Change in: `get_forecast(city, hours_ahead=24)`

---

## 📝 Quick Reference

### To Get Rain Alerts:
1. Get OpenWeatherMap API key
2. Add to `.env`: `OPENWEATHER_API_KEY=your_key`
3. Set city in your account
4. Add "umbrella" keyword
5. Wait for alerts (or click "Generate Alerts")

### To Get Festival Alerts:
1. Get Calendarific API key
2. Add to `.env`: `CALENDARIFIC_API_KEY=your_key`
3. Add festival-related keywords (lights, candles, etc.)
4. Alerts appear before festivals

### To Get Trend Alerts:
1. Add keywords you want to track
2. System automatically checks Google Trends
3. Alerts when keywords start trending

---

## 🆘 Troubleshooting

**No rain alerts?**
- ✅ Check OpenWeatherMap API key is set
- ✅ Verify city location is correct
- ✅ Make sure "umbrella" keyword is added
- ✅ Check if rain is actually predicted
- ✅ Check backend logs for API errors

**API rate limits?**
- OpenWeatherMap: 60 calls/min (plenty for our use)
- Calendarific: 1,000/month (enough for daily checks)
- Google Trends: No limits

**Missing data?**
- Check API keys are valid
- Verify email verification (OpenWeatherMap)
- Check backend logs for errors
- Test API keys manually

---

## 📚 Documentation Files

- `API_KEYS_SETUP.md` - Detailed API key setup
- `HOW_IT_WORKS.md` - Complete system explanation
- `QUICK_SETUP_GUIDE.md` - 5-minute setup guide

---

**The system is ready! Just add your API keys and start getting automatic alerts!** 🚀


