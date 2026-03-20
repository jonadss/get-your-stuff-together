import csv
import json




#######################
#########to-do#########
#- anppassen was wirklich in die json rein muss
#- automatische anpassung der namen gebeung 
#- loschen der csv
#- anlegen der datenbase
#######################






def konvertiere_csv_zu_json(csv_datei_pfad, json_datei_pfad):
    buchungen = []

    # 'utf-8-sig' hilft gegen versteckte Zeichen am Anfang (BOM), 
    # die oft in Excel-Exports vorkommen.
    with open(csv_datei_pfad, mode='r', encoding='utf-8-sig') as csv_file:
        # Deutsche Banken nutzen meist das Semikolon ';' als Trenner, 
        # da das Komma in den Beträgen vorkommt.
        csv_reader = csv.DictReader(csv_file, delimiter=';')

        for zeile in csv_reader:
            # Wir säubern den Betrag: Aus "1.250,50" machen wir "1250.50" (float-kompatibel)
            if "Betrag" in zeile and zeile["Betrag"]:
                roher_betrag = zeile["Betrag"].replace('.', '').replace(',', '.')
                try:
                    zeile["Betrag_Numerisch"] = float(roher_betrag)
                except ValueError:
                    zeile["Betrag_Numerisch"] = 0.0

            buchungen.append(zeile)

    # Als JSON speichern
    with open(json_datei_pfad, mode='w', encoding='utf-8') as json_file:
        json.dump(buchungen, json_file, indent=4, ensure_ascii=False)

    print(f"Erfolg! {len(buchungen)} Zeilen wurden in '{json_datei_pfad}' umgewandelt.")







# Beispielaufruf (Pfade anpassen!)
konvertiere_csv_zu_json('csv/kontoauszug.csv', 'json/meine_bank_daten.json')