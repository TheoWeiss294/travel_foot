# Travel Foot

**Find relative sports events in time and space.**  
This project helps football fans discover sequences of matches (e.g., UEFA Champions League) that can realistically be attended within a given travel window, based on dates and distances between venues.

---

## Features
- Fetch fixtures from the [Football-Data.org API](https://www.football-data.org/).
- Map team names to their home venues and geocode them via [OpenStreetMap Nominatim](https://nominatim.openstreetmap.org/).
- Cache venue coordinates locally to reduce API calls.
- Compute distances between venues using the haversine formula.
- Build a graph of matches and search for feasible travel paths given:
  - `min_games` – minimum matches to attend  
  - `max_days` – max number of days between first and last match  
  - `max_dist` – max travel distance allowed between matches  
  - `window_days` – total search window for fixtures

---

## Requirements

- Python **3.11+**
- A [Football-Data.org](https://www.football-data.org/) API key.

### Environment Variable
Export your API key in your shell config (`~/.zshrc` or equivalent):
