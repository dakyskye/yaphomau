import re
import requests

from yaphomau import store

_API_URI = "https://ipinfo.io/{}/geo"


def event_loop():
    for ip in ask_for_ip():
        try:
            process_ip(ip)
        except APIRequestException as e:
            print(e)
            return


def get_ip():
    ip = input("please input a valid IP address: ")
    if not re.match(r"^[0-9]+.[0-9]+.[0-9]+.[0-9]+$", ip):
        raise ValueError("the inputted IP address does not seem to be a valid one")
    return ip


def ask_for_ip(retry=False):
    if retry:
        ans = input("would you like to try again? [Y/n] ")
    else:
        ans = input("would you like to query information about an IP address? [Y/n] ")

    if ans.casefold() == "n":
        return

    try:
        retry = False
        yield get_ip()
    except ValueError as e:
        retry = True
        print(e)

    yield from ask_for_ip(retry)


class APIRequestException(Exception):
    pass


def request_and_record_ip(ip: str) -> tuple:
    res = requests.get(url=_API_URI.format(ip))
    if res.status_code != 200:
        raise APIRequestException("the response from the API isn't acceptable")

    data = res.json()

    if data.get("bogon", False):
        return (ip, "**WHAT**", "**A**", "**TRY**")

    country_id = store.get_or_record_country(data["country"])
    region_id = store.get_or_record_region(data["region"], country_id)
    city_id = store.get_or_record_city(data["city"], region_id, country_id)

    return store.get_or_record_ip(ip, country_id, region_id, city_id)


def process_ip(ip: str):
    res = store.lookup_ip(ip)
    if not res:
        res = request_and_record_ip(ip)
        print("requesting the IP information with the API")
    else:
        print("requesting the IP information from the database")
    print(f"IP: {res[0]}; Country: {res[1]}; Region: {res[2]}; City: {res[3]}")
