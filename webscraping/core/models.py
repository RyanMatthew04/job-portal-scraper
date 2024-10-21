from django.db import models

class JobPosting(models.Model):
    username=models.CharField(max_length=255,null=True)
    role = models.CharField(max_length=255)
    company_name = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    job_link = models.CharField(max_length=500)

class SavedJob(models.Model):
    username=models.CharField(max_length=255,null=True)
    role = models.CharField(max_length=255)
    company_name = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    job_link = models.CharField(max_length=500)

