from django.test import TestCase, Client, RequestFactory
from django.http import Http404
from django.contrib.auth.models import User
from .models import Katalog, Plik
from .forms import KatalogForm, PlikForm, SekcjaForm
from .views import plik
from django.urls import reverse
import json



# indeks()
class IndeksTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="testuser4", password="test")

    def test_indeks_poprawnosc(self):
        # poprawnosc wywolanych statusow/elementow:
        katalog = Katalog.objects.create(nazwa="Testowy Katalog9", wlasciciel=self.user)
        plik = Plik.objects.create(nazwa="Testowy Plik10", tresc="To jest testowy plik.", wlasciciel=self.user)

        response = self.client.get(reverse("indeks"))

        self.assertEqual(response.status_code, 200)
        katalogi_values = list(response.context["katalogi"].values_list("nazwa", flat=True))
        pliki_values = list(response.context["pliki"].values_list("nazwa", flat=True))
        self.assertEqual(katalogi_values, ["Testowy Katalog9"])
        self.assertEqual(pliki_values, ["Testowy Plik10"])



# plik() i jego formularze
class KompilacjaTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.factory = RequestFactory()
        self.user = User.objects.create_user(username="testuser6", password="test")
        self.plik = Plik.objects.create(nazwa="test.c", tresc="#include <stdio.h>", wlasciciel=self.user)
        self.client.login(username="testuser6", password="test")

    def test_plik_nie_istnieje(self):
        # sprawdza, czy wywolany blad, gdy plik nie istnieje:
        nazwa_pliku = "nie_istnieje.c"
        request = self.factory.get("/plik/" + nazwa_pliku)

        with self.assertRaises(Http404):
            plik(request, nazwa_pliku)

    def test_domyslna_prawidlowa_kompilacja(self):
        # sprawdza, czy plik o prawidlowej tresci poprawnie sie kompiluje
        request = self.factory.get("plik/" + self.plik.nazwa)

        response = plik(request, self.plik.nazwa)

        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertIn("tresc", response_data)
        self.assertIn("assembled", response_data)

        assembled = response_data["assembled"]
        self.assertTrue(assembled.startswith(";")) # wszystkie komunikaty o bledzie zaczynaja sie od litery

    def test_domyslna_nieprawidlowa_kompilacja(self):
        # sprawdza, czy jest blad przy kompilacji pliku o nieprawidlowym rozszerzeniu
        plik_blad = Plik.objects.create(nazwa="test2", tresc="123", wlasciciel=self.user)
        request = self.factory.get("plik/" + plik_blad.nazwa)

        response = plik(request, plik_blad.nazwa)

        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertIn("tresc", response_data)
        self.assertIn("assembled", response_data)

        assembled = response_data["assembled"]
        self.assertTrue(assembled.startswith("P")) # "Plik nie ma rozszerzenia .c"



# wyloguj() i zaloguj() i ich formularze
class LogowanieTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="testuser5", password="test")

    def test_zaloguj_prawidlowe_dane(self):
        # sprawdza poprawnosc przekierowan i status zalogowania
        response = self.client.post(reverse("zaloguj"), {"username": "testuser5", "password": "test"})

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("indeks"))
        self.assertTrue("_auth_user_id" in self.client.session)

    def test_zaloguj_nieprawidlowe_dane(self):
        # sprawdza, czy po bledzie logowania uzytkownik nie jest zalogowany
        response = self.client.post(reverse("zaloguj"), {"username": "testuser5", "password": "haslomaslo"})

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "login.html")
        self.assertFalse("_auth_user_id" in self.client.session)

    def test_loguj_i_wyloguj(self):
        # loguje i sprawdza poprawnosc przekierowan i brak zalogowanego uzytkownika po wylogowaniu
        self.client.login(username="testuser5", password="test")

        response = self.client.get(reverse("wyloguj"))

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("indeks"))
        self.assertFalse("_auth_user_id" in self.client.session)



# nowy_plik() i usun_plik() i ich formularze
class PlikTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse("nowy_plik")
        self.user = User.objects.create_user(username="testuser7", password="test")
        self.katalogi = [
            Katalog(nazwa="Katalog 1", opis="Opis katalogu 1", wlasciciel=self.user),
            Katalog(nazwa="Katalog 2", opis="Opis katalogu 2", wlasciciel=self.user)
        ]

    def test_nowy_plik_prawidlowe_dane(self):
        self.client.login(username='testuser7', password='test')
        form_data = {
            "nazwa": "Nowy plik",
            "opis": "Opis",
            "tresc": "a",
            "katalog_nadrzedny": "",
        }
        response = self.client.post(self.url, form_data)
        self.assertEqual(response.status_code, 302)

    def test_nowy_plik_nieprawidlowe_dane(self):
        self.client.login(username='testuser7', password='test')
        form_data = {
            "nazwa": "", # blad - pusta nazwa
            "opis": "Opis",
            "tresc": "a",
            "katalog_nadrzedny": "",
        }
        response = self.client.post(self.url, form_data)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context["form"].is_valid())
        self.assertTemplateUsed(response, "nowy_plik.html")

    def test_usun_plik(self):
        # tworzy plik i sprawdza, czy formularz usuwania poprawnie ustawia wartosci:
        plik = Plik.objects.create(nazwa="Testowy Plik12", wlasciciel=self.user)

        response = self.client.post(reverse("usun_plik"), {"plik": "Testowy Plik12"})

        self.assertEqual(response.status_code, 302)
        plik.refresh_from_db()
        self.assertFalse(plik.dostepny)
        self.assertIsNotNone(plik.modyfikacja_dostepnosci)

    def test_nowy_plik_formularz_katalog_nadrzedny(self):
        # sprawdza poprawnosc wyboru katalogu nadrzednego:
        form = PlikForm(self.katalogi)
        self.assertIn(("", "~/"), form.fields["katalog_nadrzedny"].choices)
        for katalog in self.katalogi:
            self.assertIn((katalog.nazwa, katalog), form.fields["katalog_nadrzedny"].choices)

    def test_nowy_plik_formularz_pusta_nazwa(self):
        # sprawdza, czy pusta nazwa generuje blad:
        form = PlikForm(self.katalogi, data={"nazwa": ""})
        self.assertFalse(form.is_valid())
        self.assertIn("nazwa", form.errors)



# nowy_katalog() i usun_katalog() i ich formularze
class KatalogTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse("nowy_katalog")
        self.user = User.objects.create_user(username="testuser8", password="test")
        self.client.login(username="testuser8", password="test")
        self.katalogi = [
            Katalog(nazwa="Katalog 1", opis="Opis katalogu 1", wlasciciel=self.user),
            Katalog(nazwa="Katalog 2", opis="Opis katalogu 2", wlasciciel=self.user)
        ]

    def test_nowy_katalog_prawidlowe_dane(self):
        katalogi_liczba = Katalog.objects.count()
        form_data = {
            "nazwa": "Nowy katalog",
            "opis": "Opis",
            "katalog_nadrzedny": "",
        }
        response = self.client.post(self.url, form_data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Katalog.objects.count(), katalogi_liczba + 1)

    def test_nowy_katalog_nieprawidlowe_dane(self):
        form_data = {
            "nazwa": "", # blad - pusta nazwa
            "opis": "Opis",
            "katalog_nadrzedny": "",
        }
        response = self.client.post(self.url, form_data)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context["form"].is_valid())
        self.assertTemplateUsed(response, "nowy_katalog.html")

    def test_usun_katalog(self):
        # tworzy katalog i sprawdza, czy formularz usuwania poprawnie ustawia wartosci:
        katalog = Katalog.objects.create(nazwa="Testowy Plik13", wlasciciel=self.user)

        response = self.client.post(reverse("usun_katalog"), {"katalog": "Testowy Plik13"})

        self.assertEqual(response.status_code, 302)
        katalog.refresh_from_db()
        self.assertFalse(katalog.dostepny)
        self.assertIsNotNone(katalog.modyfikacja_dostepnosci)

    def test_nowy_katalog_formularz_katalog_nadrzedny(self):
        # sprawdza poprawnosc wyboru katalogu nadrzednego:
        form = KatalogForm(self.katalogi)
        self.assertIn(("", "~/"), form.fields["katalog_nadrzedny"].choices)
        for katalog in self.katalogi:
            self.assertIn((katalog.nazwa, katalog), form.fields["katalog_nadrzedny"].choices)

    def test_nowy_katalog_formularz_pusta_nazwa(self):
        # sprawdza, czy pusta nazwa generuje blad:
        form = KatalogForm(self.katalogi, data={"nazwa": ""})
        self.assertFalse(form.is_valid())
        self.assertIn("nazwa", form.errors)



# formularz sekcji:
class SekcjaFormTest(TestCase):
    def test_sekcja_prawidlowe_dane(self):
        form_data = {
            "nazwa": "Test",
            "opis": "Opis",
            "poczatek": "1",
            "koniec": "11",
            "rodzic_sekcja": None,
            "rodzaj": "KO"
        }

        form = SekcjaForm(data=form_data)
        self.assertTrue(form.is_valid())