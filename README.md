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

---

### Demo

Bij het starten van de applicatie verschijnt een ASCII-art titel en het hoofdmenu:

```bash
    _    ____ _____ ____   ___        _                            _   
   / \  / ___|_   _|  _ \ / _ \      (_)_ __ ___  _ __   __ _  ___| |_ 
  / _ \ \___ \ | | | |_) | | | |_____| | '_ ` _ \| '_ \ / _` |/ __| __|
 / ___ \ ___) || | |  _ <| |_| |_____| | | | | | | |_) | (_| | (__| |_ 
/_/   \_\____/ |_| |_| \_\\___/      |_|_| |_| |_| .__/ \__,_|\___|\__|

Welkom bij ASTRO-impact — Simuleer de impact van een asteroïde!

Wat wil je doen?
1. Bekijk de lijst met asteroïden
2. Bekijk de lijst met landen
3. Simuleer een inslag
4. Kies een ander tabel thema
5. Sluit het programma

Maak een keuze (1–5): 
````

Voorbeeld van een tabel met asteroïden (uit NASA API):

```bash
+--------+-------------+----------------+----------------+----------------+----------------+------------+
| ID     | Naam        | Min diameter   | Max diameter   | Snelheid (km/u)| Afstand (km)   | Gevaarlijk?|
+--------+-------------+----------------+----------------+----------------+----------------+------------+
| 354251 | 2005 JU108  | 240            | 520            | 36,400         | 5,320,000      | Nee        |
| 433953 | 1997 XR2    | 120            | 270            | 58,900         | 9,840,000      | Ja         |
...
```

Voorbeeld van een impact simulatie:

```bash
🔴 **Energie van de inslag**  
- De kracht van de inslag van 2005 JU108 op Netherlands is 3,4e+18 joules.  
- Dat komt overeen met ongeveer 54 × de energie van de atoombom op Hiroshima.  
- Komt overeen met circa 820.00 megaton TNT.  

🟡 **Vergelijking met historische inslagen**  
- Deze inslag is kleiner dan Chicxulub, maar nog steeds verwoestend op regionale schaal.  

🟢 **Gevolgen voor het getroffen gebied**  
- Ongeveer 17.24% van Netherlands zou worden vernietigd.  
- Verwachte slachtoffers: 2.8 miljoen mensen
