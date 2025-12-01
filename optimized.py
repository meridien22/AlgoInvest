import csv
import os
import time
import pandas
from rich.console import Console
from rich.panel import Panel
from rich.align import Align
from rich.table import Table

os.system("clear")

LIMIT_MONEY = 500

def data_loading(path):
    """_summary_

    Args:
        path (string): chemin d'accès vers le fichier CSV

    Returns:
        dict: dictionnaire contenant les actions, leurs coûts et leurs bénéfices
    """
    data_frame = pandas.read_csv(path)
    return data_frame.to_dict(orient='records')


def data_preparation(dict_):
    """Prépare le jeu de donnée pour l'analyse.
    Convertir les nombres représentés en chaine en entier.
    Ajoute le bénéfice en Euros de chaque action.

    Args:
        dict_ (dict): dictionnaire contenant les actions, leurs coûts et leurs bénéfices
    """
    for action in dict_:
        action["cost"] = int(action["cost"])
        action["benefit"] = int(action["benefit"][:-1])
        action["benefit_value"] = action["cost"] * (action["benefit"] / 100)

def data_transformation(dict_):
    """Transforme le dictionnaire des actions en liste de tuple composé
    du nom de l'action, de son coût et de son bénéfice

    Args:
        dict_ (_type_): dictionnaire contenant les actions, leurs coûts et leurs bénéfices

    Returns:
        liste: [(Nom de l'action, coût, bénéfice)]
    """
    list_tuple = []
    for action in dict_:
        action_name = action["action"]
        cost = action["cost"]
        benefit = action["benefit_value"]
        list_tuple.append((action_name, cost, benefit))

    return list_tuple

def calculate_max_profit(limit, list_):
    """Détermine la combinsaison d'action qui générera le profit le plus élevé.

    Args:
        limit (intger): limite des dépenses
        list_ (list): Liste contenant les actions

    Returns:
        tuple : le profit maximum, la liste des actions à acheter
    """
    # On crée un tableau en 2 dimensions rempli de 0 avec (limit + 1) colonnes et (nombre d'action + 1) lignes
    # On ajoute 1 au nombre d'action pour gérer le cas ou l'on souhaite calculer le bénéfice maximum sans aucune action
    # On ajoute 1 a la limit pour gérer le cas ou cette limite serait égal à zéro
    matrice = [[0 for x in range(limit + 1)] for x in range(len(list_) + 1)]

    for act in range(1, len(list_) + 1):
        for lim in range(1, limit + 1):
            # Le coût de l'action est <= à la limite, on peut acheter l'action
            if list_[act-1][1] <= lim:
                # On prend la valeur maximale entre le bénéfice calculé précédement pour la limite 
                # et le benefice de l'action + le bénéfice calculé précédement pour la limite - le coût de cette action
                matrice[act][lim] = max(list_[act-1][2] + matrice[act-1][lim-list_[act-1][1]], matrice[act-1][lim])
            # On ne peut pas acheter l'action, la matrice prend la même valeur que l'action précédente pour la même limite
            else:
                matrice[act][lim] = matrice[act-1][lim]

    # On retrouve maintenant les actions sélectionnées en parcourant la matrice de la fin vers le début
    lim = limit
    act = len(list_)
    action_selection = []
    while lim >= 0 and act >= 0:
        action = list_[act-1]
        if matrice[act][lim] == matrice[act-1][lim-action[1]] + action[2]:
            action_selection.append(action)
            lim -= action[1]
        act -= 1

    return matrice[-1][-1], action_selection
    
def display_result(result, data, time_execute):
    console = Console()
    titre = Align.center("AlgoInvest&Trade : actions gagnantes !")
    panel_centre = Panel(
        titre,
        width = 87, # Largeur du panneau pour la démonstration
        border_style="bold blue",
        style="bold green"
    )
    console.print(panel_centre)

    action_list = result[1]
    spent = 0
    for action in action_list:
        spent += action[1]

    table = Table(title = 'Paramètre de l\'analyse "BruteForce"', show_lines=True)
    table.add_column("Paramètre", justify = "left", style = "green", width=40)
    table.add_column("Valeur", justify = "right", style = "green", width=40)

    table.add_row("Bénéfice maximum", f"{str(result[0])} €")
    table.add_row("Capital dépensé", f"{str(spent)} €")
    table.add_row("Nombre d'action à acheter", str(len(result[1])))
    table.add_row("Nombre d'action analysée", str(len(data)))
    table.add_row("Nombre de combinaison analysée", str(500*len(data)))
    table.add_row("Temps de calcul", f"{str(time_execute)} seconde(s)")
    console.print(table)

    table = Table(title = 'Détail des actions', show_lines=True)
    table.add_column("Action", justify = "left", style = "blue", width=26)
    table.add_column("Coût", justify = "right", style = "blue", width=26)
    table.add_column("Bénéfice", justify = "right", style = "blue", width=25)
    for action in action_list:
        table.add_row(action[0], str(action[1]), f"{str(round(action[2],2))} %")
    console.print(table)


action_dict = data_loading(r"atelier\liste_action.csv")
data_preparation(action_dict)
data = data_transformation(action_dict)
time_start = time.time()
result = calculate_max_profit(500, data)
time_end = time.time()
time_execute = round((time_end - time_start),3)
display_result(result, data, time_execute)
