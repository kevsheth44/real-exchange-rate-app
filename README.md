# 💱 RER Arena: Real Exchange Rate App

A Streamlit app that computes and plots the real exchange rate (RER) between any two IMF economies (or the Euro Area) using monthly IMF CPI and exchange-rate data from January 1976 where available. It adds a light game layer: big flags in a head-to-head "face-off", prediction rounds, XP, levels, streaks and badges.

## Economics

Country 1 is the "home" country and Country 2 the "foreign" country.

| Symbol | Definition |
|---|---|
| FX1(t), FX2(t) | IMF exchange rates, local currency units per 1 USD (monthly period average) |
| S(t) | FX2(t) / FX1(t) = units of Country 2 currency per 1 unit of Country 1 currency |
| P1(t), P2(t) | Monthly CPI index of Country 1 and Country 2 |
| RER(t) | S(t) × P1(t) / P2(t) |
| RER* | Average of RER(t) over valid months in the user-selected window |
| Real Index(t) | 100 × RER(t) / RER* |

- A **valid month** has all four inputs (FX1, FX2, P1, P2). Months with gaps are excluded from RER* and left blank in the charts.
- **RER* is recalculated** every time the start or end month changes.
- A **higher RER** means a real appreciation of Country 1's currency: Country 1's basket buys more of Country 2's basket. A Real Index above 100 means Country 1's currency is stronger in real terms than its average over the window.
- **Nominal S(t) is plotted in actual currency units** (Country 2 currency per 1 unit of Country 1 currency), never normalized. An optional log scale changes only the axis, not the units.

## Features

- Choose Country 1 and Country 2 from IMF member economies and the Euro Area (IMF code `G163`).
- Pick the sample window with a month-range slider.
- Interactive Plotly charts: **Real**, **Nominal**, or **Both** (Both uses separate left and right axes).
- CSV download of every month in the selected window with all inputs and calculations: FX1, FX2, S, P1, P2, RER, RER*, Real Index and a valid-month flag.
- Coverage table, data notes and the exact IMF requests used, in an expander at the bottom of the page.

### Game layer

- **Face-off header** with large flags of the two selected countries.
- **Prediction rounds.** Before the charts unlock, answer three questions about the selected window: did Country 1's currency appreciate or depreciate in real terms, is the Real Index above or below 100 at the end of the window, and which country had higher inflation. Each correct answer earns 100 XP, and a perfect round earns a 50 XP bonus. Each answer comes with an explanation that ties the result back to the formulas. A new window starts a new round.
- **Levels** from FX Intern to IMF Chief Economist, plus a streak counter, accuracy and nine badges, shown in the sidebar.
- **Quick matchups**, a random matchup button, and a swap button that flips Country 1 and Country 2.
- **Game mode** can be switched off in the sidebar to show charts immediately. A "Skip" button is also available.

Game progress is stored in the browser session only and resets on reload.

## Data

Source: IMF SDMX 3.0 API, `https://api.imf.org/external/sdmx/3.0`

| Series | Dataflow | Key |
|---|---|---|
| CPI, all items, index, monthly | `IMF.STA/CPI` | `{ISO3}.CPI._T.IX.M` |
| Exchange rate, LCU per USD, period average, monthly | `IMF.STA/ER` | `{ISO3}.XDC_USD.PA_RT.M` |

Requests look like:

```
https://api.imf.org/external/sdmx/3.0/data/dataflow/IMF.STA/CPI/~/USA.CPI._T.IX.M?c[TIME_PERIOD]=ge:1976-M01
```

with the header `Accept: text/csv`. If that fails, the app retries without the time filter and then as SDMX-JSON. Responses are cached for 6 hours; failed requests are not cached, so the Retry button works.

### Data handling and caveats

- **Coverage varies.** Many countries have short or patchy CPI or exchange-rate histories. The app uses whatever months exist and reports coverage.
- **US dollar.** The IMF may not publish a USD-per-USD series, so FX = 1 is used for the United States (and for Panama, Palau, the Marshall Islands and Micronesia, which use the dollar or a currency at par with it).
- **Euro Area (G163).** If the IMF has no G163 exchange-rate series, the euro's USD rate from 1999 is taken from a founding member's series, which is identical after adoption. If G163 has no CPI series, the HICP index is used.
- **Euro members.** Pre-adoption exchange rates in a legacy currency (for example French francs) are converted to euro-equivalent units at the irrevocable conversion rate so S(t) has no artificial jump at adoption. If a national series stops at adoption, it is spliced with the euro's USD rate. This does not change the Real Index, because constant unit changes cancel out in RER / RER*.
- **Redenominations and hyperinflation** (for example Argentina, Venezuela, Zimbabwe) can create breaks the IMF data may not fully smooth.
- The IMF data portal has occasional maintenance windows. If the app reports that it cannot reach the IMF, wait and press Retry.
- Optional: if the IMF ever requires an API key, add `IMF_SUBSCRIPTION_KEY` to the app's Streamlit secrets and it will be sent as `Ocp-Apim-Subscription-Key`.

## Files

| File | Purpose |
|---|---|
| `app.py` | The Streamlit app |
| `requirements.txt` | Python packages (tested with Python 3.12) |
| `README.md` | This file |

## Run it

**Streamlit Community Cloud (no local Python needed):** go to share.streamlit.io, sign in with GitHub, choose **Create app**, select this repository, branch `main` and main file `app.py`. Under **Advanced settings**, choose Python 3.12, then deploy.

**Locally (optional):**

```
pip install -r requirements.txt
streamlit run app.py
```

## AI usage log

- Model: Claude Opus 5.5 (Anthropic)
- Date: October 26, 2026
- Prompt: _paste your prompt(s) here_
