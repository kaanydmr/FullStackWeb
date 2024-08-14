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

url = "https://www.interpol.int/How-we-work/Notices/Red-Notices/View-Red-Notices"
driver.get(url)

unique_ids = set()  # To store unique entity IDs
notice_list = []

nati = []
for i in range(2, 218):
    wait = WebDriverWait(driver, 10)
    nation_option = wait.until(EC.element_to_be_clickable((By.XPATH, f"/html/body/div[1]/div[1]/div[6]/div/div[1]/div/div/form/div[3]/select/option[{i}]")))
    nati.append(nation_option.get_attribute("value"))

def process_data(notice):
    if notice:
        notice_list.append(notice)
        print(f"Notice {notice['entity_id']} added to list")

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


#For people that has Unkown gender
url = f"https://ws-public.interpol.int/notices/v1/red?&sexId=U&resultPerPage=160"
total = process_notices(url)

#Loop for finding people with parameters: Gender and what country is issued warrant with age as data per page is 160 notice max
for gender in ['F', 'M']:
    for nationality in nati:
        # Check the initial total
        url = f"https://ws-public.interpol.int/notices/v1/red?arrestWarrantCountryId={nationality}&resultPerPage=160"
        total = process_notices(url)

        # If total exceeds 160, fetch data for different age ranges
        if total > 160:

            url = f"https://ws-public.interpol.int/notices/v1/red?arrestWarrantCountryId={nationality}&ageMin={10}&ageMax={40}&sexId={gender}&resultPerPage=160&page=1"
            total = process_notices(url)

            if total > 160:
                for age in range(10, 40):
                    url = f"https://ws-public.interpol.int/notices/v1/red?arrestWarrantCountryId={nationality}&ageMin={age}&ageMax={age}&sexId={gender}&resultPerPage=160&page=1"
                    total = process_notices(url)


            url = f"https://ws-public.interpol.int/notices/v1/red?arrestWarrantCountryId={nationality}&ageMin={40}&ageMax={100}&sexId={gender}&resultPerPage=160&page=1"
            total = process_notices(url)

            if total > 160:
                for age in range(40, 100):
                    url = f"https://ws-public.interpol.int/notices/v1/red?arrestWarrantCountryId={nationality}&ageMin={age}&ageMax={age}&sexId={gender}&resultPerPage=160&page=1"
                    total = process_notices(url)


#Loop for finding people with parameters: Gender and what country they are from with age
for gender in ['F', 'M']:
    for nationality in nati:
        # Check the initial total
        url = f"https://ws-public.interpol.int/notices/v1/red?nationality={nationality}&sexId={gender}&resultPerPage=160"
        total = process_notices(url)

        if total > 160:
            # If total exceeds 160, fetch data for different age ranges
            url = f"https://ws-public.interpol.int/notices/v1/red?nationality={nationality}&ageMin={10}&ageMax={40}&sexId={gender}&resultPerPage=160&page=1"
            total = process_notices(url)

            if total > 160:
                for age in range(10, 40):
                    url = f"https://ws-public.interpol.int/notices/v1/red?nationality={nationality}&ageMin={age}&ageMax={age}&sexId={gender}&resultPerPage=160&page=1"
                    total = process_notices(url)

            url = f"https://ws-public.interpol.int/notices/v1/red?nationality={nationality}&ageMin={40}&ageMax={100}&sexId={gender}&resultPerPage=160&page=1"
            total = process_notices(url)

            if total > 160:
                for age in range(40, 100):
                    url = f"https://ws-public.interpol.int/notices/v1/red?nationality={nationality}&ageMin={age}&ageMax={age}&sexId={gender}&resultPerPage=160&page=1"
                    total = process_notices(url)

# Close the WebDriver after all nationalities are processed
driver.quit()

#Connection for RabbitMQ
connection_parameters = pika.ConnectionParameters('host.docker.internal')
connection = pika.BlockingConnection(connection_parameters)
channel = connection.channel()


channel.queue_declare(queue='interpol_notices')

notice_dict = {"notices": notice_list}

message_body = json.dumps(notice_dict)

# Send the JSON string as the message body to RabbitMQ
channel.basic_publish(exchange='', routing_key='interpol_notices', body=message_body)

connection.close()