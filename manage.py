import contextlib
import datetime
import os

from bs4 import BeautifulSoup
from requests import api, exceptions


def _get_public_attributes(obj):
    result = list()

    for field in dir(obj):
        if field.startswith("__") or field.endswith("__"):
            continue
        result.append(field)

    return result


def is_correct(res):
    try:
        content_type = res.headers["Content-Type"].lower()

        return (
            res.status_code == 200
            and content_type is not None
            and "html" in content_type
        )
    except Exception:
        return False


def get_content(url):
    try:
        with contextlib.closing(api.get(url, stream=True)) as response:
            if is_correct(response):
                return response.text
            else:
                return None
    except exceptions.RequestException as e:
        print(f"Error during requests to {url} : {e}")


def prepare_output(data):
    if data:
        if not os.path.exists("output"):
            os.makedirs("output")

        with open("output/data.txt", "w") as fp:
            for event in data:
                fp.write(f"{event['time']}\t{event['location']}\n")
    else:
        print("SORRY!! no rave near you.")


def main():
    html = get_content("https://algorave.com/")
    soup = BeautifulSoup(html, "html.parser")

    events = list()

    for abbr in soup.select("abbr"):
        event_time = datetime.datetime.strptime(
            abbr.get("title"), "%Y-%m-%dT%H:%M:%S"
        )
        event_location_data = abbr.next_sibling.strip()

        if (
            "india" in event_location_data.lower()
            and event_time > datetime.datetime.now()
        ):
            events.append(
                {"time": event_time, "location": event_location_data}
            )

    prepare_output(events)


if __name__ == "__main__":
    main()
