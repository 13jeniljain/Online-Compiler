from django.contrib import admin
from django.urls import path, include

from .views import homepageview, registerPage , loginPage , logoutUser , probview , verdictpage

urlpatterns = [
    path('', homepageview, name = "home"),
    path('register/', registerPage, name = "register"),
    path('login/', loginPage, name = "login"),
    path('logout/', logoutUser, name = "logout"),
    path('prob/<int:pk>', probview, name = "prob_detail"),
    path('submit/<int:pk>/', verdictpage , name = "verdict"),
]