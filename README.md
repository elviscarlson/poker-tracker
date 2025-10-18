# 🃏 Poker Statistik Tracker

En webbaserad applikation för att spåra och analysera din pokerstatistik. Byggd med Streamlit och SQLite.

## ✨ Funktioner

- **Användarhantering**: Skapa konto och logga in säkert
- **Sessionshantering**: Lägg till pokersessioner med datum, speltid och resultat
- **Omfattande statistik**:
  - Total vinst/förlust över tid
  - Kumulativ vinstgraf
  - Vinst per session och per timme
  - Win rate och antal sessioner
  - Detaljerad analys med median, standardavvikelse och trender
  - Bästa och sämsta sessioner
- **Interaktiva grafer**: Visualisering med Plotly för enkel analys
- **Sessionshistorik**: Se alla dina sessioner och ta bort felaktiga poster

## 🚀 Kom igång

### Förutsättningar

- Python 3.8 eller senare
- pip (Python package manager)

### Installation

1. Klona detta repository:
```bash
git clone <repository-url>
cd poker-tracker
```

2. Skapa en virtuell miljö (rekommenderas):
```bash
python -m venv venv
source venv/bin/activate  # På Windows: venv\Scripts\activate
```

3. Installera beroenden:
```bash
pip install -r requirements.txt
```

### Kör applikationen

```bash
streamlit run app.py
```

Applikationen öppnas automatiskt i din webbläsare på `http://localhost:8501`

## 📊 Användning

1. **Skapa konto**: Registrera dig med användarnamn och lösenord
2. **Logga in**: Använd dina uppgifter för att logga in
3. **Lägg till session**: Gå till fliken "Lägg till session" och fyll i:
   - Datum för sessionen
   - Speltid i timmar
   - Vinst (positivt tal) eller förlust (negativt tal) i kronor
4. **Analysera**: Se din statistik i Dashboard-fliken
5. **Hantera sessioner**: Se alla sessioner och ta bort felaktiga i fliken "Alla sessioner"

## 📁 Filstruktur

```
poker-tracker/
│
├── app.py                 # Huvudapplikation
├── requirements.txt       # Python-beroenden
├── .gitignore            # Git ignore-fil
├── README.md             # Denna fil
└── poker_tracker.db      # SQLite-databas (skapas automatiskt)
```

## 🔒 Säkerhet

- Lösenord hashas med SHA-256 innan de sparas i databasen
- All data sparas lokalt i en SQLite-databas
- Ingen data skickas till externa servrar

## 🛠️ Teknologi

- **Streamlit**: Webbapplikationsramverk
- **SQLite**: Lokal databas
- **Pandas**: Datahantering och analys
- **Plotly**: Interaktiva grafer och visualiseringar

## 📝 Framtida förbättringar

- Stöd för olika speltyper (turneringar, sit-and-go)
- Export av data till CSV/Excel
- Mer avancerad analys (ROI, ITM%, etc.)
- Jämförelse mellan olika tidsperioder
- Anteckningar per session
- Spelplats/kasino-spårning
- Motståndarprofiler

## 🤝 Bidrag

Bidrag är välkomna! Skapa gärna en issue eller pull request.

## 📄 Licens

Detta projekt är öppen källkod och tillgängligt under MIT-licensen.

## ⚠️ Ansvarsfriskrivning

Detta verktyg är endast till för personlig spårning och analys. Spela ansvarsfullt.