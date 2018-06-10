import signal
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

def scrape_product(url):
    record = {}
    '''Takes in url of pdp page from alibaba.com and scrapes the product details'''
    # res = requests.get(url)
    # soup = BeautifulSoup(res.text, 'html.parser')
    driver = webdriver.PhantomJS()
    driver.set_window_size(1120, 550)
    driver.set_page_load_timeout(10)
    try:
        print "loading page: ", url
        driver.get(url)
    except Exception as e:
        print "Cannot load page: ", e
        try:
            driver.service.process.send_signal(signal.SIGTERM)
            driver.quit()
        except:
            print "Fails to quit the driver."
        return record
    print "Scraping Page: ", url
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')

    # Title #
    title = soup.find('span', class_="ma-title-text").text if soup.find('span', class_="ma-title-text") is not None else ""
    record['title'] = title.encode('utf-8')

    # Images #
    image_list = []
    images = soup.find_all('div', class_ = 'thumb')
    for item in images:
        img = item.find('img').get('src') or ""
        if img is not "":
            image_list.append(img[2:].encode('utf-8'))
    record['images'] = image_list

    # Description #
    descp = soup.find('div', id = 'J-rich-text-description') or ""
    record['description'] = str(descp)
    # Attributes #
    ##############
    ma_briefs = soup.find_all('dl', class_='ma-brief-item')
    for item in ma_briefs:
        key_ = item.find('dt', class_='ma-brief-item-key')
        if key_ is None:
            continue
        key = " ".join(key_.text.split())
        key_str = key.encode('utf-8')
        value_ = item.find('dd', class_='ma-brief-item-val')
        value = " ".join(value_.text.split())
        value_str = value.encode('utf-8')
        record[key_str[-1]] = value_str

    product_details = soup.find('div', class_='do-entry do-entry-separate')
    properties = product_details.find_all('dl', class_='do-entry-item') if product_details is not None else []
    for item in properties:
        key_ = item.find('span', class_='attr-name J-attr-name')
        if key_ is None:
            continue
        key = " ".join(key_.text.split())
        key_str = key.encode('utf-8')
        value_ = item.find('div', class_='ellipsis')
        value = " ".join(value_.text.split())
        value_str = value.encode('utf-8')
        record[key_str[:-1]] = value_str

    pack_details = soup.find('div', class_='do-entry do-entry-full')
    properties = pack_details.find_all('dl', class_='do-entry-item') if pack_details is not None else []
    for item in properties:
        key_ = item.find('dt', class_='do-entry-item-key')
        if key_ is None:
            continue
        key = " ".join(key_.text.split())
        key_str = key.encode('utf-8')
        value_ = item.find('dd', class_='do-entry-item-val')
        value = " ".join(value_.text.split())
        value_str = value.encode('utf-8')
        record[key_str] = value_str

    # Company Profile #
    print "loading company profile."
    try:
        driver.find_element_by_xpath('//*[@id="J-ls-grid-desc"]/div[1]/div/div[2]/div/div[1]/div/div/div/div/div[2]/div').click()
        wait = WebDriverWait(driver, 10)
        wait.until(
            EC.presence_of_element_located((By.XPATH, '''//*[@id="J-ls-grid-desc"]/div[2]/div[2]/div[1]/div/div/div/div[1]/table/tbody/tr[1]/th'''))
        )
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        company_url = soup.find('a', class_='esite-link-default', href=True)
        if company_url is not None:
            record['company url'] = company_url['href']
        company_profile_tables = soup.find_all('table', class_='content-table')
        if len(company_profile_tables) > 0:
            for table in company_profile_tables:
                rows = table.find_all('tr')
                for item in rows:
                    key_ = item.find('th', class_='col-title')
                    if key_ is None:
                        continue
                    key = " ".join(key_.text.split())
                    key_str = key.encode('utf-8')
                    value_ = item.find('td', class_='col-value')
                    value = " ".join(value_.text.split())
                    value_str = value.encode('utf-8')
                    record[key_str[:-1]] = value_str
    except:
        print "failed loading company profile."
    try:
        driver.service.process.send_signal(signal.SIGTERM)
        driver.quit()
    except:
        print "Fails to quit the driver."
    print len(record)
    return record

def main():
    url =  raw_input('Enter pdp url:\n')
    record = scrape_product(url)
    print len(record)

if __name__ == '__main__':
    main()
