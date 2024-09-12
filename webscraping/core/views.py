from django.shortcuts import render , redirect
from django.http import HttpResponse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
import pandas as pd
from sqlalchemy import create_engine
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# Configure the MySQL connection
def get_db_engine():
    return create_engine('mysql+mysqlconnector://root:<enter pass>@127.0.0.1/webscraping_db')

# Define the function to scrape data using Selenium
def scrape_and_store_data(role, location):
    print("entered")
    user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.50 Safari/537.36'

    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument(f'user-agent={user_agent}')
    driver = webdriver.Chrome(options=options)

    driver.get('https://in.indeed.com/jobs?q=graphics+designer&l=Bangalore%2C+Karnataka&from=searchOnHP&vjk=0f89e69792d32bce')

    Title=[]
    Company=[]
    Location=[]
    hrefs=[]



    try:
        for i in range(1,3):
            Search=WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, f'(//input[@type="text"])[{i}]')))
            Search.click()
            if i == 1:
                reset=WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, f'(//button[@type="reset"])[{i}]'))).click()
                Search.send_keys(role)
            else:
                reset=WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, f'(//button[@type="reset"])[{i}]'))).click()
                Search.send_keys(location + Keys.ENTER)
                
        try:                    
            close=WebDriverWait(driver, 3).until(EC.element_to_be_clickable((By.XPATH, '//button[@aria-label="close"]'))).click()
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
        pass

    df = pd.DataFrame({'title': Title, 'company': Company, 'location': Location, 'link': hrefs})
    df['id'] = range(1, len(df) + 1)
    engine = get_db_engine()
    df.to_sql(name='jobs', con=engine, if_exists='replace', index=False)
    driver.quit()

@csrf_exempt
def home(request):


    if request.method == 'POST':
    
        # Extract the comma-separated role and location from the form data
        role_location = request.POST.get('job', '')
        if ',' in role_location:
            role, location = [x.strip() for x in role_location.split(',', 1)]
            scrape_and_store_data(role, location)
            
        else:
            return HttpResponse('Invalid input. Please enter both role and location separated by a comma.')

    # Fetch data from MySQL database
    engine = get_db_engine()
    df = pd.read_sql_table('jobs', con=engine)
    job_info_list = df.to_dict(orient='records')

    return render(request, 'core/home.html', {'job_info_list': job_info_list})

@csrf_exempt
def save_job(request):
    if request.method == 'POST':
        # Get job details from the form
        title = request.POST.get('title')
        company = request.POST.get('company')
        location = request.POST.get('location')
        link = request.POST.get('link')

        # Establish the database connection
        engine = get_db_engine()

        # Retrieve the last id from the saved_jobs table
        query = "SELECT MAX(id) AS max_id FROM saved_jobs"
        last_id_df = pd.read_sql_query(query, con=engine)
        last_id = last_id_df['max_id'].values[0] if last_id_df['max_id'].values[0] is not None else 0

        # Generate new id
        new_id = last_id + 1

        # Prepare new job data
        df = pd.DataFrame({'title': [title], 'company': [company], 'location': [location], 'link': [link], 'id': [new_id]})

        # Save to the saved_jobs table
        df.to_sql(name='saved_jobs', con=engine, if_exists='append', index=False)

        # Redirect back to the home page
        return redirect('home')

@csrf_exempt    
def saved_jobs(request):
    # Establish database connection
    engine = get_db_engine()

    # Fetch the saved jobs from the 'saved_jobs' table
    df = pd.read_sql_table('saved_jobs', con=engine)
    saved_jobs_list = df.to_dict(orient='records')

    # Render the saved_jobs.html template and pass the saved jobs list
    return render(request, 'core/saved_jobs.html', {'saved_jobs_list': saved_jobs_list})

@csrf_exempt
def delete_job(request, job_id):
    if request.method == 'POST':
        # Establish the database connection
        engine = get_db_engine()

        # Fetch the current data
        df = pd.read_sql_table('saved_jobs', con=engine)

        # Remove the row where the job ID matches
        df = df[df['id'] != job_id]

        # Write the updated DataFrame back to the database
        df.to_sql(name='saved_jobs', con=engine, if_exists='replace', index=False)

        # Redirect back to the saved jobs page
        return redirect('saved_jobs')
