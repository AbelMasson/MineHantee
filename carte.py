# -*- coding: utf-8 -*-
"""
Created on Wed Nov 13 05:18:23 2019

@author: anael
"""



#[Nord,Sud,Est,Ouest] 
connectivité={'coin':[[0,1,1,0],[1,0,1,0],[1,0,0,1],[0,1,0,1]],
              'couloir':[[1,1,0,0],[0,0,1,1]],
              'carrefour':[[1,1,1,0],[1,0,1,1],[1,1,0,1],[0,1,1,1]]}

class carte():
    def __init__(self,type_carte,dict_elements,\
                 position_graph,position_detail,
                 orientation):
        """type_carte : str
        dict_elements : dict {fantome,pepite,joueur)
        position_graph : ref noeud networkX
        position_detail : (int,int)
        orientation : int
        connectivité : [[],[],[],[]]"""
        self.type=type_carte
        self.elements=dict_elements
        self.position_G=position_graph
        self.position_D=position_detail
        self.orientation=orientation
        self.connectivité=connectivité[type_carte]
    
    def pivoter(self,sens):
        if sens=='horaire' :
            if self.orientation < len(self.connectivité):
                self.orientation=self.connectivité[self.orientation+1]
            else :
                self.orientation=self.connectivité[0] #retour au premier
        
        else: #anti-horaire
            if self.orientation > 0:
                self.orientation=self.connectivité[self.orientation-1]
            else :
                self.orientation=self.connectivité[-1] #retour au dernier

