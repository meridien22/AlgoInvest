import csv
import os
import time
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
    with open(path, mode='r', encoding='utf-8') as csv_file:
        reader = csv.DictReader(csv_file)
        dict_ = list(reader)
    return dict_

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

def calculate_max_profit(limit, list_, action_selection = []):
    """Calcul le profit maximum 

    Args:
        limit (_type_): _description_
        list_ (_type_): _description_
        action_selection (list, optional): _description_. Defaults to [].

    Returns:
        _type_: _description_
    """
    if list_:
        # cas ou on n'achète pas l'action, on appelle récusrsivement la fonction
        # en enlevant un élément de la liste et sans modifier la limite
        benefit1, action_selection_1 = calculate_max_profit(limit, list_[1:], action_selection)
        action = list_[0]
        if action[1] <= limit:
            # cas ou on peut on et achète l'action, on appelle récusrsivement la fonction
            # en enlevant un élément de la liste, en modifier la limite et en ajoutant l'action
            # a la liste des actions selectionnées
            benefit2, action_selection_2 = calculate_max_profit(limit - action[1], list_[1:], action_selection + [action])
            if benefit1 < benefit2:
                return benefit2, action_selection_2

        return benefit1, action_selection_1
    else:
        return sum([action[2] for action in action_selection]), action_selection
    
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
    table.add_row("Nombre de combinaison analysée", str(2**len(data)))
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
