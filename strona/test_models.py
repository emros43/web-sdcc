from django.test import TestCase
from django.contrib.auth.models import User
from .models import Katalog, Plik, Sekcja, Uzytkownik



class UzytkownikTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser0", password="test")
    
    def test_utworzenie_uzytkownika(self):
        uzytkownik = Uzytkownik.objects.create(user=self.user, nazwa="Testowy Uzytkownik")
        self.assertEqual(uzytkownik.user, self.user)
        self.assertEqual(uzytkownik.nazwa, "Testowy Uzytkownik")



class KatalogTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", password="test")

    def test_katalog_unikalna_nazwa(self):
        # tworzy dwa obiekty z ta sama nazwa
        Katalog.objects.create(nazwa="Testowy Katalog1", wlasciciel=self.user)
        with self.assertRaises(Exception):
            Katalog.objects.create(nazwa="Testowy Katalog1", wlasciciel=self.user)

    def test_katalog_domyslne_wartosci(self):
        # sprawdza poprawnosc domyslnie ustawianych wartosci
        # dostepnosc:
        katalog = Katalog.objects.create(nazwa="Testowy Katalog2", wlasciciel=self.user)
        self.assertTrue(katalog.dostepny)
        # daty:
        katalog = Katalog.objects.create(nazwa="Testowy Katalog3", wlasciciel=self.user)
        self.assertIsNotNone(katalog.utworzenie)
        self.assertIsNotNone(katalog.modyfikacja)
        self.assertIsNone(katalog.modyfikacja_dostepnosci)
        # wlasciciel:
        katalog = Katalog.objects.create(nazwa="Testowy Katalog4", wlasciciel=self.user)
        self.assertEqual(katalog.wlasciciel, self.user)
        # powiazanie z katalogiem:
        katalog1 = Katalog.objects.create(nazwa="Testowy Katalog5", wlasciciel=self.user)
        katalog2 = Katalog.objects.create(nazwa="Testowy Katalog6", wlasciciel=self.user, rodzic_folder=katalog1)
        self.assertEqual(katalog1.rodzic_folder, None)
        self.assertEqual(katalog2.rodzic_folder, katalog1)

    def test_katalog_aktualizacja_dostepnosci(self):
        # aktualizacja modyfikacja_dostepnosci
        katalog = Katalog.objects.create(nazwa="Testowy Katalog8", wlasciciel=self.user)
        katalog.dostepny = False
        katalog.save()
        self.assertIsNotNone(katalog.modyfikacja_dostepnosci)



class PlikTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser2", password="test")

    def test_plik_unikalna_nazwa(self):
        # tworzy dwa obiekty z ta sama nazwa
        Plik.objects.create(nazwa="Testowy Plik1", wlasciciel=self.user)
        with self.assertRaises(Exception):
            Plik.objects.create(nazwa="Testowy Plik1", wlasciciel=self.user)

    def test_plik_domyslne_wartosci(self):
        # sprawdza poprawnosc domyslnie ustawianych wartosci
        # dostepnosc:
        plik = Plik.objects.create(nazwa="Testowy Plik2", wlasciciel=self.user)
        self.assertTrue(plik.dostepny)
        # daty:
        plik = Plik.objects.create(nazwa="Testowy Plik3", wlasciciel=self.user)
        self.assertIsNotNone(plik.utworzenie)
        self.assertIsNotNone(plik.modyfikacja)
        self.assertIsNone(plik.modyfikacja_dostepnosci)
        # wlasciciel:
        plik = Plik.objects.create(nazwa="Testowy Plik4", wlasciciel=self.user)
        self.assertEqual(plik.wlasciciel, self.user)
        # powiazanie z katalogiem:
        katalog = Katalog.objects.create(nazwa="Testowy Katalog7", wlasciciel=self.user)
        plik = Plik.objects.create(nazwa="Testowy Plik6", wlasciciel=self.user, rodzic_folder=katalog)
        self.assertEqual(plik.rodzic_folder, katalog)

    def test_plik_aktualizacja_dostepnosci(self):
        # aktualizacja modyfikacja_dostepnosci
        plik = Plik.objects.create(nazwa="Testowy Plik8", wlasciciel=self.user)
        plik.dostepny = False
        plik.save()
        self.assertIsNotNone(plik.modyfikacja_dostepnosci)



class SekcjaTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser3", password="test")
        self.plik = Plik.objects.create(nazwa="Testowy Plik9", wlasciciel=self.user)

    def test_sekcja_domyslne_wartosci(self):
        sekcja = Sekcja.objects.create(
            nazwa="Testowa Sekcja1",
            poczatek=1,
            koniec=10,
            rodzaj="PR",
            rodzic_plik=self.plik
        )
        self.assertEqual(sekcja.status, "BEZ")
        self.assertEqual(sekcja.dane_statusu, "")
        self.assertIsNotNone(sekcja.utworzenie)
        self.assertEqual(sekcja.rodzic_plik, self.plik)

    def test_sekcja_inne_wartosci(self):
        sekcja = Sekcja.objects.create(
            nazwa="Inna Sekcja",
            poczatek=5,
            koniec=15,
            rodzaj="KO",
            status="Z",
            dane_statusu="Kompiluje się z ostrzeżeniami",
            rodzic_plik=self.plik
        )
        self.assertEqual(sekcja.status, "Z")
        self.assertEqual(sekcja.dane_statusu, "Kompiluje się z ostrzeżeniami")
        self.assertIsNotNone(sekcja.utworzenie)
        self.assertEqual(sekcja.rodzic_plik, self.plik)