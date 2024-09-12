from django.urls import path
from . import views

urlpatterns = [
    path('',views.home,name='home'),
    path('save_job', views.save_job, name='save_job'),
    path('saved_jobs/', views.saved_jobs, name='saved_jobs'),
    path('delete_job/<int:job_id>/', views.delete_job, name='delete_job'), 
    
]