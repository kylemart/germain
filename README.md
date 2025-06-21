# Germain 🕰️✨

This Azure Function provides an HTTP endpoint to patch missing or incorrect Windows time zone IDs (TZID) in iCalendar (.ics) files, converting them to Olson (IANA) time zone names for better compatibility.

I created this project after running into issues displaying calendar events on my [TRMNL](https://usetrmnl.com). For some reason, Outlook refused to serve my iCalendar with a `VTIMEZONE` for Eastern Standard Time despite having events with this TZID. This didn't gel well with the gem [TRMNL uses](https://github.com/icalendar/icalendar). Hopefully TRMNL will address this internally, but in the meantime this this has proven useful as a workaround.

## Usage 🛠️

### HTTP Endpoint 🌐
- **Route:** `/api/patch`
- **Method:** `GET`
- **Query Parameter:** `ics_url` (URL to the `.ics` file)

#### Example Request
```
GET /api/patch?ics_url=https://example.com/calendar.ics
```

#### Example Response
- Returns the patched `.ics` file with corrected TZIDs.
- If errors occur (missing parameter, fetch failure, invalid calendar), returns an appropriate HTTP error code and message.

## Local Development 💻

### Prerequisites 📋
- Python 3.12+
- [Azure Functions Core Tools](https://docs.microsoft.com/azure/azure-functions/functions-run-local)
- [pip](https://pip.pypa.io/en/stable/)

### Setup 🏗️
1. Create and activate a virtual environment:
   ```sh
   python3 -m venv .venv
   source .venv/bin/activate
   ```
2. Install dependencies:
   ```sh
   python -m pip install -r requirements.txt
   ```
3. Start the function locally:
   ```sh
   func start
   ```
