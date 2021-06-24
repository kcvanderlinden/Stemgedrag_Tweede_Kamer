# Tweede Kamer moties indexeren
## Scraping votes on motions in the Dutch Parliament
Because this code is specifically written on scraping motions in the Dutch Parliament, I will continue my story in DUtch, but if you're intreseted in my work, just contact me. 

Met de code van dit project wordt de gebruiker in staat gesteld om (alle) moties uit de Tweede Kamer te indexeren in 4 tabellen: 
1. eentje met de informatie over de motie zelf ```motie_table.csv```, 
2. eentje over de informatie van de indieners van de motie ```indieners_table.csv```,
3. eentje met de informatie over de stemuitslag ```vote_table.csv``` en
4. eentje met de verwijzingen naar het debat e.d. waar de motie is ingediend ```actviteiten_table.csv```.

Hierdoor wordt de informatie uit de Tweede Kamer met betrekking tot de moties toegankelijk gemaakt voor onderzoek. De code die je hier vindt is in staat om alle informatie van de individuele motie webpagina's te indexeren inclusief de motietekst zelf die in een PDF gevonden wordt op de webpagina van elke motie. Hierdoor kan er onderzoek gedaan worden naar stemgedrag van individuele leden van de Tweede Kamer of gehele partijen. Dit kan op basis van de titels van de moties, maar dus ook op basis van de inhoud van de moties. Een waardevolle toevoeging voor dit project zou zijn om automatisch thema's aan de moties te kunnen voegen op basis van de motie tekst.

Dit project is geschreven in Python, omdat het veel mogelijkheden biedt aan de programmeur. Python is van extra waarde in mijn optiek, omdat veel bestuurskundige, politicologen en andere studenten of leraren van sociale studies weinig ervaring hebben met programmeertalen. Python is beginnersvriendelijk en de output van dit script makkelijk te gebruiken in welbekende statistiekprogramma's. Daarnaast leent de output van dit script zich ook om geïmporteerd te worden in een database omgeving zoals met MySQL. Hierdoor kunnen de verschillende tabellen die als output volgen uit dit script gekoppeld worden en kunnen er meer geavanceerde zoekopdrachten uitgevoerd worden over de datasets.

Voor dit python script zijn de modulen nodig die gevonden worden in ```requirements.txt```. Deze kunnen geïnstalleerd worden met het volgende commando uit te voeren in de project map met een terminal.
```bash
$ pip install -r requirements.txt
```

Dit vereist wel dat [Python](https://www.python.org/downloads/) zelf is geïnstalleerd op het systeem. Vergeet bij de installatie niet het vakje aan te vinken om Python toe te voegen aan PATH.

om het script uit te voeren, moet een terminal geopend worden in de project map en de volgende commando's uitgevoerd worden:
```bash
$ python
>>> from main import run

# als je meerdere overzicht pagina's wilt indexeren, vervang dan 'a' met het pagina nummer van de eerste overzicht pagina en 'b' met de laatste overzicht pagina die je wilt indexeren. het is dus 'a' tot en met 'b'.
>>> run(a, b)

# als je een enkele overzicht pagina wilt indexeren, geef dan alleen de paginanummer van die enkele overzicht pagina.
>>> run(a)
```

De output als de drie .csv bestanden worden opgeslagen in de projectmap.

## Variabelen
De volgende variabelen worden geïndexeerd met dit script.
In ```motie_table.csv```:
1. motie_id (uniek voor elke motie en gegenereerd door de website van de Tweede Kamer zelf)
2. Subject (onderwerp/titel van de motie)
3. Date (datum van de motie)
4. Text (tekst van de motie)
5. Title (een nietszeggende titel van de motie webpagina)
6. State_Document (document status)

In ```indieners_table.csv```:
1. motie_id (uniek voor elke motie en gegenereerd door de website van de Tweede Kamer zelf)
2. name_submitter (naam motie indiener)
3. submitter_type (indiener, ondertekenaar, mede-indiener, etc.)
4. party_submitter (politieke partij van indiener)
5. personal_page (url naar de persoonlijke pagina van de indiener)

In ```vote_table.csv```:
1. motie_id (uniek voor elke motie en gegenereerd door de website van de Tweede Kamer zelf)
2. party_name (Naam van politieke partij)
3. vote_count (hoeveelheid van stemmen)
4. vote (voor, tegen of afwezig)

In ```actviteiten_table.csv```:
1. motie_id (uniek voor elke motie en gegenereerd door de website van de Tweede Kamer zelf)
2. activities (verwijzing d.m.v. url naar het debat of stemming waar de motie deel van is)
