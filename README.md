# 90minut.pl – Wyniki meczów

Integracja Home Assistant pobierająca dane o meczach i wynikach z serwisu [90minut.pl](https://www.90minut.pl/).

## 🇵🇱 Funkcje
- Stan sensora = ostatni rozegrany mecz (np. `Górnik Zabrze 2-1 Jagiellonia Białystok`)
- Atrybuty `matches` zawierają listę ostatnich i nadchodzących spotkań
- Automatyczne wykrywanie sezonu (`auto`)
- Rekonfiguracja z poziomu UI
- Dynamiczne odświeżanie (6 h lub 10 min w trakcie meczu)
- Lokalne herby w `/local/herby/`

### Instalacja przez HACS
1. W HACS → „Niestandardowe repozytoria” → dodaj  
   `https://github.com/GieOeRZet/matches_90minut`  
   jako *Integracja (Integration)*.
2. Zainstaluj i zrestartuj Home Assistanta.
3. Dodaj integrację **„90minut.pl – Wyniki meczów”** w UI.

💡 **Powiązana karta frontendowa:**  
👉 [Matches Card (frontend)](https://github.com/GieOeRZet/matches-card)

---

## 🇬🇧 90minut.pl – Match Results

Home Assistant integration fetching football match data from [90minut.pl](https://www.90minut.pl/).

### Features
- Sensor state = latest played match (e.g., `Górnik Zabrze 2-1 Jagiellonia Białystok`)
- `matches` attributes list recent and upcoming games
- Automatic season detection (`auto`)
- Reconfigurable from UI
- Dynamic update interval (6 h or 10 min during matches)
- Local crests in `/local/herby/`

### Installation via HACS
1. In HACS → “Custom repositories” → add  
   `https://github.com/GieOeRZet/matches_90minut`  
   as *Integration*.
2. Install and restart Home Assistant.
3. Add integration **“90minut.pl – Match Results”** in UI.

💡 **Related Lovelace card:**  
👉 [Matches Card (frontend)](https://github.com/GieOeRZet/matches-card)
