# -*- coding: utf-8 -*-
"""
Created on Sun Nov 24 23:53:33 2019

@author: HP
"""

import pandas
import numpy as np
import pygame
from pygame.locals import *
import random
import os
import networkx as nx
import matplotlib.pyplot as plt

class Carte(object):
    
    def __init__(self,type_,elements,position_graph,position_detail,orientation) :
        self.type = type_
        self.elements = elements
        self.position_graph = position_graph
        self.position_detail = position_detail
        self.orientation = orientation
        
        dico_connectivite = {'couloir' : [[0,0,1,1],[1,1,0,0],[0,0,1,1],[1,1,0,0]],
                             'coin' : [[0,1,1,0],[0,1,0,1],[1,0,0,1],[1,0,1,0]],
                             'carrefour' : [[0,1,1,1],[1,1,0,1],[1,0,1,1],[1,1,1,0]]}
        
        self.connectivite = dico_connectivite[self.type]
        
    def pivoter(self,n) :
        '''
        L'action de pivoter correspond à tourner la carte de 45° dans le sens des
        aiguilles d'une montre.
        
        n : nombre de pivot à appliquer
        '''
        
        orientation_new = (self.orientation + n)%4
        self.orientation = orientation_new

###############################################################################
# Classe Plateau
###############################################################################
cartes_disponibles = {'coin' : 20, 'couloir' : 25, 'carrefour' : 16}

class Plateau(object) :
    '''
    Le fichier de configuration en exemple :
    fichier Config :
        dim_plateau,7
        nb_fantomes, 8
        nb_pepites, 10
        
        #types dict et list non pris en charge dans le format csv
        proportion cartes types [0.33,0.33,0.34] #pas les bonnes proportions
        cartes_disponibles, {'coin' : 20, 'couloir' : 25, 'carrefour' : 16}
                            #pas les bons chiffres
    '''
    
    def __init__(self, chemin_fichier_config) :
        
        self.config = pandas.read_csv(chemin_fichier_config, sep=';', 
                                      header = None, index_col = 0).T
        
        
        self.taille = int(self.config.dim_plateau)
        self.labyrinthe_detail = np.array([[object]*self.taille]*self.taille)
        
        graph = nx.Graph()
        graph.add_nodes_from(list(range(self.taille**2)))
        node_pos = [(i,j) for i in range(self.taille) for j in range(self.taille)]
        
        for k in range(self.taille**2) : 
            graph.node[k]['pos'] = node_pos[k]
        
        self.node_pos = node_pos
        self.graph = graph
        
        print(self.config)
        
    
    def placer_carte(self, i, j, cartes_disponibles=None, carte_a_placer=None) :
        '''
        placer une carte de la classe Carte à l'emplacement i,j dans la 
        matrice self.labyrithe_détail
            
        i, j : entiers compris entre 0 et dim_plateau - 1.
        carte_a_placer : FACULTATIF carte de la classe Carte, à placer 
        sur la case (i,j) du plateau
        cartes_disponibles : FACULTATIF dict, dictionnaire donnant le 
        nombre de cartes disponibles par type de cartes
        '''
        
        if carte_a_placer == None :
        
            choix_type_carte = [key for key in cartes_disponibles.keys() 
                                if cartes_disponibles[key] > 0]
            
            type_ = np.random.choice(choix_type_carte)
            orientation = np.random.randint(0,3)
            position_detail = (i,j)
            
            carte = Carte(type_, {}, [], position_detail, orientation) 
            
            cartes_disponibles[type_] -= 1
        
        else :
            
            carte = carte_a_placer
        
        #Connexion Nord
        if carte.connectivite[carte.orientation][0] == 1 and i != 0:
            if self.labyrinthe_detail[i-1][j].connectivite[self.labyrinthe_detail[i-1][j].orientation][1] == 1 :
                print('Youhou !')
                self.graph.add_edge(self.node_pos.index((i-1,j)),self.node_pos.index((i,j)))
        
        #Connexion Ouest
        if carte.connectivite[carte.orientation][3] == 1 and j != 0:
            if self.labyrinthe_detail[i][j-1].connectivite[self.labyrinthe_detail[i][j-1].orientation][2] == 1 :
                self.graph.add_edge(self.node_pos.index((i,j)),self.node_pos.index((i,j-1)))
        
        '''
        #Connexion Est
        if carte.connectivite[carte.orientation][2] == 1 and j != self.taille-1:
            if self.labyrinthe_detail[i][j+1].connectivite[self.labyrinthe_detail[i][j+1].orientation][3] == 1 :
                self.graph.add_edge(self.node_pos.index((i,j)),self.node_pos.index((i,j+1)))
        
        #Connexion Sud
        if carte.connectivite[carte.orientation][1] == 1 and i != self.taille-1:
            if self.labyrinthe_detail[i+1][j].connectivite[self.labyrinthe_detail[i+1][j].orientation][0] == 1 :
                self.graph.add_edge(self.node_pos.index((i,j)),self.node_pos.index((i+1,j)))
        ''' 
        
        self.labyrinthe_detail[i][j] = carte
            
        
    def placer_fantomes(self, i, j, num_fantome) :
        '''
        place le fantome identifié par num_fantome sur la carte située en 
        i, j sur le plateau
        
        num_fantome : entier identifiant du fantome
        '''
        
        self.labyrinthe_detail[i][j].elements['fantome'] = num_fantome
    
    def placer_pepite(self, i, j) :
        '''
        place une pepite sur la carte située en i, j sur le plateau
        '''
        
        self.labyrinthe_detail[i][j].elements['pepite'] = True
    
    def placer_joueur(self, i, j, num_joueur) :
        '''
        place le fantome identifié par num_joueur sur la carte située en 
        i, j sur le plateau
        
        num_fantome : entier identifiant du fantome
        '''
        
        self.labyrinthe_detail[i][j].elements['joueur'] = num_joueur
    

    def generer_plateau(self) :
        '''
        génère un plateau aléatoirement selon les contraintes imposées 
        dans le fichier de configuration
        '''
        
        #Generation des cartes sur le plateau
        taille = self.taille
        
        Nb_CF = (taille//2 + 1)**2
        Pair = (Nb_CF%2 == 0)
        
        dico_connectivite = {'couloir' : [[0,0,1,1],[1,1,0,0],[0,0,1,1],[1,1,0,0]],
                             'coin' : [[0,1,1,0],[0,1,0,1],[1,0,0,1],[1,0,1,0]],
                             'carrefour' : [[0,1,1,1],[1,1,0,1],[1,0,1,1],[1,1,1,0]]}
        
        #Construction des listes des cartes fixes sur le plateau, selon
        #que le nombre de cartes fixes est pair ou impair
        liste_CF_PP = [(i,j) for i in range(0,taille, 2) for j in range(0, taille, 2)]
        liste_CF_PI = [(i,j) for i in range(1,taille, 2) for j in range(1, taille, 2)]
    
        #On stocke la liste des index des cartes fixes sur le plateau
        if Pair :
            self.Index_Cartes_fixes = liste_CF_PP
        else :
            self.Index_Cartes_fixes = liste_CF_PI

        
        for i in range(taille) :
            for j in range(taille) :
                
                if (Pair and (i,j) in liste_CF_PP) or (not(Pair) and (i,j) in liste_CF_PI) :
                    print((i,j))
                    
                    Nord_ouvert = (i > 0 and i <= taille-1)  
                    Sud_ouvert =  (i >= 0 and i < taille-1)
                    Est_ouvert = (j < taille//2)
                    Ouest_ouvert = (j > taille//2)
                    
                    orientation_CF = [int(Nord_ouvert), int(Sud_ouvert),
                                         int(Est_ouvert), int(Ouest_ouvert)]
                    
                    if sum(orientation_CF) > 2 :
                        type_CF = 'carrefour'
                    else :
                        type_CF = 'coin'
                    
                        carte_a_placer = Carte(type_CF, {}, [], 
                                               (i,j), dico_connectivite[type_CF].index(orientation_CF))
        
                    self.placer_carte(i,j,carte_a_placer=carte_a_placer)
                
                else : 
                    print('NF : {}'.format((i,j)))
                    
                    self.placer_carte(i,j,cartes_disponibles)
        
        #Generation de la carte en dehors du plateau 
        choix_type_carte = [key for key in cartes_disponibles.keys() 
                                if cartes_disponibles[key] > 0]
            
        type_ = np.random.choice(choix_type_carte)
        orientation = np.random.randint(0,3)
            
        carte_en_dehors = Carte(type_, {}, [], None, orientation) 
        self.carte_en_dehors = carte_en_dehors
        
        #Placer les fantomes
        Nb_F_restant = int(self.config.nb_fantomes)
        
        while Nb_F_restant > 0 :
            i = np.random.randint(0,taille-1) ; j = np.random.randint(0,taille-1)
            
            if 'fantome' not in self.labyrinthe_detail[i][j].elements.keys() :
                self.placer_fantomes(i,j,Nb_F_restant)
            
            Nb_F_restant -= 1
    
        #Placer les pepites
        Nb_P_restantes = int(self.config.nb_pepites)
        
        while Nb_P_restantes > 0 :
            i = np.random.randint(0,taille-1) ; j = np.random.randint(0,taille-1)
            
            if 'pepite' not in self.labyrinthe_detail[i][j].elements.keys() :
                self.placer_pepite(i,j)
            
            Nb_P_restantes -= 1
            
        #Placer Joueur
        a = (taille//2)-1
        b = (taille//2)+1
            
                
        possibles = [(a,a),(a,b),(b,a),(b,b)]
        Nb_joueur_a_placer = int(self.config.nb_joueurs)
            
        while Nb_joueur_a_placer > 0 :
                
            position = possibles[Nb_joueur_a_placer-1]
            self.placer_joueur(position[0], position[1], Nb_joueur_a_placer)
                
            Nb_joueur_a_placer -= 1
    
   
    def coulisser_detail (self,coord_x, coord_y):
        """
        Change les positions des objets cartes dans la matrice “self.labyrinthe_detail”
        :param coord_x: abscisse du lieu où l'on souhaite faire coulisser la carte
        :param coord_y: ordonnée du lieu où l'on souhaite faire coulisser la carte
        :return:
        """
        ## on modifie la ligne
        # en coulissant de gauche à droite
        carte_sortante = self.carte_en_dehors
        if coord_x == -1 :
            carte_sortante = self.labyrinthe_detail[self.taille-1,coord_y]
            for i in range(self.taille-1, 0, -1) :
                self.labyrinthe_detail[i,coord_y] = self.labyrinthe_detail[i-1,coord_y]
            self.labyrinthe_detail[0,coord_y] = self.carte_en_dehors
        # en coulissant de droite à gauche    
        if coord_x == self.taille :
            carte_sortante = self.labyrinthe_detail[0,coord_y]
            for i in range(self.taille) :
                self.labyrinthe_detail[i,coord_y] = self.labyrinthe_detail[i+1,coord_y]
            self.labyrinthe_detail[self.taille-1,coord_y] = self.carte_en_dehors
                
        ## on modifie la colonne
        # en coulissant de haut en bas
        if coord_y == -1 :
            carte_sortante = self.labyrinthe_detail[coord_x, self.taille-1]
            for i in range(self.taille-1, 0, -1) :
                self.labyrinthe_detail[coord_x,i] = self.labyrinthe_detail[coord_x, i-1]
            self.labyrinthe_detail[coord_x, 0] = self.carte_en_dehors
        # en coulissant du bas vers le haut
        if coord_y == self.taille :
            carte_sortante = self.labyrinthe_detail[coord_x,0]
            for i in range(self.taille) :
                self.labyrinthe_detail[coord_x, i] = self.labyrinthe_detail[coord_x,i+1]
            self.labyrinthe_detail[coord_x,self.taille-1] = self.carte_en_dehors
        
        #la nouvelle carte à coulisser sera la carte qui est sortie
        self.carte_en_dehors = carte_sortante 
        
        #On regénère le graphe des connextivités
        new_graph = nx.Graph()
        new_graph.add_nodes_from(list(range(self.taille**2)))
        node_pos = [(i,j) for i in range(self.taille) for j in range(self.taille)]
        
        for k in range(self.taille**2) : 
            new_graph.node[k]['pos'] = node_pos[k]
        
        for i in range(self.taille) :
            for j in range(self.taille) :
                
                #Connexion Nord
                if self.labyrinthe_detail[i][j].connectivite[self.labyrinthe_detail[i][j].orientation][0] == 1 and i != 0:
                    if self.labyrinthe_detail[i-1][j].connectivite[self.labyrinthe_detail[i-1][j].orientation][1] == 1 :
                        print('Youhou !')
                        new_graph.add_edge(self.node_pos.index((i-1,j)),self.node_pos.index((i,j)))
                
                #Connexion Ouest
                if self.labyrinthe_detail[i][j].connectivite[self.labyrinthe_detail[i][j].orientation][3] == 1 and j != 0:
                    if self.labyrinthe_detail[i][j-1].connectivite[self.labyrinthe_detail[i][j-1].orientation][2] == 1 :
                        new_graph.add_edge(self.node_pos.index((i,j)),self.node_pos.index((i,j-1)))
        
        self.node_pos = node_pos
        self.graph = new_graph
    
    def check_deplacement (self):
        """
        Vérifie que le déplacement demandé par un joueur
        est valide. Si possible, effectue la mise à jour de la position du
        joueur sinon, renvoie un message d’erreur visible par le joueur.
        """
        pass
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        