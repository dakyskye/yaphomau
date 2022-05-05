from contextlib import contextmanager
import sqlite3
from typing import Union


@contextmanager
def connect():
    global _db
    global _cur
    _db = sqlite3.connect("store.db")
    _cur = _db.cursor()
    try:
        _init()
        yield
    finally:
        _db.commit()
        _db.close()


def _init():
    with open("./init_db/init.sql", "r") as f:
        _cur.executescript(f.read())
    _db.commit()


def _must_record_country(country: str) -> int:
    _cur.execute(f"insert into countries (country) values ('{country}') returning id")
    return _cur.fetchall()[0][0]


def get_or_record_country(country: str) -> int:
    _cur.execute(f"select id from countries where country = '{country}'")
    ret = _cur.fetchall()
    if len(ret) == 0:
        return _must_record_country(country)
    return ret[0][0]


def _must_record_region(region: str, country_id: int) -> int:
    _cur.execute(
        f"insert into regions (region, country_id) values ('{region}', {country_id}) returning id"
    )
    return _cur.fetchall()[0][0]


def get_or_record_region(region: str, country_id: int) -> int:
    _cur.execute(
        f"select id from regions where region = '{region}' and country_id = '{country_id}'"
    )
    ret = _cur.fetchall()
    if len(ret) == 0:
        return _must_record_region(region, country_id)
    return ret[0][0]


def _must_record_city(city: str, region_id: int, country_id: int) -> int:
    _cur.execute(
        f"insert into cities (city, region_id, country_id) values ('{city}', {region_id}, {country_id}) returning id"
    )
    return _cur.fetchall()[0][0]


def get_or_record_city(city: str, region_id: int, country_id: int) -> int:
    _cur.execute(
        f"select id from cities where city = '{city}' and region_id = '{region_id}' and country_id = '{country_id}'"
    )
    ret = _cur.fetchall()
    if len(ret) == 0:
        return _must_record_city(city, region_id, country_id)
    return ret[0][0]


def lookup_ip(ip: str) -> Union[None, tuple]:
    _cur.execute(
        f"""
        select ips.ip, co.country, re.region, ct.city from ip_addresses ips
        inner join cities ct
            on ct.id = ips.city_id
        inner join regions re
            on re.id = ct.region_id
        inner join countries co
            on co.id = re.country_id
        where ip = '{ip}'
    """
    )

    ret = _cur.fetchall()
    if len(ret) == 0:
        return
    return ret[0]


def _must_record_ip(ip: str, country_id: int, region_id: int, city_id: int):
    _cur.execute(
        f"""
        insert into ip_addresses (ip, country_id, region_id, city_id)
        values ('{ip}', {country_id}, {region_id}, {city_id})
    """
    )


def get_or_record_ip(ip: str, country_id: int, region_id: int, city_id: int) -> tuple:
    _cur.execute(
        f"""
        select ips.ip, co.country, re.region, ct.city from ip_addresses ips
        inner join cities ct
            on ct.id = ips.city_id
        inner join regions re
            on re.id = ct.region_id
        inner join countries co
            on co.id = re.country_id
        where ip = '{ip}'
    """
    )

    ret = _cur.fetchall()
    if len(ret) == 0:
        _must_record_ip(ip, country_id, region_id, city_id)
        return get_or_record_ip(ip, country_id, region_id, city_id)
    return ret[0]
