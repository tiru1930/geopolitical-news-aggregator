# GeoNews Intelligence
## AI-Powered Geopolitical News Aggregator

A production-ready, Docker-based news aggregation platform with AI-powered strategic analysis. Designed for analysts, researchers, policy experts, and think-tank members.

**Features:**
- Clean, professional UI theme (light mode)
- Role-based access control (Admin, Analyst, Viewer)
- AI-powered strategic summaries using Groq/Llama 3.1
- Interactive geopolitical map
- Custom alerts system
- Admin-only source management

---

## Table of Contents

1. [Quick Start](#quick-start)
2. [User Guide](#user-guide)
   - [Registration & Login](#registration--login)
   - [Dashboard](#dashboard)
   - [Intelligence Reports](#intelligence-reports)
   - [Theatre Map](#theatre-map)
   - [Sources Management](#sources-management-admin-only)
   - [Alerts Configuration](#alerts-configuration)
   - [Settings](#settings)
3. [User Roles & Permissions](#user-roles--permissions)
4. [Architecture](#architecture)
5. [API Reference](#api-reference)
6. [Adding News Sources](#adding-news-sources)
7. [Troubleshooting](#troubleshooting)

---

## Quick Start

### Prerequisites
- Docker and Docker Compose
- Groq API Key (free at https://console.groq.com/)

### 1. Setup Environment

```bash
cd geopolitical-news-aggregator
copy .env.example .env
```

Edit `.env` and add your Groq API key:
```env
GROQ_API_KEY=your_groq_api_key_here
```

### 2. Launch Application

```bash
docker-compose up -d --build
```

### 3. Initialize Data

```bash
# Add default news sources
curl -X POST http://localhost:8000/api/sources/seed-defaults

# Fetch initial articles
curl -X POST http://localhost:8000/api/sources/fetch-all
```

### 4. Access Application

| Service | URL |
|---------|-----|
| **Frontend** | http://localhost:5173 |
| **API Docs** | http://localhost:8000/docs |
| **API Health** | http://localhost:8000/health |

---

## User Guide

### Registration & Login

#### Accessing the Login Page

Navigate to **http://localhost:5173** to see the login screen.

#### Quick Login (Demo Accounts)

Use these pre-configured accounts for testing:

| Account | Username | Password | Role |
|---------|----------|----------|------|
| Administrator | `admin` | `admin123` | Admin |
| Intelligence Analyst | `analyst` | `analyst123` | Analyst |
| Demo User | `demo` | `demo123` | Viewer |

#### Creating a New Account

1. Click **"Create Account"** on the login page
2. Fill in the registration form:

| Field | Description | Required |
|-------|-------------|----------|
| **Username** | Unique identifier (alphanumeric) | Yes |
| **Email** | Valid email address | Yes |
| **Full Name** | Display name | Yes |
| **Password** | Minimum 6 characters | Yes |
| **Role** | Access level selection | Yes |
| **Invite Code** | Required for Analyst/Admin roles | Conditional |

#### Role Selection & Invite Codes

| Role | Description | Invite Code |
|------|-------------|-------------|
| **Viewer** | Read-only access to all intelligence reports | Not required |
| **Analyst** | Create alerts + all Viewer permissions | `GEONEWS-ANALYST-2024` |
| **Admin** | Full access including source management | `GEONEWS-ADMIN-2024` |

**Note:** Keep invite codes secure. Change them in production by editing `backend/app/api/auth.py`.

---

### Dashboard

The main dashboard provides a **Situation Report** overview.

#### Stats Cards (Top Row)

| Card | Description |
|------|-------------|
| **Total Reports** | All articles in database |
| **Critical** | High-priority articles (relevance > 0.7) |
| **Last 24 Hours** | Recently published articles |
| **Active Sources** | Number of enabled news feeds |

#### Priority Intelligence (Left Panel)

Shows the latest high-relevance articles:
- **CRITICAL** (red badge): Highest strategic importance
- **PRIORITY** (gold badge): Significant developments
- **ROUTINE** (olive badge): Standard monitoring

Click any article to view full details.

#### Regional Activity (Right Panel)

Top regions by article count with quick links to filtered views.

#### Trend Analysis (Bottom)

7-day chart showing article volume patterns.

---

### Intelligence Reports

Access via **Sidebar > Intelligence**

#### Article List View

Each article card displays:
- **Priority Badge**: CRITICAL, PRIORITY, or ROUTINE
- **Region Tag**: Geographic area (South Asia, East Asia, etc.)
- **Theme Tag**: Strategic category
- **Title**: Article headline
- **Summary**: AI-generated brief (first 2 lines)
- **Source & Date**: Origin and publication time
- **External Link**: Opens original article

#### Filtering Articles

Click **"Filters"** button to show filter panel:

| Filter | Options |
|--------|---------|
| **Region** | South Asia, East Asia, Middle East, Europe, Africa, Americas, Indo-Pacific |
| **Theme** | Military Operations, Diplomatic Relations, Economic Security, Territorial Disputes, etc. |
| **Priority** | Critical, Priority, Routine |
| **Domain** | Land, Maritime, Air, Cyber, Space, Nuclear, Diplomatic, Economic |

#### Article Detail View

Click any article to see:
- Full AI-generated analysis
- **What Happened**: Event description
- **Why It Matters**: Strategic significance
- **Implications**: Impact analysis
- **Key Entities**: Countries, leaders, organizations
- **Relevance Score**: Percentage score with breakdown
- **Original Source Link**: Button to view source article

---

### Theatre Map

Access via **Sidebar > Theatre Map**

#### Interactive World Map

- **Circle Markers**: Indicate regional activity levels
- **Marker Size**: Proportional to critical report count
- **Marker Colors**:
  - **Maroon (Red)**: High activity intensity (>50%)
  - **Gold**: Moderate activity
- **Click Markers**: View region popup with article count

#### Map Legend

Located below the map explaining marker meanings.

#### Coverage Statistics

**By Region Panel**: Shows all regions with article counts
- Click any region to filter articles

**Top Countries Panel**: Shows top 15 countries by mention
- Click any country to filter articles

---

### Sources Management (Admin Only)

Access via **Sidebar > Sources**

**Note:** This section is only visible to users with **Admin** role.

#### Source List View

Each source card displays:
- **Status Indicator**: Green (active) or gray (disabled)
- **Source Name**: Display name
- **Type Badge**: RSS, API, GDELT, or Twitter
- **Category Badge**: Think Tank, News Agency, etc.
- **URL**: Source website
- **Article Count**: Total articles fetched
- **Last Fetch**: Time of last successful fetch

#### Adding a New Source

1. Click **"Add Source"** button
2. Fill in the form:

| Field | Description | Example |
|-------|-------------|---------|
| **Name** | Display name | "Reuters World News" |
| **URL** | Website URL | "https://reuters.com" |
| **Feed URL** | RSS feed URL | "https://feeds.reuters.com/reuters/worldNews" |
| **Type** | Source type | RSS, API, GDELT, Twitter |
| **Category** | Classification | News Agency, Think Tank, Government |
| **Region Focus** | Geographic specialty | South Asia, Global |
| **Reliability** | Trust score (0.0-1.0) | 0.9 |

3. Click **"Add Source"**

#### Managing Individual Sources

| Action | Icon | Description |
|--------|------|-------------|
| **Toggle Active** | Power icon | Enable/disable fetching |
| **Delete** | Trash icon | Remove source permanently |

#### Bulk Operations (Admin Actions)

| Button | Description |
|--------|-------------|
| **Seed Defaults** | Add pre-configured reliable sources (Reuters, Al Jazeera, etc.) |
| **Seed Additional** | Add extended source list (think tanks, regional) |
| **Fetch All** | Trigger immediate fetch from all active sources |
| **Cleanup Irrelevant** | Remove articles with relevance < 0.3 |
| **Cleanup Duplicates** | Remove duplicate articles |
| **Reprocess Scores** | Recalculate relevance scores for all articles |
| **Reprocess LLM** | Regenerate AI summaries for articles |

#### Sync Operations (API Fetches)

| Button | Description |
|--------|-------------|
| **Sync RSS** | Fetch from all RSS sources |
| **Sync GDELT** | Fetch from GDELT global database |
| **Sync NewsAPI** | Fetch from NewsAPI (requires API key) |
| **Sync Twitter** | Fetch from Twitter (requires API key) |

---

### Alerts Configuration

Access via **Sidebar > Alerts**

#### Creating an Alert

1. Click **"New Alert"** button
2. Fill in the form:

| Field | Description |
|-------|-------------|
| **Alert Name** | Descriptive identifier (e.g., "China Military Activity") |
| **Keywords** | Terms to match - press Enter after each keyword |
| **Minimum Priority** | Routine and above, Priority and above, or Critical only |
| **Frequency** | Immediate, Hourly, Daily, or Weekly |

3. Click **"Create Alert"**

#### Managing Alerts

| Action | Description |
|--------|-------------|
| **Toggle** | Green = active, Gray = disabled |
| **Delete** | Remove alert permanently |
| **Trigger Count** | Shows how many times alert has matched |

---

### Settings

Access via **Sidebar > Settings**

#### Profile Section
- **Display Name**: Your name shown in the app
- **Organization**: Your organization/unit
- **Email**: Contact email

#### Intelligence Preferences
- **Priority Regions**: Comma-separated list of preferred regions
- **Priority Themes**: Comma-separated list of preferred themes

#### System Status
- **Version**: Application version
- **API Status**: Backend connection status
- **LLM Provider**: AI service being used
- **Intel Fetch Interval**: How often news is fetched

---

## User Roles & Permissions

### Permission Matrix

| Feature | Viewer | Analyst | Admin |
|---------|--------|---------|-------|
| View Dashboard | Yes | Yes | Yes |
| View Articles | Yes | Yes | Yes |
| View Article Details | Yes | Yes | Yes |
| View Theatre Map | Yes | Yes | Yes |
| Create/Manage Alerts | Yes | Yes | Yes |
| Modify Settings | Yes | Yes | Yes |
| **View Sources Page** | No | No | Yes |
| **Add Sources** | No | No | Yes |
| **Edit/Delete Sources** | No | No | Yes |
| **Trigger Fetches** | No | No | Yes |
| **Run Cleanup Operations** | No | No | Yes |
| **Reprocess Articles** | No | No | Yes |

### Changing User Roles

To upgrade a user's role:
1. User must re-register with the appropriate invite code, OR
2. Admin can directly update the database

---

## Architecture

### System Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                         Frontend                             │
│                    React + TypeScript                        │
│               Tailwind CSS (Army Theme)                      │
│                   Leaflet Maps                               │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      Backend API                             │
│                   FastAPI + SQLAlchemy                       │
│                  JWT Authentication                          │
├─────────────────────────────────────────────────────────────┤
│  News Fetcher  │  AI Analyzer  │  Relevance Scorer          │
└─────────────────────────────────────────────────────────────┘
        │                 │                    │
        ▼                 ▼                    ▼
┌───────────┐    ┌───────────────┐    ┌───────────────┐
│ PostgreSQL│    │  Groq API     │    │    Redis      │
│  Database │    │  (Llama 3.1)  │    │  Cache/Queue  │
└───────────┘    └───────────────┘    └───────────────┘
                                              │
                                              ▼
                                      ┌───────────────┐
                                      │ Celery Workers│
                                      │ (Background)  │
                                      └───────────────┘
```

### Services

| Service | Port | Description |
|---------|------|-------------|
| frontend | 5173 | React dashboard |
| backend | 8000 | FastAPI server |
| db | 5432 | PostgreSQL database |
| redis | 6379 | Cache and task queue |
| celery_worker | - | Background processing |
| celery_beat | - | Scheduled tasks |

### Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | React 18, TypeScript, Vite, Tailwind CSS |
| UI Theme | Professional (Olive, Khaki, Maroon, Gold) |
| Backend | FastAPI, Python 3.11, SQLAlchemy |
| Database | PostgreSQL 16 |
| Cache/Queue | Redis 7, Celery |
| AI/LLM | Groq API (Llama 3.1 70B) |
| Maps | Leaflet.js + OpenStreetMap |
| Auth | JWT tokens with role-based access |

---

## API Reference

### Authentication

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/auth/register` | POST | Create new account |
| `/api/auth/login` | POST | Get access token |
| `/api/auth/me` | GET | Get current user info |

### Articles

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/articles/` | GET | List articles with filters |
| `/api/articles/{id}` | GET | Get article detail |
| `/api/articles/high-relevance` | GET | Top strategic articles |

### Dashboard

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/dashboard/stats` | GET | Overview statistics |
| `/api/dashboard/trends` | GET | Article trends |
| `/api/dashboard/hotspots` | GET | Map hotspot data |
| `/api/dashboard/region-stats` | GET | Articles by region |
| `/api/dashboard/theme-stats` | GET | Articles by theme |
| `/api/dashboard/country-stats` | GET | Articles by country |

### Sources (Admin Only)

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/api/sources/` | GET | Any | List all sources |
| `/api/sources/` | POST | Admin | Add new source |
| `/api/sources/{id}` | PUT | Admin | Update source |
| `/api/sources/{id}` | DELETE | Admin | Delete source |
| `/api/sources/{id}/toggle` | POST | Admin | Enable/disable source |
| `/api/sources/seed-defaults` | POST | Admin | Add default sources |
| `/api/sources/seed-additional` | POST | Admin | Add extended sources |
| `/api/sources/fetch-all` | POST | Admin | Fetch from all sources |
| `/api/sources/fetch-rss` | POST | Admin | Fetch RSS sources |
| `/api/sources/fetch-gdelt` | POST | Admin | Fetch from GDELT |
| `/api/sources/fetch-newsapi` | POST | Admin | Fetch from NewsAPI |
| `/api/sources/fetch-twitter` | POST | Admin | Fetch from Twitter |
| `/api/sources/cleanup-irrelevant` | POST | Admin | Remove low-relevance articles |
| `/api/sources/cleanup-duplicates` | POST | Admin | Remove duplicates |
| `/api/sources/reprocess-scores` | POST | Admin | Recalculate scores |
| `/api/sources/reprocess-llm` | POST | Admin | Regenerate summaries |

### Alerts

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/alerts/` | GET | List user alerts |
| `/api/alerts/` | POST | Create alert |
| `/api/alerts/{id}` | DELETE | Delete alert |
| `/api/alerts/{id}/toggle` | POST | Enable/disable alert |

---

## Adding News Sources

### Default Sources (Seed)

Run these commands as admin to populate sources:

```bash
# Add default RSS sources
curl -X POST http://localhost:8000/api/sources/seed-defaults \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"

# Add additional think tank sources
curl -X POST http://localhost:8000/api/sources/seed-additional \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"
```

### Pre-configured Sources

| Category | Sources |
|----------|---------|
| **Indian News** | The Hindu, Times of India, Indian Express |
| **International** | Reuters, Al Jazeera, AP News |
| **Defence** | Defense News, Military Times |
| **Think Tanks** | CSIS, Brookings, Carnegie, ORF, IDSA |
| **Regional** | The Diplomat, SCMP, Nikkei Asia |

### Adding Custom Source (UI)

1. Login as Admin
2. Go to **Sources** page
3. Click **"Add Source"**
4. Fill in the form
5. Click **"Add Source"**

### Adding Custom Source (API)

```bash
curl -X POST http://localhost:8000/api/sources/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -d '{
    "name": "New Source Name",
    "url": "https://example.com",
    "feed_url": "https://example.com/rss.xml",
    "source_type": "rss",
    "category": "think_tank",
    "region_focus": "South Asia",
    "reliability_score": 0.8
  }'
```

---

## Troubleshooting

### Common Issues

#### "Cannot connect to backend"
```bash
# Check container status
docker ps

# Restart services
docker-compose restart

# View backend logs
docker-compose logs backend
```

#### "No articles appearing"
```bash
# Seed sources (requires admin token)
curl -X POST http://localhost:8000/api/sources/seed-defaults

# Trigger fetch
curl -X POST http://localhost:8000/api/sources/fetch-all

# Check worker logs
docker-compose logs celery_worker
```

#### "AI summaries not generating"
1. Verify `GROQ_API_KEY` in `.env`
2. Check key at https://console.groq.com/
3. View logs: `docker-compose logs celery_worker`

#### "Login not working"
```bash
# Reset database (WARNING: deletes all data)
docker-compose down -v
docker-compose up -d --build
```

#### "Sources page not visible"
- Ensure you're logged in as Admin
- Check user role: call `/api/auth/me` endpoint

### Viewing Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f celery_worker
```

### Stopping Application

```bash
# Stop services
docker-compose down

# Stop and delete data
docker-compose down -v
```

---

## Environment Variables

```env
# Database
POSTGRES_USER=newsagg
POSTGRES_PASSWORD=your_secure_password
POSTGRES_DB=geopolitical_news

# Redis
REDIS_URL=redis://redis:6379/0

# AI/LLM (Required)
GROQ_API_KEY=your_groq_api_key
LLM_PROVIDER=groq

# App
SECRET_KEY=your_secret_key_change_in_production
DEBUG=false

# Optional API Keys
TWITTER_BEARER_TOKEN=your_twitter_token
NEWSAPI_KEY=your_newsapi_key
MEDIASTACK_KEY=your_mediastack_key

# Fetch Settings
FETCH_INTERVAL_MINUTES=30
```

---

## Security Notes

1. **Change Invite Codes**: In production, modify invite codes in `backend/app/api/auth.py`
2. **Change Secret Key**: Generate a strong `SECRET_KEY` for production
3. **Use HTTPS**: Deploy behind HTTPS in production
4. **Restrict API Access**: Use proper firewall rules
5. **Regular Updates**: Keep dependencies updated

---

## Production Deployment

```bash
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

This enables:
- Multi-worker backend
- Optimized frontend build
- Nginx reverse proxy
- Auto-restart policies

---

## Legal Disclaimer

### RSS Feed Usage

This application aggregates content from publicly available RSS feeds for **research, educational, and analytical purposes**. RSS (Really Simple Syndication) feeds are designed by publishers for content syndication and third-party consumption.

**How this application handles content:**
- Fetches only publicly available RSS feeds
- Displays article headlines and brief summaries
- Always links back to original source articles
- Does not store or republish full article content
- Uses AI to generate analytical summaries (transformative use)

### User Responsibilities

By using this software, you agree to:

1. **Respect Source Terms of Service**: Some publishers may have specific terms regarding automated access. Users are responsible for reviewing and complying with individual source ToS.

2. **Non-Commercial Use**: This software is provided for research and internal analysis. Commercial redistribution of aggregated content may require licensing agreements with content providers.

3. **Attribution**: Always maintain links to original sources. Do not remove or obscure source attribution.

4. **Rate Limiting**: The default 30-minute fetch interval is designed to be respectful to source servers. Do not modify settings to aggressively scrape sources.

### Content Ownership

- All aggregated articles remain the intellectual property of their respective publishers
- AI-generated summaries are analytical derivatives for research purposes
- This software does not claim ownership of any aggregated content

### No Warranty

THIS SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED. THE AUTHORS ARE NOT RESPONSIBLE FOR:
- Accuracy of aggregated content
- Availability of source feeds
- Any legal issues arising from misuse of this software
- Decisions made based on aggregated intelligence

### Recommended Sources

For compliant usage, prioritize:
- Government and official sources (public domain)
- Sources with explicit RSS syndication policies
- Creative Commons licensed content
- Sources that encourage aggregation

### GDELT Notice

This application integrates with GDELT (Global Database of Events, Language, and Tone), which is a free, open platform supported by Google Jigsaw. GDELT data is available for unrestricted use.

---

## License

MIT License - See LICENSE file for details.

This license applies to the **software code only**, not to any content aggregated through RSS feeds.

---

## Contributing

Contributions are welcome! Please ensure any new sources added are:
- Publicly available RSS feeds
- From reputable publishers
- Compliant with the source's terms of service

---

**GeoNews Intelligence v1.0.0**
*Geopolitical Intelligence Platform*
