# -*- coding: utf-8 -*-

"""
***************************************************************************
*                                                                         *
*   Cet outil met à jour la table du reseau viaire rattachée au           *
*   référentiel routier IGN.                                             *
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
    OUTPUT_1 = 'OUTPUT_1'

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
        return 'maj_reseau_viaire'

    def displayName(self):
        """
        Returns the translated algorithm name, which should be used for any
        user-visible display of the algorithm name.
        """
        return self.tr('maj_reseau_viaire')

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
        v1 = "\nCet outil met à jour la table du reseau viaire rattachée au référentiel routier à partir des points qualité issu de la mise à jour IGN."
        return self.tr(v0+v1)

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
                self.tr('Point qualite maj IGN'),
                [QgsProcessing.TypeVectorAnyGeometry]
            )
        )

        # We add the input vector features source. It can have any kind of
        # Table.
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.INPUT_2,
                self.tr('Table reseau viaire actuelle'),
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
                self.OUTPUT_1,
                self.tr('Table du reseau viaire à jour')
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
                feedback.pushWarning("!!{} déjà dans {}!!".format(field_name, layer.name()))

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
            
        def rename_dp_field(layer, oldname, newname):
          findex = layer.dataProvider().fieldNameIndex(oldname)
          if findex != -1:
            layer.dataProvider().renameAttributes({findex: newname})
            layer.updateFields()
          else:
              feedback.pushWarning("!! rename field : problème avec le champ {}!!".format(oldname))

        def InputToQgslayer(layer):
            ##if '/' not in layer :
            if not os.path.exists(layer):
                for feat in QgsProject.instance().mapLayers().values():
                    if feat.id() == layer:
                        qgs_layer = feat
            else:
                name = Path(layer).stem
                qgs_layer = QgsVectorLayer(layer, name)
            return qgs_layer


        # *************************************************************
        # Conversion des id input en QgsVectorLayer
        feedback.pushInfo('**************************')
        pt_qualite = self.parameterAsLayer(parameters, self.INPUT_1, context)
        tab_viaire = self.parameterAsFile(parameters, self.INPUT_2, context)
        new_ref    = self.parameterAsLayer(parameters, self.INPUT_3, context)

        feedback.pushInfo('INPUTS :')
        feedback.pushInfo(str(pt_qualite))
        feedback.pushInfo(str(tab_viaire))
        feedback.pushInfo(str(new_ref))
        
        feedback.pushInfo('**************************')
        # ************************ TRAITEMENTS
        feedback.pushInfo("------------DEBUT DES TRAITEMENTS------------")
        # _______________________Jointures
        
        # Jointure de la table du reseau viaire sur le nouveau référentiel
        feedback.pushInfo("*** Jointures ***")
        feedback.pushInfo("- Jointure de la table du reseau viaire sur le nouveau référentiel")
        params = {'DISCARD_NONMATCHING': False, 'FIELD': 'ID',
                  'FIELDS_TO_COPY': [], 'FIELD_2': 'ID',
                  'INPUT': new_ref, 'INPUT_2':tab_viaire, 'METHOD': 1, 'OUTPUT': 'memory:jointure',
                  'PREFIX': ''}
        jointure_1 = processing.run("native:joinattributestable", params, context=context, feedback=feedback)['OUTPUT']
        
        # Jointure de la table du reseau viaire sur les points qualites de la maj IGN
        feedback.pushInfo("- Jointure de la table du reseau viaire sur les points qualites de la maj IGN")
        params = {'DISCARD_NONMATCHING': False, 'FIELD': 'ID_3',
                  'FIELDS_TO_COPY': [], 'FIELD_2': 'ID',
                  'INPUT':pt_qualite, 'INPUT_2':tab_viaire, 'METHOD': 1, 'OUTPUT': 'memory:jointure',
                  'PREFIX': ''}
        jointure_2 = processing.run("native:joinattributestable", params, context=context, feedback=feedback)['OUTPUT']
    
        
        # _______________________Préparation de la table réseau viaire final
        feedback.pushInfo("*** Préparation de la table réseau viaire à jour ***")
        
        # Création d'une couche avec les correspondance point qualite et la table du reseau viaire
        feedback.pushInfo("- Création d'une couche avec les correspondance point qualite et la table du reseau viaire")
        join_match = jointure_1.setSubsetString('"ID_2" is not null')
        params = {'INPUT': jointure_1, 'OUTPUT': 'memory:join_match_ref', 'LAYER_NAME': 'join_match_ref',
                  'DATASOURCE_OPTIONS': '', 'LAYER_OPTIONS': ''}
        temp= processing.run("native:savefeatures", params, context=context, feedback=feedback)['OUTPUT']
        tab_viaire_temp=context.takeResultLayer(temp)
        
        # Création de la table réseau viaire à jour
        feedback.pushInfo("- Création de la table réseau viaire à jour")
        field_save = ['ID','CODE_GPE_PRECONISATION','CHANTIER_EN_COURS','DATE_MAJ_2']
        field_del =[]
        field_names = [field.name() for field in tab_viaire_temp.fields()]
        for f in field_names: # Suppression des champs inutiles pour la création de la nouvelle table
            if f not in field_save:
                field_del.append (f)
        del_fields (tab_viaire_temp,field_del) 
        rename_dp_field(tab_viaire_temp, 'DATE_MAJ_2', 'DATE_MAJ') # Rename du champ DAT_MAJ car il existe déjà dans avec les tronçons IGN
        tab_viaire_final = QgsVectorLayer('None', 'Tab_viaire_new', 'memory')
        CreateMemory(tab_viaire_temp, tab_viaire_final)
        
        # Création d'une couche avec les correspondance point qualite et la table du reseau viaire
        feedback.pushInfo("- Création d'une couche avec les correspondance point qualite et la table du reseau viaire")
        join_match = jointure_2.setSubsetString('"GID_2" is not null')
        params = {'INPUT': jointure_2, 'OUTPUT': 'memory:join_match', 'LAYER_NAME': 'join_match',
                  'DATASOURCE_OPTIONS': '', 'LAYER_OPTIONS': ''}
        temp_2= processing.run("native:savefeatures", params, context=context, feedback=feedback)['OUTPUT']
        tab_viaire_temp=context.takeResultLayer(temp_2)
        
        # Intgration des pertes dans la nouvelle table reseau viaire
        feedback.pushInfo("- Intgration des pertes dans la nouvelle table reseau viaire")
        field_save = ['ID','CODE_GPE_PRECONISATION','CHANTIER_EN_COURS','DATE_MAJ_3']
        field_del =[]
        field_names = [field.name() for field in tab_viaire_temp.fields()]
        for f in field_names: # Suppression des champs inutiles pour l'insertion dans la nouvelle table
            if f not in field_save:
                field_del.append (f)
        del_fields (tab_viaire_temp,field_del)
        rename_dp_field(tab_viaire_temp, 'DATE_MAJ_3', 'DATE_MAJ') # Rename du champ DAT_MAJ car il existe déjà dans avec les tronçons IGN
        ajout=0
        for elem in tab_viaire_temp.getFeatures():
            ajout+=1
            feat = QgsFeature()
            feat.setAttributes(elem.attributes())
            tab_viaire_final.dataProvider().addFeatures([feat])
            tab_viaire_final.updateExtents()
        feedback.pushInfo ('!!!!!!!!!!! RECUPERATION DES PERTES = {} !!!!!!!!!!!'.format(str(ajout)))
        
        # Output 1 du processing  : TEST
        output1 = self.parameterAsOutputLayer(parameters, self.OUTPUT_1, context)
        params = {'INPUT': tab_viaire_final, 'OUTPUT': output1, 'LAYER_NAME': 'TEST',
                  'DATASOURCE_OPTIONS': '', 'LAYER_OPTIONS': ''}
        layer_output1 = processing.run("native:savefeatures", params, context=context, feedback=feedback)['OUTPUT']
        
        return {self.OUTPUT_1: layer_output1}