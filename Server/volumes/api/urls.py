from django.contrib import admin
from django.urls import path
from api import views
urlpatterns = [
    path('admin/', admin.site.urls),
    path('idDuplicateCheck',views.idCheck),
    path('signup',views.signup),
    path('test/',views.path),
    path('searchMusic/',views.searchMusic())
]
