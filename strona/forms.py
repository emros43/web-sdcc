from django import forms
from .models import Plik, Katalog, Sekcja

class PlikForm(forms.ModelForm):
    katalog_nadrzedny = forms.ChoiceField(choices=[], required=False, label='Folder nadrzędny')

    class Meta:
        model = Plik
        fields = ['nazwa', 'opis', 'tresc']
        labels = {'nazwa': 'Nazwa pliku',
                    'opis': 'Opis pliku',
                    'tresc': 'Treść pliku',
                 }
        
    def __init__(self, katalogi, *args, **kwargs):
        super(PlikForm, self).__init__(*args, **kwargs)
        self.fields['katalog_nadrzedny'].choices = [('', '~/')] + [(k.nazwa, k) for k in katalogi]



class KatalogForm(forms.ModelForm):
    katalog_nadrzedny = forms.ChoiceField(choices=[], required=False, label='Folder nadrzędny')

    class Meta:
        model = Katalog
        fields = ['nazwa', 'opis']
        labels = {'nazwa': 'Nazwa katalogu',
                    'opis': 'Opis katalogu'
                 }
        
    def __init__(self, katalogi, *args, **kwargs):
        super(KatalogForm, self).__init__(*args, **kwargs)
        self.fields['katalog_nadrzedny'].choices = [('', '~/')] + [(k.nazwa, k) for k in katalogi]


class SekcjaForm(forms.ModelForm):
    class Meta:
        model = Sekcja
        fields = ['nazwa', 'opis', 'poczatek', 'koniec', 'rodzic_sekcja', 'rodzaj']
        labels = {'nazwa': 'Nazwa sekcji',
                    'opis': 'Opis sekcji',
                    'poczatek': 'Poczatek sekcji',
                    'koniec': 'Koniec sekcji',
                    'rodzic_sekcja': 'Sekcja w sekcji',
                    'rodzaj': 'Rodzaj sekcji'
                 }
