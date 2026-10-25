# 🌍 Personalized Travel Itinerary Planner (Capstone Project 4)

A complete, production-ready full-stack Travel SaaS web application built with **Python & Streamlit**. It optimizes journeys using **geographic clustering** to prevent transit backtracking, provides real-time **multi-currency budget telemetry** (Local, USD, INR), supports **dynamic single-slot activity swapping**, persists trips in a **zero-dependency simulated JSON database**, and generates publication-grade **offline PDF travel guides** complete with 24/7 emergency contact checklists.

---

## 🌟 Key Modules & Core Epics

### 1. Configuration & User Preferences (Epic 3)
- **Multi-LLM Provider Engine**: Seamlessly switch between **Google Gemini** (`gemini-2.5-flash`, `gemini-1.5-flash`), **Groq Cloud** (`llama-3.3-70b-versatile`, `llama-3.1-8b-instant`), or instant offline **Demo Mode** (no API keys required).
- **Secure Key Masking**: Masked password inputs with intelligent error recovery.
- **Granular Preference Form**: Destination search, trip duration (1-10 days), travel dates, budget tiers (Budget, Moderate, Luxury), travel party types (Solo, Couple, Family, Friends), travel pace, and specific interest tags.

### 2. Tab 1 - Smart Destination Recommender (Epic 3)
- Curated AI recommendation engine for travelers without a fixed destination.
- Matches travel mood/vibe, travel season/timeframe, and budget level against global travel trends.
- Displays match scores, highlights, flight/rail connectivity ratings, and daily cost projections.
- **1-Click Adoption**: "Plan Trip Now" adopts the city into preferences and switches directly to Tab 2 to build the itinerary.

### 3. Tab 2 - Day-by-Day Optimized Itinerary Generator (Epic 4)
- **Geographic Clustering Logic**: Eliminates cross-city zig-zagging by clustering each day into a single neighborhood or district (e.g. Higashiyama District in Kyoto, Le Marais in Paris).
- **Sequential Daily Time Slots**:
  - `Morning (09:00 - 12:00)`: Cultural anchors, scenic landmarks, avoiding peak crowds.
  - `Lunch (12:30 - 14:00)`: Authentic regional culinary recommendations with dietary tags.
  - `Afternoon (14:30 - 17:30)`: Leisure, artisan workshops, pedestrian promenades.
  - `Evening (18:30 - 22:00)`: Dining, sunset views, nighttime atmosphere.
- **Multi-Currency Budget Telemetry**:
  - Itemized estimated costs per activity.
  - Dynamic currency conversion between **Local Destination Currency**, **USD ($)**, and **Indian Rupee (₹)**.
  - Visual budget metrics (target benchmark, total expenditure, budget variance, and progress consumption bar).

### 4. Tab 3 - Vibe Customization & Dynamic Activity Swap (Epic 4)
- Interactive granular controls: pick any day and time slot.
- Swap presets: "Find vegetarian/vegan dining", "Swap for outdoor artisan market", "More relaxed scenic vibe", "High-adrenaline adventure", or enter any custom prompt.
- **Zero Plan Disruption**: Re-generates and recalculates only that single slot without wiping the rest of your itinerary.

### 5. Tab 4 - Trip Management & Offline PDF Export (Epic 5)
- **Simulated DB Persistence**: Stores trips in a local JSON database (`trips_db.json`) synced with `st.session_state`.
- **Trip History Archive**: Browse, load, delete, or clone previously saved itineraries.
- **1-Click Offline PDF Travel Guide**:
  - Publication-grade PDF generated on the fly via ReportLab.
  - Includes cover metadata, day-by-day clustered tables, financial summaries, and a comprehensive **Emergency Contact Checklist** (Police, Ambulance, International Hospital, Consular tips, and Packing Checklist).

---

## 🛠️ Project Structure

```
new genai project/
├── app.py              # Main Streamlit web application & tab orchestrator
├── config.py           # Currencies, exchange rates, benchmark budgets, metadata
├── models.py           # Pydantic schemas for validation and type safety
├── llm_service.py      # Dual Gemini/Groq LLM engine + resilient demo generator
├── recommender.py      # Tab 1: Smart Destination Recommender UI & logic
├── generator.py        # Tab 2: Clustered Itinerary Generator & budget tracker
├── customizer.py       # Tab 3: Dynamic single-slot activity swap & vibe tuning
├── trip_manager.py     # Tab 4: Trip history viewer & PDF download interface
├── storage.py          # Zero-dependency local JSON database persistence
├── pdf_exporter.py     # ReportLab offline printable PDF guide generator
├── styles.py           # Wanderlust CSS theme, responsive cards & metric chips
├── requirements.txt    # Production dependencies
└── README.md           # Documentation & architecture guide
```

---

## 🚀 Quickstart & Local Execution

### 1. Prerequisites
Python 3.10+ installed.

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Launch the Application
```bash
streamlit run app.py
```
Open your browser at `http://localhost:8501`.

---

## 🌐 Deploy to Streamlit Community Cloud (1-Click)

1. Push this folder to a GitHub repository.
2. Go to [share.streamlit.io](https://share.streamlit.io).
3. Select your repository, branch, and set `Main file path` to `app.py`.
4. (Optional) Add your `GEMINI_API_KEY` or `GROQ_API_KEY` in Streamlit App Secrets:
   ```toml
   GEMINI_API_KEY = "your-key-here"
   GROQ_API_KEY = "your-key-here"
   ```
5. Click **Deploy**! The app requires zero external databases and is 100% self-contained.

---

## 🛡️ License
MIT License. Built for Skill Wallet Capstone Project 4.
