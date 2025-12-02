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
        path (string): path to the CSV file

    Returns:
        dict: dictionary containing stocks, their costs and their profits,
        actions with a cost of 0 or less are removed.
    """
    data_frame = pandas.read_csv(path)
    name_column1 = data_frame.columns[0]
    name_column2 = data_frame.columns[1]
    name_column3 = data_frame.columns[2]
    data_frame = data_frame.rename(columns={
        name_column1: 'name',
        name_column2: 'cost',
        name_column3: 'benefit'
    })
    # On filtre le dataframe pour enlever les actions avec un coût <= à 0
    data_frame = data_frame[(data_frame['cost'] > 0)]
    # On convertit les Euros en centimes
    data_frame['cost'] = data_frame['cost'] * 100
    return data_frame.to_dict(orient='records')

def data_preparation(dict_):
    """Prepare the dataset for analysis.
       Convert profits to integers and absolute values.

    Args:
        dict_ (dict): dictionary containing stocks, their costs and their profits
    """
    for action in dict_:
        action["cost"] = int(action["cost"])
        if isinstance(action["benefit"], str):
            benefit = int(action["benefit"][:-1])
        else:
            benefit = action["benefit"]
        action["benefit"] = action["cost"] * (benefit / 100)

def data_transformation(dict_):
    """Transform the dictionary of actions into a list of tuples composed of:
       the action name, its cost, and its profit

    Args:
        dict_ (_type_): dictionary containing stocks, their costs and their profits

    Returns:
        liste: [(action name, cost, benefit)]
    """
    list_tuple = []
    for action in dict_:
        action_name = action["name"]
        cost = action["cost"]
        benefit = action["benefit"]
        list_tuple.append((action_name, cost, benefit))

    return list_tuple

def calculate_max_profit(limit, list_):
    """Determine the combination of actions that will generate the highest profit.

    Args:
        limit (intger): Spending limit
        list_ (list): List containing the actions

    Returns:
        tuple : maximum profit, list of stocks to buy
    """
    # On crée un tableau en 2 dimensions rempli de 0 avec (limit + 1) colonnes et (nombre d'action + 1) lignes
    # On ajoute 1 au nombre d'action pour gérer le cas ou l'on souhaite calculer le bénéfice maximum sans aucune action
    # On ajoute 1 a la limit pour gérer le cas ou cette limite serait égale à zéro
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
        if lim - action[1] >= 0:
            if matrice[act][lim] == matrice[act-1][lim-action[1]] + action[2]:
                action_selection.append(action)
                lim -= action[1]
        act -= 1

    return matrice[-1][-1], action_selection
    
def display_result(result, data, time_execute):
    """Displays the analysis results in a table format

    Args:
        result (_type_): Analysis results
        data (_type_): Data analyzed
        time_execute (_type_): Execution time
    """
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

    table = Table(title = 'Paramètre de l\'analyse "Optimized"', show_lines=True)
    table.add_column("Paramètre", justify = "left", style = "green", width=40)
    table.add_column("Valeur", justify = "right", style = "green", width=40)

    table.add_row("Bénéfice maximum", f"{str(result[0]/100)} €")
    table.add_row("Capital dépensé", f"{str(spent/100)} €")
    table.add_row("Nombre d'action à acheter", str(len(result[1])))
    table.add_row("Nombre d'action analysée", str(len(data)))
    table.add_row("Nombre de combinaison analysée", str(50000*len(data)))
    table.add_row("Temps de calcul", f"{str(time_execute)} seconde(s)")
    console.print(table)

    table = Table(title = 'Détail des actions', show_lines=True)
    table.add_column("Action", justify = "left", style = "blue", width=26)
    table.add_column("Coût", justify = "right", style = "blue", width=26)
    table.add_column("Bénéfice", justify = "right", style = "blue", width=25)
    for action in action_list:
        table.add_row(action[0], f"{str(action[1]/100)} €", f"{str(round(action[2]/100,2))} €")
    console.print(table)


# action_dict = data_loading(r"atelier\dataset0.csv")
# action_dict = data_loading(r"atelier\dataset1.csv")
action_dict = data_loading(r"atelier\dataset2.csv")
data_preparation(action_dict)
data = data_transformation(action_dict)
time_start = time.time()
result = calculate_max_profit(50000, data)
time_end = time.time()
time_execute = round((time_end - time_start),3)
display_result(result, data, time_execute)
