from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils import timezone
from django.core.exceptions import ValidationError



class Uzytkownik(models.Model): # rozszerza klase User, ktora juz posiada login i haslo, o pole nazwa
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    nazwa = models.CharField(max_length=50)



class Katalog(models.Model):
    nazwa = models.CharField(max_length=100, unique=True, primary_key=True)
    opis = models.TextField(null=True, blank=True)
    dostepny = models.BooleanField(default=True)
    utworzenie = models.DateTimeField(auto_now_add=True)
    modyfikacja = models.DateTimeField(auto_now=True)
    modyfikacja_dostepnosci = models.DateTimeField(blank=True, null=True)
    wlasciciel = models.ForeignKey(User, on_delete=models.CASCADE)
    rodzic_folder = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        if self.rodzic_folder == None:
            return f"~/{self.nazwa}"
        return f"{self.rodzic_folder}/{self.nazwa}"

@receiver(pre_save, sender=Katalog)
def update_modyfikacja_dostepnosci(sender, instance, **kwargs):
    if instance.pk is not None and instance.dostepny != True:
        instance.modyfikacja_dostepnosci = timezone.now()



class Plik(models.Model):
    nazwa = models.CharField(max_length=100, unique=True, primary_key=True)
    opis = models.TextField(null=True, blank=True)
    dostepny = models.BooleanField(default=True)
    utworzenie = models.DateTimeField(auto_now_add=True)
    modyfikacja = models.DateTimeField(auto_now=True)
    modyfikacja_dostepnosci = models.DateTimeField(blank=True, null=True)
    wlasciciel = models.ForeignKey(User, on_delete=models.CASCADE)
    tresc = models.TextField(blank=False, null=False) # wygodniej tutaj trzymac calosc, niz w sekcji kawalki
    rodzic_folder = models.ForeignKey(Katalog, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        if self.rodzic_folder == None:
            return f"~/{self.nazwa}"
        return f"{self.rodzic_folder}/{self.nazwa}"

@receiver(pre_save, sender=Plik)
def update_modyfikacja_dostepnosci_pliku(sender, instance, **kwargs):
    if instance.pk is not None and instance.dostepny != True:
        instance.modyfikacja_dostepnosci = timezone.now()



class Sekcja(models.Model):
    nazwa = models.CharField(max_length=100, null=True, blank=True)
    opis = models.TextField(null=True, blank=True)
    utworzenie = models.DateTimeField(auto_now_add=True)
    poczatek = models.PositiveIntegerField()
    koniec = models.PositiveIntegerField()
    rodzic_plik = models.ForeignKey(Plik, on_delete=models.CASCADE)
    rodzic_sekcja = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)

    RODZAJE_SEKCJI = [
        ('PR', 'Procedura'),
        ('KO', 'Komentarz'),
        ('DK', 'Dyrektywny kompilatora'),
        ('DZ', 'Deklaracje zmiennych'),
        ('WS', 'Wstawka asemblerowa'),
    ]
    STATUSY_SEKCJI = [
        ('Z', 'Kompiluje się z ostrzeżeniami'),
        ('BEZ', 'Kompiluje się bez ostrzeżeń'),
        ('NIE', 'Nie kompiluje się'),
    ]
    rodzaj = models.CharField(max_length=3, choices=RODZAJE_SEKCJI)
    status = models.CharField(max_length=3, choices=STATUSY_SEKCJI, default='BEZ')
    dane_statusu = models.TextField(blank=True)
    
    def __str__(self):
        if self.rodzic_folder == None:
            return f"~/{self.nazwa}"
        return f"{self.rodzic}/{self.nazwa}"

