# Slab Radar

Weekly NFL usage breakouts (nflverse) next to card population and gem rates, for a personal card strategy.
Live site: https://rdsciv.github.io/slab-radar/ — personal research tool, not financial advice.

- **Breakout radar**: target share, air-yards share, snap share, carry share, red-zone share, xFP, dropbacks — recorded
  nflverse data only (no route estimates). Score and P(share rose) are labeled model outputs. Definitions on the site's
  Methodology page.
- **Cards**: population and shrunk gem rates (with n and 95% intervals) from GemRate player exports. No sale prices
  until a comp source is approved (see `docs/data-sources.md`).

## Run locally

```sh
cd etl && uv run pytest                                          # ETL tests (live nflverse checks)
uv run --project etl slab-radar run --season 2026 --stage nfl    # radar + player JSON → web/public/data
uv run --project etl slab-radar run --season 2026 --stage cards  # needs local fixtures/gemrate/*.csv (not committed)
cd web && npm ci && npm test && npm run build                    # static site → web/out
```

GitHub Actions rebuilds and deploys on push, on demand, and Tue/Thu 15:17 UTC. Plan, schema and source evaluation are in `docs/`.
