from datetime import datetime
import logging

import azure.functions as func
import requests
from icalendar import Calendar

app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)

@app.route(route="normalize", methods=["GET"])
def normalize(req: func.HttpRequest) -> func.HttpResponse:
    logging.info(f"Processing request.")

    url = req.params.get('ics_url')
    if not url:
        return func.HttpResponse(
            "Missing 'ics_url' parameter in the query string.",
            status_code=400
        )

    url_response = requests.get(url)
    if not url_response.ok:
        return func.HttpResponse(
            f"Failed to fetch the calendar from '{url}'.",
            status_code=url_response.status_code
        )
    
    calendar: Calendar = None
    missing_tzids: set[str] = {}
    try: 
        calendar = Calendar.from_ical(url_response.content)
        if not calendar:
            return func.HttpResponse(
                "No calendar data found.",
                status_code=400
            )
        
        missing_tzids = calendar.get_missing_tzids()
        if not missing_tzids:
            return func.HttpResponse(
                calendar.to_ical(),
                mimetype='text/calendar'
            )
        
    except ValueError as e:
        logging.error(f"Failed to parse the calendar: {e}")
        return func.HttpResponse(
            f"Invalid calendar data at '{url}'.",
            status_code=400
        )

    for event in calendar.events:
        patched = False
        if event['DTSTART'].params.get('TZID') in missing_tzids:
            event.DTSTART = event.DTSTART.astimezone(event.DTSTART.tzinfo)
            patched = True
        if event['DTEND'].params.get('TZID') in missing_tzids:
            event.DTEND = event.DTEND.astimezone(event.DTEND.tzinfo)
            patched = True
        if patched:
            logging.info(f"Patched event: uid='{event.uid}'.")

    return func.HttpResponse(
        calendar.to_ical(), 
        mimetype='text/calendar'
    )
