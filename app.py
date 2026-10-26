from __future__ import annotations

import io
import os
import random
import time
import unicodedata
from dataclasses import dataclass, field

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import requests
import streamlit as st
from plotly.subplots import make_subplots

st.set_page_config(
    page_title="RER Arena | Real Exchange Rates",
    page_icon="💱",
    layout="wide",
)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
IMF_BASE = "https://api.imf.org/external/sdmx/3.0"
AGENCY = "IMF.STA"
START_MONTH = pd.Timestamp("1976-01-01")
REQUEST_TIMEOUT = 30  # seconds

# ISO3 | ISO2 (for flags) | Name | Current currency
COUNTRY_TABLE = """
G163|eu|Euro Area|EUR
AFG|af|Afghanistan|AFN
ALB|al|Albania|ALL
DZA|dz|Algeria|DZD
AND|ad|Andorra|EUR
AGO|ao|Angola|AOA
ATG|ag|Antigua and Barbuda|XCD
ARG|ar|Argentina|ARS
ARM|am|Armenia|AMD
ABW|aw|Aruba|AWG
AUS|au|Australia|AUD
AUT|at|Austria|EUR
AZE|az|Azerbaijan|AZN
BHS|bs|Bahamas|BSD
BHR|bh|Bahrain|BHD
BGD|bd|Bangladesh|BDT
BRB|bb|Barbados|BBD
BLR|by|Belarus|BYN
BEL|be|Belgium|EUR
BLZ|bz|Belize|BZD
BEN|bj|Benin|XOF
BTN|bt|Bhutan|BTN
BOL|bo|Bolivia|BOB
BIH|ba|Bosnia and Herzegovina|BAM
BWA|bw|Botswana|BWP
BRA|br|Brazil|BRL
BRN|bn|Brunei Darussalam|BND
BGR|bg|Bulgaria|EUR
BFA|bf|Burkina Faso|XOF
BDI|bi|Burundi|BIF
CPV|cv|Cabo Verde|CVE
KHM|kh|Cambodia|KHR
CMR|cm|Cameroon|XAF
CAN|ca|Canada|CAD
CAF|cf|Central African Republic|XAF
TCD|td|Chad|XAF
CHL|cl|Chile|CLP
CHN|cn|China|CNY
COL|co|Colombia|COP
COM|km|Comoros|KMF
COD|cd|Congo, Democratic Republic of the|CDF
COG|cg|Congo, Republic of|XAF
CRI|cr|Costa Rica|CRC
CIV|ci|Côte d'Ivoire|XOF
HRV|hr|Croatia|EUR
CYP|cy|Cyprus|EUR
CZE|cz|Czech Republic|CZK
DNK|dk|Denmark|DKK
DJI|dj|Djibouti|DJF
DMA|dm|Dominica|XCD
DOM|do|Dominican Republic|DOP
ECU|ec|Ecuador|USD
EGY|eg|Egypt|EGP
SLV|sv|El Salvador|USD
GNQ|gq|Equatorial Guinea|XAF
ERI|er|Eritrea|ERN
EST|ee|Estonia|EUR
SWZ|sz|Eswatini|SZL
ETH|et|Ethiopia|ETB
FJI|fj|Fiji|FJD
FIN|fi|Finland|EUR
FRA|fr|France|EUR
GAB|ga|Gabon|XAF
GMB|gm|Gambia|GMD
GEO|ge|Georgia|GEL
DEU|de|Germany|EUR
GHA|gh|Ghana|GHS
GRC|gr|Greece|EUR
GRD|gd|Grenada|XCD
GTM|gt|Guatemala|GTQ
GIN|gn|Guinea|GNF
GNB|gw|Guinea-Bissau|XOF
GUY|gy|Guyana|GYD
HTI|ht|Haiti|HTG
HND|hn|Honduras|HNL
HKG|hk|Hong Kong SAR|HKD
HUN|hu|Hungary|HUF
ISL|is|Iceland|ISK
IND|in|India|INR
IDN|id|Indonesia|IDR
IRN|ir|Iran|IRR
IRQ|iq|Iraq|IQD
IRL|ie|Ireland|EUR
ISR|il|Israel|ILS
ITA|it|Italy|EUR
JAM|jm|Jamaica|JMD
JPN|jp|Japan|JPY
JOR|jo|Jordan|JOD
KAZ|kz|Kazakhstan|KZT
KEN|ke|Kenya|KES
KIR|ki|Kiribati|AUD
KOR|kr|Korea|KRW
KOS|xk|Kosovo|EUR
KWT|kw|Kuwait|KWD
KGZ|kg|Kyrgyz Republic|KGS
LAO|la|Lao P.D.R.|LAK
LVA|lv|Latvia|EUR
LBN|lb|Lebanon|LBP
LSO|ls|Lesotho|LSL
LBR|lr|Liberia|LRD
LBY|ly|Libya|LYD
LIE|li|Liechtenstein|CHF
LTU|lt|Lithuania|EUR
LUX|lu|Luxembourg|EUR
MAC|mo|Macao SAR|MOP
MDG|mg|Madagascar|MGA
MWI|mw|Malawi|MWK
MYS|my|Malaysia|MYR
MDV|mv|Maldives|MVR
MLI|ml|Mali|XOF
MLT|mt|Malta|EUR
MHL|mh|Marshall Islands|USD
MRT|mr|Mauritania|MRU
MUS|mu|Mauritius|MUR
MEX|mx|Mexico|MXN
FSM|fm|Micronesia|USD
MDA|md|Moldova|MDL
MNG|mn|Mongolia|MNT
MNE|me|Montenegro|EUR
MAR|ma|Morocco|MAD
MOZ|mz|Mozambique|MZN
MMR|mm|Myanmar|MMK
NAM|na|Namibia|NAD
NRU|nr|Nauru|AUD
NPL|np|Nepal|NPR
NLD|nl|Netherlands|EUR
NZL|nz|New Zealand|NZD
NIC|ni|Nicaragua|NIO
NER|ne|Niger|XOF
NGA|ng|Nigeria|NGN
MKD|mk|North Macedonia|MKD
NOR|no|Norway|NOK
OMN|om|Oman|OMR
PAK|pk|Pakistan|PKR
PLW|pw|Palau|USD
PAN|pa|Panama|PAB
PNG|pg|Papua New Guinea|PGK
PRY|py|Paraguay|PYG
PER|pe|Peru|PEN
PHL|ph|Philippines|PHP
POL|pl|Poland|PLN
PRT|pt|Portugal|EUR
QAT|qa|Qatar|QAR
ROU|ro|Romania|RON
RUS|ru|Russia|RUB
RWA|rw|Rwanda|RWF
WSM|ws|Samoa|WST
SMR|sm|San Marino|EUR
STP|st|São Tomé and Príncipe|STN
SAU|sa|Saudi Arabia|SAR
SEN|sn|Senegal|XOF
SRB|rs|Serbia|RSD
SYC|sc|Seychelles|SCR
SLE|sl|Sierra Leone|SLE
SGP|sg|Singapore|SGD
SVK|sk|Slovak Republic|EUR
SVN|si|Slovenia|EUR
SLB|sb|Solomon Islands|SBD
SOM|so|Somalia|SOS
ZAF|za|South Africa|ZAR
SSD|ss|South Sudan|SSP
ESP|es|Spain|EUR
LKA|lk|Sri Lanka|LKR
KNA|kn|St. Kitts and Nevis|XCD
LCA|lc|St. Lucia|XCD
VCT|vc|St. Vincent and the Grenadines|XCD
SDN|sd|Sudan|SDG
SUR|sr|Suriname|SRD
SWE|se|Sweden|SEK
CHE|ch|Switzerland|CHF
SYR|sy|Syria|SYP
TJK|tj|Tajikistan|TJS
TZA|tz|Tanzania|TZS
THA|th|Thailand|THB
TLS|tl|Timor-Leste|USD
TGO|tg|Togo|XOF
TON|to|Tonga|TOP
TTO|tt|Trinidad and Tobago|TTD
TUN|tn|Tunisia|TND
TUR|tr|Türkiye|TRY
TKM|tm|Turkmenistan|TMT
TUV|tv|Tuvalu|AUD
UGA|ug|Uganda|UGX
UKR|ua|Ukraine|UAH
ARE|ae|United Arab Emirates|AED
GBR|gb|United Kingdom|GBP
USA|us|United States|USD
URY|uy|Uruguay|UYU
UZB|uz|Uzbekistan|UZS
VUT|vu|Vanuatu|VUV
VEN|ve|Venezuela|VES
VNM|vn|Vietnam|VND
PSE|ps|West Bank and Gaza|ILS
YEM|ye|Yemen|YER
ZMB|zm|Zambia|ZMW
ZWE|zw|Zimbabwe|ZWG
"""

# Some economies appear under more than one code across IMF releases.
ALT_CODES = {"KOS": ["UVK", "XKX"]}

# Economies whose currency is (or is pegged at par to) the US dollar for the whole
# sample. The IMF may not publish a USD-per-USD series, so 1.0 is used if missing.
USD_AT_PAR = {"USA", "PAN", "PLW", "MHL", "FSM"}

# Euro adoption month and irrevocable conversion rate (legacy units per euro).
EURO_ADOPTION = {
    "AUT": ("1999-01", 13.7603), "BEL": ("1999-01", 40.3399),
    "FIN": ("1999-01", 5.94573), "FRA": ("1999-01", 6.55957),
    "DEU": ("1999-01", 1.95583), "IRL": ("1999-01", 0.787564),
    "ITA": ("1999-01", 1936.27), "LUX": ("1999-01", 40.3399),
    "NLD": ("1999-01", 2.20371), "PRT": ("1999-01", 200.482),
    "ESP": ("1999-01", 166.386), "GRC": ("2001-01", 340.750),
    "SVN": ("2007-01", 239.640), "CYP": ("2008-01", 0.585274),
    "MLT": ("2008-01", 0.429300), "SVK": ("2009-01", 30.1260),
    "EST": ("2011-01", 15.6466), "LVA": ("2014-01", 0.702804),
    "LTU": ("2015-01", 3.45280), "HRV": ("2023-01", 7.53450),
    "BGR": ("2026-01", 1.95583),
}

QUICK_MATCHUPS = [
    ("USA", "JPN"), ("USA", "G163"), ("GBR", "G163"), ("CHN", "USA"),
    ("MEX", "USA"), ("CHE", "G163"), ("TUR", "USA"), ("IND", "USA"),
]
RANDOM_POOL = [
    "USA", "JPN", "G163", "GBR", "CAN", "AUS", "CHE", "CHN", "IND", "BRA",
    "MEX", "KOR", "ZAF", "TUR", "SWE", "NOR", "NZL", "IDN", "THA", "POL",
    "CHL", "COL", "ISR", "DNK", "SGP", "PHL", "MYS", "EGY", "HUN", "CZE",
]

LEVELS = [
    (0, "🎒 FX Intern"),
    (300, "📊 Junior Analyst"),
    (700, "💹 Currency Trader"),
    (1200, "🏦 Portfolio Manager"),
    (2000, "🏛️ Central Banker"),
    (3000, "🌐 IMF Chief Economist"),
]

BADGES = {
    "rookie": ("🎮", "Rookie", "Played your first prediction round"),
    "sharpshooter": ("🎯", "Sharpshooter", "Got all three predictions right in one round"),
    "on_fire": ("🔥", "On Fire", "Five correct predictions in a row"),
    "globetrotter": ("🌍", "Globetrotter", "Explored five different country pairs"),
    "time_traveler": ("⏳", "Time Traveler", "Analyzed a window that starts before 1985"),
    "euro": ("💶", "Euro Enthusiast", "Put the Euro Area in a matchup"),
    "inflation_hunter": ("🌋", "Inflation Hunter", "Found a country averaging 25%+ inflation a year"),
    "perspective": ("🔄", "Perspective Shift", "Swapped Country 1 and Country 2"),
    "data_nerd": ("📥", "Data Nerd", "Downloaded the CSV"),
}


def _sort_key(name: str) -> str:
    return unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode().lower()


def _parse_countries() -> dict[str, dict]:
    rows = {}
    for line in COUNTRY_TABLE.strip().splitlines():
        iso3, iso2, name, cur = (p.strip() for p in line.split("|"))
        rows[iso3] = {"iso3": iso3, "iso2": iso2, "name": name, "cur": cur}
    return rows


COUNTRIES = _parse_countries()
ORDERED_CODES = ["G163"] + sorted(
    (c for c in COUNTRIES if c != "G163"), key=lambda c: _sort_key(COUNTRIES[c]["name"])
)


def flag_emoji(iso3: str) -> str:
    iso2 = COUNTRIES[iso3]["iso2"].upper()
    return "".join(chr(0x1F1E6 + ord(ch) - ord("A")) for ch in iso2)


def flag_url(iso3: str) -> str:
    return f"https://flagcdn.com/{COUNTRIES[iso3]['iso2']}.svg"


def country_label(iso3: str) -> str:
    c = COUNTRIES[iso3]
    return f"{flag_emoji(iso3)}  {c['name']} ({c['cur']})"


def name(iso3: str) -> str:
    return COUNTRIES[iso3]["name"]


def cur(iso3: str) -> str:
    return COUNTRIES[iso3]["cur"]


def month_index() -> pd.DatetimeIndex:
    end = pd.Timestamp.today().to_period("M").to_timestamp()
    return pd.date_range(START_MONTH, end, freq="MS")


# ---------------------------------------------------------------------------
# IMF data access
# ---------------------------------------------------------------------------
class IMFUnavailable(Exception):
    """The IMF API could not be reached or returned errors (never cached)."""


def _subscription_key() -> str | None:
    key = os.environ.get("IMF_SUBSCRIPTION_KEY")
    if key:
        return key
    try:
        return st.secrets.get("IMF_SUBSCRIPTION_KEY")
    except Exception:
        return None


def _get(url: str, accept: str) -> requests.Response:
    headers = {
        "Accept": accept,
        "User-Agent": "real-exchange-rate-app/1.0 (educational Streamlit app)",
        "Cache-Control": "no-cache",
    }
    key = _subscription_key()
    if key:
        headers["Ocp-Apim-Subscription-Key"] = key
    resp = None
    for attempt in range(3):
        resp = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT)
        if resp.status_code in (429, 502, 503, 504) and attempt < 2:
            time.sleep(1.5 * (attempt + 1))
            continue
        break
    return resp


def _to_monthly_series(periods, values) -> pd.Series:
    """Turn IMF period labels (e.g. '1976-M01') and values into a clean monthly series."""
    periods = pd.Series(periods, dtype="object").astype(str)
    parts = periods.str.extract(r"^\s*(\d{4})[-/]?M?(\d{1,2})(?!\d)")
    dates = pd.to_datetime(parts[0] + "-" + parts[1].str.zfill(2), format="%Y-%m", errors="coerce")
    vals = pd.to_numeric(pd.Series(values, dtype="object"), errors="coerce")
    s = pd.Series(vals.to_numpy(dtype=float), index=pd.DatetimeIndex(dates))
    s = s[s.index.notna()]
    s = s[np.isfinite(s) & (s > 0)]
    s = s.groupby(level=0).last().sort_index()
    s = s[s.index >= START_MONTH]
    s.index.name = None
    return s.astype(float)


def _parse_csv(text: str) -> pd.Series:
    if not text or not text.strip():
        return pd.Series(dtype=float)
    df = pd.read_csv(io.StringIO(text), dtype=str, low_memory=False)
    cols = {str(c).strip().upper(): c for c in df.columns}
    tcol, vcol = cols.get("TIME_PERIOD"), cols.get("OBS_VALUE")
    if tcol is None or vcol is None:
        raise ValueError("response is not the expected SDMX CSV")
    return _to_monthly_series(df[tcol], df[vcol])


def _parse_json(payload: dict) -> pd.Series:
    """Parse SDMX-JSON (series or flat observation layouts)."""
    data = payload.get("data", payload)
    structures = data.get("structures") or ([data["structure"]] if isinstance(data.get("structure"), dict) else [])
    if not structures and isinstance(payload.get("structure"), dict):
        structures = [payload["structure"]]
    datasets = data.get("dataSets") or []
    if not datasets:
        return pd.Series(dtype=float)
    if not structures:
        raise ValueError("SDMX-JSON without structure")
    obs_dims = structures[0].get("dimensions", {}).get("observation", [])
    tpos = next((i for i, d in enumerate(obs_dims) if d.get("id") == "TIME_PERIOD"), None)
    if tpos is None:
        raise ValueError("SDMX-JSON without TIME_PERIOD")
    tvals = [v.get("value") or v.get("id") for v in obs_dims[tpos].get("values", [])]
    periods, values = [], []

    def collect(observations: dict):
        for okey, obs in (observations or {}).items():
            idx = int(str(okey).split(":")[tpos])
            periods.append(tvals[idx])
            values.append(obs[0] if isinstance(obs, list) and obs else obs)

    for ds in datasets:
        for ser in (ds.get("series") or {}).values():
            collect(ser.get("observations"))
        collect(ds.get("observations"))
    return _to_monthly_series(periods, values)


@st.cache_data(ttl=6 * 3600, show_spinner=False, max_entries=500)
def fetch_imf_series(flow: str, key: str) -> tuple[pd.Series, list[str]]:
    """Fetch one monthly IMF series. Returns (series, request log).

    An empty series means the IMF answered but has no data for that key (cached).
    Raises IMFUnavailable if the API could not be reached (not cached, so a retry works).
    """
    base = f"{IMF_BASE}/data/dataflow/{AGENCY}/{flow}/~/{key}"
    attempts = [
        ("csv", f"{base}?c[TIME_PERIOD]=ge:1976-M01"),
        ("csv", base),
        ("json", base),
    ]
    log: list[str] = []
    answered_empty = False
    for i, (fmt, url) in enumerate(attempts):
        accept = "text/csv" if fmt == "csv" else "application/json"
        try:
            resp = _get(url, accept)
        except (requests.Timeout, requests.ConnectionError) as exc:
            log.append(f"{url} → {exc.__class__.__name__}")
            raise IMFUnavailable(" | ".join(log)) from exc
        except requests.RequestException as exc:
            log.append(f"{url} → {exc.__class__.__name__}")
            continue
        if resp.status_code == 404:
            log.append(f"{url} → HTTP 404 (no data)")
            answered_empty = True
            if i == 0:
                continue  # try once without the time filter
            break
        if resp.status_code != 200:
            log.append(f"{url} → HTTP {resp.status_code}")
            continue
        try:
            s = _parse_csv(resp.text) if fmt == "csv" else _parse_json(resp.json())
        except Exception as exc:
            log.append(f"{url} → unreadable response ({exc.__class__.__name__})")
            continue
        log.append(f"{url} → HTTP 200, {len(s)} monthly observations")
        if not s.empty:
            return s, log
        answered_empty = True
        if i == 0:
            continue
        break
    if answered_empty:
        return pd.Series(dtype=float), log
    raise IMFUnavailable(" | ".join(log))


@dataclass
class CountryData:
    iso: str
    cpi: pd.Series = field(default_factory=lambda: pd.Series(dtype=float))
    fx: pd.Series = field(default_factory=lambda: pd.Series(dtype=float))
    notes: list[str] = field(default_factory=list)
    log: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


def _first_available(cd: CountryData, flow: str, keys: list[str]) -> tuple[pd.Series, str | None]:
    for key in keys:
        try:
            s, log = fetch_imf_series(flow, key)
        except IMFUnavailable as exc:
            cd.errors.append(f"{flow}/{key}: {exc}")
            return pd.Series(dtype=float), None
        cd.log.extend(log)
        if not s.empty:
            return s, key
    return pd.Series(dtype=float), None


def _euro_area_fx(cd: CountryData) -> pd.Series:
    """EUR per USD. Uses G163; falls back to a founding member's post-1999 euro rate."""
    s, _ = _first_available(cd, "ER", ["G163.XDC_USD.PA_RT.M"])
    if not s.empty or cd.errors:
        return s
    for member in ("DEU", "FRA", "ITA", "ESP", "NLD"):
        m, _ = _first_available(cd, "ER", [f"{member}.XDC_USD.PA_RT.M"])
        post = m[m.index >= pd.Timestamp("1999-01-01")]
        if len(post) >= 12 and 0.5 < post.median() < 1.5:
            cd.notes.append(
                f"The IMF has no exchange-rate series for G163, so the euro's USD rate from 1999 on "
                f"is taken from {name(member)}'s series (identical after euro adoption)."
            )
            return post
    return pd.Series(dtype=float)


def _harmonize_euro_member(cd: CountryData) -> None:
    """Express a euro member's exchange rate in euro-equivalent units throughout."""
    adopt_str, rate = EURO_ADOPTION[cd.iso]
    adopt = pd.Timestamp(f"{adopt_str}-01")
    fx = cd.fx
    pre, post = fx[fx.index < adopt], fx[fx.index >= adopt]
    if not pre.empty and not post.empty:
        ratio = pre.iloc[-1] / post.iloc[0]
        if abs(np.log(ratio) - np.log(rate)) < abs(np.log(ratio)):
            cd.fx = pd.concat([pre / rate, post])
            cd.notes.append(
                f"{name(cd.iso)}: pre-{adopt:%Y} rates were in the legacy currency, so they were "
                f"converted to euro-equivalent units at the irrevocable rate ({rate:g} per euro). "
                f"This removes an artificial jump in S(t); the Real Index is unaffected by the units."
            )
        return
    euro = _euro_area_fx(cd)
    euro_post = euro[euro.index >= adopt]
    if euro_post.empty:
        return
    if not pre.empty:
        cd.fx = pd.concat([pre / rate, euro_post])
        cd.notes.append(
            f"{name(cd.iso)}: the IMF national series stops at euro adoption. Legacy rates were "
            f"converted at {rate:g} per euro and spliced with the euro's USD rate from {adopt:%b %Y}."
        )
    else:
        cd.fx = euro_post
        cd.notes.append(
            f"{name(cd.iso)}: no national exchange-rate series, so the euro's USD rate is used from {adopt:%b %Y}."
        )


def load_country(iso: str) -> CountryData:
    cd = CountryData(iso)
    codes = [iso] + ALT_CODES.get(iso, [])

    cpi, key = _first_available(cd, "CPI", [f"{c}.CPI._T.IX.M" for c in codes])
    if cpi.empty and not cd.errors:
        cpi, key = _first_available(cd, "CPI", [f"{c}.HICP._T.IX.M" for c in codes])
        if not cpi.empty:
            cd.notes.append(f"{name(iso)}: no CPI series, so the HICP index ({key}) is used for prices.")
    cd.cpi = cpi

    if cd.errors:
        return cd

    fx, _ = _first_available(cd, "ER", [f"{c}.XDC_USD.PA_RT.M" for c in codes])
    if fx.empty and iso == "G163":
        fx = _euro_area_fx(cd)
    if fx.empty and iso in USD_AT_PAR and not cd.errors:
        fx = pd.Series(1.0, index=month_index())
        cd.notes.append(f"{name(iso)}: currency is the US dollar or at par with it, so FX = 1 per USD.")
    cd.fx = fx
    if iso in EURO_ADOPTION and not cd.errors:
        _harmonize_euro_member(cd)
    return cd


# ---------------------------------------------------------------------------
# Economics
# ---------------------------------------------------------------------------
def build_frame(d1: CountryData, d2: CountryData) -> pd.DataFrame:
    idx = month_index()
    df = pd.DataFrame(index=idx)
    df["FX1"] = d1.fx.reindex(idx)  # Country 1 currency per USD
    df["FX2"] = d2.fx.reindex(idx)  # Country 2 currency per USD
    df["P1"] = d1.cpi.reindex(idx)
    df["P2"] = d2.cpi.reindex(idx)
    df["S"] = df["FX2"] / df["FX1"]  # Country 2 currency per 1 unit of Country 1 currency
    rer = df["S"] * df["P1"] / df["P2"]
    df["RER"] = rer.where(np.isfinite(rer) & (rer > 0))
    df.index.name = "month"
    return df


def window_calc(df: pd.DataFrame, start: pd.Timestamp, end: pd.Timestamp) -> tuple[pd.DataFrame, float]:
    w = df.loc[start:end].copy()
    w["valid"] = w["RER"].notna()
    rer_star = float(w.loc[w["valid"], "RER"].mean()) if w["valid"].any() else float("nan")
    w["RER_star"] = rer_star
    w["Real_Index"] = 100.0 * w["RER"] / rer_star
    return w, rer_star


def window_facts(w: pd.DataFrame) -> dict:
    v = w[w["valid"]]
    first, last = v.iloc[0], v.iloc[-1]
    months = max(len(pd.date_range(v.index[0], v.index[-1], freq="MS")) - 1, 1)
    p1_ratio, p2_ratio = last["P1"] / first["P1"], last["P2"] / first["P2"]
    peak_date, trough_date = v["Real_Index"].idxmax(), v["Real_Index"].idxmin()
    return {
        "first_date": v.index[0], "last_date": v.index[-1], "n_valid": len(v), "n_total": len(w),
        "rer_first": first["RER"], "rer_last": last["RER"],
        "real_chg": last["RER"] / first["RER"] - 1,
        "nom_chg": last["S"] / first["S"] - 1,
        "relp_chg": p1_ratio / p2_ratio - 1,
        "p1_ratio": p1_ratio, "p2_ratio": p2_ratio,
        "infl1_ann": p1_ratio ** (12 / months) - 1,
        "infl2_ann": p2_ratio ** (12 / months) - 1,
        "idx_last": last["Real_Index"],
        "peak": v["Real_Index"].max(), "peak_date": peak_date,
        "trough": v["Real_Index"].min(), "trough_date": trough_date,
    }


# ---------------------------------------------------------------------------
# Formatting helpers
# ---------------------------------------------------------------------------
def fmt_month(m) -> str:
    return pd.Timestamp(m).strftime("%b %Y")


def fmt_num(x: float) -> str:
    if x is None or not np.isfinite(x):
        return "—"
    ax = abs(x)
    if ax >= 1000:
        return f"{x:,.0f}"
    if ax >= 10:
        return f"{x:,.2f}"
    if ax >= 0.01:
        return f"{x:,.4f}"
    return f"{x:.3e}"


def fmt_pct(x: float) -> str:
    return "—" if x is None or not np.isfinite(x) else f"{x * 100:+,.1f}%"


def coverage_text(s: pd.Series) -> str:
    if s.empty:
        return "no data"
    return f"{fmt_month(s.index[0])} – {fmt_month(s.index[-1])} ({len(s)} months)"


# ---------------------------------------------------------------------------
# Game state
# ---------------------------------------------------------------------------
ss = st.session_state


def init_state() -> None:
    defaults = {
        "c1": "USA", "c2": "JPN", "game_mode": True, "view": "Both", "log_nominal": False,
        "xp": 0, "streak": 0, "best_streak": 0, "rounds_played": 0,
        "answers_total": 0, "answers_correct": 0,
        "badges": set(), "pairs_seen": set(), "revealed": set(), "rounds": {},
        "toasts": [], "celebrate": False,
    }
    for k, v in defaults.items():
        if k not in ss:
            ss[k] = v.copy() if isinstance(v, (set, dict, list)) else v


def level_info(xp: int) -> tuple[str, int, int | None]:
    current = LEVELS[0]
    nxt = None
    for i, lvl in enumerate(LEVELS):
        if xp >= lvl[0]:
            current = lvl
            nxt = LEVELS[i + 1] if i + 1 < len(LEVELS) else None
    return current[1], current[0], (nxt[0] if nxt else None)


def award(badge_id: str) -> None:
    if badge_id not in ss.badges:
        ss.badges.add(badge_id)
        emoji, title, desc = BADGES[badge_id]
        ss.toasts.append((f"Badge unlocked: **{title}** — {desc}", emoji))


def cb_swap() -> None:
    ss.c1, ss.c2 = ss.c2, ss.c1
    award("perspective")


def cb_random() -> None:
    a, b = random.sample(RANDOM_POOL, 2)
    ss.c1, ss.c2 = a, b


def cb_set_pair(a: str, b: str) -> None:
    ss.c1, ss.c2 = a, b


def cb_reveal(pair_key: frozenset) -> None:
    ss.revealed.add(pair_key)


def cb_downloaded() -> None:
    award("data_nerd")


def flush_toasts() -> None:
    for msg, icon in ss.toasts:
        st.toast(msg, icon=icon)
    ss.toasts = []


# ---------------------------------------------------------------------------
# UI pieces
# ---------------------------------------------------------------------------
CSS = """
<style>
.rer-hero h1 {font-size: 2.4rem; font-weight: 900; margin: 0 0 .1rem 0; letter-spacing: -.02em;}
.rer-hero p {opacity: .75; margin: 0 0 .6rem 0;}
.faceoff {display:flex; align-items:center; justify-content:center; gap: 1.5rem; flex-wrap: wrap;
  padding: 1.4rem 1rem 1.2rem; margin: .4rem 0 1rem; border-radius: 22px;
  background: linear-gradient(120deg, rgba(37,99,235,.12), rgba(168,85,247,.08) 50%, rgba(245,158,11,.12));
  border: 1px solid rgba(128,128,128,.25);}
.fighter {text-align:center; flex: 1 1 240px; max-width: 440px;}
.fighter img {height: clamp(110px, 19vw, 230px); width: auto; max-width: 100%;
  border-radius: 10px; filter: drop-shadow(0 10px 18px rgba(0,0,0,.30));
  animation: bob 4.5s ease-in-out infinite;}
.fighter.two img {animation-delay: -2.25s;}
.fighter .tag {display:inline-block; font-size:.75rem; font-weight:700; letter-spacing:.08em;
  text-transform: uppercase; padding:.15rem .6rem; border-radius:999px; margin-bottom:.6rem;
  background: rgba(37,99,235,.18);}
.fighter.two .tag {background: rgba(245,158,11,.22);}
.fighter .fname {font-size: 1.55rem; font-weight: 800; margin-top: .7rem; line-height: 1.15;}
.fighter .fmeta {opacity: .7; font-size: .95rem;}
.vsbox {text-align:center; flex: 0 0 auto;}
.vs {font-size: 3.4rem; font-weight: 900; line-height: 1;
  background: linear-gradient(135deg, #ef4444, #f59e0b); -webkit-background-clip: text;
  background-clip: text; color: transparent; animation: pulse 1.8s ease-in-out infinite;}
.vsbox .def {font-size:.8rem; opacity:.7; margin-top:.4rem;}
@keyframes bob {0%,100% {transform: translateY(0) rotate(-1.2deg);} 50% {transform: translateY(-7px) rotate(1.2deg);}}
@keyframes pulse {0%,100% {transform: scale(1);} 50% {transform: scale(1.12);}}
.meter {margin: .3rem 0 1rem;}
.meter .bar {position: relative; height: 18px; border-radius: 999px;
  background: linear-gradient(90deg, #2563eb, rgba(148,163,184,.35) 50%, #f59e0b);}
.meter .mid {position:absolute; left:50%; top:-4px; bottom:-4px; width:2px; background: rgba(128,128,128,.8);}
.meter .pin {position:absolute; top:50%; transform: translate(-50%,-50%); font-size: 1.6rem;
  filter: drop-shadow(0 2px 3px rgba(0,0,0,.4));}
.meter .ends {display:flex; justify-content:space-between; font-size:.85rem; opacity:.8; margin-top:.35rem;}
.stats {display:grid; grid-template-columns: repeat(3, 1fr); gap:.4rem; margin:.2rem 0 .9rem;}
.stat {text-align:center; padding:.45rem .2rem; border-radius:12px; border:1px solid rgba(128,128,128,.3);}
.stat .v {font-size:1.25rem; font-weight:800; line-height:1.2;}
.stat .k {font-size:.72rem; opacity:.7;}
.badges {display:flex; flex-wrap:wrap; gap:.35rem;}
.badge {font-size:.78rem; padding:.2rem .55rem; border-radius:999px; border:1px solid rgba(128,128,128,.35);}
.badge.off {opacity:.35; filter: grayscale(1);}
</style>
"""


def render_faceoff(c1: str, c2: str) -> None:
    st.markdown(
        f"""
<div class="faceoff">
  <div class="fighter one">
    <div class="tag">Country 1 · home</div><br>
    <img src="{flag_url(c1)}" alt="Flag of {name(c1)}">
    <div class="fname">{name(c1)}</div>
    <div class="fmeta">{cur(c1)} · P1(t)</div>
  </div>
  <div class="vsbox"><div class="vs">VS</div>
    <div class="def">S(t) = {cur(c2)} per 1 {cur(c1)}</div></div>
  <div class="fighter two">
    <div class="tag">Country 2 · foreign</div><br>
    <img src="{flag_url(c2)}" alt="Flag of {name(c2)}">
    <div class="fname">{name(c2)}</div>
    <div class="fmeta">{cur(c2)} · P2(t)</div>
  </div>
</div>
""",
        unsafe_allow_html=True,
    )


def render_meter(c1: str, c2: str, idx_last: float) -> None:
    # Country 1 sits on the left. Index above 100 (Country 1 strong) pulls the pin left.
    pos = float(np.clip((150 - idx_last) / 100, 0.02, 0.98)) * 100
    st.markdown(
        f"""
<div class="meter">
  <div style="font-weight:700; margin-bottom:.35rem;">⚖️ Real strength meter · Real Index at end of window: {idx_last:.1f}</div>
  <div class="bar"><div class="mid"></div><div class="pin" style="left:{pos:.1f}%">📍</div></div>
  <div class="ends"><span>{flag_emoji(c1)} {cur(c1)} strong in real terms (index &gt; 100)</span>
  <span>100 = window average</span>
  <span>{cur(c1)} weak in real terms (index &lt; 100) {flag_emoji(c2)}</span></div>
</div>
""",
        unsafe_allow_html=True,
    )


def render_scoreboard(box) -> None:
    with box:
        st.markdown("### 🏆 Scoreboard")
        title, floor, ceil = level_info(ss.xp)
        st.markdown(f"**{title}** · {ss.xp:,} XP")
        if ceil is None:
            st.progress(1.0, text="Max level reached!")
        else:
            st.progress((ss.xp - floor) / (ceil - floor), text=f"{ceil - ss.xp:,} XP to next level")
        acc = f"{100 * ss.answers_correct / ss.answers_total:.0f}%" if ss.answers_total else "—"
        stats = [("🔥 Streak", ss.streak), ("🏁 Rounds", ss.rounds_played), ("🎯 Accuracy", acc)]
        cells = "".join(f'<div class="stat"><div class="v">{v}</div><div class="k">{k}</div></div>' for k, v in stats)
        st.markdown(f'<div class="stats">{cells}</div>', unsafe_allow_html=True)
        chips = "".join(
            f'<span class="badge{"" if bid in ss.badges else " off"}" title="{desc}">{emo} {title}</span>'
            for bid, (emo, title, desc) in BADGES.items()
        )
        st.markdown(f"**Badges** ({len(ss.badges)}/{len(BADGES)})")
        st.markdown(f'<div class="badges">{chips}</div>', unsafe_allow_html=True)
        st.caption("Progress lives in this browser session and resets when you reload.")


def build_questions(c1: str, c2: str, f: dict) -> list[dict]:
    period = f"{fmt_month(f['first_date'])} → {fmt_month(f['last_date'])}"
    up = f"📈 Real appreciation: {name(c1)} became relatively more expensive"
    down = f"📉 Real depreciation: {name(c1)} became relatively cheaper"
    above = f"⬆️ Above 100: the {cur(c1)} is strong vs. its window average"
    below = f"⬇️ Below 100: the {cur(c1)} is weak vs. its window average"
    opt1, opt2 = f"{flag_emoji(c1)} {name(c1)}", f"{flag_emoji(c2)} {name(c2)}"
    higher = opt1 if f["p1_ratio"] > f["p2_ratio"] else opt2
    return [
        {
            "prompt": f"**1.** From {period}, did the {cur(c1)} **appreciate or depreciate in real terms** against the {cur(c2)}?",
            "options": [up, down],
            "answer": up if f["real_chg"] > 0 else down,
            "explain": (
                f"RER went from {fmt_num(f['rer_first'])} to {fmt_num(f['rer_last'])} ({fmt_pct(f['real_chg'])}). "
                f"That combines the nominal move in S ({fmt_pct(f['nom_chg'])}) with the relative price "
                f"level P1/P2 ({fmt_pct(f['relp_chg'])}): (1 + real) = (1 + nominal) × (1 + relative prices)."
            ),
        },
        {
            "prompt": f"**2.** At the end of the window ({fmt_month(f['last_date'])}), is the Real Index **above or below 100**?",
            "options": [above, below],
            "answer": above if f["idx_last"] > 100 else below,
            "explain": (
                f"The Real Index ended at {f['idx_last']:.1f}. Over the window it peaked at {f['peak']:.1f} "
                f"({fmt_month(f['peak_date'])}) and bottomed at {f['trough']:.1f} ({fmt_month(f['trough_date'])})."
            ),
        },
        {
            "prompt": "**3.** Which country had **higher inflation** over the window?",
            "options": [opt1, opt2],
            "answer": higher,
            "explain": (
                f"Prices rose ×{f['p1_ratio']:,.2f} in {name(c1)} ({fmt_pct(f['infl1_ann'])}/yr) vs "
                f"×{f['p2_ratio']:,.2f} in {name(c2)} ({fmt_pct(f['infl2_ann'])}/yr). Higher inflation at home "
                f"pushes RER up unless the currency depreciates enough to offset it."
            ),
        },
    ]


def score_round(round_key: str, pair_key: frozenset, questions: list[dict], picks: list[str]) -> None:
    old_title = level_info(ss.xp)[0]
    correct = [p == q["answer"] for p, q in zip(picks, questions)]
    for ok in correct:
        ss.streak = ss.streak + 1 if ok else 0
        ss.best_streak = max(ss.best_streak, ss.streak)
        if ss.streak >= 5:
            award("on_fire")
    gained = 100 * sum(correct) + (50 if all(correct) else 0)
    ss.xp += gained
    ss.rounds_played += 1
    ss.answers_total += len(correct)
    ss.answers_correct += sum(correct)
    ss.rounds[round_key] = {"questions": questions, "picks": picks, "correct": correct, "gained": gained}
    ss.revealed.add(pair_key)
    award("rookie")
    if all(correct):
        award("sharpshooter")
        ss.celebrate = True
    new_title = level_info(ss.xp)[0]
    if new_title != old_title:
        ss.toasts.append((f"Level up! You are now a **{new_title}**", "🎉"))


def render_game(c1: str, c2: str, w: pd.DataFrame, round_key: str, pair_key: frozenset) -> None:
    st.subheader("🎮 Prediction round")
    if int(w["valid"].sum()) < 12:
        st.caption("Pick a window with at least 12 months of data to play a round.")
        return
    facts = window_facts(w)
    result = ss.rounds.get(round_key)
    if result is None:
        st.caption(
            "Call it before you see the chart: +100 XP per correct answer, +50 bonus for a perfect round."
            + (" New window, new round. No peeking at the chart below! 👀" if pair_key in ss.revealed else "")
        )
        questions = build_questions(c1, c2, facts)
        with st.form(f"form_{round_key}"):
            picks = [
                st.radio(q["prompt"], q["options"], index=None, key=f"{round_key}_q{i}")
                for i, q in enumerate(questions)
            ]
            submitted = st.form_submit_button("🔒 Lock in my predictions", type="primary")
        if submitted:
            if any(p is None for p in picks):
                st.warning("Answer all three questions before locking in.")
            else:
                score_round(round_key, pair_key, questions, picks)
                st.rerun()
        return

    n_right = sum(result["correct"])
    headline = ["😬 Tough round", "🙂 Warming up", "💪 Nice call", "🏆 Perfect round!"][n_right]
    st.markdown(f"#### {headline} · {n_right}/3 correct · +{result['gained']} XP")
    for q, pick, ok in zip(result["questions"], result["picks"], result["correct"]):
        box = st.success if ok else st.error
        verdict = "Correct" if ok else f"Not quite. Answer: {q['answer']}"
        box(f"{q['prompt']}\n\nYou said: {pick}. **{verdict}.**\n\n{q['explain']}", icon="✅" if ok else "❌")


def make_chart(w: pd.DataFrame, view: str, c1: str, c2: str, log_nominal: bool) -> go.Figure:
    x = w.index
    real_color, nom_color = "#2563eb", "#f59e0b"
    s_label = f"S(t): {cur(c2)} per 1 {cur(c1)}"
    real = go.Scatter(x=x, y=w["Real_Index"], name="Real Index (100 = RER*)", mode="lines",
                      line=dict(color=real_color, width=2.4),
                      hovertemplate="Real Index %{y:.1f}<extra></extra>")
    nominal = go.Scatter(x=x, y=w["S"], name=s_label, mode="lines",
                         line=dict(color=nom_color, width=2),
                         hovertemplate=f"S %{{y:,.4g}} {cur(c2)}/{cur(c1)}<extra></extra>")
    base = go.Scatter(x=[x[0], x[-1]], y=[100, 100], name="RER* (window average = 100)", mode="lines",
                      line=dict(color="gray", width=1, dash="dash"), hoverinfo="skip")

    if view == "Both":
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        fig.add_trace(real, secondary_y=False)
        fig.add_trace(base, secondary_y=False)
        fig.add_trace(nominal, secondary_y=True)
        fig.update_yaxes(title_text="Real Index (RER* = 100)", secondary_y=False)
        fig.update_yaxes(title_text=f"{cur(c2)} per 1 {cur(c1)}", secondary_y=True, showgrid=False,
                         type="log" if log_nominal else "linear")
    elif view == "Real":
        fig = go.Figure([real, base])
        fig.update_yaxes(title_text="Real Index (RER* = 100)")
    else:
        fig = go.Figure([nominal])
        fig.update_yaxes(title_text=f"{cur(c2)} per 1 {cur(c1)}", type="log" if log_nominal else "linear")

    fig.update_layout(
        height=480, hovermode="x unified", margin=dict(l=10, r=10, t=40, b=10),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
    )
    fig.update_xaxes(title_text=None)
    return fig


def export_table(w: pd.DataFrame, c1: str, c2: str) -> pd.DataFrame:
    out = pd.DataFrame({
        "month": w.index.strftime("%Y-%m"),
        f"FX1_{cur(c1)}_per_USD": w["FX1"].to_numpy(),
        f"FX2_{cur(c2)}_per_USD": w["FX2"].to_numpy(),
        f"S_{cur(c2)}_per_{cur(c1)}": w["S"].to_numpy(),
        f"P1_CPI_{c1}": w["P1"].to_numpy(),
        f"P2_CPI_{c2}": w["P2"].to_numpy(),
        "RER": w["RER"].to_numpy(),
        "RER_star": w["RER_star"].to_numpy(),
        "Real_Index": w["Real_Index"].to_numpy(),
        "valid_month": w["valid"].to_numpy(),
    })
    return out


def render_explainer() -> None:
    with st.expander("📚 How the numbers are built"):
        st.markdown(
            "IMF exchange rates are **local currency units per US dollar** (monthly period average). "
            "With FX1 and FX2 the rates for Country 1 and Country 2:"
        )
        st.latex(r"S(t) = \frac{FX_2(t)}{FX_1(t)} \;=\; \text{units of Country 2 currency per 1 unit of Country 1 currency}")
        st.latex(r"RER(t) = S(t)\times\frac{P_1(t)}{P_2(t)}")
        st.latex(r"RER^{*} = \frac{1}{N}\sum_{t\,\in\,\text{valid months}} RER(t), \qquad \text{Real Index}(t) = 100\times\frac{RER(t)}{RER^{*}}")
        st.markdown(
            "- **Higher RER = real appreciation of Country 1.** Country 1's basket buys more of Country 2's basket.\n"
            "- **Real Index above 100:** Country 1's currency is stronger in real terms than its average over the "
            "window; below 100, weaker. RER* is recalculated whenever you move the window.\n"
            "- A valid month has all four inputs (FX1, FX2, P1, P2). Months with gaps are skipped in RER* and left blank in the chart.\n"
            "- CPI base years don't matter for the Real Index: rescaling P1 or P2 by a constant cancels out in RER/RER*.\n"
            "- S(t) is plotted in actual currency units, never normalized."
        )


def render_data_notes(d1: CountryData, d2: CountryData) -> None:
    with st.expander("🔧 Data coverage and IMF requests"):
        cov = pd.DataFrame({
            "Country": [name(d1.iso), name(d2.iso)],
            "CPI coverage": [coverage_text(d1.cpi), coverage_text(d2.cpi)],
            "Exchange-rate coverage": [coverage_text(d1.fx), coverage_text(d2.fx)],
        })
        st.dataframe(cov, hide_index=True, width="stretch")
        for note in d1.notes + d2.notes:
            st.info(note, icon="ℹ️")
        st.caption("Requests sent to the IMF SDMX 3.0 API (results cached for 6 hours):")
        st.code("\n".join(d1.log + d2.log + d1.errors + d2.errors) or "No requests logged.", language=None)


# ---------------------------------------------------------------------------
# Main app
# ---------------------------------------------------------------------------
def main() -> tuple[CountryData, CountryData] | None:
    c1, c2 = ss.c1, ss.c2

    st.markdown(
        '<div class="rer-hero"><h1>💱 RER Arena</h1>'
        "<p>Pick two economies, predict how their real exchange rate moved, then check the IMF data.</p></div>",
        unsafe_allow_html=True,
    )
    quick = st.container(horizontal=True, gap="small")
    quick.markdown("**Quick matchups:**")
    for a, b in QUICK_MATCHUPS:
        quick.button(f"{flag_emoji(a)} vs {flag_emoji(b)}", key=f"quick_{a}_{b}", on_click=cb_set_pair,
                     args=(a, b), help=f"{name(a)} vs {name(b)}")

    render_faceoff(c1, c2)
    if c1 == c2:
        st.warning("Pick two different countries to start a matchup.")
        return None

    with st.spinner(f"Fetching IMF CPI and exchange rates for {name(c1)} and {name(c2)}…"):
        d1, d2 = load_country(c1), load_country(c2)

    if d1.errors or d2.errors:
        st.error(
            "Couldn't reach the IMF API right now, so no data was loaded. The IMF data portal has "
            "occasional maintenance windows; wait a moment and retry.",
            icon="🛰️",
        )
        st.button("🔄 Retry", type="primary")
        return d1, d2

    df = build_frame(d1, d2)
    valid = df["RER"].dropna()
    if valid.empty:
        missing = [
            f"{label} for {name(d.iso)}"
            for d in (d1, d2)
            for label, s in (("CPI", d.cpi), ("exchange rates", d.fx))
            if s.empty
        ]
        detail = f"Missing: {', '.join(missing)}." if missing else "The two countries' data never overlap in time."
        st.warning(f"The IMF has no months where all four series exist for this pair. {detail} Try another matchup.",
                   icon="🕳️")
        return d1, d2

    pair_key = frozenset((c1, c2))
    ss.pairs_seen.add(pair_key)
    if len(ss.pairs_seen) >= 5:
        award("globetrotter")
    if "G163" in pair_key:
        award("euro")

    months = [d.strftime("%Y-%m") for d in pd.date_range(valid.index[0], valid.index[-1], freq="MS")]
    sel = st.select_slider(
        "📅 Sample window (start → end month). RER* is the average RER over valid months in this window.",
        options=months, value=(months[0], months[-1]), format_func=fmt_month, key=f"win_{c1}_{c2}",
    )
    start, end = pd.Timestamp(f"{sel[0]}-01"), pd.Timestamp(f"{sel[1]}-01")
    w, rer_star = window_calc(df, start, end)
    n_valid = int(w["valid"].sum())
    if n_valid == 0:
        st.warning("No valid months in this window. Widen it.", icon="🕳️")
        return d1, d2
    if n_valid < len(w):
        st.caption(f"⚠️ {len(w) - n_valid} of {len(w)} months in this window are missing at least one input and are skipped.")

    round_key = f"{c1}|{c2}|{sel[0]}|{sel[1]}"
    if ss.game_mode:
        render_game(c1, c2, w, round_key, pair_key)

    if ss.game_mode and pair_key not in ss.revealed:
        st.info("🔒 Charts, stats and the data download unlock once you lock in your predictions.", icon="🎮")
        st.button("Skip the game and show me the charts", on_click=cb_reveal, args=(pair_key,))
        return d1, d2

    facts = window_facts(w)
    if facts["first_date"] < pd.Timestamp("1985-01-01"):
        award("time_traveler")
    if max(facts["infl1_ann"], facts["infl2_ann"]) > 0.25:
        award("inflation_hunter")

    st.subheader("📊 Match stats")
    m = st.columns(5)
    m[0].metric("RER* (avg)", fmt_num(rer_star), border=True,
                help="Average of RER(t) = S(t)·P1(t)/P2(t) over valid months in the window.")
    m[1].metric("Real Index, end", f"{facts['idx_last']:.1f}", f"{facts['idx_last'] - 100:+.1f} vs. RER*", border=True)
    m[2].metric("Real change", fmt_pct(facts["real_chg"]), border=True,
                help=f"RER change from {fmt_month(facts['first_date'])} to {fmt_month(facts['last_date'])}.")
    m[3].metric(f"Nominal S change", fmt_pct(facts["nom_chg"]), border=True,
                help=f"Change in {cur(c2)} per 1 {cur(c1)}. Positive = the {cur(c1)} buys more {cur(c2)}.")
    gap_pp = (facts["infl1_ann"] - facts["infl2_ann"]) * 100
    m[4].metric("Inflation gap / yr", f"{gap_pp:+.1f} pp",
                f"{fmt_pct(facts['infl1_ann'])} vs {fmt_pct(facts['infl2_ann'])}",
                delta_color="off", delta_arrow="off", border=True,
                help=f"Annualized CPI inflation in {name(c1)} minus {name(c2)}, in percentage points.")
    render_meter(c1, c2, facts["idx_last"])

    st.subheader("📈 Charts")
    ctl = st.columns([3, 2])
    with ctl[0]:
        view = st.segmented_control("Show", ["Real", "Nominal", "Both"], key="view", required=True)
    with ctl[1]:
        log_nominal = st.checkbox("Log scale for nominal S(t)", key="log_nominal",
                                  help="Helpful for high-inflation currencies. Values stay in actual currency units.")
    st.plotly_chart(make_chart(w, view or "Both", c1, c2, log_nominal), width="stretch")
    st.caption(
        f"Real Index = 100 × RER(t) / RER*, with RER* = {fmt_num(rer_star)} over {n_valid} valid months. "
        f"Nominal S(t) is in {cur(c2)} per 1 {cur(c1)}. Rising lines mean the {cur(c1)} is getting stronger."
    )

    st.subheader("🧾 Data")
    table = export_table(w, c1, c2)
    st.dataframe(table, hide_index=True, width="stretch", height=320)
    st.download_button(
        "📥 Download CSV (all months in the window)",
        data=table.to_csv(index=False).encode("utf-8"),
        file_name=f"rer_{c1}_{c2}_{sel[0]}_{sel[1]}.csv",
        mime="text/csv",
        on_click=cb_downloaded,
        type="primary",
    )
    return d1, d2


init_state()
st.markdown(CSS, unsafe_allow_html=True)
if ss.celebrate:
    st.balloons()
    ss.celebrate = False

with st.sidebar:
    st.markdown("## 💱 Pick your matchup")
    st.selectbox("Country 1 (home)", ORDERED_CODES, format_func=country_label, key="c1")
    st.selectbox("Country 2 (foreign)", ORDERED_CODES, format_func=country_label, key="c2")
    b1, b2 = st.columns(2)
    b1.button("⇄ Swap", on_click=cb_swap, width="stretch")
    b2.button("🎲 Random", on_click=cb_random, width="stretch")
    st.toggle("🎮 Game mode", key="game_mode",
              help="Predict the outcome before the charts unlock. Turn off to see everything right away.")
    st.divider()
    scoreboard = st.container()

loaded = main()
render_explainer()
if loaded:
    render_data_notes(*loaded)
st.caption("Data: IMF SDMX 3.0 API (CPI and ER datasets). Flags: flagcdn.com. Built for an international finance class.")
render_scoreboard(scoreboard)
flush_toasts()
