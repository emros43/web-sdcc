from django.urls import path
from . import views

urlpatterns = [
    path('', views.indeks, name='indeks'),
    path('zaloguj', views.zaloguj, name='zaloguj'),
    path('wyloguj', views.wyloguj, name='wyloguj'),
    path('plik/<path:nazwa_pliku>', views.plik, name='plik'),
    path('edytuj/nowy_plik', views.nowy_plik, name='nowy_plik'),
    path('edytuj/nowy_katalog', views.nowy_katalog, name='nowy_katalog'),
    path('edytuj/usun_plik', views.usun_plik, name='usun_plik'),
    path('edytuj/usun_katalog', views.usun_katalog, name='usun_katalog'),
]
