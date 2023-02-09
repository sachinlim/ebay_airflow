import requests
from bs4 import BeautifulSoup
import statistics


def format_search_term(link):
    # eBay wants to use + in place of spaces in the search term
    formatted_search_term = link.replace(" ", "+")

    return formatted_search_term


def website_data(search):
    # URL contains search filters: "Exact words, any order", Used, Sold listings, and UK only
    url = f'https://www.ebay.co.uk/sch/i.html?_from=R40&_nkw={search}' \
          f'&_in_kw=4&_ex_kw=&_sacat=0&LH_Sold=1&_udlo=&_udhi=&LH_ItemCondition=4&_samilow=&_samihi=' \
          f'&_stpos=M300AA&_sargn=-1%26saslc%3D1&_fsradio2=%26LH_LocatedIn%3D1&_salic=3&LH_SubLocation=1' \
          f'&_sop=12&_dmd=1&_ipg=60&LH_Complete=1&rt=nc&LH_PrefLoc=1'

    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'html.parser')
    return soup


def get_data(soup):
    products = []
    results = soup.find('div', {'class': 'srp-river-results clearfix'}).find_all('li', {'class':
                                                                                            's-item s-item__pl-on-bottom'})
    for item in results:
        price = item.find('span', class_='s-item__price').text.replace('£', '').replace(',', '')

        # Removing the results that show a range of prices for the same (sold) listing
        # For example, £169.99 to £189.99 does not show the exact sold price
        if 'to' not in price:
            price = float(price)
            products.append(price)

    original_results_length = len(products)

    # Results must be trimmed as some outliers may exist in the list of sold prices from the search results
    # The results are trimmed from both ends of the list once the data has been sorted from low to high
    trim_percentage = 0.15
    trimming = original_results_length * trim_percentage
    trimming = round(trimming)

    products.sort()
    trimmed_results_list = products[trimming:-trimming]

    return trimmed_results_list, trim_percentage, trimming, original_results_length


def calculate_range(result_list):
    # Calculating the first and last values in the sorted list of results for the range
    minimum_value = min(result_list)
    maximum_value = max(result_list)

    return minimum_value, maximum_value


def get_average(search_term):
    formatted_search_term = format_search_term(search_term)

    soup = website_data(formatted_search_term)
    trimmed_result_list, trim_percentage, trimming, original_results_length = get_data(soup)

    if not trimmed_result_list:
        return 'no results'

    else:
        # There are sold items in the search result and the list has values

        trimmed_mean = statistics.mean(trimmed_result_list)
        # minimum_value, maximum_value = self.calculate_range(trimmed_result_list)
        return f'{trimmed_mean:.2f}'


print(get_average('rtx 3070 ti gpu'))
