# -*- coding: cp1252 -*-
#-------------------------------------------------------------------------------
# Name:        Chargement couche WFS PyQGIS
# Author:      J Samaniego
# Created:     12/05/2022
# Contenu :
# Le script pemret de chargé d'appeler un couche WFS (PyQGIS)
#-------------------------------------------------------------------------------

def call_wfs(url,layer_name,crs,size,version):
    uri = QgsDataSourceUri()
    uri.setParam('pageSize',size)#10000
    uri.setParam('pagingEnabled', 'true')
    uri.setParam('preferCoordinatesForWfsT11', 'false')
    uri.setParam('restrictToRequestBBOX', '1')
    uri.setParam('service', 'wfs')
    uri.setParam('version', version)#2.0.0
    uri.setParam('request', 'GetFeature')
    uri.setParam('typename', layer_name)
    uri.setParam('srsName', crs)#EPSG:2154
    uri.setParam('url',url)#https://wxs-gpu.mongeoportail.ign.fr/externe/39wtxmgtn23okfbbs1al2lz3/wfs
    #uri.setUsername('me')
    #uri.setPassword('my_password')
    layer=QgsVectorLayer(uri.uri(), layer_name, 'WFS')
    if layer.isValid():
        print (layer_name+' WFS chargé')
    else:
        print (layer_name+' WFS problème chargement')
    return layer
    
url='https://wxs-gpu.mongeoportail.ign.fr/externe/39wtxmgtn23okfbbs1al2lz3/wfs'#url wfs
layer_name=''#Nom de la donnée

layer_wfs = call_wfs(url,layer_name,'EPSG:2154','10000','2.0.0')
#QgsProject.instance().addMapLayer(layer_wfs)
print ('termine')
