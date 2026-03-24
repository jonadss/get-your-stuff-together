# Open-Source Finanzmanager

## Projektziel
Eine kostenlose, quelloffene Alternative zu Finanzguru schaffen, die lokal auf dem Rechner läuft.

## Kernfunktionen
* Automatischer Import von Buchungen
* Übersichtliche Anzeige
* Kategorisierung
* Wiederkehrende Buchungen

## Umsetzung

### Import

Da Bank API teuer brauch ich ein Workaround Beispielweise 
* manuele Expotieren der CSV über die Webseite
* Bot der manules Exportieren der CSV über die Webseite
    * bei anderungen an der Webseite funktioniert es moglicherweise nicht mehr 
* ...

#### Anspruche an den Import
* Betrag in eine einheitrlichen Datentyp umzuwandeln
* Ignurieren von schon bereits vorhanden Buchungen
* Problemlose Margin von altern Buchungen


Für den Protyp habe ich mich für manuele Expotieren der CSV entscheiden.
Dafür hab ich für Python entschieden und hab ein script geschrieben der die CSV in json umwandelt.
\
Siehe  *import_csv-json/conv_csv-jason.py* .
\
\
Diese Methode hab ich schnell wieder verworfen und bin zu SQLITE gewechselt. 
\
Siehe Datenbank-Struktur *doku-draw/doku_Datenbanken.xlsx* .
\
##### Betrag in eine einheitrlichen Datentyp umzuwandeln

```
    if pd.isna(wert) or str(wert).strip() == "":
        return 0.0
    bereinigt = re.sub(r"\.", "", str(wert).strip())
    bereinigt = bereinigt.replace(",", ".")
    try:
        return float(bereinigt)
    except ValueError:
        return 0.0
```