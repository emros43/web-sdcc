from django.shortcuts import render, redirect
from django.http import Http404, HttpResponse, JsonResponse
from datetime import datetime
from .models import Katalog, Plik, Sekcja
from .forms import KatalogForm, PlikForm, SekcjaForm
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
import subprocess, os



def indeks(request):
    katalogi = Katalog.objects.all()
    pliki = Plik.objects.all()
    return render(request, "index.html", {"katalogi": katalogi, "pliki": pliki})



def plik(request, nazwa_pliku):
    try: # sciaganie zawartosci pliku:
        wyswietlany = Plik.objects.get(nazwa=nazwa_pliku)
    except Plik.DoesNotExist:
        raise Http404("Plik o tej nazwie nie istnieje w bazie.")

    if request.method == "GET" and nazwa_pliku.endswith(".c"):
        standard = request.GET.get("item1", "--std-c11")
        speed = request.GET.get("speed", "")
        size = request.GET.get("size", "")
        nolabel = request.GET.get("nolabel", "")
        procesor = request.GET.get("item3", "-mstm8")
        zalezna1 = request.GET.get("zalezna1", "")
        zalezna2 = request.GET.get("zalezna2", "")
        zalezna3 = request.GET.get("zalezna3", "")

        assembled = ""

        if "submit-form-save" in request.GET: # zmienna na obsluge pobierania
            czy_pobierac = True
        else:
            czy_pobierac = False

        terminal = ["sdcc", "-S", procesor, standard]
        if (speed != ""):
            terminal.append(speed)
        if (size != ""):
            terminal.append(size)
        if (nolabel != ""):
            terminal.append(nolabel)
        if (zalezna1 != ""):
            terminal.append(zalezna1)
        if (zalezna2 != ""):
            terminal.append(zalezna2)
        if (zalezna3 != ""):
            terminal.append(zalezna3)
        terminal.append(nazwa_pliku)
        
        with open(nazwa_pliku, "w") as f: # tworzenie tymczasowego pliku o tresci:
            f.write(wyswietlany.tresc)

        try: # kompilacja
            subprocess.run(terminal, check=True)
        except subprocess.CalledProcessError as e:
            if e.stderr == None:
                assembled += f"Wystąpił błąd w składni C"
            else:
                assembled += f"Wystąpił błąd: {e.stderr}"
            os.remove(nazwa_pliku)
            return JsonResponse({"tresc": wyswietlany.tresc, "assembled": assembled})

        assembled_nazwa = nazwa_pliku[:-2] + ".asm" # zapisywanie tresci pliku wynikowego
        with open(assembled_nazwa) as f:
            assembled = f.read()
        if czy_pobierac:
            response = HttpResponse(assembled)
            response["Content-Disposition"] = f"attachment; filename='{assembled_nazwa}'"
            os.remove(nazwa_pliku)
            os.remove(assembled_nazwa)
            return response

        os.remove(nazwa_pliku)
        os.remove(assembled_nazwa)

        # assembled = "sdcc -S " + procesor + " " + standard + " " + speed + " " + size + " " + nolabel + " " + zalezna1 + " " + zalezna2 + " " + zalezna3 + " " +nazwa_pliku

    elif not (nazwa_pliku.endswith(".c")):
        assembled = "Plik nie ma rozszerzenia .c"
    return JsonResponse({"tresc": wyswietlany.tresc, "assembled": assembled})



def zaloguj(request):
    if request.method == "POST":
        form = AuthenticationForm(request, request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect("indeks")
            else:
                messages.error(request,"Podany login lub hasło są nieprawidłowe.")
        else:
            messages.error(request,"Podany login lub hasło są nieprawidłowe.")
    form = AuthenticationForm()
    return render(request, "login.html", {"form": form})


def wyloguj(request):
	logout(request)
	messages.info(request, "Wylogowano.")
	return redirect("indeks")



def nowy_plik(request):
    katalogi = Katalog.objects.filter(wlasciciel = request.user)
    if request.method == "POST":
        form = PlikForm(katalogi, request.POST)

        if form.is_valid():
            form.instance.wlasciciel = request.user
            nazwa_katalogu = request.POST["katalog_nadrzedny"]
            if nazwa_katalogu != "":
                katalog = Katalog.objects.get(nazwa=nazwa_katalogu)
                form.instance.rodzic_folder = katalog

            form.save()
            return redirect("indeks")
    else:
        form = PlikForm(katalogi)
    return render(request, "nowy_plik.html", {"form": form, "katalogi": katalogi})

def nowy_katalog(request):
    katalogi = Katalog.objects.filter(wlasciciel = request.user)
    if request.method == "POST":
        form = KatalogForm(katalogi, request.POST)

        if form.is_valid():
            form.instance.wlasciciel = request.user
            nazwa_katalogu = request.POST["katalog_nadrzedny"]
            if nazwa_katalogu != "":
                katalog = Katalog.objects.get(nazwa=nazwa_katalogu)
                form.instance.rodzic_folder = katalog
            form.save()
            return redirect("indeks")
    else:
        form = KatalogForm(katalogi)
    return render(request, "nowy_katalog.html", {"form": form, "katalogi": katalogi})



def usun_plik(request):
    if request.method == "POST":
        nazwa_pliku = request.POST["plik"]
        plik = Plik.objects.get(nazwa = nazwa_pliku)
        plik.dostepny = False
        plik.modyfikacja_dostepnosci = datetime.now()

        plik.save()
        return redirect("indeks")
    else:
        pliki = Plik.objects.filter(dostepny = True)
        return render(request, "usun_plik.html", {"pliki": pliki})

def usun_katalog(request):
    if request.method == "POST":
        nazwa_katalogu = request.POST["katalog"]
        katalog = Katalog.objects.get(nazwa = nazwa_katalogu)
        katalog.dostepny = False
        katalog.modyfikacja_dostepnosci = datetime.now()

        katalog.save()
        return redirect("indeks")
    else:
        katalogi = Katalog.objects.filter(dostepny = True)
        return render(request, "usun_katalog.html", {"katalogi": katalogi})
