from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pandas as pd
from sqlalchemy import create_engine
import json

def lambda_handler(event, context):
    user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.50 Safari/537.36'

    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument(f'user-agent={user_agent}')
    driver = webdriver.Chrome(options=options)

    driver.get('https://in.indeed.com/jobs?q=graphics+designer&l=Bangalore%2C+Karnataka&from=searchOnHP&vjk=0f89e69792d32bce')
    roles=['Data Analyst']
    locations=['Mumbai']
    Title=[]
    Company=[]
    Location=[]
    hrefs=[]

    for role in roles:
        for loc in locations:
            try:
                for i in range(1,3):
                    Search=WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, f'(//input[@type="text"])[{i}]')))
                    Search.click()
                    if i == 1:
                        reset=WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, f'(//button[@type="reset"])[{i}]'))).click()
                        Search.send_keys(role)
                    else:
                        reset=WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, f'(//button[@type="reset"])[{i}]'))).click()
                        Search.send_keys(loc + Keys.ENTER)
                        
                try:                    
                    close=WebDriverWait(driver, 1).until(EC.element_to_be_clickable((By.XPATH, '//button[@aria-label="close"]'))).click()
                    date=WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//button[@id="filter-dateposted"]'))).click()
                    time.sleep(2)
                    day=WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//a[contains(@href, 'fromage=3')]"))).click()
                    
                    
                    title=WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.XPATH, '//a[@class="jcs-JobTitle css-jspxzf eu4oa1w0"]')))

                    for t in title:
                        hrefs.append(t.get_attribute('href'))
                        Title.append(t.text)
                    company=WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.XPATH, '//span[@data-testid="company-name"]')))
                    for c in company:
                        Company.append(c.text)
                    location=WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.XPATH, '//div[@data-testid="text-location"]')))
                    for l in location:
                        Location.append(l.text)
                except:
                    date=WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//button[@id="filter-dateposted"]'))).click()
                    time.sleep(2)
                    day=WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//a[contains(@href, 'fromage=3')]"))).click()
                    title=WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.XPATH, '//a[@class="jcs-JobTitle css-jspxzf eu4oa1w0"]')))
                    for t in title:
                        hrefs.append(t.get_attribute('href'))
                        Title.append(t.text)
                    company=WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.XPATH, '//span[@data-testid="company-name"]')))
                    for c in company:
                        Company.append(c.text)
                    location=WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.XPATH, '//div[@data-testid="text-location"]')))
                    for l in location:
                        Location.append(l.text)
            except:
                continue
                    
    df=pd.DataFrame({'title':Title, 'company': Company, 'location': Location,'link':hrefs})
    print(df)
    engine = create_engine('mysql+mysqlconnector://root:Pass%40123@127.0.0.1/webscraping_db')
    df.to_sql(name='jobs', con=engine, if_exists='replace', index=False) 

    return{
        'statusCode': 200,
        'body': json.dumps(f'Successfully scraped and stored {len(df)} jobs')
    }