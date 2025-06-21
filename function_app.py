import logging

import azure.functions as func
import requests
from icalendar import Calendar

app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)

@app.route(route="patch", methods=["GET"])
def patch(req: func.HttpRequest) -> func.HttpResponse:
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
    
    calendar: Calendar | None = None
    try: 
        calendar = Calendar.from_ical(url_response.content)
    except ValueError as e:
        logging.error(f"Failed to parse the calendar: {e}")
        return func.HttpResponse(
            f"Invalid calendar data at '{url}'.",
            status_code=400
        )
    
    if not calendar:
        return func.HttpResponse(
            "No calendar data found.",
            status_code=400
        )

    calendar.add_missing_timezones()
    return func.HttpResponse(
        calendar.to_ical(), 
        mimetype='text/calendar'
    )
