# -*- coding: utf-8 -*-

"""
***************************************************************************
*                                                                         *
*   This program is free software; you can redistribute it and/or modify  *
*   it under the terms of the GNU General Public License as published by  *
*   the Free Software Foundation; either version 2 of the License, or     *
*   (at your option) any later version.                                   *
*                                                                         *
***************************************************************************
"""
import sys, os
from pathlib import Path
from qgis.PyQt.QtCore import (QCoreApplication, QVariant)
from qgis.core import (QgsProcessing,
                       QgsFeatureSink,
                       QgsFeature,
                       QgsField,
                       QgsFields,
                       QgsVectorLayerJoinInfo,
                       QgsVectorLayer,
                       QgsCoordinateReferenceSystem,
                       QgsFeatureSource,
                       QgsFeatureRequest,
                       QgsProject,
                       QgsExpression,
                       QgsProcessingException,
                       QgsProcessingAlgorithm,
                       QgsProcessingParameterFeatureSource,
                       QgsProcessingParameterFeatureSink,
                       QgsProcessingParameterField,
                       QgsProcessingParameterVectorDestination,
                       QgsProcessingOutputVectorLayer,
                       QgsProcessingParameterFileDestination
                       )
##from qgis.analysis import QgsNativeAlgorithms
##import processing
from qgis import processing


class ExampleProcessingAlgorithm(QgsProcessingAlgorithm):
    """
    This is an example algorithm that takes a vector layer and
    creates a new identical one.

    It is meant to be used as an example of how to create your own
    algorithms and explain methods and variables used to do it. An
    algorithm like this will be available in all elements, and there
    is not need for additional work.

    All Processing algorithms should extend the QgsProcessingAlgorithm
    class.
    """

    # Constants used to refer to parameters and outputs. They will be
    # used when calling the algorithm from another algorithm, or when
    # calling from the QGIS console.

    INPUT_1 = 'INPUT_1'
    INPUT_2 = 'INPUT_2'
    INPUT_3 = 'INPUT_3'
    INPUT_4 = 'INPUT_4'
    OUTPUT_1 = 'OUTPUT_1'
    OUTPUT_2 = 'OUTPUT_2'
    OUTPUT_3 = 'OUTPUT_3'

    def tr(self, string):
        """
        Returns a translatable string with the self.tr() function.
        """
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return ExampleProcessingAlgorithm()

    def name(self):
        """
        Returns the algorithm name, used for identifying the algorithm. This
        string should be fixed for the algorithm, and must not be localised.
        The name should be unique within each provider. Names should contain
        lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'maj_section_comptage'

    def displayName(self):
        """
        Returns the translated algorithm name, which should be used for any
        user-visible display of the algorithm name.
        """
        return self.tr('maj_section_comptage')

    def group(self):
        """
        Returns the name of the group this algorithm belongs to. This string
        should be localised.
        """
        return self.tr('CD94')

    def groupId(self):
        """
        Returns the unique ID of the group this algorithm belongs to. This
        string should be fixed for the algorithm, and must not be localised.
        The group id should be unique within each provider. Group id should
        contain lowercase alphanumeric characters only and no spaces or other
        formatting characters.
        """
        return 'CD94'

    def shortHelpString(self):
        """
        Returns a localised short helper string for the algorithm. This string
        should provide a basic description about what the algorithm does and the
        parameters and outputs associated with it..
        """
        v0 = "Description :"
        v1 = "\n Ce script permet de générer une nouvelle table des sections de comptage à jour à partir du nouveau référentiel routier IGN, de la nouvelle table CD94 et du référentiel routier actuel"
        v2 = "\n L'outil se focalise sur les RD du CD94 et il permet aussi de générer des ponctuels (Point qualité des mises à jour) avec un contrôle qualité des tronçons mis à jours (champ qualite_maj) :"
        v3 = "\n - qualité 1= une correspondace été trouvée pour réaffacter le bon identifiant de la section de comptage"
        v4 = "\n - qualité 2= Aucun tronçon trouvé pour établir une correspondance => vérifier qu'il s'agit bien de tronçons qui sont normalement sans section de comptage"
        return self.tr(v0+v1+v2+v3+v4)

    def initAlgorithm(self, config=None):
        """
        Here we define the inputs and output of the algorithm, along
        with some other properties.
        """

        # We add the input vector features source. It can have any kind of
        # geometry.
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.INPUT_1,
                self.tr('New référentiel IGN'),
                [QgsProcessing.TypeVectorAnyGeometry]
            )
        )
        
        # We add the input vector features source. It can have any kind of
        # geometry.
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.INPUT_2,
                self.tr('Nouvelle table CD94'),
                [QgsProcessing.TypeFile]
            )
        )

        # We add the input vector features source. It can have any kind of
        # geometry.
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.INPUT_3,
                self.tr('Référentiel IGN actuel'),
                [QgsProcessing.TypeVectorAnyGeometry]
            )
        )
        
        # We add the input vector features source. It can have any kind of
        # geometry.
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.INPUT_4,
                self.tr('Table des sections de comptage'),
                [QgsProcessing.TypeFile]
            )
        )

        # We add a feature sink in which to store our processed features (this
        # usually takes the form of a newly created vector layer when the
        # algorithm is run in QGIS).
        '''
        self.addParameter(
            QgsProcessingParameterFeatureSink(
                self.OUTPUT,
                self.tr('Output layer')
            )
        )



        self.addOutput(
            QgsProcessingOutputVectorLayer(
                self.OUTPUT_x,
                self.tr('memory'),
                type = QgsProcessing.TypeVectorAnyGeometry)
        )
        '''

        self.addParameter(
            QgsProcessingParameterVectorDestination(
                self.OUTPUT_1,
                self.tr('Troncons sans jointure section')
            )
        )
        
        self.addParameter(
            QgsProcessingParameterVectorDestination(
                self.OUTPUT_2,
                self.tr('Point qualité des mises à jour')
            )
        )
        '''
        self.addParameter(
            QgsProcessingParameterFileDestination(
                self.OUTPUT_4,
                self.tr('Table CD94 à jour'), ##!!!pas de fichier temporaire en sortie il faut choisir une destinnation!!!'),
                'CSV files (*.csv)',
            )
        )
        '''
        self.addParameter(
            QgsProcessingParameterVectorDestination(
                self.OUTPUT_3,
                self.tr('Table section de comptage à jour')
            )
        )

    def processAlgorithm(self, parameters, context, feedback):

        # *******************Fonctions*********************************

        def CreateMemory(layer, memory_out):
            attrs = layer.dataProvider().fields().toList()
            temp_prov = memory_out.dataProvider()
            temp_prov.addAttributes(attrs)
            memory_out.updateFields()
            for elem in layer.getFeatures():
                feat = QgsFeature()
                ##geom = elem.geometry()
                ##feat.setGeometry(geom)
                feat.setAttributes(elem.attributes())
                memory_out.dataProvider().addFeatures([feat])
                memory_out.updateExtents()

        def AddField(layer, field_name,type):
            field_names = [field.name() for field in layer.fields()]
            if field_name not in field_names:
                layer.startEditing()  # Mise en édition de la donnée
                temp_prov = layer.dataProvider()
                new_field = QgsField(field_name, type)
                temp_prov.addAttributes([new_field])
                layer.updateFields()
                layer.commitChanges()  # Fermture de l'édition de la donnée
            else:
                feedback.pushInfo("!!{} déjà dans {}!!".format(field_name, layer.name()))

        def CalcField (layer,field_name,new_value):
            layer.startEditing()
            rows = layer.getFeatures()
            idx_id = layer.fields().lookupField(field_name)
            for row in rows:
                layer.changeAttributeValue(row.id(), idx_id, new_value)
            layer.commitChanges()

        def del_fields(layer, list_del):
            list_del_id = []
            for f in layer.fields():
                if f.name() in list_del:
                    list_del_id.append(layer.dataProvider().fieldNameIndex(f.name()))
            layer.dataProvider().deleteAttributes(list_del_id)
            layer.updateFields()
            
        def crs_encodage (layer,crs,encodage):
            feedback.pushInfo(layer.name() + ' chargé')
            if layer.isValid():
                layer.setProviderEncoding(encodage)
                mycrs = QgsCoordinateReferenceSystem(crs)
                layer.setProviderEncoding(encodage)
                feedback.pushInfo('\t- => crs : 2154')
                feedback.pushInfo('\t- => encodage utf-8')
            else:
                feedback.reportError(layer.name() + " probleme chargement !!!")
                sys.exit()
            

        # *************************************************************
        # Conversion des id input en QgsVectorLayer
        feedback.pushInfo('**************************')
        new_ref = self.parameterAsLayer(parameters, self.INPUT_1, context)
        tab_cd94 = self.parameterAsLayer(parameters, self.INPUT_2, context)
        ref_old = self.parameterAsLayer(parameters, self.INPUT_3, context)
        tab_section_old = self.parameterAsLayer(parameters, self.INPUT_4, context)
                
        feedback.pushInfo('INPUTS :')
        feedback.pushInfo(str(new_ref))
        feedback.pushInfo(str(tab_cd94))
        feedback.pushInfo(str(ref_old))
        feedback.pushInfo(str(tab_section_old))

        # Véréfication des couhces et encade utf8 (nex ref et tab cd94)
        feedback.pushInfo('Chargement des données :')
        list = [new_ref]
        for f in list:
            crs_encodage(f,2154,'utf-8')

        feedback.pushInfo('**************************')
        # ************************ TRAITEMENTS
        feedback.pushInfo("------------DEBUT DES TRAITEMENTS------------")
        # ______________________Jointures sur le nouveau référentiel
        step=1
        feedback.pushInfo(str(step)+"- *** Jointures sur le nouveau référentiel *** ")
        step+=1
        # Jointure nouvelle table CD94 sur le nouveau référentiel
        feedback.pushInfo("- Jointure nouvelle table CD94 sur le nouveau référentiel ")
        params = {'DISCARD_NONMATCHING': False, 'FIELD': 'ID',
                  'FIELDS_TO_COPY': ["NUMERO_ROUTE","CLASSEMENT"], 'FIELD_2': 'ID',
                  'INPUT': new_ref, 'INPUT_2': tab_cd94, 'METHOD': 1, 'OUTPUT': 'memory:jointure',
                  'PREFIX': ''}
        jointure_1 = processing.run("native:joinattributestable", params, context=context, feedback=feedback)['OUTPUT']
        
        # Jointure table section de comptage sur le nouveau référentiel
        feedback.pushInfo("- Jointure table section de comptage sur le nouveau référentiel ")
        params = {'DISCARD_NONMATCHING': False, 'FIELD': 'ID',
                  'FIELDS_TO_COPY': [], 'FIELD_2': 'id',
                  'INPUT': jointure_1, 'INPUT_2': tab_section_old, 'METHOD': 1, 'OUTPUT': 'memory:jointure',
                  'PREFIX': ''}
        jointure_2 = processing.run("native:joinattributestable", params, context=context, feedback=feedback)['OUTPUT']

        # Application de la selection dans la couche avec la requête du dessus (exp)
        exp1 = '"CLASSEMENT" in (\'Départementale magistrale\',\'Départementale principale\',\'Départementale secondaire\')'
        exp2 = ' and "section" is null'
        exp  = exp1+exp2
        feedback.pushInfo(exp)
        selection = jointure_2.selectByExpression(exp)
        layer = jointure_2.selectedFeatures()

        # Affichage le nombre de tronçon à mettre à jour (perte jointure table cd94)
        feedback.pushInfo("\t- Creation des tronçons à vérifier")
        # Paramètres du processing de sauvegarde la selection en une couche mémoire
        params = {
            'INPUT': jointure_2,
            'OUTPUT': 'memory: tronons à vérifier'}
        save_select = processing.run("native:saveselectedfeatures", params)
        out_select = save_select['OUTPUT']  # Variable pour appeler la couche
        
        jointure_2.removeSelection()# Supprime la selection dans jointure 2

        # Output 1 du processing  : Troncons sans jointure section
        output1 = self.parameterAsOutputLayer(parameters, self.OUTPUT_1, context)
        params = {'INPUT': out_select, 'OUTPUT': output1, 'LAYER_NAME': 'Troncons sans jointure section',
                  'DATASOURCE_OPTIONS': '', 'LAYER_OPTIONS': ''}
        layer_output1 = processing.run("native:savefeatures", params, context=context, feedback=feedback)['OUTPUT']
        
        # ______________________Génération des points au centre des tronçons
        
        feedback.pushInfo(str(step)+"- *** Génération des points au centre des tronçons *** ")
        step+=1

        # Création de la couche en mémoire pour accueillir les points
        temp = QgsVectorLayer("Point?crs=epsg:2154", "point_milieu_troncon_comptage", "memory")
        # Mise en édition de la couche et ajout des champs issues de out_select
        temp.startEditing()
        attrs = out_select.dataProvider().fields().toList()
        temp_prov = temp.dataProvider()
        temp_prov.addAttributes(attrs)
        temp.updateFields()
        # Boucle sur les tronçons sans jointure pour créer un point au centre
        ##step =0
        for elem in out_select.getFeatures():
            ##step +=1
            ##print ("\t - {}".format (step))
            feat = QgsFeature()
            geom = elem.geometry().interpolate(elem.geometry().length() / 2)
            feat.setGeometry(geom)
            feat.setAttributes(elem.attributes())
            temp.addFeatures([feat])
            temp.updateExtents()
        feedback.pushInfo("- Ajout du champ qualie_maj dans la donnée des points")
        field_quali = 'qualite_maj'
        new_field = QgsField(field_quali, QVariant.Int)
        temp_prov.addAttributes([new_field])
        temp.updateFields()
        # Ecriture dans la donnée temp créée au dessus (points au centre des tronçons)
        temp.commitChanges()
 
        # ______________________Récupération des sections de comptage
        
        feedback.pushInfo(str(step)+"- *** Récupération des sections de comptage manquentes dans le référentiel *** ")
        step+=1
        
        # Création des liste des tronçons à filtrer (rd,rn, autoroute)
        feedback.pushInfo("Création de la liste des RD avec perte section de comptage")
        list_rd_temp = [i['NUMERO_ROUTE'] for i in temp.getFeatures()]
        list_rd = []
        for i in list_rd_temp:
            if i not in list_rd and i != '' and i != None:
                list_rd.append(i)  # Récupération des numéro de route de façon unique
        feedback.pushInfo(str(list_rd))
        
        # Jointure table section de comptage sur l'ancien référentiel
        feedback.pushInfo("- Jointure table section de comptage sur le référentiel actuel")
        params = {'DISCARD_NONMATCHING': False, 'FIELD': 'ID',
                  'FIELDS_TO_COPY': [], 'FIELD_2': 'id',
                  'INPUT': ref_old, 'INPUT_2': tab_section_old, 'METHOD': 1, 'OUTPUT': 'memory:jointure',
                  'PREFIX': ''}
        jointure_3 = processing.run("native:joinattributestable", params, context=context, feedback=feedback)['OUTPUT']
        
        feedback.pushInfo("Projection des points sur l'ancien référentiel")
        creation_temp_2 =0
        list_join = []
        for rd in list_rd:
            creation_temp_2 += 1
            # Création des filtres pour projeté le point sur le même numero de route
            feedback.pushInfo("--> {}".format(rd))
            exp1 = '"NUMERO_ROUTE"= \'{}\''.format(rd)
            exp2 = '"NUMERO_ROUTE"= \'{}\''.format(rd)
            filter_1 = jointure_3.setSubsetString(exp1)
            filter_2 = temp.selectByExpression(exp2)
            temp.selectedFeatures()
            params = {
                'INPUT': temp,
                'OUTPUT': 'memory: projection'}
            select_temp = processing.run("native:saveselectedfeatures", params)[
                'OUTPUT']  # Variable pour appeler la couche
            ##filter_2 = temp.setSubsetString(exp2)
            # Pojection des points sur les tronçons correspondant (numéro de route)
            params = {'INPUT': select_temp, 'INPUT_2': jointure_3,
                      'FIELDS_TO_COPY': [], 'DISCARD_NONMATCHING': False,
                      'PREFIX': '', 'NEIGHBORS': 1, 'MAX_DISTANCE': 20, 'OUTPUT': 'TEMPORARY_OUTPUT'}
            process_join_nearest = processing.run("native:joinbynearest", params)
            join_nearest = process_join_nearest['OUTPUT']
            feedback.pushInfo(str(exp2))

            # Si premier join_nearest : crétation de la donnée temp_2
            if creation_temp_2 == 1:
                temp_2 = QgsVectorLayer("Point?crs=epsg:2154", "join_attribut", "memory")
                temp_2.startEditing()
                attrs = join_nearest.dataProvider().fields().toList()
                temp_prov_2 = temp_2.dataProvider()
                temp_prov_2.addAttributes(attrs)
                temp_2.updateFields()
            # Ecriture du point dans la donnée temporaire (temp_2)
            ajout = 0
            for elem in join_nearest.getFeatures():
                ajout += 1
                feat = QgsFeature()
                geo = elem.geometry()
                feat.setGeometry(geo)
                feat.setAttributes(elem.attributes())
                temp_2.addFeatures([feat])
                temp_2.updateExtents()
            feedback.pushInfo("AJOUT temp_2 : " + str(ajout))
            list_join.append(ajout)
        # Cloture de l'adiation de la couche en mémoire jointure par attribut le plus proche
        temp_2.commitChanges()
        feedback.pushInfo("!!!!!! Total des corrections : {} !!!!!!".format(str(sum(list_join))))
        
        # Ecriture du champ qualite_maj
        feedback.pushInfo("Ecriture du champ qualite_maj")
        temp_2.startEditing()
        rows = temp_2.getFeatures()
        for row in rows:
            id_section = row['section_2']
            idx_id = temp_2.fields().lookupField(field_quali)
            # Si une correspondance avec la projection a fonctionné => qualie_maj =1
            if id_section != None:
                new_att = 1
                temp_2.changeAttributeValue(row.id(), idx_id, new_att)
            # Si pas de correspondance avec la projection => qualie_maj =2
            else:
                new_att = 2
                temp_2.changeAttributeValue(row.id(), idx_id, new_att)
        temp_2.commitChanges()
        
        # Output 2 du processing  : Point qualité des mises à jour
        output2 = self.parameterAsOutputLayer(parameters, self.OUTPUT_2, context)
        params = {'INPUT': temp_2, 'OUTPUT': output2, 'LAYER_NAME': 'Point qualité des mises à jour',
                  'DATASOURCE_OPTIONS': '', 'LAYER_OPTIONS': ''}
        layer_output2 = processing.run("native:savefeatures", params, context=context, feedback=feedback)['OUTPUT']
        
        
        
        # ______________________Ecriture de la nouvelle table des sections
        
        feedback.pushInfo(str(step)+"- *** Ecriture de la nouvelle table des sections *** ")
        step+=1
        
        # Jointure des projections sur le nouveau référentiel avec jointure de la table des sections
        feedback.pushInfo("- Jointure des projections sur le nouveau référentiel avec jointure de la table des sections")
        params = {'DISCARD_NONMATCHING': False, 'FIELD': 'ID',
                  'FIELDS_TO_COPY': [field_quali,'section_2'], 'FIELD_2': 'ID',
                  'INPUT': jointure_2, 'INPUT_2': temp_2, 'METHOD': 1, 'OUTPUT': 'memory:jointure',
                  'PREFIX': ''}
        jointure_4 = processing.run("native:joinattributestable", params, context=context, feedback=feedback)['OUTPUT']
        
        # Ecriture du champs section_2 dans section pour les troncons à mettre à jour
        jointure_4.startEditing()
        req = QgsFeatureRequest().setFilterExpression('"section_2" is not null and "qualite_maj"=1')
        rows = jointure_4.getFeatures(req) # Selection des tronçons à mettre à jour
        
        for row in rows:
            id_section = row['section_2']
            idx_id = temp_2.fields().lookupField('section')
            jointure_4.changeAttributeValue(row.id(), idx_id, id_section)
        jointure_4.commitChanges()
        
        # Prépration de la future table des sections
        field_names = [field.name() for field in jointure_4.fields()]
        
        list_ok = ['ID','section']
        list_del= []
        for f in field_names:
            if f not in list_ok:
                list_del.append (f)
        
        del_fields(jointure_4, list_del)
        jointure_4.setSubsetString('"section" is not null')
        
        # Création de la table en mémoire
        tab_section_new = QgsVectorLayer('None', 'Tab_cd94_new', 'memory')
        CreateMemory(jointure_4, tab_section_new)
        
        # Output 3 du processing  : Table section de comptage à jour
        output3 = self.parameterAsOutputLayer(parameters, self.OUTPUT_3, context)
        params = {'INPUT': tab_section_new, 'OUTPUT': output3, 'LAYER_NAME': 'Table section de comptage à jour',
                  'DATASOURCE_OPTIONS': '', 'LAYER_OPTIONS': ''}
        layer_output3 = processing.run("native:savefeatures", params, context=context, feedback=feedback)['OUTPUT']
        
        
        return {self.OUTPUT_1: layer_output1,self.OUTPUT_2: layer_output2,self.OUTPUT_3: layer_output3}