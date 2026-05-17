import requests
from bs4 import BeautifulSoup
import os
import json
import datetime as dt

# =========================================================
# CACHE
# =========================================================

CACHE_DIR = "cache"

CACHE_FILE = os.path.join(
    CACHE_DIR,
    "forexfactory_events.json"
)

CACHE_TTL_HOURS = 24

os.makedirs(
    CACHE_DIR,
    exist_ok=True
)
# =========================================================
# FOREX FACTORY URL
# =========================================================

FF_URL = (
    "https://www.forexfactory.com/calendar"
)

# =========================================================
# GOLD RELEVANT EVENTS
# =========================================================

GOLD_KEYWORDS = [

    "CPI",
    "Inflation",

    "Non-Farm",
    "NFP",

    "FOMC",
    "Fed",

    "Interest Rate",

    "Powell",

    "PCE",

    "GDP",

    "Unemployment"
]

# =========================================================
# CACHE HELPERS
# =========================================================

def cache_is_valid():

    if not os.path.exists(
        CACHE_FILE
    ):

        return False

    modified = dt.datetime.fromtimestamp(
        os.path.getmtime(
            CACHE_FILE
        ),
        tz=dt.timezone.utc
    )

    now = dt.datetime.now(
        dt.timezone.utc
    )

    age_hours = (
        now - modified
    ).total_seconds() / 3600

    return (
        age_hours
        < CACHE_TTL_HOURS
    )


def load_cache():

    try:

        with open(
            CACHE_FILE,
            "r"
        ) as f:

            return json.load(f)

    except:

        return []


def save_cache(data):

    with open(
        CACHE_FILE,
        "w"
    ) as f:

        json.dump(
            data,
            f,
            default=str
        )
# =========================================================
# FETCH EVENTS
# =========================================================

def fetch_forexfactory_events():
    # =====================================================
# USE CACHE
# =====================================================

    if cache_is_valid():

        cached = load_cache()

        parsed = []

        for event in cached:

            try:

                parsed.append({

                    "name": event["name"],

                    "time":
                    dt.datetime.fromisoformat(
                        event["time"]
                    ),

                    "impact":
                    event["impact"],

                    "color":
                    event["color"]
                })

            except:

                continue

        print(
            f"Loaded {len(parsed)} "
            f"cached events"
        )

        return parsed

    headers = {

        "User-Agent":
        (
            "Mozilla/5.0 "
            "(Windows NT 10.0; Win64; x64)"
        )
    }

    response = requests.get(

        FF_URL,

        headers=headers,

        timeout=20
    )

    soup = BeautifulSoup(
        response.text,
        "lxml"
    )

    events = []

    rows = soup.select(
        "tr.calendar__row"
    )

    current_date = None

    current_time = None

    for row in rows:

        try:

            # =============================================
            # DATE
            # =============================================

            date_cell = row.select_one(
                ".calendar__date"
            )

            if (
                date_cell
                and
                date_cell.text.strip()
            ):

                current_date = (
                    date_cell.text.strip()
                )

            # =============================================
            # TIME
            # =============================================

            time_cell = row.select_one(
                ".calendar__time"
            )

            if (
                time_cell
                and
                time_cell.text.strip()
            ):

                current_time = (
                    time_cell.text.strip()
                )

            # =============================================
            # CURRENCY
            # =============================================

            currency_cell = row.select_one(
                ".calendar__currency"
            )

            if not currency_cell:

                continue

            currency = (
                currency_cell.text.strip()
            )

            # Only USD events
            if currency != "USD":

                continue

            # =============================================
            # IMPACT
            # =============================================

            impact_cell = row.select_one(
                ".calendar__impact"
            )

            impact_html = str(
                impact_cell
            ).lower()

            # HIGH
            if (
                "red" in impact_html
                or
                "high" in impact_html
            ):

                impact = "high"
                color = "red"

            # MEDIUM
            elif (
                "orange" in impact_html
                or
                "medium" in impact_html
            ):

                impact = "medium"
                color = "orange"

            # LOW
            elif (
                "yellow" in impact_html
                or
                "low" in impact_html
            ):

                impact = "low"
                color = "yellow"

            else:

                impact = "low"
                color = "gray"

            # =============================================
            # GOLD FILTER
            # =============================================

            event_lower = (
                event_name.lower()
            )

            relevant = any(

                keyword.lower()
                in event_lower

                for keyword
                in GOLD_KEYWORDS
            )

            if not relevant:

                continue

            # =============================================
            # DATETIME PARSING
            # =============================================

            if (
                current_date is None
                or
                current_time is None
            ):

                continue

            # Example:
            # Tue May 20
            # 8:30am

            year = (
                dt.datetime.now().year
            )

            dt_str = (
                f"{current_date} "
                f"{year} "
                f"{current_time}"
            )

            try:

                event_time = (
                    dt.datetime.strptime(
                        dt_str,
                        "%a %b %d %Y %I:%M%p"
                    )
                )

            except:

                continue

            event_time = (
                event_time.replace(
                    tzinfo=dt.timezone.utc
                )
            )

            events.append({

                "name": event_name,

                "time": event_time,

                "impact": impact,

                "color": color
            })

        except Exception:

            continue

    events = sorted(

        events,

        key=lambda x: x["time"]
    )

    print(
        f"Loaded {len(events)} "
        f"ForexFactory events"
    )

    # =====================================================
    # SAVE CACHE
    # =====================================================

    cache_ready = []

    for event in events:

        cache_ready.append({

            "name":
            event["name"],

            "time":
            event["time"].isoformat(),

            "impact":
            event["impact"],

            "color":
            event["color"]
        })

    save_cache(
        cache_ready
    )

    return events


# =========================================================
# UPCOMING EVENTS
# =========================================================

def get_upcoming_gold_events(
    hours=24
):

    now = dt.datetime.now(
        dt.timezone.utc
    )

    future_limit = (
        now
        + dt.timedelta(hours=hours)
    )

    events = (
        fetch_forexfactory_events()
    )

    upcoming = []

    for event in events:

        print(event)

        event_time = (
            event["time"]
        )

        if (
            now
            <= event_time
            <= future_limit
        ):

            upcoming.append(
                event
            )

    return upcoming

# =========================================================
# MACRO RISK ENGINE
# =========================================================

def get_macro_risk():

    events = (
        get_upcoming_gold_events(
            hours=24
        )
    )

    now = dt.datetime.now(
        dt.timezone.utc
    )

    if len(events) == 0:

        return {

            "risk": "LOW",

            "multiplier": 1.0,

            "next_event": None,

            "minutes_to_event": None
        }

    nearest = events[0]

    minutes = (
        nearest["time"]
        - now
    ).total_seconds() / 60

    # =============================================
    # RISK LEVELS
    # =============================================

    if minutes <= 30:

        risk = "EXTREME"
        multiplier = 0.40

    elif minutes <= 120:

        risk = "HIGH"
        multiplier = 0.65

    elif minutes <= 240:

        risk = "MEDIUM"
        multiplier = 0.85

    else:

        risk = "LOW"
        multiplier = 1.0

    return {

        "risk": risk,

        "multiplier": multiplier,

        "next_event": nearest,

        "minutes_to_event": int(minutes)
    }