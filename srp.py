# -*- coding: utf-8 -*-
import git
import signal
import csv
import json
import pdp
from selenium import webdriver
from bs4 import BeautifulSoup

# scrape SRP #
##############
def scrape_srp(search_input, page_input, cat_input):
    search_term = "_".join(search_input.split())
    page = page_input.replace(" ", "")
    cat = cat_input.replace(" ", "")
    if cat == "":
        url = "https://www.alibaba.com/products/" + search_term + "/" + page + ".html"
        file_name = search_term + "_" + page
    else:
        url = "https://www.alibaba.com/products/F0/" + search_term + "/" + cat + "/" + page + ".html"
        file_name = search_term + "_" + cat + "_" + page
    print "Searching: ", url

    records = []
    records_csv = []
    keys = []

    driver = webdriver.PhantomJS()
    driver.set_window_size(1120, 550)
    driver.set_page_load_timeout(10)
    try:
        driver.get(url)
    except Exception as e:
        print "Cannot load page: ", e
        try:
            driver.service.process.send_signal(signal.SIGTERM)
            driver.quit()
        except:
            print "Fails to quit the driver."
        return
    print "Scraping SRP: ", url
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    try:
        driver.service.process.send_signal(signal.SIGTERM)
        driver.quit()
    except:
        print "Fails to quit the driver."

    products = soup.find_all('div', class_='main-wrap')
    print "No. of products in this page: ", len(products)
    for i, product in enumerate(products):
        # Title #
        title = product.find('h2', class_='title')
        if title is None:
            continue
        record = {}
        # MOQ #
        moq_ = product.find('div', class_='min-order').text if product.find('div', class_='min-order') is not None else ""
        moq = " ".join(moq_.split())
        record['moq'] = moq.encode('utf-8')
        # Price #
        price_ = product.find('div', class_='price').text if product.find('div', class_='price') is not None else ""
        price = " ".join(price_.split())
        record['price'] = price.encode('utf-8')
        # SRP-attributes #
        attrs = product.find_all('div', class_="kv")
        for item in attrs:
            attr = " ".join(item.text.split())
            attr_str = attr.encode('utf-8')
            key_value = attr_str.split(':')
            record[key_value[0]] = key_value[1]
        # PDP #
        pdp_url = product.find('a', href=True)
        res = pdp.scrape_product("http:" + pdp_url['href'])
        record.update(res)
        print len(record)
        records.append(record)

    json_file = "output/" + file_name + '.json'
    with open(json_file, 'w') as fp:
        json.dump(records, fp)

    for item in records:
        if 'description' in item.keys():
            del item['description']
        records_csv.append(item)
        for key in item.keys():
            if key not in keys:
                keys.append(key)

    csv_file = "output/" + file_name + '.csv'
    with open(csv_file, 'wb') as f:
        w = csv.DictWriter(f, keys)
        w.writeheader()
        w.writerows(records_csv)

    repo = git.Repo('.')
    repo.git.add('./output/')
    repo.git.commit(m=file_name)
    origin = repo.remotes['origin']
    origin.push('running-branch')


def main():
    search_input =  raw_input('Enter search term:\n')
    page_input = raw_input('Enter page number:\n')
    cat_input = raw_input('Enter category:\n')
    scrape_srp(search_input, page_input, cat_input)

if __name__ == '__main__':
    main()
