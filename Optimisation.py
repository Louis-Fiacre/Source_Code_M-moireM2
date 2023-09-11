import os
import random
import pandas as pd
import shutil
from pulp import LpMaximize, LpProblem, LpVariable

def select_files_by_optimization(source_folder, target_sum_per_genre, mode='caracteres'):
    # Création du dossier de destination s'il n'existe pas
    destination_folder = 'data/corpus_balanced_optimized/'
    if not os.path.exists(destination_folder):
        os.makedirs(destination_folder)

    # Liste des genres
    genres = set()
    
    # Dictionnaire pour stocker les caractéristiques par genre
    caracteristiques_par_genre = {}
    
    # Parcours de tous les fichiers dans le dossier source
    for nom_fichier in os.listdir(source_folder):
        if nom_fichier.endswith('.txt'):
            genre = nom_fichier.split('_')[0]
            genres.add(genre)
            
            # Lecture du contenu du fichier
            chemin_fichier = os.path.join(source_folder, nom_fichier)
            with open(chemin_fichier, 'r') as f:
                contenu = f.read()
                if mode == 'caracteres':
                    longueur = len(contenu)
                elif mode == 'mots':
                    longueur = len(contenu.split())
                else:
                    raise ValueError("Le mode doit être 'caracteres' ou 'mots'")
            
            if genre not in caracteristiques_par_genre:
                caracteristiques_par_genre[genre] = {'fichiers': [], 'somme': 0}
            
            caracteristiques_par_genre[genre]['fichiers'].append((chemin_fichier, longueur))
            caracteristiques_par_genre[genre]['somme'] += longueur
    
    # Initialisation du problème d'optimisation
    prob = LpProblem("Optimisation_Selection_Fichiers", LpMaximize)
    
    # Variables binaires pour décider quels fichiers inclure
    fichiers_selectionnes = LpVariable.dicts("Fichier", [(genre, idx) for genre in genres for idx in range(len(caracteristiques_par_genre[genre]['fichiers']))], 0, 1, LpVariable.isInteger)

    # Maximiser le nombre total de fichiers sélectionnés
    prob += sum(fichiers_selectionnes[(genre, idx)] for genre in genres for idx in range(len(caracteristiques_par_genre[genre]['fichiers'])))

    # Contrainte de somme par genre
    for genre in genres:
        prob += sum(fichiers_selectionnes[(genre, idx)] * caracteristiques_par_genre[genre]['fichiers'][idx][1] for idx in range(len(caracteristiques_par_genre[genre]['fichiers']))) <= target_sum_per_genre
    
    # Résolution du problème
    prob.solve()

    # Copie des fichiers sélectionnés
    for genre in genres:
        for idx, (_, _) in enumerate(caracteristiques_par_genre[genre]['fichiers']):
            if fichiers_selectionnes[(genre, idx)].value() > 0.5:
                shutil.copy(caracteristiques_par_genre[genre]['fichiers'][idx][0], os.path.join(destination_folder, os.path.basename(caracteristiques_par_genre[genre]['fichiers'][idx][0])))

# Paramètres
source_folder = 'data/2000romans19e20e/'
target_sum_per_genre = 2931562  # La somme totale de caractères/mots par genre à ne pas dépasser
mode = 'mots'  # Choisir 'caracteres' ou 'mots'


# Sélection des fichiers par optimisation
select_files_by_optimization(source_folder, target_sum_per_genre, mode)



