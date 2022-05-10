# -*- coding: cp1252 -*-
#Date : 18/02/2021
#Auteur : Julien Samaniego
#**************************DESCRIPTION DU SCRIPT******************************
#*  Ce script appelle une donnée avec depuis oracle
#*****************************************************************************

# -------- improt des modules
import sys,os
from qgis.core import *


def LoadOracle (name,request,LoadProject):
    # Connexion Oracle
    uri= QgsDataSourceUri()
    uri.setConnection("ssig-prod-ora","1521","SSIGPROD.cg94.loc",
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
    if LoadProject == 'yes':
        load= QgsProject.instance().addMapLayer(layer)
    else :
        pass
    return layer

LoadOracle ("V_BD_TOPO_ROUTE_94","\"NUMERO_ROUTE\" = 'D5'","yes")

print ("terminé")
