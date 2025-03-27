"""
projekt_3.py: třetí projekt do Engeto Online Python Akademie

author: Tereza Růžičková
email: terkaruzicka@seznam.cz
discord: terka_99
"""

import sys
import csv
from pathlib import Path
from requests import get
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse


# Function gets simplified name of running script file.

def get_script_name():
    fp = Path(sys.argv[0])
    return fp.name


# Function prints OK text with color green.

def print_ok():
    print("\033[32m[OK]\033[0m")


# Function prints NOK text with color red.

def print_nok():
    print("\033[31m[NOK]\033[0m")


# Function prints error message related to invalid input arguments together with script execution instructions.

def print_input_error(reason_msg):
    print(
        reason_msg,
        f"To run script '{get_script_name()}' write: python {sys.argv[0]} <election_location_url> <result_output_csv_file>",
        sep="\n"
    )


# Function prints message about terminating running script file.

def print_script_termination():
    print(f"\nTERMINATING {get_script_name()}\n")


# Function checks if the given value is valid URL.

def is_valid_url(url):
    try:
        parsed_url = urlparse(url)
        return all([parsed_url.scheme, parsed_url.netloc, parsed_url.path])
    except ValueError:
        return False


# Function checks if the given output filename is valid .csv file.

def is_valid_csv_file(csv_file):
    if len(csv_file.strip()) == 0:
        return False
    fp = Path(csv_file)
    return fp.suffix == ".csv" and fp.name == csv_file


# Function validates input arguments.

def validate_input_arguments():
    # Script expects exactly 2 arguments on input
    if len(sys.argv[1:]) != 2:
        return False, "Incorrect number of input arguments."

    # First argument must be valid URL value
    if not is_valid_url(sys.argv[1]):
        return False, f"Given input value '{sys.argv[1]}' is not a valid URL."

    # Second argument must be valid .csv file for storing scraped data.
    if not is_valid_csv_file(sys.argv[2]):
        return False, f"Given input value '{sys.argv[2]}' is not a valid .csv file."

    return True, "OK."


# Function gets base URL from given original URL.

def get_base_url(url):
    parsed_url = urlparse(url)
    new_path = "/".join(parsed_url.path.rstrip("/").split("/")[:-1])
    return urljoin(url, new_path + "/")


# Function downloads content from given URL and parses it to HTML.

def get_parsed_html(url):
    return BeautifulSoup(get(url).text, features="html.parser")


# Function retrieves row data from tables related to city info from given HTML.

def get_all_cities_table_rows(parsed_html):
    city_rows = dict()

    # Get all divs with tables
    t1_divs = parsed_html.find_all("div", { "class": "t1" })
    t2_divs = parsed_html.find_all("div", { "class": "t2" })
    t3_divs = parsed_html.find_all("div", { "class": "t3" })

    if t1_divs:
        divs = t1_divs
    elif t2_divs:
        divs = t2_divs
    else:
        divs = t3_divs

    dc = 0

    # In each table find all rows related to city info
    for div in divs:
        dc += 1
        div_city_rows = list()
        all_div_tr_tags = div.find_all("tr")
        for tr_tag in all_div_tr_tags:
            code_header_att = "t" + str(dc) + "sa1 t" + str(dc) + "sb1"
            name_header_att = "t" + str(dc) + "sa1 t" + str(dc) + "sb2"
            if (tr_tag.find("td", { "headers": code_header_att, })
                    and tr_tag.find("td", { "headers": name_header_att })
                    and not tr_tag.find("td", { "class": "hidden_td" })):
                div_city_rows.append(tr_tag)
        city_rows[dc] = div_city_rows

    return city_rows


# Function gets basic info about city from HTML data row (code, name, ref).

def get_city_info(city_row, div_counter):
    # For each city election reference info we want retrieve city code, name and actual ref path
    code_header_att = "t" + str(div_counter) + "sa1 t" + str(div_counter) + "sb1"
    name_header_att = "t" + str(div_counter) + "sa1 t" + str(div_counter) + "sb2"
    city_code_col = city_row.find("td", { "headers": code_header_att })
    city_code = city_code_col.get_text(strip=True)
    city_ref = city_code_col.a.attrs["href"]
    city_name = city_row.find("td", { "headers": name_header_att }).get_text(strip=True)

    # Wrap retrieved data into dictionary as city row record
    city_info = {
        "code": city_code,
        "ref": city_ref,
        "location": city_name
    }

    return city_info


# Function gets info about all found cities from given URL, where
# important part is reference (relative path) at each city, which
# leads to election data of that city.

def get_all_cities_info(url):
    all_cities_info = list()
    parsed_html = get_parsed_html(url)

    city_rows = get_all_cities_table_rows(parsed_html)
    for city_rows_key in city_rows.keys():
        for city_row in city_rows[city_rows_key]:
            all_cities_info.append(get_city_info(city_row, city_rows_key))

    return all_cities_info


# Function updates info of each given city with established valid URL
# which lead to election data of particular city.

def update_cities_with_urls(base_url, all_cities_info):
    cities_with_urls = list()

    for city_info in all_cities_info:
        city_url = urljoin(base_url, city_info["ref"])
        if is_valid_url(city_url):
            updated_city_info = {
                "code": city_info["code"],
                "location": city_info["location"],
                "url": city_url
            }
            cities_with_urls.append(updated_city_info)

    return cities_with_urls


# Function gets election info for particular city from summary table.

def get_city_election_sum_info(parsed_html):
    info_table = parsed_html.find("table", { "id": "ps311_t1" })
    registered = info_table.find("td", { "class": "cislo", "headers": "sa2", "data-rel": "L1" }).get_text(strip=True)
    envelopes = info_table.find("td", {"class": "cislo", "headers": "sa3", "data-rel": "L1"}).get_text(strip=True)
    valid = info_table.find("td", {"class": "cislo", "headers": "sa6", "data-rel": "L1"}).get_text(strip=True)

    city_election_sum_info = {
        "registered": registered,
        "envelopes": envelopes,
        "valid": valid
    }

    return city_election_sum_info


# Function gets info about each political party and its votes received in election
# in particular city or location.

def get_city_election_parties_info(parsed_html):
    divs = parsed_html.find_all("div", { "class": "t2_470" })
    tc = 0
    parties_info = list()

    for div in divs:
        tc += 1

        # Get all party names from table
        party_names = list()
        party_names_headers = "t" + str(tc) + "sa1 t" + str(tc) + "sb2"
        party_names_tds = div.find_all("td", { "headers": party_names_headers })
        for party_name_td in party_names_tds:
            party_names.append(party_name_td.get_text(strip=True))

        # Get all valid votes from table
        party_votes = list()
        party_votes_headers = "t" + str(tc) + "sa2 t" + str(tc) + "sb3"
        party_votes_tds = div.find_all("td", { "headers": party_votes_headers })
        for party_votes_td in party_votes_tds:
            party_votes.append(party_votes_td.get_text(strip=True))

        # Merge retrieved data together
        for i in range(len(party_names)):
            party_info = {
                "party_name": party_names[i],
                "party_votes": party_votes[i]
            }
            parties_info.append(party_info)

    return parties_info


# Function gets whole election info data package for particular city or location.

def get_city_election_data(city_info):
    city_election_data = {
        "code": city_info["code"],
        "location": city_info["location"]
    }
    parsed_html = get_parsed_html(city_info["url"])
    election_sum_info = get_city_election_sum_info(parsed_html)
    election_parties_info = get_city_election_parties_info(parsed_html)

    city_election_data["registered"] = election_sum_info["registered"]
    city_election_data["envelopes"] = election_sum_info["envelopes"]
    city_election_data["valid"] = election_sum_info["valid"]

    for party_info in election_parties_info:
        city_election_data[party_info["party_name"]] = party_info["party_votes"]

    return city_election_data


# Function tries to download all election data from given URL.

def try_download_data(feed_url):
    election_data = list()
    base_nav_url = get_base_url(feed_url)

    # Get basic info about each city from specified location (URL) which will be used for scraping election data
    all_cities_info = get_all_cities_info(feed_url)
    if len(all_cities_info) == 0:
        return False, election_data, f"Unable to find any city info which would lead to election data from URL '{feed_url}'."

    # Prepare valid URL for each city from which will be scraped election data
    cities_with_urls = update_cities_with_urls(base_nav_url, all_cities_info)
    if len(cities_with_urls) == 0:
        return False, election_data, f"Unable prepare any valid URL from {base_nav_url} and retrieved cities info {all_cities_info}."

    # Download election data for each city and store into result list
    for city_info in cities_with_urls:
        election_data.append(get_city_election_data(city_info))

    return True, election_data, "OK."


# Function saves dictionary data into given csv file.

def save_to_csv_file(election_data, csv_filename):
    with open(csv_filename, mode="w", newline="") as csv_file:
        field_names = election_data[0].keys()
        csv_writer = csv.DictWriter(csv_file, delimiter=";", lineterminator="\r\n", fieldnames=field_names)
        csv_writer.writeheader()

        for city_election_data in election_data:
            csv_writer.writerow(city_election_data)


# Function performs data scraping by the given inputs.

def scrape_data():
    # Perform basic inputs validations

    print("\nVALIDATING INPUTS")
    (val_res, val_msg) = validate_input_arguments()
    if not val_res:
        print_input_error(val_msg)
        print_nok()
        print_script_termination()
        sys.exit(1)
    else:
        print_ok()

    # Proceed with data scraping - retrieve data from given URL and temporarily stores in variable

    source_url = sys.argv[1]
    print(f"DOWNLOADING DATA FROM SPECIFIED URL: {source_url}")

    (result, data, message) = try_download_data(source_url)
    if not result:
        print(f"Downloading data from '{source_url}' did not succeed. {message}")
        print_nok()
        print_script_termination()
        sys.exit(1)
    else:
        print_ok()

    # Proceed with saving downloaded data to a specified .csv file

    filename = sys.argv[2]
    print(f"SAVING DATA TO FILE: {filename}")

    save_to_csv_file(data, filename)
    print_ok()

    # After all work is done, print info about self termination
    print_script_termination()

if __name__ == "__main__":
    scrape_data()
else:
    print_input_error(f"Script '{get_script_name()}' must be run directly.")