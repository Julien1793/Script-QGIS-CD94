# -*- coding: cp1252 -*-
# Date : j/m/a
# Auteur : Julien Samaniego
# Objet du script : Comparaison données bus GTFS IDFM et OSM

#                            DESCRIPTION DU SCRIPT
# *****************************************************************************
# *****************************************************************************
import sys, os

os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = r'C:\Program Files\QGIS 3.16\apps\Qt5\plugins'
os.environ['PATH'] += r';C:\Program Files\QGIS 3.16\apps\qgis-ltr\bin;~C:\Program Files\QGIS 3.16\apps\Qt5\bin'


from qgis.core import *
from qgis.gui import *
from PyQt5.QtCore import *
from qgis.utils import plugins

from qgis.analysis import QgsNativeAlgorithms


quickosm = os.environ['OSM']=r'C:\Users\samaniego\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins'
sys.path.append(quickosm)

#processingroot = '/usr/share/qgis/python/plugins/'
#sys.path.append(processingroot)
#from QuickOSM.quick_osm_processing.provider import Provider



# See https://gis.stackexchange.com/a/155852/4972 for details about the prefix
# Supply the path to the qgis install location
QgsApplication.setPrefixPath(r'C:\Program Files\QGIS 3.16\apps\qgis-ltr', True)
#  start QGIS processing application
os.environ['QGIS_PREFIX_PATH'] = r'C:\Program Files\QGIS 3.16\apps\qgis-ltr'
os.environ['GDAL_DATA'] = r'C:\Program Files\QGIS 3.16\share\gdal'
os.environ['PROJ_LIB'] = r'C:\Program Files\QGIS 3.16\share\proj'

# Append the path where processing plugin can be found
sys.path.append(r'C:\Program Files\QGIS 3.16\apps\qgis-ltr\python\plugins')

#                         Demarrage QGIS et import des modules processing
# *********************************************************************************
# Lancement du projet QGIS
print("démarrage QGIS")
qgs = QgsApplication([], True)
qgs.initQgis()
# Systeme de projection du projet
mycrs = QgsCoordinateReferenceSystem(2154)
QgsProject.instance().setCrs(mycrs)

# Import du module processing QGIS (native)
import processing
from processing.core.Processing import Processing
Processing.initialize()
QgsApplication.processingRegistry().addProvider(QgsNativeAlgorithms())

# Import du module processing pluggin QuickOSM
from QuickOSM.quick_osm import QuickOSMPlugin
QuickOSMPlugin.initProcessing(QuickOSMPlugin)

project =QgsProject.instance()
# *********************************************************************************


#                                      FUNCTIONS
# :::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::
def RemoveMemory(layer):
    project.addMapLayer(layer)
    project.removeMapLayer(project.mapLayersByName(layer.name())[0].id())

def CreateMemory(layer, memory_out):
    attrs = layer.dataProvider().fields().toList()
    temp_prov = memory_out.dataProvider()
    temp_prov.addAttributes(attrs)
    memory_out.updateFields()
    for elem in layer.getFeatures():
        feat = QgsFeature()
        geom = elem.geometry()
        feat.setGeometry(geom)
        feat.setAttributes(elem.attributes())
        memory_out.dataProvider().addFeatures([feat])
        memory_out.updateExtents()

def AddField(layer, field_name, type):
    field_names = [field.name() for field in layer.fields()]
    if field_name not in field_names:
        layer.startEditing()  # Mise en édition de la donnée
        temp_prov = layer.dataProvider()
        new_field = QgsField(field_name, type)
        temp_prov.addAttributes([new_field])
        layer.updateFields()
        layer.commitChanges() # Fermture de l'édition de la donnée
    else:
        print("!!{} déjà dans {}!!".format(field_name, layer.name()))

def rename_dp_field(layer, oldname, newname):
  findex = layer.dataProvider().fieldNameIndex(oldname)
  if findex != -1:
    layer.dataProvider().renameAttributes({findex: newname})
    layer.updateFields()
  else:
      print("!! rename field : problème avec le champ {}!!".format(oldname))

def del_fields (layer,list_del):
    list_del_id = []
    for f in layer.fields():
        if f.name() in list_del:
            list_del_id.append(layer.dataProvider().fieldNameIndex(f.name()))
    layer.dataProvider().deleteAttributes(list_del_id)
    layer.updateFields()
# :::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::


#                                     TRAITEMENTS
# ---------------------------------------------------------------------------------
# _______________________Path and QgsVectorLayer
print('Prépration inputs')
path_1 = r'H:\10_Steg\10_11_SIG\02_Dossiers_ponctuels\03-23_Regroupement_arrets_bus_CDVIA\gtfs_IDFM\stops.gpkg'
stops = QgsVectorLayer(path_1, 'stops_cd94', 'ogr')
path_2 = r'H:\10_Steg\10_11_SIG\02_Dossiers_ponctuels\03-23_Regroupement_arrets_bus_CDVIA\IDFM_octobre_2021\Referentiel_ligne_IDFM_CD94.gpkg'
line = QgsVectorLayer(path_2, 'Ligne IDFM', 'ogr')
path_3=r'H:\10_Steg\10_11_SIG\02_Dossiers_ponctuels\03-23_Regroupement_arrets_bus_CDVIA\IDFM_octobre_2021\Arrets_ZDE_CD94.gpkg'
arret_zde = QgsVectorLayer(path_3, 'Arret ZDE CD94', 'ogr')

# _______________________Récupération des line_id et des noms
print("1- Création de la liste des stop_id+line_id")
rows = stops.getFeatures()
list_line_id = []
for row in rows:
    list_temp = []
    stop_id = row['stop_id']
    line_id = row['line_id']
    if line_id != None:
        list_temp.append(stop_id)
        list_id = line_id.split(';')
        for i in list_id:
            list_temp.append(i)
        list_line_id.append(list_temp)

print("\t- Récupération des nom de ligne")
rows = line.getFeatures()
list_name_line = []
for row in rows:
    list_temp = []
    line_id = row['lineid']
    name = row['linename']
    short_name = row['lineshortn']
    for e in [line_id, name, short_name]:
        list_temp.append(e)
    list_name_line.append(list_temp)

# _______________________Intégration des noms de ligne dans stops
print("2- Préparation des listes pour intégration")
list_update_name = []
list_update_shortname = []
for i in list_line_id:
    list_line = []
    list_temp = []
    list_temp_2 = []
    list_temp.append(i[0])
    list_temp_2.append(i[0])
    step = 0
    for e in i:
        step += 1
        if step >= 2:
            list_line.append(e)
    for name_line in list_line:
        for elem in list_name_line:
            if name_line == elem[0]:
                list_temp.append(elem[1])
                list_temp_2.append(elem[2])
    list_update_name.append(list_temp)
    list_update_shortname.append(list_temp_2)

print("\t- Ajout des champs name line")
field_add= ['name_line','shortname_line'] # Nom des champs name des lignes à ajouter
for f in field_add:
    AddField(stops,f,QVariant.String)

print("\t\t- Intégration des noms de ligne dans stops")
stops.startEditing()
rows= stops.getFeatures()
idx_1=stops.fields().lookupField(field_add[0])
idx_2=stops.fields().lookupField(field_add[1])
u=0
nomatch=0
for row in rows:
    id=row['stop_id']
    for i in list_update_name:
        if id==i[0] and len(i)>1:
            u += 1
            print("\t\t\t- Maj name line {}/{}".format(u, len(list_update_name)))
            new_name = ';'.join(str(e) for e in i[1:])
            stops.changeAttributeValue(row.id(), idx_1, new_name)
        if id==i[0] and len(i)==1:
            nomatch+=1
    for i in list_update_name:
        if id==i[0] and len(i)>1:
            new_shortname = ';'.join(str(e) for e in i[1:])
            stops.changeAttributeValue(row.id(), idx_2, new_shortname)
stops.commitChanges()
print ("!!Pas de correspondance avec le référentiel de ligne : {}!!".format(nomatch))

# _______________________Jointure stops sur arret_zde
print("3- Création du champ arret_id")
field_arret_id = 'arret_id'
AddField(stops,field_arret_id,QVariant.Int)
stops.startEditing()
rows= stops.getFeatures()
print("Réécriture de stop_id dans {}".format(field_arret_id))
idx = stops.fields().lookupField(field_arret_id)
for row in rows:
    stop_id = row['stop_id']
    list_temp=stop_id.split(':')
    for i in list_temp:
        try:
            int(i)
            stops.changeAttributeValue(row.id(), idx, int(i))
        except:
            pass
stops.commitChanges()


# _______________________Export temporaire des arrêts de bus OMS sur le CD94
print("4- Chargement données OSM")
params={
'QUERY':'{{geocodeArea:val-de-marne}}->.searchArea;\nnode\n''  [bus=yes]\n  (area.searchArea);\nnode\n  [highway=bus_stop]\n''  (area.searchArea);\nout;',
'TIMEOUT':25,
'SERVER':'https://lz4.overpass-api.de/api/interpreter',
'EXTENT':'0.000000000,1.000000000,0.000000000,1.000000000 [EPSG:2154]',
'AREA':'',
'FILE':'TEMPORARY_OUTPUT'
}
process_osm=processing.run("quickosm:downloadosmdatarawquery", params)
point_query =process_osm['OUTPUT_POINTS']

# _______________________Delta des positions référentiel ZDE et OSM
print ("5- Delta des positions référentiel ZDE et OSM")
# Liste des id ZDE pour établir les filtres
print ("\t- Création de la liste des id ZDE")
rows= arret_zde.getFeatures()
list_id = []
for row in rows:
    id_zde = row['ArRId']
    if id_zde not in list_id:
        list_id.append (id_zde)

# Projection des arret ZDE sur les arrets OSM
print ("\t- Projection des arret ZDE sur les arrets OSM:")
u=0
list_change = []
for i in list_id:
    u+=1
    #Création des filtres pour projeter l'arret zde sur les arrets OSM
    exp_zde   = '"ArRId"={}'.format(i)
    exp_osm = '"ref:FR:STIF"=\'{}\''.format(str(i))
    filter_zde = arret_zde.setSubsetString (exp_zde)
    filter_zde = point_query.setSubsetString (exp_osm)
    params = {'INPUT':arret_zde,'INPUT_2':point_query,
    'FIELDS_TO_COPY':['full_id','osm_id','route_ref'],'DISCARD_NONMATCHING':False,
    'PREFIX':'osm_','NEIGHBORS':1,'MAX_DISTANCE':None,'OUTPUT':'TEMPORARY_OUTPUT'}
    process_join_nearest = processing.run("native:joinbynearest",params)
    join_nearest = process_join_nearest ['OUTPUT']
    # Si premier join_nearest : crétation de la donnée temp
    if u==1:
        temp = QgsVectorLayer("Point?crs=epsg:2154", "join_nearest", "memory")
        temp.startEditing()
        attrs = join_nearest.dataProvider().fields().toList()
        temp_prov = temp.dataProvider()
        temp_prov.addAttributes(attrs)
        temp.updateFields()
    ajout=0
    # Ecriture du point dans la donnée temp
    for elem in join_nearest.getFeatures():
        dist=elem['distance']
        if dist==None:
            dist=0
        # Si la distance avec la postion OSM est égal ou sup à 15m :
        # la postion x;y de l'arret OSM est retenue
        if dist >=15:
            for new in point_query.getFeatures():
                ajout += 1
                feat = QgsFeature()
                geo = new.geometry()
                sourceCrs = QgsCoordinateReferenceSystem(4326)
                tr = QgsCoordinateTransform(sourceCrs, mycrs, project)
                geo.transform(tr) # Conversion des coordonnées du point OSM en WGS84 (4326) vers lambert93 (2354)
                feat.setGeometry(geo)
                feat.setAttributes(elem.attributes())
                temp.addFeatures([feat])
                temp.updateExtents()
                list_change.append (i)
        # Si la distance avec la postion OSM est inférieure à 15m:
        # La postion x;y du référentiel IDFM ZDE est gardée
        if dist<15:
            ajout+=1
            feat = QgsFeature()
            geo = elem.geometry()
            feat.setGeometry(geo)
            feat.setAttributes(elem.attributes())
            temp.addFeatures([feat])
            temp.updateExtents()
    RemoveMemory(join_nearest)
    print ("\t\t- {}/{} ajout:{}".format(u,len(list_id),ajout))
temp.commitChanges()

# Nettoyage des champs
print ("\t -Nettoyage des champs")
fields_del = ['n','feature_x','feature_y','nearest_x','nearest_y'] # Champs du géotraitement à supprimer
del_fields(temp,fields_del)
rename_dp_field(temp, 'distance', 'osm_distance')


# _______________________Récupération des champs stops sur la donnée finale
path_out= r'H:\10_Steg\10_11_SIG\02_Dossiers_ponctuels\03-23_Regroupement_arrets_bus_CDVIA\IDFM_octobre_2021'
name_out ='\IDFM_ZDE_FINAL.gpkg'
print ("6- Création de l'export {}".format(name_out))

params={'INPUT':temp,'FIELD':'ArRId',
'INPUT_2':stops,'FIELD_2':'arret_id',
'FIELDS_TO_COPY':['stop_id','line_id','name_line','shortname_line'],
'METHOD':1,'DISCARD_NONMATCHING':False,
'PREFIX':'stop_','OUTPUT':path_out+name_out
}
join = processing.run("native:joinattributestable",params)
join_final = join['OUTPUT']

# Rename des doublons prefix
layer_final = QgsVectorLayer(join_final,'Arret IDFM Final','ogr')
doublon_1 = 'osm_osm_id'
doublon_2 = 'stop_stop_id'
rename_dp_field(layer_final, doublon_1, 'osm_id')
rename_dp_field(layer_final, doublon_2, 'stop_id')

# Fermeture du projet QGIS
qgs.exitQgis()

print("Terminé")
