from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium import webdriver
import selenium.webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import json
import pika
import time

time.sleep(5)

options = webdriver.ChromeOptions()  
options.add_argument('--no-sandbox')
driver = webdriver.Remote(
    command_executor='http://selenium:4444/wd/hub',
    options=options,
)
min_age = 15
mid_age = 40
max_age = 100
url = "https://www.interpol.int/How-we-work/Notices/Red-Notices/View-Red-Notices"
driver.get(url)

unique_ids = set()

nati = []
for i in range(2, 218):
    wait = WebDriverWait(driver, 10)
    nation_option = wait.until(EC.element_to_be_clickable((By.XPATH, f"/html/body/div[1]/div[1]/div[6]/div/div[1]/div/div/form/div[3]/select/option[{i}]")))
    nati.append(nation_option.get_attribute("value"))

# Connection for RabbitMQ
connection_parameters = pika.ConnectionParameters('host.docker.internal')
connection = pika.BlockingConnection(connection_parameters)
channel = connection.channel()

channel.queue_declare(queue='interpol_notices')

def searchBy_arrestwarrantcountry(gender, nations, min_age, mid_age, max_age):
    for nationality in nations:
        url = f"https://ws-public.interpol.int/notices/v1/red?arrestWarrantCountryId={nationality}&resultPerPage=160"
        total = process_notices(url)

        if total > 160:
            url = f"https://ws-public.interpol.int/notices/v1/red?arrestWarrantCountryId={nationality}&ageMin={min_age}&ageMax={mid_age}&sexId={gender}&resultPerPage=160&page=1"
            total = process_notices(url)

            if total > 160:
                for age in range(min_age, mid_age):
                    url = f"https://ws-public.interpol.int/notices/v1/red?arrestWarrantCountryId={nationality}&ageMin={age}&ageMax={age}&sexId={gender}&resultPerPage=160&page=1"
                    total = process_notices(url)

            url = f"https://ws-public.interpol.int/notices/v1/red?arrestWarrantCountryId={nationality}&ageMin={mid_age}&ageMax={max_age}&sexId={gender}&resultPerPage=160&page=1"
            total = process_notices(url)

            if total > 160:
                for age in range(mid_age, max_age):
                    url = f"https://ws-public.interpol.int/notices/v1/red?arrestWarrantCountryId={nationality}&ageMin={age}&ageMax={age}&sexId={gender}&resultPerPage=160&page=1"
                    total = process_notices(url)

def searchBy_nationality(gender, nations, min_age, mid_age, max_age):
    for nationality in nations:
        url = f"https://ws-public.interpol.int/notices/v1/red?nationality={nationality}&sexId={gender}&resultPerPage=160"
        total = process_notices(url)
        if total > 160:
            url = f"https://ws-public.interpol.int/notices/v1/red?nationality={nationality}&ageMin={min_age}&ageMax={mid_age}&sexId={gender}&resultPerPage=160&page=1"
            total = process_notices(url)

            if total > 160:
                for age in range(min_age, mid_age):
                    url = f"https://ws-public.interpol.int/notices/v1/red?nationality={nationality}&ageMin={age}&ageMax={age}&sexId={gender}&resultPerPage=160&page=1"
                    total = process_notices(url)

            url = f"https://ws-public.interpol.int/notices/v1/red?nationality={nationality}&ageMin={mid_age}&ageMax={max_age}&sexId={gender}&resultPerPage=160&page=1"
            total = process_notices(url)

            if total > 160:
                for age in range(mid_age, max_age):
                    url = f"https://ws-public.interpol.int/notices/v1/red?nationality={nationality}&ageMin={age}&ageMax={age}&sexId={gender}&resultPerPage=160&page=1"
                    total = process_notices(url)

def search_notices(nations, min_age, mid_age, max_age):
    for gender in ['F', 'M']:
        searchBy_arrestwarrantcountry(gender, nations, min_age, mid_age, max_age)
        searchBy_nationality(gender, nations,min_age, mid_age, max_age)

def process_data(notice):
    if notice:
        notice_dict = {"notices": [notice]}
        message_body = json.dumps(notice_dict)
        channel.basic_publish(exchange='', routing_key='interpol_notices', body=message_body)
        print(f"Notice {notice['entity_id']} sent to RabbitMQ")

def process_notices(url):
    driver.get(url)
    page_source = driver.page_source
    json_start = page_source.find('{')
    json_end = page_source.rfind('}') + 1
    json_text = page_source[json_start:json_end]
    try:
        data = json.loads(json_text)
        total = int(data['total'])

        if total == 0:
            print(f"No data for URL: {url}")
            return 0

        notices = data['_embedded']['notices']
        for notice in notices:
            entity_id = notice['entity_id']
            if entity_id not in unique_ids:
                unique_ids.add(entity_id)
                process_data(notice)

        return total
    except json.JSONDecodeError:
        print("Failed to parse JSON data.")
        return 0

# For people that have Unknown gender
url = f"https://ws-public.interpol.int/notices/v1/red?&sexId=U&resultPerPage=160"
total = process_notices(url)
search_notices(nati, min_age, mid_age, max_age)

driver.quit()
connection.close()
