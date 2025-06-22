import logging

import azure.functions as func
import requests
from icalendar import Calendar
from icalendar.timezone.windows_to_olson import WINDOWS_TO_OLSON

app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)

@app.route(route="patch", methods=["GET"])
def patch(req: func.HttpRequest) -> func.HttpResponse:
    logging.info(f"Processing request.")

    url = req.params.get('ics_url')
    if not url:
        logging.info("Missing 'ics_url' parameter.")
        return func.HttpResponse(
            "Missing 'ics_url' parameter in the query string.",
            status_code=400
        )

    url_response = requests.get(url)
    if not url_response.ok:
        logging.info(f"Failed to fetch the calendar.")
        return func.HttpResponse(
            f"Failed to fetch the calendar at '{url}'.",
            status_code=url_response.status_code
        )
    
    calendar: Calendar | None = None
    try: 
        calendar = Calendar.from_ical(url_response.content)
    except ValueError as e:
        logging.info(f"Failed to parse the calendar: {e}")
        return func.HttpResponse(
            f"Invalid calendar data at '{url}'.",
            status_code=400
        )
    
    if not calendar:
        logging.info("No calendar data found.")
        return func.HttpResponse(
            "No calendar data found.",
            status_code=400
        )

    missing_tzids: list[str] | None = None
    try: 
        missing_tzids = calendar.get_missing_tzids()
    except ValueError as e:
        logging.info(f"Failed to get missing TZIDs: {e}")
        return func.HttpResponse(
            f"Invalid calendar data at '{url}'.",
            status_code=400
        )
    
    if not missing_tzids:
        logging.info("No missing TZIDs found.")
        return func.HttpResponse(
            calendar.to_ical(), 
            mimetype='text/calendar'
        )

    for event in calendar.events:
        patched = False
        for dt_key in ['DTSTART', 'DTEND']:
            dt = event.get(dt_key)
            tzid = dt.params.get('TZID')
            if tzid in missing_tzids:
                dt.params['TZID'] = WINDOWS_TO_OLSON.get(tzid, tzid)
                patched = True
        if patched:
            logging.info(f"Patched TZIDs for event '{event.uid}'.")

    return func.HttpResponse(
        calendar.to_ical(), 
        mimetype='text/calendar'
    )
