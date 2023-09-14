import re
import time
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
import pandas as pd
import json
import mysql.connector
from dotenv import load_dotenv, dotenv_values
import os
from sqlalchemy import create_engine
import pymysql
from circles_importer.importer import Importer
from logger_local.Logger import Logger
from logger_local.LoggerComponentEnum import LoggerComponentEnum
from circles_local_database_python.connector import Connector
from entity_type.EntityType import EntityType
from location_local.country import Country
import dotenv

REAL_ESTATE_REALTOR_COM_SELENIUM_IMP_COMPONENT_ID = 146
REAL_ESTATE_REALTOR_COM_SELENIUM_IMP_COMPONENT_NAME = 'real-estate-realtor_com-selenium-imp-local-python-package'
GET_LISTING_LINKS_FROM_LOCATION_FUNCTION_NAME = 'real-estate-realtor_com-selenium-imp-local-python-package/realtor.py get_listing_links_from_location()'
BASE_URL = "https://www.realtor.com/international/"
PAGE_LIMIT = 5
LISTINGS_LIMIT_PER_PAGE = 6
df = pd.DataFrame(columns=['listing_id', 'agent_name', 'agent_office_phone', 'price', 'property_type', 'land_size',
                           'building_size', 'num_of_bedrooms', 'num_of_bathrooms'])

logger_code_init = {
    'component_id': REAL_ESTATE_REALTOR_COM_SELENIUM_IMP_COMPONENT_ID,
    'component_name': REAL_ESTATE_REALTOR_COM_SELENIUM_IMP_COMPONENT_NAME,
    'component_category': LoggerComponentEnum.ComponentCategory.Code.value,
    'developer_email': 'tal@circlez.ai'
}
logger = Logger.create_logger(object=logger_code_init)

importer1 = Importer()
dotenv.load_dotenv()

def get_listing_links_from_location(driver, location):
    object_start = {
        'driver': driver,
        'location': location
    }
    logger.start(GET_LISTING_LINKS_FROM_LOCATION_FUNCTION_NAME, object=object_start)
    listings = []
    page_num = 1
    location_base_url = get_link_from_location(location)
    while True:
        if page_num > PAGE_LIMIT:
            break

        url = location_base_url + f"/p{page_num}"
        driver.get(url)
        # Wait for the page to load
        time.sleep(6)
        logger.info("get_listing_links_from_location()", object={'url': url})
        listings += extract_listings_from_listings_page(driver)

        page_num += 1
    logger.end(GET_LISTING_LINKS_FROM_LOCATION_FUNCTION_NAME,
               object={'listings': listings})
    return listings

def extract_listings_from_listings_page(driver):
    object_start = {
        'driver': driver
    }
    logger.start(object=object_start)
    links = []
    ul_elements = driver.find_elements(By.CLASS_NAME, "tier-one-listing-table")
    # ul_next_page_elements = driver.find_elements(By.CLASS_NAME, "pagination-box")
    for x in ul_elements:
        li_element = x.find_elements(By.CLASS_NAME, "listing")
        for i in range(len(li_element)):
            link = li_element[i].find_element(
                By.TAG_NAME, "a").get_attribute('href')
            links.append(link)
            logger.info("link", {link: link})
        # li_next_page_element = ul_next_page_elements.find_element(By.TAG_NAME,"a").get_attribute('href')
    logger.end(
        object={'links[:LISTINGS_LIMIT_PER_PAGE]': links[:LISTINGS_LIMIT_PER_PAGE]})
    return links[:LISTINGS_LIMIT_PER_PAGE]

def insert_to_table(connection, cursor, line, location):
    object_start = {
        'connection': connection,
        'cursor': cursor,
        'line': line,
        'location': location
    }
    logger.start(object=object_start)
    entity_type_id = EntityType.get_entity_type_id_by_name("Real Estate")
    if (not entity_type_id):
        EntityType.insert_entity_type_id_by_name("Real Estate", 1)
        entity_type_id = EntityType.get_entity_type_id_by_name("Real Estate")
        country_name = Country.get_country_name(location)
    # TODO replace with a call to location Class location-local-python-package
    query = """Select id from `location`.`location_table` join `location`.`country_table` on `country_id`=id Where iso=%s"""
    cursor.execute(query, (country_name))
    id = cursor.ferchone()[0]
    importer1.insert_record_data_source(15, id, entity_type_id, BASE_URL, 1)
    # Specify the table name
    table_name = 'listings'
    # Create a new record
    try:
        dict_values = line.to_dict()
        if dict_values['agent_office_phone'] == -1:
            logger.end(object={})
            return
        sql = "INSERT INTO listings (listing_id, agent_name, agent_office_phone, price, property_type, land_size,building_size,num_of_bedrooms,num_of_bathrooms) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
        # Execute the query
        cursor.execute(sql, tuple(line.to_dict().values()))
        # the connection is not autocommited by default. So we must commit to save our changes.
        connection.commit()
    except Exception as e:
        if mysql.connector.errors.IntegrityError:
            logger.error("Duplicate key has detected")
        logger.exception(object=e)

    # # Specify the table name
    # table_name = 'listings'
    # # Insert the row into the table
    # line.to_sql(name=table_name, con=engine, if_exists='replace', index=False)
    # engine.dispose()
    # with engine.connect() as conn:
    #     conn.execute(text("SELECT * FROM users")

    # new_row = {'listing_id': listing_id_int, 'agent_name': agent_name, 'agent_office_phone': phone_int,
    #            'price': price_int, 'property_type': property_type, 'land_size': land_int,
    #            'building_size': building_size_int, 'num_of_bedrooms': num_bedrooms,
    #            'num_of_bathrooms': num_bathrooms}


def wrapper_extract_data(driver, links):
    object_start = {
        'driver': driver,
        'links': links
    }
    logger.start(object=object_start)
    combined_df = pd.DataFrame()
    for x in links:
        logger.info(object={'x': x})
        driver.get(str(x))
        title = driver.title
        # print(title)
        new_df = extract_data(driver, title)
        time.sleep(5)
        pd.set_option('display.max_columns', None)
        pd.set_option('display.max_rows', None)
        combined_df = pd.concat([combined_df, new_df], ignore_index=True)
        # print(combined_df)
    logger.end(object={'combined_df': combined_df})
    return combined_df

def extract_data(driver, title):
    object_start = {
        'driver': str(driver),
        'title': title
    }
    logger.start(object=object_start)
    try:
        address = re.findall(r'(\w+(?:-\w+)? (?:\w+,? )+\d+)', title)
        if not address:
            pass
        else:
            address = address[0]
            logger.info(object={'address': address})
    except Exception as e:
        logger.exception(object=e)
        if NoSuchElementException:
            logger.error(f"No address id found on page {title}")
    try:
        listing_id_element = driver.find_element(By.CLASS_NAME, "listing-id")
        listing_id = listing_id_element.text
        listing_id_int = int(listing_id)
    except Exception as e:
        logger.exception(object=e)
        if NoSuchElementException:
            logger.error(f"No listing id found on page {title}")
        listing_id = "N/A"
        listing_id_int = -1
    try:
        agent_name_element = driver.find_element(By.CLASS_NAME, "agent-name")
        agent_name = agent_name_element.text
        # print(agent_name)
    except Exception as e:
        logger.exception(object=e)
        if NoSuchElementException:
            logger.error(f"No agent name found on page {title}")
        agent_name = "N/A"
    try:
        agent_office_phone_element = driver.find_element(
            By.CLASS_NAME, "agent-officephone")
        agent_office_phone = agent_office_phone_element.get_attribute('href')
        # print(agent_office_phone)
        office_phone_num_list = re.findall(r'\d+', agent_office_phone)
        phone_str = ''.join(office_phone_num_list)
        phone_int = int(phone_str)
        logger.info(object={'phone_int': phone_int})
    except Exception as e:
        logger.exception(object=e)
        if NoSuchElementException:
            logger.error(f"No agent office phone found on page {title}")
        agent_office_phone = "N/A"
        phone_int = -1
    try:
        price_element = driver.find_element(By.CLASS_NAME, "property-price")
        price = price_element.text
        price_list = re.findall(r'\d+', price)
        price_str = ''.join(price_list)
        price_int = int(price_str)
        logger.info(object={'price_int': price_int})
    except Exception as e:
        logger.exception(object=e)
        if NoSuchElementException:
            logger.error(f"No property price found on page {title}")
        price = "N/A"
        price_int = -1
    try:
        property_type_element = driver.find_element(
            by='css selector', value=".propertyTypes .basicInfoValue")
        property_type = property_type_element.text
    except Exception as e:
        logger.exception(object=e)
        if NoSuchElementException:
            logger.error(f"No property type found on page {title}")
        property_type = "N/A"
    try:
        land_size_element = driver.find_element(
            by='css selector', value=".landSize .basicInfoValue span")
        land_size = land_size_element.text
        building_size_until_point = re.search(
            r'\d[\d,.]*(?=\.)', land_size).group(0)
        land_list = re.findall(r'\d+', building_size_until_point)
        land_str = ''.join(land_list)
        land_int = int(land_str)
        logger.info(object={'land_int': land_int})
    except Exception as e:
        logger.exception(object=e)
        if NoSuchElementException:
            logger.error(f"No land size found on page {title}")
        land_size = "N/A"
        land_int = -1
    try:
        building_size_element = driver.find_element(by='xpath',
                                                    value="//div[text()='Building Size']/following-sibling::div/span")
        building_size = building_size_element.text
        building_size_until_point = re.search(
            r'\d[\d,.]*(?=\.)', building_size).group(0)
        building_size_list = re.findall(r'\d+', building_size_until_point)
        building_size_str = ''.join(building_size_list)
        building_size_int = int(building_size_str)
        logger.info(object={'building_size_int': building_size_int})
    except Exception as e:
        logger.exception(object=e)
        if NoSuchElementException:
            logger.error(f"No building size found on page {title}")
        building_size = "N/A"
        building_size_int = -1
    try:
        rooms_element = driver.find_element(
            by='css selector', value=".rooms .basicInfoValue")
        rooms = rooms_element.text
        rooms_list = rooms.split(',')
        for room in rooms_list:
            room_type = re.findall(r'[a-z]+', room)[0]
            if room_type.startswith('bath'):
                num_bathrooms = int(re.findall(r'\d+', room)[0])
                if len(rooms_list) == 1:
                    num_bedrooms = 0
            elif room_type.startswith('bed'):
                num_bedrooms = int(re.findall(r'\d+', room)[0])
                if len(rooms_list) == 1:
                    num_bathrooms = 0
            else:
                logger.error("you didn't prepared well")
                raise Exception("you didn't prepared well")
    except Exception as e:
        logger.exception(object=e)
        if NoSuchElementException:
            logger.error(f"No rooms found on page {title}")
        num_bedrooms = -1
        num_bathrooms = -1
    logger.info(
        f"{listing_id = }\n{agent_name = }\n{agent_office_phone = }\n{price = }\n{property_type = }\n{land_size = }\n{building_size = }\n The listing includes:{num_bedrooms = },{num_bathrooms = }")
    new_row = {'listing_id': listing_id_int, 'agent_name': agent_name, 'agent_office_phone': phone_int,
               'price': price_int, 'property_type': property_type, 'land_size': land_int,
               'building_size': building_size_int, 'num_of_bedrooms': num_bedrooms,
               'num_of_bathrooms': num_bathrooms}
    # create a new dataframe from the new_row dictionary
    new_df = pd.DataFrame([new_row])
    # concatenate the new dataframe to the original dataframe
    logger.end(object={'new_df': str(new_df)})
    return new_df

def read_locations_from_json():
    logger.start(object={})
    with open('locations.json') as f:
        locations = json.load(f)
    logger.end(object={'locations["locations"]': locations["locations"]})
    return locations["locations"]

def get_link_from_location(location):
    object_start = {
        'location': location
    }
    logger.start(object=object_start)
    link = BASE_URL + location
    logger.end(object={'link': link})
    return link

def main():
    logger.start(object={})
    load_dotenv()
    config = dotenv_values(".env")
    # connect to the database
    connection = Connector.connect("marketplace_goods_realestate")
    # read locations from JSON configuration file
    locations = read_locations_from_json()
    cursor = connection.cursor()
    # create a new ChromeDriver instance
    # r"C:\Program Files (x86)\WebDriver\chromedriver.exe"
    service = Service(executable_path='./chromedriver.exe')
    options = webdriver.ChromeOptions()
    driver = webdriver.Chrome(service=service, options=options)
    all_df = pd.DataFrame()
    try:
        for location in locations:
            url = f"mysql+mysqlconnector://{config['RDS_USERNAME']}:{config['RDS_PASSWORD']}@{config['RDS_HOSTNAME']}:{3306}/{config['DATABASE']}"
            engine = create_engine(url)
            # Get the links of all the listings
            listing_links = get_listing_links_from_location(driver, location)
            # for listing_link in listing_links:
            #   extract_listing_data(driver, listing_link)
            curr_location_listings = wrapper_extract_data(driver, listing_links)
            for line in curr_location_listings.iterrows():
                insert_to_table(connection, cursor, line, location)
            all_df = pd.concat([all_df, curr_location_listings], ignore_index=True)
            logger.info(object={'all_df': all_df})
    except Exception as error:
        logger.exception(object=error)
    finally:
        driver.quit()
        logger.end(object={})

if __name__ == "__main__":
    main()
