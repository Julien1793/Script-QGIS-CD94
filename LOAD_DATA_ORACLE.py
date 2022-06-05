# -*- coding: cp1252 -*-
#Date : 18/02/2021
#Auteur : Julien Samaniego
#**************************DESCRIPTION DU SCRIPT******************************
#*  Ce script appelle une donnée avec depuis oracle
#*****************************************************************************

# -------- improt des modules
import sys,os
from qgis.core import *

# Fonction pour appeler une donnée depuis Oracle (CD94)
def LoadOracle (NAME_DATA =name,WHERE_CLAUSE=request,LOAD_DATA=LoadProject):
    # Connexion Oracle
    uri= QgsDataSourceUri()
    uri.setConnection("",","","") #mettre les paramètres de connexion (serveur, port,...)
    "NEXT_DIFF","sigprod")
    # Setdatasource(schéma,table,géométrie,sql,clé)
    name_data = name
    req = request
    uri.setDataSource("",name_data,"GEOMETRY",req,"GID")
    # Récupération de la donnéé en variable
    layer = QgsVectorLayer(uri.uri(),name,"oracle")
    # Test si la donnée est correctement récupérée
    if  not layer.isValid():
        print ("{} : problème de chargement de la donnée !".format(name_data))
    else :
        print ("couche {} chargée".format(name_data))
    # Réécriture CRS en 2154
    mycrs = QgsCoordinateReferenceSystem(2154)
    layer.setCrs(mycrs,True)
    # Chargement de la donnée dans le projet QGIS
    if LoadProject == true:
        print ('La couche {} est ajouée dans le projet QGIS'.format(name))
        load= QgsProject.instance().addMapLayer(layer)
    else :
        print ("La couche oracle {} est gardée en mémoire".format(name))
    return layer # retourne la variable avec la fonction QgsVectorLayer pour lire et écrire dans la donnée

# Variable de la donnée Oracle (lancement de la fonction)
layer_route = LoadOracle ("V_BD_TOPO_ROUTE_94","\"NUMERO_ROUTE\" = 'D5'",False) # QgsVectorLayer de la donnée Oracle

print ("terminé")
