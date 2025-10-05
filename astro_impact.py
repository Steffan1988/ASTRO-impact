# ----------------------------------------- Import van modules en packages ------------------------------------------- #
import json # json bestanden uit api-points of eigen files kunnen bekijken
import requests # API-requests mogelijk maken
import random # random module
import math # voor de berekening in joules & magnitude
import os

from prettytable.colortable import ColorTable, Themes       # Prettytable met kleurthema's
from cprint import cprint                                   # Printen in kleurtjes
from pyfiglet import Figlet                                 # Voor ASCII-art in het hoofdmenu
from richter_schaal import richter_schaal_data              # Dictionary import uit eigen bestand

# humanize
import humanize
from humanize import intword
humanize.i18n.activate("nl_NL") # Activeer de Nederlandse taal

# voor timestamps
from datetime import datetime, timedelta
import platform

# ------------------------------------ Constanten voor simulatie berekening ------------------------------------------ #
# De energie van de Chicxulub-inslag wordt geschat op ongeveer 5,0 x 10^23 joules
CHICXULUB_ENERGY = 1e23
# Wereldbevolking, int want er zijn geen mensen achter de komma, volgens de officiële statistieken dan....
WORLD_POP = int(8.2e9)
# Volgens bronnen zoals Our World in Data: Bewoonbaar landoppervlak ≈ 104 miljoen km²
BEWOONBAAR_OPPERVLAK = 104_000_000
# Totale oppervlakte aarde 510.1 miljoen km²
TOTAAL_OPPERVLAKTE_AARDE = 510_100_000

HIROSHIMA_JOULES = 6.3e13     # De (geschatte) energie van de Hiroshima bom
MEGATON_TNT_JOULE = 4.184e15      # 1 megaton TNT

# ------------------------------------------- UI-instellingen en opmaak ---------------------------------------------- #
#Standaard instellingen van de tabel
table = ColorTable()
table.theme = Themes.DYSLEXIA_FRIENDLY
table.align = "l"
table.float_format = ".0"

# Font figlet
f = Figlet(font='standard')

# ----------------------------------------------- API-configuratie --------------------------------------------------- #
# dotenv activeren voor veilige API-KEY
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv("API_KEY")

# Startdatum instellen op 6 dagen geleden zodat de NASA-feed de volledige laatste 7 dagen meepakt.
# Deze API-call is live best traag, maar dankzij de cache is de app alsnog snel.
# NASA ondersteunt max. 7 dagen per call — daarom kies ik hier bewust voor het maximale bereik.
start_date = (datetime.today() - timedelta(days=6)).strftime("%Y-%m-%d")

# -------------------------------------------------- Hulpfuncties ---------------------------------------------------- #
def toon_value_error():
    """Herbruikbare value error"""
    cprint("Je kunt hier alleen getallen invoeren.", c="rB")

def toon_bestand_error():
    """Herbruikbare file error"""
    cprint(f"Er is iets mis met het bestand: De cache kon niet correct worden ingelezen.", c="rB")

def clear_screen():
    """Maakt het scherm leeg, platform-onafhankelijk."""
    if platform.system() == "Windows":
        os.system("cls")
    else:
        os.system("clear")

# ----------------------------------------------------API-Calls------------------------------------------------------- #
def toon_nabije_asteroid(api_key_nasa, start_datum):
    """
    Haalt near-earth object data op van de NASA API voor een opgegeven startdatum.
    """
    url = f"https://api.nasa.gov/neo/rest/v1/feed"
    params = {
        "start_date": start_datum,
        "api_key": api_key_nasa
    }
    response = requests.get(url, params=params)

    if response.ok:
        data = response.json()
        return data
    else:
        print("Er is iets misgegaan")
        print("Statuscode:", response.status_code)
        return None

def haal_landen_op():
    """Haalt gegevens op van alle landen via de REST Countries API.
    Per land wordt de volgende info opgehaald:
    - Landnaam
    - Populatie
    - Oppervlakte (in km²)"""
    url = "https://restcountries.com/v3.1/all?fields=name,population,area"
    response = requests.get(url)

    if response.ok:
        landen = response.json()
        # direct met een list comprehension de data formatteren voor in de tabel
        return [
            [
                land["name"]["common"],
                land["population"],
                land["area"],
                # Dit zat niet in de API dus hier wordt de bevolkingsdichtheid berekend
                round(land['population'] / land['area'],0)
            ]
            for land in landen]
    else:
        cprint("Fout bij ophalen landdata:", response.status_code, c="rB")
        return []

# -------------------------------------- Functies voor tabellen en dataweergave -------------------------------------- #
def build_table():
    """
    Laadt de asteroïde-data uit de lokale cache.
    Als de cache ontbreekt of verouderd is, wordt deze automatisch vernieuwd.
    De functie returned een lijst met asteroïde informatie voor tabelweergave.
    """
    # lees de cache en stop de inhoud in een lijst
    asteroidenlijst = read_cache()

    # Als er geen cache beschikbaar wordt een loop uitgevoerd waar:
    # -de data ververst wordt en opgeslagen
    # -een nieuw bestand wordt aangemaakt als deze nog niet bestaat en beschreven uit de end-point van NASA
    # -een nieuw pad wordt aangemaakt als deze niet nog bestaat
    while not asteroidenlijst:
        cprint("Je hebt nog geen cache, hij wordt beschreven", c="rB")
        write_cache()
        return build_table()
    time_cache = asteroidenlijst["timestamp"]

    # Hier moest de cache time eerst ge-parsed worden van string naar een datetime object,
    # Anders deed mijn vergelijking voor de actualiteit van de cache niet
    cache_time_parsen = datetime.strptime(time_cache, "%d%m%Y%H%M")
    if datetime.now().date() != cache_time_parsen.date():
        cprint("Je cache is ouder dan een dag, de cache wordt herladen", c="rB")
        write_cache()
    try:
        data = []
        for astro in asteroidenlijst["objecten"]:
            diameter = astro["estimated_diameter"]["meters"]
            min_d = diameter["estimated_diameter_min"]
            max_d = diameter["estimated_diameter_max"]

            approach = astro["close_approach_data"][0]
            snelheid = float(approach["relative_velocity"]["kilometers_per_hour"])
            afstand = float(approach["miss_distance"]["kilometers"])

            data.append([
                astro["id"],
                astro["name"],
                round(min_d,0),
                round(max_d,0),
                round(snelheid,0),
                round(afstand,0),
                "Ja" if astro["is_potentially_hazardous_asteroid"] else "Nee"
            ])
        return data
    except KeyError:
        cprint("Foutieve sleutel in de data. Probeer je cache te verversen.", c="rB")
    except FileNotFoundError:
        toon_bestand_error()
    except TypeError:
        cprint("Je had nog geen cache, de tabel wordt opnieuw opgebouwd.", c="y")

    return build_table()

def show_table(data, kolommen, titel="Tabel"):
    """
    Laat een interactieve tabel zien waarin je zelf kiest hoeveel rijen per pagina je wilt zien.

    PrettyTable ondersteunt maar één actieve tabel tegelijk. Daarom is deze functie herbruikbaar
    gemaakt, zodat je toch meerdere tabellen kunt tonen binnen hetzelfde script.

    :param data: De rijen van de tabel (lijst van lijsten).
    :param kolommen: De kolomnamen bovenaan de tabel.
    :param titel: De titel van de tabel.
    """
    table.field_names = kolommen

    # Een FOR-loop gebruiken om alle data in rijen te zetten
    for rij in data:
        table.add_row(rij)

    cprint(f"\n{titel}", c="bB")
    try:
        # page_size = int(input(f"Hoeveel rijen wil je per pagina tonen? (max {len(data)}): "))
        # While loop om te voorkomen dat de gebruiker een hoger getal invoer dan dat er aan data entries is.
        while True:
            page_size = int(input(f"Hoeveel rijen wil je per pagina tonen? (max {len(data)}): "))
            if page_size > len(data):
                cprint(f"\nJe gaf {page_size} op, maar deze dataset bevat slechts {len(data)} rijen.", c="rB")
            else:
                break

        start_index = 0
        while True:
            # start_index = start_index
            clear_screen()
            huidige_pagina = int(start_index / page_size) + 1
            # math.ceil() gebruikt want deze rond een getal omhoog af naar het dichtstbijzijnde hele waarde.
            # Dit om te zorgen dat de laatste pagina ook getoond wordt, zelfs als die niet volledig gevuld is.
            aantal_paginas = math.ceil(len(data) / page_size)
            while huidige_pagina == aantal_paginas + 1:
                cprint("\nJe bent op het einde van de tabel aangekomen.", c="y")
                start_pagina = input(
                    "Terug naar het begin?\nTyp 'j' om opnieuw te starten, of 'n' voor het hoofdmenu: "
                ).lower().strip()

                if start_pagina == "j":
                    start_index = 0
                    huidige_pagina = 1
                    break
                elif start_pagina == "n":
                    return
                else:
                    cprint(f"Ongeldige invoer: '{start_pagina}'. Probeer 'j' of 'n'.", c="r")

            # In eerste instantie probeerde ik de tabel te pagineren met slicing:
            # print(table[start_index: start_index + page_size])
            # Dit leek logisch, maar bleek fout: deze slicing negeerde sortering en gaf de rijen in willekeurige
            # volgorde weer. In de documentatie van PrettyTable
            # (hoofdstuk “Displaying your table in ASCII form” en “Controlling which data gets displayed”)
            # ontdekte ik dat je voor gesorteerde en correcte output gebruik moet maken van de get_string()-methode.
            # Deze respecteert sortby, reversesort én ondersteunt slicing via start en end.
            # Zo kreeg ik de code uiteindelijk wel werkend!
            print(table.get_string(start=start_index, end=start_index + page_size))

            cprint(f"Pagina {huidige_pagina} van {aantal_paginas}", c="g")

            actie = input(
                "Kies 1 van de volgende opties:\n"
                "[V]olgende  |  [T]erug  |  [K]iezen  |  [S]orteren  |  [H]oofdmenu\n> "
            ).lower().strip()

            if actie == 'v':
                start_index += page_size
            elif actie == 't' and start_index >= page_size:
                start_index -= page_size
            elif actie == 'k':
                if titel == "Near-earth objects":
                    sessie_data["asteroide"] = set_asteroide_in_sessie()
                    return
                elif titel == "Landen overzicht":
                    sessie_data["land"] = set_land_in_sessie()
                    return
            # Deze code onder de elif actie is om je data te sorteren
            elif actie == 's':
                cprint("\nWelke kolom wil je sorteren?", c="b")
                for i in range(len(kolommen)):
                    # + omdat je anders de keuzes 0,1,2,3 krijgt i.p.v. 1,2,3,4
                    # voor een gebruiker is dit namelijk veel logischer
                    cprint(f"{i + 1}. {kolommen[i]}", c="c")
                try:
                    kolom_keuze = int(input("\nVoer het nummer van de kolom in: "))
                    kolom_naam = kolommen[kolom_keuze - 1]
                    table.sortby = kolom_naam
                    # Uitzondering voor de kolom 'gevaarlijk' omdat dit iets logischer voelt voor het gebruik
                    if kolom_naam == 'Gevaarlijk?':
                        richting = input(
                            f"Sorteervolgorde '{kolom_naam}': [G]evaarlijk → Ongevaarlijk, "
                            f"[O]ngevaarlijk → Gevaarlijk\n> "
                        ).lower().strip()
                        table.reversesort = richting == "o"
                    else:
                        richting = input(
                            f"Sorteervolgorde '{kolom_naam}': [O]plopend of [A]flopend?\n> "
                        ).lower().strip()
                        table.reversesort = richting == "a"

                    start_index = 0

                except (ValueError, IndexError):
                    cprint("Ongeldige keuze, sorteren wordt overgeslagen.", c="r")
            elif actie == 'h':
                break
            else:
                cprint("Ongeldige keuze", c="r")

    except ValueError:
        toon_value_error()

def show_astroids():
    """
    Toont een tabel met near-earth objects uit de lokale cache van de NASA API.
    """
    show_table(
        data=build_table(),
        kolommen=["ID",
        "Naam",
        "Min diameter (m)",
        "Max diameter (m)",
        "Snelheid (km/u)",
        "Afstand (km)",
        "Gevaarlijk?"],
        titel="Near-earth objects"
    )

def tabel_met_landen():
    """
    Toont een tabel met informatie uit de API de REST Countries API.
    """
    show_table(
        data=haal_landen_op(),
        kolommen=["Land", "Populatie", "Oppervlakte (km²)", "Dichtheid (p/km²)"],
        titel="Landen overzicht"
    )

# ------------------------------------- Functies voor cachebeheer en data-opslag ------------------------------------- #
def get_cache_path():
    """
    Geeft het volledige pad naar het cachebestand en zorgt dat de map bestaat
    """
    path = os.path.join("files", "nabije_asteroid.json")
    os.makedirs("files", exist_ok=True)
    return path

def read_cache():
    """
    Leest de cache als die bestaat en geldig is, anders lege dict
    """
    path = get_cache_path()
    try:
        with open(path, 'r') as file:
            return json.load(file)
    except (json.JSONDecodeError, FileNotFoundError):
        toon_bestand_error()
        return {}

def write_cache():
    """
    Haalt verse data op en schrijft die naar het cachebestand
    """
    objecten, tijd = refresh_data()
    cache_data = {
        "objecten": objecten,
        "timestamp": tijd
    }
    path = get_cache_path()
    time_stamp_parsen = datetime.strptime(tijd, "%d%m%Y%H%M")
    with open(path, 'w') as file:
        json.dump(cache_data, file, indent=4)
    cprint(f"Cache is bijgewerkt op {time_stamp_parsen}", c="g")

def refresh_data():
    """
    Haalt de nieuwste near-earth object data op uit de NASA API en koppelt daar een timestamp aan.
    """
    data = toon_nabije_asteroid(api_key, start_date)
    neo_data = data["near_earth_objects"]
    asteroidenlijst = [asteroid for datum, lijst in neo_data.items() for asteroid in lijst]
    tijd = time_stamp()
    return asteroidenlijst, tijd

def time_stamp():
    """
    Geeft een datum-timestamp terug voor controle van cache geldigheid.
    """
    nu = datetime.now()
    if platform.system() == "Windows":
        return nu.strftime("%#d%#m%Y%H%M")
    else:
        # voor een ander platform
        return nu.strftime("%d%m%Y%H%M")

# ---------------------------------- Functies voor objectselectie door gebruiker ------------------------------------- #
def set_asteroide_in_sessie():
    """Vraag de gebruiker een asteroïde te selecteren op basis van ID.
      Blijft vragen totdat een geldige ID is ingevoerd."""
    # Cache-gegevens inlezen
    asteroidenlijst = read_cache()["objecten"]
    # Houd de gebruiker in een while loop totdat een geldig id gekozen is
    while True:
        gekozen_id = input("Voer het ID van de asteroïde in: ").strip()
        for asteroid in asteroidenlijst:
            if asteroid["id"] == gekozen_id:
                # _, is voor ongebruikte info, in dit geval snelheid_kms
                naam, d_min, d_max, snelheid, _, gevaarlijk = extract_asteroide_data(asteroid)

                cprint("Asteroïde geselecteerd:", c="yB")
                cprint(f"  Naam: {naam}", c="y")
                cprint(f"  ID: {gekozen_id}", c="y")
                cprint(f"  Diameter: {d_min:.0f}–{d_max:.0f} meter", c="y")
                cprint(f"  Snelheid: {int(snelheid):,} km/u", c="y")
                cprint(f"  Gevaarlijk: {gevaarlijk}", c="y")
                return asteroid
        cprint("Geen asteroïde gevonden met dat ID. Probeer opnieuw.", c="r")

def set_land_in_sessie():
    """
    Laat je een land kiezen op naam en toont informatie zodra het klopt.
    Geeft pas iets terug als je een geldig land hebt ingevoerd.
    """
    landen = haal_landen_op()
    # Een "disclaimer" erbij gezet omdat ik opmerkte dat bepaalde gegevens niet klopte, zoals over Nederland
    cprint("Let op: sommige landgegevens, zoals populatie, kunnen verouderd zijn (bron: REST Countries API).",
           c="yI")
    while True:
        invoer = input("Voer de Engelse naam van het land in (bijv. Netherlands): ").strip().title()
        for land in landen:
            naam, populatie, oppervlakte, dichtheid = land
            if naam == invoer:
                cprint("Selectie land:", c="yB")
                cprint(f"  Naam: {naam}", c="y")
                cprint(f"  Populatie: {intword(populatie)} mensen", c="y")
                cprint(f"  Oppervlakte: {int(oppervlakte):,} km²", c="y")
                cprint(f"  Bevolkingsdichtheid: {int(dichtheid)} mensen/km²", c="y")
                return land
        cprint(f"'{invoer}' staat niet in de lijst met landen. Probeer opnieuw.", c="r")

def extract_asteroide_data(asteroid):
    """
    Haalt de belangrijkste gegevens uit een asteroïde-object,
    dit heb ik gedaan omdat ik deze info eigenlijk oorspronkelijk 2 keer extraheerde dat vond ik niet heel DRY.
    Ook loste deze functie deze warning op: Unexpected type(s):(strPossible type(s):(SupportsIndex(slice)
    - naam
    - min/max diameter
    - snelheid (km/u)
    - snelheid (km/s)
    - gevaar-indicatie (Ja/Nee)
    """
    naam = asteroid["name"]
    diameter_min = asteroid["estimated_diameter"]["meters"]["estimated_diameter_min"]
    diameter_max = asteroid["estimated_diameter"]["meters"]["estimated_diameter_max"]
    snelheid_kmu = float(asteroid["close_approach_data"][0]["relative_velocity"]["kilometers_per_hour"])
    snelheid_kms = float(asteroid["close_approach_data"][0]["relative_velocity"]["kilometers_per_second"])
    gevaarlijk = "Ja" if asteroid["is_potentially_hazardous_asteroid"] else "Nee"
    return naam, diameter_min, diameter_max, snelheid_kmu, snelheid_kms, gevaarlijk

# -------------------------------------- Functies voor berekeningen en simulatie ------------------------------------- #
def impactenergie_asteroide():
    """Deze formule berekent de impactenergie van je gekozen asteroïde in de eenheid joules
    Ik heb hiervoor de volgende formule gebruikt:
    -E = ½ × m × v²
    -m = massa = dichtheid × volume (volume = ⁴⁄₃ × π × (r³)) # in dit geval volume van een bol
    -v = snelheid in m/s"""
    astro = sessie_data["asteroide"]

    # Extraheer de gegevens van de asteroïde uit de sessie data
    # _, is voor ongebruikte info, in dit geval naam, snelheid_kmu en gevaarlijk
    _, diameter_min, diameter_max, _, snelheid_kms, _ = extract_asteroide_data(astro)

    # gemiddelde diameter in meters
    diameter = (diameter_min + diameter_max) / 2
    straal = diameter / 2

    # volume van een bol berekenen in m³
    volume = (4 / 3) * math.pi * (straal ** 3)

    # Hier heb ik gewoon een aangenomen waarde gebruikt de hoogste dichtheid van steen = 3000 kg/m³
    # omdat een asteroïde gesteente is, vond ik dat wel gepast. Maar het blijft natuurlijk een benadering
    massa = volume * 3000

    # snelheid omzetten naar m/s
    snelheid_ms = snelheid_kms * 1000

    # energie uitrekenen in joules
    energie = 0.5 * massa * snelheid_ms ** 2

    return energie

def impact_simulatie():
    """
    Simuleert de impact van een asteroïde op een land.
    Toont schade, magnitude, slachtoffers en vergelijkt met historische inslagen.
    Vereist dat zowel een land als asteroïde geselecteerd is.
    """
    # Controleer of de gebruiker een asteroid of een land heeft geselecteerd bij het bekijken van de tabellen
    if not sessie_data["asteroide"] or not sessie_data["land"]:
        if not sessie_data["asteroide"]:
            cprint("Je hebt nog geen asteroïde geselecteerd.", c="y")
            keuze_astro = input("Wil je een willekeurige asteroïde selecteren? (j/n): ").lower()
            if keuze_astro == "j":
                random_asteroide()
                print()
            elif keuze_astro == "n":
                # Reset tabel om conflicten bij herhaalde weergave te voorkomen
                table.clear()
                show_astroids()
                impact_simulatie()
                return
            else:
                return

        if not sessie_data["land"]:
            cprint("Je hebt nog geen land geselecteerd.", c="y")
            keuze_land = input("Wil je een willekeurig land selecteren? (j/n): ").lower()
            if keuze_land == "j":
                random_land()
                print()
            # 'n' afvangen om doorsijpelen naar page_size-input te voorkomen
            elif keuze_land == "n":
                table.clear()
                tabel_met_landen()
                impact_simulatie()
                return
            else:
                return

    land = sessie_data["land"]

    # Variables toewijzen in de lijst, land: [naam, populatie, oppervlakte_land, dichtheid]
    naam, populatie, oppervlakte_land, dichtheid = land

    # haal de berekende energie op uit de functie impactenergie_asteroide()
    joules = impactenergie_asteroide()
    megaton_tnt = joules / MEGATON_TNT_JOULE
    aantal_bommen = joules / HIROSHIMA_JOULES
    cprint("\nEnergie van de inslag", c="mB")

    # Uitpakken hieronder gedaan om een Unexpected type(s):(str)Possible type(s):(SupportsIndex)(slice) op te lossen
    naam_object, _, _, _, _, _ = extract_asteroide_data(sessie_data['asteroide'])
    cprint(f"- De kracht van de inslag van {naam_object} "
           f"op {naam} is {intword(joules)} joules.", c="c")

    # percentage van de kracht van een Hiroshima bom, als het om een kleine inslag gaat.
    if aantal_bommen <= 1:
        cprint(
            f"- Dat komt overeen met ongeveer {(aantal_bommen * 100):.2f}% "
            f"van de energie van de atoombom op Hiroshima.", c="c")
    else:
        cprint(
            f"- Dat komt overeen met ongeveer {intword(aantal_bommen)} × "
            f"de energie van de atoombom op Hiroshima.", c="c")

    # TNT
    cprint(f"- Komt overeen met circa {megaton_tnt:.2f} megaton TNT.", c="c")


    # Chicxulub (de inslag die de dinosaurussen uitroeide, 66 miljoen jaar geleden)
    # We gebruiken een boolean flag om te bepalen of een asteroïde meer energie heeft dan dat event.
    # Tot nu toe heb ik 'helaas' er nog geen asteroïde in de dataset gevonden die dit niveau overschrijdt.
    extinction_event = False
    ratio_dino_extinctie = joules / CHICXULUB_ENERGY
    cprint("\nVergelijking met historische inslagen", c="mB")
    if ratio_dino_extinctie >= 1:
        cprint(f"- Dit object is {ratio_dino_extinctie:.2f}× krachtiger dan de Chicxulub-inslag "
               f"(die de dinosaurussen uitroeide).", c="rB")
        cprint("- Dit zou een wereldwijd uitstervingsscenario veroorzaken.", c="r")
        extinction_event = True
    elif ratio_dino_extinctie > 0.01:
        cprint(f"- Deze inslag heeft ongeveer {ratio_dino_extinctie:.2%} van de energie van het Chicxulub-event.",
               c="y")
        cprint("- Ernstige gevolgen, mogelijk continentale schade.", c="y")
    else:
        cprint("- Deze inslag is kleiner dan Chicxulub, maar nog steeds verwoestend op regionale schaal.", c="c")

    # Extra online info
    cprint("\nMeer weten over de Chicxulub-inslag?", c="bBI")
    print(
        "🌍 Wikipedia: https://nl.wikipedia.org/wiki/Chicxulubkrater\n"
        "🎥 Kurzgesagt-video: https://www.youtube.com/watch?v=dFCbJmgeHmA\n"
    )
    # Magnitude berekenen
    # Om de magnitude (op de schaal van Richter) van een aardbeving te berekenen op basis van de vrijgekomen energie
    # in joules, kun je een formule gebruiken die de energie (E) relateert aan de magnitude (M).
    # De formule is: E = 10^(4.8 + 1.5M). Je kunt deze formule herleiden om M te vinden: M = (log10(E) - 4.8) / 1.5.
    magnitude = (math.log10(joules) - 4.8) / 1.5

    # Aardbeving vergelijkingen als het geen extinction event is
    if not extinction_event:
        cprint("\nGevolgen voor het getroffen gebied", c="mB")
        # FOR-loop die toetst in welke schaal de aardbeving valt.
        for schaal in richter_schaal_data:
            if schaal["min_magnitude"] <= magnitude <= schaal["max_magnitude"]:
                cprint(f"- De inslag komt overeen met een aardbeving van magnitude {magnitude:.2f} "
                       f"op de schaal van Richter.", c="c")
                cprint(f"- Categorie: {schaal['label']}", c="c")
                cprint(f"- Effect: {schaal['effect']}", c="c")
                break

        # Door de bom was er ongeveer 13 km² vernietigd in Hiroshima (stad),
        # inslag modellen van de nasa waren nogal complex ook miste ik de benodigde data.
        # Daarom heb ik er voor gekozen om gewoon van de vernietigingsradius van de Hiroshima bom uit te gaan.
        vernietigde_oppervlakte = (joules / HIROSHIMA_JOULES) * 13

        if vernietigde_oppervlakte > oppervlakte_land:
            # Extra oppervlak berekenen wat ook buiten het gekozen land vernietigd wordt
            extra_oppervlak = vernietigde_oppervlakte - oppervlakte_land

            # De extra slachtoffers worden berekend door de gemiddelde bevolkingsdichtheid van de wereld te nemen.
            # We nemen aan dat dat extra oppervlak vergelijkbaar bevolkt is als het gemiddelde van de bewoonbare aarde.
            # Dit is niet ideaal voor het model, maar het geeft een grove indicatie
            extra_slachtoffers = (extra_oppervlak / BEWOONBAAR_OPPERVLAK) * WORLD_POP
            slachtoffers = populatie + extra_slachtoffers
            percentage = (vernietigde_oppervlakte / TOTAAL_OPPERVLAKTE_AARDE) * 100
            cprint(f"- Het volledige land {naam} zou worden vernietigd!", c="rB")
            cprint(f"- Totale vernietigde oppervlakte: {intword(vernietigde_oppervlakte)} km²", c="y")
            # Om output te voorkomen zoals "Dat is 0.00% van het aardoppervlak" bij zeer kleine inslagen.
            if percentage < 0.01:
                cprint("- Dat is minder dan 0.01% van het aardoppervlak.", c="y")
            else:
                cprint(f"- Dat is {percentage:.2f}% van het aardoppervlak.", c="y")
            # Deze IF/ELSE-statement voorkomt dat er meer mensen sterven dan er op aarde zijn, dit kan natuurlijk niet!
            if slachtoffers < WORLD_POP:
                cprint(f"- Verwachte slachtoffers: {intword(slachtoffers)} mensen", c="y")
            else:
                cprint(f"- Verwachte slachtoffers: praktisch de hele wereldbevolking ({intword(WORLD_POP)} "
                       f"mensen)", c="rB")
        else:
            procent_land = (vernietigde_oppervlakte / oppervlakte_land) * 100
            slachtoffers = (procent_land / 100) * populatie
            cprint(f"- Ongeveer {procent_land:.2f}% van {naam} zou worden vernietigd.", c="y")
            cprint(f"- Totale vernietigde oppervlakte: {intword(vernietigde_oppervlakte)} km²", c="y")
            cprint(f"- Verwachte slachtoffers: {intword(slachtoffers)} mensen", c="y")

    # Reset sessie data zodat de gebruiker nog een keer een willekeurige impact kan simuleren
    sessie_data["asteroide"] = []
    sessie_data["land"] = []

# ---------------------------------------- Functies voor willekeurige selectie --------------------------------------- #
def random_asteroide():
    """Deze functie haalt een willekeurige asteroïde op en zet hem vast in de sessie data """
    asteroiden = read_cache()["objecten"]
    sessie_data["asteroide"] = random.choice(asteroiden)

    # Uitpakken hieronder om een Unexpected type(s):(str)Possible type(s):(SupportsIndex)(slice) warning op te lossen
    naam_object, _, _, _, _, _ = extract_asteroide_data(sessie_data['asteroide'])
    cprint(f"Geselecteerde asteroïde: {naam_object}", c="g")

def random_land():
    """Deze functie haalt een willekeurig land op en zet hem vast in de sessie data """
    landen = haal_landen_op()
    sessie_data["land"] = random.choice(landen)
    cprint(f"Geselecteerd land: {sessie_data['land'][0]}", c="g")

# ------------------------------------ Functie voor gebruikersinstellingen (thema) ----------------------------------- #
def choice_of_theme():
    """Loop door de directory met thema's voor de package prettytable en vraag de gebruiker 1 te selecteren"""
    thema = {}
    for nummer, theme in enumerate(dir(Themes), start=1):
        # Om zaken uit te sluiten die geen thema's zijn
        if not theme.startswith("__"):
            cprint(f"{nummer}. {theme}", c="c")
            thema[nummer] = theme
    welk_thema = int(input(f'\nWelk thema wil je gebruiken? (1-{len(thema)})'))
    keuze_thema = thema[welk_thema]
    print(f'Je hebt gekozen voor het thema {keuze_thema}')
    # Voor de build-in functie 'getattr()' had ik toch echt even hulp van chatGPT nodig, ik had eerst gewoon
    # table.theme = thema_naam maar dat werkte niet. Na het even gebruiken van ChatGPT als docent heb ik begrepen
    # als je keuzes wilt maken je die functie uit een library niet zomaar een 'string' op die plaats kunt zetten.
    # Maar dat je ook letterlijk het attribuut (object) moet fetchen uit de library colortable.py
    table.theme = getattr(Themes, keuze_thema)
    return

# ----------------------------------------- Initialisatie van sessie en cache ---------------------------------------- #
sessie_data = {
    "asteroide": [],
    "land": []
}

# Bij opstart build_table() uitvoeren om er voor te zorgen dat cache-geldigheid check wordt uitgevoerd.
build_table()

# Boolean flag om te zien of dit de eerste keer is dat de gebruiker het programma opstart
eerste_keer = True

# -------------------------------------------- Hoofdmenu en programmaloop -------------------------------------------- #
while True:
    # Toon een pauze zodat de gebruiker de informatie kan lezen voordat het scherm wordt gewist
    if not eerste_keer:
        input("\nDruk op Enter om terug te keren naar het hoofdmenu...")
    else:
        eerste_keer = False
    clear_screen()
    print(f.renderText("ASTRO-impact"))
    cprint("Welkom bij ASTRO-impact — Simuleer de impact van een asteroïde!", c="bB")

    print("\nWat wil je doen?")
    cprint("1. Bekijk de lijst met asteroïden", c="c")
    cprint("2. Bekijk de lijst met landen", c="c")
    cprint("3. Simuleer een inslag", c="c")
    cprint("4. Kies een ander tabel thema", c="c")
    cprint("5. Sluit het programma", c="c")

    # Ik gebruik hier de functie table.clear() van pretty-tables zodat ik de tabel kan hergebruiken
    table.clear()

    try:
        keuze = int(input("\nMaak een keuze (1–5): "))
        print()

        if keuze == 1:
            show_astroids()
        elif keuze == 2:
            tabel_met_landen()
        elif keuze == 3:
            impact_simulatie()
        elif keuze == 4:
            choice_of_theme()
        elif keuze == 5:
            cprint("Bedankt voor het gebruiken van ASTRO-impact! Tot de volgende keer.", c="g")
            break
        else:
            cprint("Ongeldige keuze. Kies een getal tussen 1 en 5.", c="rB")

    except ValueError:

        toon_value_error()

