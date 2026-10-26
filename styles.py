"""
Wanderlust-Inspired Modern CSS Styling and Visual Components for Streamlit.
"""

import streamlit as st


def apply_wanderlust_theme():
    """Injects bespoke wanderlust-themed CSS into the Streamlit app."""
    custom_css = """
    <style>
    /* Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=Playfair+Display:ital,wght@0,600;0,700;1,400&display=swap');

    /* Global Typography & Palette */
    :root {
        --wl-primary: #E07A5F;
        --wl-primary-hover: #D0694E;
        --wl-secondary: #2A9D8F;
        --wl-dark: #0F172A;
        --wl-slate: #1E293B;
        --wl-amber: #E76F51;
        --wl-gold: #F4A261;
        --wl-bg: #F8FAFC;
        --wl-card-bg: #FFFFFF;
        --wl-border: #E2E8F0;
        --wl-text-main: #1E293B;
        --wl-text-muted: #64748B;
    }

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
        color: var(--wl-text-main);
    }

    /* Main Container Padding */
    .block-container {
        padding-top: 1.8rem;
        padding-bottom: 3.5rem;
        max-width: 1200px;
    }

    /* Hero Brand Banner */
    .hero-banner {
        background: linear-gradient(135deg, #0F172A 0%, #1E293B 55%, #2A4365 100%);
        border-radius: 16px;
        padding: 30px 36px;
        color: #FFFFFF;
        margin-bottom: 24px;
        box-shadow: 0 10px 25px -5px rgba(15, 23, 42, 0.2);
        border: 1px solid rgba(255, 255, 255, 0.1);
        position: relative;
        overflow: hidden;
    }

    .hero-banner::after {
        content: "✈ 🌴 🗺";
        position: absolute;
        right: 25px;
        top: 20px;
        font-size: 3.2rem;
        opacity: 0.12;
        letter-spacing: 8px;
    }

    .hero-title {
        font-family: 'Playfair Display', serif;
        font-size: 2.3rem;
        font-weight: 700;
        margin-bottom: 6px;
        color: #FFFFFF;
        letter-spacing: -0.5px;
    }

    .hero-tagline {
        font-size: 1.05rem;
        color: #CBD5E1;
        font-weight: 400;
        max-width: 750px;
        line-height: 1.5;
    }

    .hero-badges {
        display: flex;
        gap: 10px;
        margin-top: 14px;
        flex-wrap: wrap;
    }

    .hero-badge-item {
        background: rgba(255, 255, 255, 0.12);
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.8rem;
        color: #F1F5F9;
        font-weight: 500;
        border: 1px solid rgba(255, 255, 255, 0.2);
    }

    /* Cards & Containers */
    .wl-card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 14px;
        padding: 22px;
        margin-bottom: 18px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }

    .wl-card:hover {
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.08);
    }

    .day-header-card {
        background: linear-gradient(to right, #FAF5FF, #F0FDF4);
        border: 1px solid #CBD5E1;
        border-left: 6px solid #2A9D8F;
        border-radius: 12px;
        padding: 16px 20px;
        margin: 20px 0 14px 0;
    }

    .day-title {
        font-family: 'Playfair Display', serif;
        font-size: 1.45rem;
        font-weight: 700;
        color: #0F172A;
        margin: 0;
    }

    .day-cluster-pill {
        display: inline-block;
        background: #2A9D8F;
        color: #FFFFFF;
        font-size: 0.78rem;
        font-weight: 600;
        padding: 3px 10px;
        border-radius: 12px;
        margin-left: 10px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    /* Activity Slot Styles */
    .slot-card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 16px 18px;
        margin-bottom: 12px;
        border-left: 4px solid #CBD5E1;
        transition: all 0.2s ease;
    }

    .slot-card.morning { border-left-color: #F4A261; }
    .slot-card.lunch { border-left-color: #E76F51; }
    .slot-card.afternoon { border-left-color: #2A9D8F; }
    .slot-card.evening { border-left-color: #264653; }

    .slot-time {
        font-size: 0.82rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.6px;
        color: #64748B;
        margin-bottom: 4px;
    }

    .slot-title {
        font-size: 1.12rem;
        font-weight: 700;
        color: #0F172A;
        margin-bottom: 6px;
    }

    .slot-desc {
        font-size: 0.92rem;
        color: #475569;
        line-height: 1.45;
        margin-bottom: 8px;
    }

    .slot-transit {
        font-size: 0.82rem;
        color: #0284C7;
        background: #F0F9FF;
        padding: 6px 10px;
        border-radius: 8px;
        border: 1px solid #BAE6FD;
        margin-bottom: 8px;
        display: inline-block;
    }

    .slot-meta-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        flex-wrap: wrap;
        gap: 8px;
        margin-top: 6px;
        padding-top: 6px;
        border-top: 1px dashed #F1F5F9;
    }

    .tag-chip {
        background: #F1F5F9;
        color: #334155;
        font-size: 0.75rem;
        font-weight: 500;
        padding: 2px 8px;
        border-radius: 6px;
        margin-right: 4px;
    }

    .cost-badge {
        font-size: 0.9rem;
        font-weight: 700;
        color: #15803D;
        background: #DCFCE7;
        padding: 3px 9px;
        border-radius: 8px;
        border: 1px solid #BBF7D0;
    }

    /* Metric Summary Bar */
    .metric-pill-box {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 16px;
        text-align: center;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02);
    }

    .metric-pill-val {
        font-size: 1.6rem;
        font-weight: 800;
        color: #0F172A;
        margin: 4px 0;
    }

    .metric-pill-lbl {
        font-size: 0.8rem;
        font-weight: 600;
        color: #64748B;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    /* Recommendation Cards */
    .rec-card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 14px;
        padding: 20px;
        margin-bottom: 16px;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.04);
        position: relative;
        transition: transform 0.2s ease, border-color 0.2s ease;
    }

    .rec-card:hover {
        transform: translateY(-2px);
        border-color: #2A9D8F;
    }

    .rec-header {
        display: flex;
        justify-content: space-between;
        align-items: baseline;
        margin-bottom: 8px;
    }

    .rec-city {
        font-family: 'Playfair Display', serif;
        font-size: 1.5rem;
        font-weight: 700;
        color: #0F172A;
    }

    .rec-score {
        background: #FEF3C7;
        color: #92400E;
        font-weight: 700;
        font-size: 0.85rem;
        padding: 3px 9px;
        border-radius: 12px;
        border: 1px solid #FDE68A;
    }

    .rec-tagline {
        font-size: 0.95rem;
        color: #475569;
        font-style: italic;
        margin-bottom: 12px;
    }

    /* Streamlit Tab Enhancements */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }

    .stTabs [data-baseweb="tab"] {
        font-size: 0.98rem;
        font-weight: 600;
        padding: 10px 18px;
        border-radius: 8px 8px 0 0;
    }

    /* Segmented Navigation Bar Styling */
    div[role="radiogroup"] {
        display: flex;
        flex-direction: row;
        gap: 8px;
        background: #F1F5F9;
        padding: 6px;
        border-radius: 12px;
        margin-bottom: 22px;
        border: 1px solid #CBD5E1;
        width: 100%;
    }

    div[role="radiogroup"] > label {
        flex: 1;
        background: transparent;
        padding: 10px 16px;
        border-radius: 8px;
        text-align: center;
        justify-content: center;
        margin: 0;
        cursor: pointer;
        transition: all 0.2s ease;
        font-weight: 600;
        font-size: 0.95rem;
    }

    div[role="radiogroup"] > label:hover {
        background: rgba(255, 255, 255, 0.7);
    }

    div[role="radiogroup"] > label:has(input:checked) {
        background: #FFFFFF;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -2px rgba(0, 0, 0, 0.05);
        color: #0F172A;
        border-bottom: 3px solid #2A9D8F;
    }

    div[role="radiogroup"] > label input {
        display: none;
    }

    /* Custom Alert Boxes */
    .info-callout {
        background-color: #EFF6FF;
        border-left: 4px solid #3B82F6;
        padding: 12px 16px;
        border-radius: 8px;
        font-size: 0.9rem;
        color: #1E40AF;
        margin: 12px 0;
    }

    .success-callout {
        background-color: #F0FDF4;
        border-left: 4px solid #22C55E;
        padding: 12px 16px;
        border-radius: 8px;
        font-size: 0.9rem;
        color: #15803D;
        margin: 12px 0;
    }
    </style>
    """
    st.markdown(custom_css, unsafe_allow_html=True)


def render_hero_banner():
    """Renders the top branding hero banner."""
    html = """
    <div class="hero-banner">
        <div class="hero-title">🌍 Personalized Travel Itinerary Planner</div>
        <div class="hero-tagline">
            Autonomous AI travel architect engineered with geographic cluster optimization, 
            multi-currency budget telemetry, interactive activity swapping, and 1-click offline PDF travel guides.
        </div>
        <div class="hero-badges">
            <span class="hero-badge-item">📍 Zero-Backtracking Clustering</span>
            <span class="hero-badge-item">💰 Live USD / INR / Local Currency</span>
            <span class="hero-badge-item">⚡ Dynamic Slot Swap</span>
            <span class="hero-badge-item">📄 Offline PDF Guide Ready</span>
            <span class="hero-badge-item">🛡 Zero External DB Dependencies</span>
        </div>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)
