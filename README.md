# 🛰️ Drone Swarm Optimizer

Projekt magisterski – symulacja zachowania rojów dronów w poszukiwaniu globalnego ekstremum (źródła sygnału) z użyciem **algorytmów optymalizacyjnych inspirowanych naturą**. 

Wykorzystany do analizy i porównania zachowań różnych metaheurystyk, rezultaty oraz wnioski opisano w pracy magisterskiej:
"Poszukiwanie źródła sygnału z wykorzystaniem metod inspirowanych metaheurystykami populacyjnymi", Nikodem Korohoda, AGH, 2025

## 📌 Opis
System symuluje grupy dronów eksplorujących dwuwymiarową mapę w celu lokalizacji punktu o maksymalnej wartości sygnału.  
Każdy rój sterowany jest innym **metaheurystycznym algorytmem optymalizacji**, co pozwala porównać ich skuteczność i szybkość zbieżności.

Dostępne algorytmy:
- 🐺 **GWO** – Grey Wolf Optimizer  
- 🐦 **PSO** – Particle Swarm Optimization  
- 🔥 **PSA** – Population Simulated Annealing  
- 🐜 **ACO** – Ant Colony Optimization (zaprzestano rozwijania) 
- 🎲 Algorytmy bazowe: losowe wyszukiwanie, tabu search itp.

## ⚙️ Funkcjonalności
- Interaktywna wizualizacja w **Tkinterze** (mapa, drony, ścieżki, feromony).  
- Sterowanie symulacją: start/stop, ukrywanie/widoczność wizualizacji.  
- Logowanie metryk do plików `.csv`:  
  - średni maksymalny sygnał,  
  - liczba dronów, które osiągnęły maksimum,  
  - średni sygnał bieżący.  
- Automatyczne generowanie wykresów w **Matplotlib** (SVG/PDF, wektorowe).  
- Obsługa wielu rojów jednocześnie → porównanie algorytmów na jednej mapie.  
- Elastyczna konfiguracja poprzez plik `conf`.


## 🧪 Eksperymenty
- Możesz ustawić parametry w pliku konfiguracyjnym (`conf`) lub w kodzie:
  - liczba iteracji,  
  - liczba dronów,  
  - rozmiar mapy,  
  - parametry algorytmów (np. `alpha, beta, rho` w ACO).  

- W folderze `assets/graphs` znajdziesz wygenerowane wykresy porównawcze.
