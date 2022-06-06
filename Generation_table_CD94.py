# -*- coding: utf-8 -*-

"""
***************************************************************************
*                                                                         *
*   Cet outil met permet de générer la table CD94 à partir de la vu       *
*   Oracle V_BD_TOPO_ROUTE_94 du schéma NEXT_DIFF.
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
                       QgsDataSourceUri,
                       QgsCoordinateReferenceSystem,
                       QgsFeatureSource,
                       QgsFeatureRequest,
                       QgsProject,
                       QgsExpression,
                       QgsProcessingException,
                       QgsProcessingAlgorithm,
                       QgsProcessingParameterFeatureSource,
                       QgsProcessingParameterBoolean,
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
        return 'Generation_table_CD94'

    def displayName(self):
        """
        Returns the translated algorithm name, which should be used for any
        user-visible display of the algorithm name.
        """
        return self.tr('Generation_table_CD94')

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
        v1 = "\nCet outil génère la table CD94 à partir du référentiel routier V_BD_TOPO_ROUTE_94 de la vue oracle (NEXT_DIFF)"
        v2 = "\n!!!!! Si coché : un champ cd94 est rajouté dans la table et il codifié en 1 pour tous les tronçons. Il permet de mieux identifier les éléments joints  lors d'une jointure sur le référentiel routier !!!!!"
        return self.tr(v0+v1+v2)

    def initAlgorithm(self, config=None):
        """
        Here we define the inputs and output of the algorithm, along
        with some other properties.
        """
        '''
        # We add the input vector features source. It can have any kind of
        # geometry.
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.INPUT_1,
                self.tr('New référentiel IGN'),
                [QgsProcessing.TypeVectorAnyGeometry]
            )
        )
        '''
        '''
        # We add the input vector features source. It can have any kind of
        # geometry.
        self.addParameter(
            QgsProcessingParameterFeatureSource(
                self.INPUT_2,
                self.tr('Table CD94 actuelle'),
                [QgsProcessing.TypeFile]
            )
        )
        '''
        self.addParameter(
            QgsProcessingParameterBoolean(
                self.INPUT_1,
                self.tr('Ajout du champ cd94 dans la table ?'),
                optional=True,
                defaultValue=0
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
                self.tr('Table CD94')
            )
        )

    def processAlgorithm(self, parameters, context, feedback):

        # *******************Fonctions*********************************
        
        def LoadOracle (name,request,LoadProject):
            # Connexion Oracle
            uri= QgsDataSourceUri()
            uri.setConnection(server,port,BDD,
            utlisateur,mdp)# !!!! Remplacer pour le github public
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
        test = self.parameterAsBool(parameters, self.INPUT_1, context)
        if test == True :
            feedback.pushInfo("Ajout du champ cd94 coché")
        else :
            feedback.pushInfo("Ajout du champ cd94 décoché")
        feedback.pushInfo('**************************')
        ref = LoadOracle ("V_BD_TOPO_ROUTE_94","","no")
        feedback.pushInfo('INPUTS :')
        feedback.pushInfo(str(ref))

        
        feedback.pushInfo('**************************')
        # ************************ TRAITEMENTS
        feedback.pushInfo("------------DEBUT DES TRAITEMENTS------------")
        # _______________________Préparation de la table CD94
        feedback.pushInfo("- Création de la table CD94 actuelle")
        params = {'INPUT': ref, 'OUTPUT': 'memory: ref_copy'}
        run_memory = processing.run("native:savefeatures", params, context=context, feedback=feedback)['OUTPUT']
        ref_layer_modif = context.takeResultLayer(run_memory) 
 
        exp1 = "((\"CLASSEMENT\" in ('Autoroute','Nationale','Départementale','Départementale magistrale','Départementale principale','Départementale secondaire')) or"
        exp2 = "(\"INSEECOM_G\" like '94%' or \"INSEECOM_D\" like '94%') or"
        exp3 = "(\"INSEECOM_G\" in ('93051','77083','92007') or \"INSEECOM_D\" in ('93051','77083','92007')))"
        exp = exp1 + exp2 + exp3
        # Application de la selection dans la couche avec la requête du dessus (exp)
        selection = ref_layer_modif.selectByExpression(exp)
        select = ref_layer_modif.selectedFeatures()
        feedback.pushInfo (str(len(select)))
        
        # Paramètres du processing de sauvegarde la selection en une couche mémoire
        feedback.pushInfo("- Sauvegarde selection tronçon pour la table CD94")
        params = {
            'INPUT': ref_layer_modif,
            'OUTPUT': 'memory: selection cd94'}
        save_select = processing.run("native:saveselectedfeatures", params)
        tab_cd94 = save_select['OUTPUT']  # Variable pour appeler la couche
        
        list_add = ['ID']
        if test == True:
            list_add.append ('cd94')
            
        field_names = [field.name() for field in ref.fields()]
        index_add = field_names.index('CODE_ROUTE_VH_PRIORITE')
        for f in field_names :
            index = field_names.index(f)
            if index >= index_add:
                list_add.append(f)

        feedback.pushInfo("- Ecriture de la table CD94")
        if test == True:
            AddField (tab_cd94,'cd94',QVariant.Int)
            CalcField(tab_cd94, 'cd94', 1)
            
        fields_del = []
        field_names = [field.name() for field in tab_cd94.fields()]
        for f in field_names:
            if f not in list_add:
                fields_del.append (f)
        del_fields(tab_cd94, fields_del)
        
        # Output 4 : création de la table cd94 en csv
        tab_c94_memory = QgsVectorLayer('None', 'Tab_cd94', 'memory')
        CreateMemory(tab_cd94, tab_c94_memory)
        output1 = self.parameterAsOutputLayer(parameters, self.OUTPUT_1, context)
        params = {'INPUT': tab_c94_memory, 'OUTPUT': output1, 'LAYER_NAME': 'TABLE_CD94',
                  'DATASOURCE_OPTIONS': '', 'LAYER_OPTIONS': ''}
        layer_output1 = processing.run("native:savefeatures", params, context=context, feedback=feedback)['OUTPUT']

        return {self.OUTPUT_1: layer_output1}
