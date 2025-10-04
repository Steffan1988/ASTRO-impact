# ASTRO-impact

**ASTRO-impact** is een interactieve command-line applicatie geschreven in Python.
Met ASTRO-impact kun je simuleren wat er gebeurt als een asteroïde de aarde raakt, inclusief energie, schade, slachtoffers en vergelijkingen met historische inslagen zoals Chicxulub.

### Functies

Met ASTRO-impact kun je:

* Near-Earth asteroïden bekijken via de NASA API
* Landinformatie ophalen via de REST Countries API
* Een willekeurige of specifieke asteroïde en land selecteren
* De impact simuleren met berekende energie, magnitude en schade
* Vergelijken met de Chicxulub-inslag en de schaal van Richter
* Tabelthema’s kiezen voor een gepersonaliseerde weergave
* Werken met een lokale JSON-cache voor snelle API-laadtijden

### Gebruikte libraries

* **requests** – API-verkeer (NASA en REST Countries)
* **prettytable**, **colortable** – tabellen en thema’s
* **cprint**, **pyfiglet** – kleurrijke CLI en ASCII-art
* **humanize** – leesbare getallen (zoals ‘miljoen’ of ‘miljard’)
* **math**, **random**, **datetime**, **os**, **platform** – standaard Python-modules
* **dotenv** (optioneel) – voor veilige API-key opslag

### Over dit project

ASTRO-impact is ontwikkeld als eindproject binnen de module *Programming Fundamentals* bij NOVI Hogeschool.
Het project combineert API-integratie, bestandsbeheer, datastructuren, wiskundige berekeningen en gebruikersinteractie in een visueel aantrekkelijke CLI-simulatie.

### English summary

*ASTRO-impact is an interactive Python CLI simulation that models asteroid impacts on Earth using live NASA data. It calculates energy, magnitude, and damage estimates, comparing them to real-world events like the Chicxulub impact, with dynamic tables, colorful output, and API integrations.*

---

### Installatie & gebruik

**Vereisten:**

* Python 3.10 of hoger
* Een gratis NASA API key (verkrijgbaar via [api.nasa.gov](https://api.nasa.gov))

1. Clone de repository:

   ```bash
   git clone https://github.com/Steffan1988/astro-impact.git
   cd astro-impact
   ```

2. Installeer de dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Maak een `.env` bestand aan en voeg je NASA API key toe:

   ```bash
   cp .env.example .env
   # Open .env en vul je eigen API_KEY in
   ```

4. Start de applicatie:

   ```bash
   python astro_impact.py
   ```
