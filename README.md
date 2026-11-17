# AirAware

Explains air-quality standards and city action plans from CPCB and NCAP documents and combines them with live AQI data.

**Status:** Day 1 foundation (FastAPI skeleton, quality gates). Live URL from Day 5.

## Who it's for

Environment engineer in the Greater Chennai Corporation NCAP cell preparing monthly air-quality action reports.

## The problem

Municipal engineers in the Greater Chennai Corporation NCAP cell regularly cross-reference CPCB NAAQS notifications, AQI breakpoint tables, and city clean-air action plans when compiling monthly reports. Calculating sub-indices across up to eight pollutants with differing averaging windows (8-hour vs. 24-hour) by hand is tedious and prone to unit or threshold mix-ups. AirAware solves this by computing AQI deterministically in Python while using an LLM strictly to explain standards and cite action-plan targets.

## Data sources

CPCB NAAQS notification, National AQI technical document, NCAP guidelines, city clean-air action plans for Tamil Nadu cities, CPCB annual reports.

- https://cpcb.nic.in/
- https://airquality.cpcb.gov.in/
- https://prana.cpcb.gov.in/
- Terms: Public CPCB/MoEFCC documents.

## Hardest problem (my interview story)

Computation vs text: AQI comes from sub-indices with breakpoints and 24-hour vs 8-hour averaging. The app must compute AQI in code from the CPCB breakpoint table and only use the LLM to explain.

## Signature feature

AQI explainer: enter pollutant readings and see the computed AQI, the dominant pollutant and the health message, with the table cited.

## Target metric

AQI computed exactly for 100% of 30 test readings; standards answered correctly for 90%+ of 40 questions. (Record lookup latency is targeted under 200 ms and per-answer cost under Rs 0.40 because the small, structured CPCB/NCAP dataset fits cleanly in indexed storage with short prompts.)

## Run it locally

```bash
uv sync
cp .env.example .env   # Windows: copy .env.example .env
uv run uvicorn airaware.api.main:create_app --factory --reload