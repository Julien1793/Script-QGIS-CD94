# -*- coding: cp1252 -*-
# Date : 27/05/2021
# Auteur : Julien Samaniego
# Objet du script : Récupération id_line sur donnée stops (gtfs IDFM)

# **************************DESCRIPTION DU SCRIPT******************************
# *****************************************************************************
import sys, os

os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = r'C:\Program Files\QGIS 3.16\apps\Qt5\plugins'
os.environ['PATH'] += r';C:\Program Files\QGIS 3.16\apps\qgis-ltr\bin;~C:\Program Files\QGIS 3.16\apps\Qt5\bin'

from qgis.core import *
from qgis.gui import *
from PyQt5.QtCore import *

from qgis.analysis import QgsNativeAlgorithms

# See https://gis.stackexchange.com/a/155852/4972 for details about the prefix
# Supply the path to the qgis install location
QgsApplication.setPrefixPath(r'C:\Program Files\QGIS 3.16\apps\qgis-ltr', True)
#  start QGIS processing application
os.environ['QGIS_PREFIX_PATH'] = r'C:\Program Files\QGIS 3.16\apps\qgis-ltr'
os.environ['GDAL_DATA'] = r'C:\Program Files\QGIS 3.16\share\gdal'
os.environ['PROJ_LIB'] = r'C:\Program Files\QGIS 3.16\share\proj'

# Append the path where processing plugin can be found
sys.path.append(r'C:\Program Files\QGIS 3.16\apps\qgis-ltr\python\plugins')

#                         Demarrage QGIS et import du module processing
# *********************************************************************************
qgs = QgsApplication([], True)
qgs.initQgis()
print("démarrage QGIS")
import processing
from processing.core.Processing import Processing

Processing.initialize()
QgsApplication.processingRegistry().addProvider(QgsNativeAlgorithms())
# *********************************************************************************
def RemoveMemory(layer):
    qgs.addMapLayer(layer)
    qgs.removeMapLayer(qgs.mapLayersByName(layer.name())[0].id())


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


# _______________________Path and QgsVectorLayer
print('Prépration inputs')
path_1 = r'H:\10_Steg\10_11_SIG\02_Dossiers_ponctuels\03-23_Regroupement_arrets_bus_CDVIA\gtfs_IDFM\stops.gpkg'
stops = QgsVectorLayer(path_1, 'stops_cd94', 'ogr')
print("Chargement stop_times")
path_2 = r'H:\10_Steg\10_11_SIG\02_Dossiers_ponctuels\03-23_Regroupement_arrets_bus_CDVIA\gtfs_IDFM\stop_times.txt'
fullname = path_2.replace('\\', '/')
uri = 'file:///%s?type=%s&delimiter=%s&geomType=nones' % (fullname, 'csv', ',')
stop_times = QgsVectorLayer(uri, 'Stop times test', 'delimitedtext')
##print("récup des champs stop_times")
##field_names = [field.name() for field in stop_times.fields()]

# _______________________Jointure 1/n stop_times sur stops
print("Jointure 1/n stop_times sur stops")
prefix = 'stop_times_'
params = {
    'INPUT': stops,
    'FIELD': 'stop_id',
    'INPUT_2': stop_times,
    'FIELD_2': 'stop_id',
    'FIELDS_TO_COPY': ['trip_id'],
    'METHOD': 0, 'DISCARD_NONMATCHING': False,
    'PREFIX': prefix,
    'OUTPUT': 'TEMPORARY_OUTPUT'
}
process_join = processing.run("native:joinattributestable", params)
join_layer = process_join['OUTPUT']

# _______________________Boucle dans la jointure : récupération des id de ligne par arret (stops)
print("Création de la liste des stop_id")
rows = stops.getFeatures()
list_stop_id = []
for row in rows:
    stop_id = row['stop_id']
    if stop_id not in list_stop_id:
        list_stop_id.append(stop_id)

print("Boucle dans la jointure : récupération des id de ligne par arret (stops):")

list_full = []
rows = join_layer.getFeatures()
u = 0
for row in rows:
    u += 1
    print("\t -step :{}".format(u))
    list_temp = []
    stop_id = row['stop_id']
    list_temp.append(stop_id)
    trip_id = row[prefix + 'trip_id']
    if trip_id == None:
        trip_id = ''
        list_temp.append(trip_id)
    else:
        sp = trip_id.split('-')
        list_temp.append(sp[1])
    list_full.append(list_temp)

print("Création liste appareillage stop_id et line_id:")
list_upload = []
u = 0
for id in list_stop_id:
    u += 1
    print("\t -Appareillage {}/{}".format(u, len(list_stop_id)))
    list_temp = []
    list_temp.append(id)
    for f in list_full:
        if id == f[0]:
            if f[1] not in list_temp:
                list_temp.append(f[1])
    list_upload.append(list_temp)
# _______________________Intégration des line_id dans stops
print("Intégration des line_id dans stops")
field_names = [field.name() for field in stops.fields()]
field_line = 'line_id'

if field_line not in field_names:
    stops.startEditing()  # Mise en édition de la donnée stops
    temp_prov = stops.dataProvider()
    new_field = QgsField(field_line, QVariant.String)
    temp_prov.addAttributes([new_field])
    stops.updateFields()
    stops.commitChanges()

stops.startEditing()  # Mise en édition de la donnée stops
rows = stops.getFeatures()
idx_id = stops.fields().lookupField(field_line)
u = 0
line_id_vide = 0
for row in rows:
    u += 1
    print("\t -Maj line_id {}/{}".format(u, len(list_stop_id)))
    stop_id = row['stop_id']
    list_temp = []
    for up in list_upload:
        if up[0] == stop_id:
            step = 0
            for a in up:
                if step > 0 and a != '':
                    list_temp.append(a)
                step += 1
            if len(list_temp) > 0:
                line_id = ';'.join(str(e) for e in list_temp)
                print("\t\t -Ajout line_id :{}".format(line_id))
                stops.changeAttributeValue(row.id(), idx_id, line_id)
            else:
                line_id_vide += 1
                print("\t\t -Pas de line_id")
stops.commitChanges()
print("!! Nombre d'arrêts sans correspondance de ligne : {} !!".format(line_id_vide))
qgs.exitQgis()

print("Terminé")
