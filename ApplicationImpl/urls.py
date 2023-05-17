from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path("", views.frontpage),
    path("signup/", views.signup, name='signup'),
    path("feedback/", views.feedback, name='feedback'),
    path("frontpage/", views.frontpage, name='frontpage'),
    path("login/", views.login, name='login'),
    path("forget/", views.forget, name='forget'),
    path("prediction/", views.prediction, name='prediction'),
]
