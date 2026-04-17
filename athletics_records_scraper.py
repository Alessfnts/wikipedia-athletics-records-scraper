"""
Contexte :
Ce script récupère les tableaux de records du monde d'athlétisme depuis Wikipédia
et les exporte en fichiers CSV (hommes et femmes).

Objectif :
- Parser les tableaux HTML de la page
- Nettoyer les données
- Trier les épreuves
- Exporter en CSV exploitable
"""

import urllib.request
from html.parser import HTMLParser
import csv
import ssl

# URL cible
URL = "https://fr.wikipedia.org/wiki/Records_du_monde_d%27athl%C3%A9tisme"

# --- Récupération du HTML ---
headers = {"User-Agent": "Mozilla/5.0"}

try:
    req = urllib.request.Request(URL, headers=headers)
    context = ssl._create_unverified_context()
    response = urllib.request.urlopen(req, context=context)
    html = response.read().decode("utf-8")
except urllib.error.URLError as e:
    print(f"Erreur lors de l'accès à l'URL : {e.reason}")
    exit()


# --- Parseur HTML pour extraire les tableaux Wikipédia ---
class WikiTableParser(HTMLParser):
    """
    Extrait les tableaux HTML ayant la classe 'wikitable'
    et les convertit en listes Python.
    """

    def __init__(self):
        super().__init__()
        self.in_table = False
        self.in_row = False
        self.in_cell = False

        self.tables = []
        self.current_table = []
        self.current_row = []
        self.current_cell = ""

    def handle_starttag(self, tag, attrs):
        if tag == "table":
            for attr in attrs:
                if attr[0] == "class" and "wikitable" in attr[1]:
                    self.in_table = True
                    self.current_table = []

        if self.in_table and tag == "tr":
            self.in_row = True
            self.current_row = []

        if self.in_row and tag in ("td", "th"):
            self.in_cell = True
            self.current_cell = ""

    def handle_endtag(self, tag):
        if self.in_cell and tag in ("td", "th"):
            self.in_cell = False
            self.current_row.append(self.current_cell.strip().replace("\n", " "))

        if self.in_row and tag == "tr":
            self.in_row = False
            if self.current_row:
                self.current_table.append(self.current_row)

        if self.in_table and tag == "table":
            self.in_table = False
            if self.current_table:
                self.tables.append(self.current_table)

    def handle_data(self, data):
        if self.in_cell:
            self.current_cell += data


# --- Exécution du parsing ---
parser = WikiTableParser()
parser.feed(html)


# --- Fonction de traitement des tableaux ---
def process_table(table):
    """
    Nettoie et trie un tableau :
    - supprime les lignes incomplètes
    - trie par nom d'épreuve
    """
    headers = table[0]
    data = table[1:]

    filtered_data = [row for row in data if len(row) >= 5]
    sorted_data = sorted(filtered_data, key=lambda x: x[0])

    return [headers] + sorted_data


# --- Export CSV ---
output_files = ["records_men.csv", "records_women.csv"]

# Indices des tableaux sur Wikipédia (peuvent varier si la page change)
table_indices = [1, 2]

for i, filename in enumerate(output_files):
    if i < len(table_indices) and table_indices[i] < len(parser.tables):

        final_table = process_table(parser.tables[table_indices[i]])

        try:
            with open(filename, "w", newline="", encoding="utf-8-sig") as f:
                writer = csv.writer(f, delimiter=";")
                writer.writerows(final_table)

            print(f"Fichier '{filename}' créé ({len(final_table)} lignes).")

        except Exception as e:
            print(f"Erreur lors de l'écriture de '{filename}' : {e}")


# --- Aperçu rapide ---
print("\n--- Aperçu des données ---")

for i, filename in enumerate(output_files):
    if i < len(table_indices) and table_indices[i] < len(parser.tables):

        final_table = process_table(parser.tables[table_indices[i]])

        print(f"\nAperçu de '{filename}' :")
        for row in final_table[:5]:
            print(row)
