from django.shortcuts import render , redirect
from django.contrib import messages
from django.http import HttpResponse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render,HttpResponse,redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import JobPosting, SavedJob
import pandas as pd
from sqlalchemy import create_engine
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import re
from django.urls import reverse


@login_required(login_url='login')
@csrf_exempt
def HomePage(request):
    return render (request,'core/initial.html')



@csrf_exempt
def home(request):

    save = request.GET.get('save', None)  # Fetch the 'save' parameter

    if save == 'True':
        if request.method == 'POST':
    
            # Extract the comma-separated role and location from the form data
            role = request.POST.get('role', '')
            location= request.POST.get('location', '')
            
            JobPosting.objects.all().delete()
            scrape_and_store_data(role, location, request.user.username)
                
            

            job_postings = JobPosting.objects.filter(username=request.user.username)
            job_info_list = job_postings.values('role', 'company_name', 'location', 'job_link')
            return render(request, 'core/home.html', {'job_info_list': job_info_list})
    
        job_postings = JobPosting.objects.filter(username=request.user.username)
        job_info_list = job_postings.values('role', 'company_name', 'location', 'job_link')
        return render(request, 'core/home.html', {'job_info_list': job_info_list})

    if request.method == 'POST':
    
        # Extract the comma-separated role and location from the form data
        role = request.POST.get('role', '')
        location= request.POST.get('location', '')
        
        JobPosting.objects.all().delete()
        scrape_and_store_data(role, location, request.user.username)
            
        

        job_postings = JobPosting.objects.filter(username=request.user.username)
        job_info_list = job_postings.values('role', 'company_name', 'location', 'job_link')
        return render(request, 'core/home.html', {'job_info_list': job_info_list})

    return render(request, 'core/home.html', {'job_info_list': None})
    
    

@csrf_exempt
def SignupPage(request):
    if request.method == 'POST':
        uname = request.POST.get('username')
        email = request.POST.get('email')
        pass1 = request.POST.get('password1')
        pass2 = request.POST.get('password2')

        if User.objects.filter(username=uname).exists():
            messages.error(request, "Username already exists.")
            return redirect('signup')
        
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already exists.")
            return redirect('signup')
        
        if pass1 != pass2:
            messages.error(request, "Your password and confirm password do not match.")
            return redirect('signup')

        my_user = User.objects.create_user(username=uname, email=email, password=pass1)
        my_user.save()
        return redirect('login')

    return render(request, 'core/signup.html')

@csrf_exempt
def LoginPage(request):
    if request.method=='POST':
        username=request.POST.get('username')
        pass1=request.POST.get('pass')
        user=authenticate(request,username=username,password=pass1)
        if user is not None:
            login(request,user)
            return redirect('home')
        else:
            messages.error(request, "Invalid Credentials!")

    return render (request,'core/login.html')

@csrf_exempt
def LogoutPage(request):
    logout(request)
    return redirect('login')


@csrf_exempt
def scrape_and_store_data(role, location, username):

    role = role.replace(' ', '+')
    location = location.replace(' ', '+')

    user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.50 Safari/537.36'
    options = webdriver.ChromeOptions()
    options.add_argument('--headless=old')
    options.add_argument(f'user-agent={user_agent}')
    driver = webdriver.Chrome(options=options)
    driver.get(f'https://in.indeed.com/jobs?q={role}&l={location}')

    Title=[]
    Company=[]
    Location=[]
    hrefs=[]
    
    try:                    
        date=WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//button[@id="filter-dateposted"]'))).click()
        day=WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//a[contains(@href, 'fromage=3')]"))).click()
        close=WebDriverWait(driver, 3).until(EC.element_to_be_clickable((By.XPATH, '//button[@aria-label="close"]'))).click()
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        title=WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.XPATH, '//a[contains(@class, "JobTitle")]')))

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
        
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        try:
            close=WebDriverWait(driver, 3).until(EC.element_to_be_clickable((By.XPATH, '//button[@aria-label="close"]'))).click()
        except:
            pass

        # Optionally, you can wait for the page to load more content
        time.sleep(2)
        title=WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.XPATH, '//a[contains(@class, "JobTitle")]')))
        for t in title:
            hrefs.append(t.get_attribute('href'))
            Title.append(t.text)
        company=WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.XPATH, '//span[@data-testid="company-name"]')))
        for c in company:
            Company.append(c.text)
        location=WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located((By.XPATH, '//div[@data-testid="text-location"]')))
        for l in location:
            Location.append(l.text)
    


    for title, company, location, href in zip(Title, Company, Location, hrefs):
        JobPosting.objects.create(username=username,role=title, company_name=company, location=location, job_link=href)
    driver.quit()



@csrf_exempt
def save_job(request):
    if request.method == 'POST':
    
        title = request.POST.get('title')
        company = request.POST.get('company')
        location = request.POST.get('location')
        link = request.POST.get('link')

        SavedJob.objects.create(username=request.user.username, role=title, company_name=company, location=location, job_link=link)
        

        return redirect(f"{reverse('home')}?save=True")

@csrf_exempt    
def saved_jobs(request):

    saved_jobs_list = SavedJob.objects.filter(username=request.user.username).values('role', 'company_name', 'location', 'job_link')

    return render(request, 'core/saved_jobs.html', {'saved_jobs_list': saved_jobs_list})

@csrf_exempt
def delete_job(request):
    if request.method == 'POST':
        # Extract the fields you want to match from the POST data
        job_title = request.POST.get('title')
        job_location = request.POST.get('location')
        company_name = request.POST.get('company')
        job_link = request.POST.get('link')  # Extract the job link

        # Filter based on multiple fields including job_link
        SavedJob.objects.filter(
            role=job_title, 
            location=job_location, 
            company_name=company_name,
            job_link=job_link
        ).delete()

        return redirect('saved_jobs')
