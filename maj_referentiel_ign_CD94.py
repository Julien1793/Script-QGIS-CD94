# -*- coding: utf-8 -*-

"""
***************************************************************************
*                                                                         *
*   Cet outil met à jour la table CD94 qui est associée au référentiel    *
*   routier IGN. La table est mise à jour automatiquement en établissant  *
*   un contrôle qualité. Certains tronçons sont mis jour de manière forcée*
*   (qualité 2 et 3) et d'autres (cas très rares) sont à mettre à jour    *
*   manuellement (qualité 4).                                             *
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
    OUTPUT_2 = 'OUTPUT_2'
    OUTPUT_3 = 'OUTPUT_3'
    OUTPUT_4 = 'OUTPUT_4'

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
        return 'maj_referentiel_ign'

    def displayName(self):
        """
        Returns the translated algorithm name, which should be used for any
        user-visible display of the algorithm name.
        """
        return self.tr('maj_referentiel_ign')

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
        v1 = "\n Ce script identifie le delta entre le référentiel IGN actuel et le nouveau. Il met à jour les pertes de la table CD94."
        v2 = "\n Un champ qualité_maj est ajouté en sortie (dans point qualité et table cd94 à jour),il permet de contrôler le résultat des mises à jour:"
        v3 = "\n - qualité 1= un tronçon a été trouvé"
        v4 = "\n - qualité 2= Aucun tronçon trouvé => valeurs forcées agglo en oui et RGC en non (Sentier ou Escalier ou Chemin ou Piste cyclable)"
        v5 = "\n - qualité 3= Aucun tronçon trouvé => valeurs forcées agglo en oui et RGC en non (route chaussée et empierrée)"
        v6 = "\n - qualité 4= Aucun tronçon trouvé => mise à jour automatique impossible : opération manuelle obligatoire (concerne les RD,RN et Autoroutes)"
        return self.tr(v0 + v1 + v2 + v3 + v4 + v5 + v6)

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
        self.addParameter(
            QgsProcessingParameterVectorDestination(
                self.OUTPUT_1,
                self.tr('Tronçons perte jointure (nouveau référentiel)')
            )
        )

        self.addParameter(
            QgsProcessingParameterVectorDestination(
                self.OUTPUT_2,
                self.tr('Tronçons perte jointure (référentiel actuel)')
            )
        )

        self.addParameter(
            QgsProcessingParameterVectorDestination(
                self.OUTPUT_3,
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
                self.OUTPUT_4,
                self.tr('Table CD94 à jour')
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
        new_ref = self.parameterAsLayer(parameters, self.INPUT_1, context)
        ##tab_cd94 = self.parameterAsLayer(parameters, self.INPUT_2, context)
        ref_old_layer = self.parameterAsLayer(parameters, self.INPUT_3, context)
        feedback.pushInfo('INPUTS :')
        feedback.pushInfo(str(new_ref))
        feedback.pushInfo(str(ref_old_layer))

        feedback.pushInfo('Chargement des données :')
        '''
        new_ref       = InputToQgslayer (new_ref_temp)
        tab_cd94      = InputToQgslayer (tab_cd94_temp)
        ref_old_layer = InputToQgslayer (ref_old)
        '''
        # Véréfication des couhces et encade utf8 (nex ref et tab cd94)
        list = [new_ref, ref_old_layer]
        for layer in list:
            if layer.isValid():
                feedback.pushInfo(layer.name() + ' chargé')
                if layer != ref_old_layer:
                    layer.setProviderEncoding('utf8')
                    mycrs = QgsCoordinateReferenceSystem(2154)
                    layer.setProviderEncoding('utf8')
                    feedback.pushInfo('\t- => crs : 2154')
                    feedback.pushInfo('\t- => encodage utf-8')
            else:
                feedback.reportError(layer.name() + " probleme chargement !!!")
                sys.exit()

        feedback.pushInfo('**************************')
        # ************************ TRAITEMENTS
        feedback.pushInfo("------------DEBUT DES TRAITEMENTS------------")
        # _______________________Préparation de la table CD94
        feedback.pushInfo("0- Création de la table CD94 actuelle")
        params = {'INPUT': ref_old_layer, 'OUTPUT': 'memory: ref_old_copy'}
        run_memory = processing.run("native:savefeatures", params, context=context, feedback=feedback)['OUTPUT']
        ref_old_layer_modif = context.takeResultLayer(run_memory) 
 
        exp1 = "((\"CLASSEMENT\" in ('Autoroute','Nationale','Départementale','Départementale magistrale','Départementale principale','Départementale secondaire')) or"
        exp2 = "(\"INSEECOM_G\" like '94%' or \"INSEECOM_D\" like '94%') or"
        exp3 = "(\"INSEECOM_G\" in ('93051','77083','92007') or \"INSEECOM_D\" in ('93051','77083','92007')))"
        exp = exp1 + exp2 + exp3
        # Application de la selection dans la couche avec la requête du dessus (exp)
        selection = ref_old_layer_modif.selectByExpression(exp)
        select = ref_old_layer_modif.selectedFeatures()
        feedback.pushInfo (str(len(select)))
        
        # Paramètres du processing de sauvegarde la selection en une couche mémoire
        feedback.pushInfo("\t- Sauvegarde selection tronçon pour la table CD94")
        params = {
            'INPUT': ref_old_layer_modif,
            'OUTPUT': 'memory: selection cd94'}
        save_select = processing.run("native:saveselectedfeatures", params)
        tab_cd94 = save_select['OUTPUT']  # Variable pour appeler la couche
        
        list_add = ['ID','cd94']
        field_names = [field.name() for field in ref_old_layer.fields()]
        index_add = field_names.index('CODE_ROUTE_VH_PRIORITE')
        for f in field_names :
            index = field_names.index(f)
            if index >= index_add:
                list_add.append(f)

        feedback.pushInfo("\t- Ecriture de la table CD94")
        AddField (tab_cd94,'cd94',QVariant.Int)
        CalcField(tab_cd94, 'cd94', 1)
        fields_del = []
        field_names = [field.name() for field in tab_cd94.fields()]
        for f in field_names:
            if f not in list_add:
                fields_del.append (f)
        del_fields(tab_cd94, fields_del)
        
        # _______________________Recalcul des champs rue null en ''
        feedback.pushInfo("1- Création d'une copie en mémoire du référentiel actuel")
        feedback.pushInfo("\t- Recalcul des champs nom de rue dans la copie du référentiel actuel")
        exp1 = "NOM_1_D"
        exp2 = "NOM_1_G"
        ref_old_layer_modif.startEditing()
        for c in [exp1, exp2]:
            exp = '"{}" is null'.format(c)
            feedback.pushInfo("\t - calcule sur :{}".format(exp))
            for row in ref_old_layer_modif.getFeatures(exp):
                idx_id = ref_old_layer_modif.fields().lookupField(c)
                new_rue = ''
                ref_old_layer_modif.changeAttributeValue(row.id(), idx_id, new_rue)
        ref_old_layer_modif.commitChanges()


        # _______________________Jointure table CD94 sur new ref
        feedback.pushInfo("2- Création des jointures")
        feedback.pushInfo("\t- Création jointure table cd94 sur nouveau référentiel")
        # Jointure Table CD94 sur new référentiel
        params = {'DISCARD_NONMATCHING': False, 'FIELD': 'id',
                  'FIELDS_TO_COPY': [], 'FIELD_2': 'id',
                  'INPUT': new_ref, 'INPUT_2': tab_cd94, 'METHOD': 1, 'OUTPUT': 'memory:jointure',
                  'PREFIX': ''}
        jointure = processing.run("native:joinattributestable", params, context=context, feedback=feedback)['OUTPUT']
        # Jointure Table CD94 sur référentiel actuel
        feedback.pushInfo("\t- Création jointure nouveau référentiel sur référentiel actuel")
        params = {'DISCARD_NONMATCHING': False, 'FIELD': 'ID',
                  'FIELDS_TO_COPY': [], 'FIELD_2': 'id',
                  'INPUT': ref_old_layer, 'INPUT_2': new_ref, 'METHOD': 1, 'OUTPUT': 'memory:jointure',
                  'PREFIX': ''}
        jointure_2 = processing.run("native:joinattributestable", params, context=context, feedback=feedback)['OUTPUT']


        # _______________________Selection des RD du CD94 sans jointure
        feedback.pushInfo("3- Selection des RD du CD94 sans jointure")
        # -------- Création de la requête pour selectionner les tronçon à maj qui
        #          ont perdu la jointure de la table CD94
        # Requête pour selectionner les tronçon qui ont perdu la jointure (new ref)
        # (changement ID tronçon IGN)
        exp1 = "((\"cl_admin\" in ('Autoroute','Départementale','Nationale')) or"
        exp2 = "(\"inseecom_g\" like '94%' or \"inseecom_d\" like '94%') or"
        exp3 = "(\"inseecom_g\" in ('93051','77083','92007') or \"inseecom_d\" in ('93051','77083','92007'))) and"
        exp4 = "(\"cd94\" is null)"
        exp = exp1 + exp2 + exp3 + exp4
        # Application de la selection dans la couche avec la requête du dessus (exp)
        selection = jointure.selectByExpression(exp)
        layer = jointure.selectedFeatures()

        # Affichage le nombre de tronçon à mettre à jour (perte jointure table cd94)
        feedback.pushInfo("\t- Pertes ancien ref sur new ref = {}".format(len(layer)))
        # Paramètres du processing de sauvegarde la selection en une couche mémoire
        feedback.pushInfo("\t- Création couche perte jointure (nouveau référentiel)")
        params = {
            'INPUT': jointure,
            'OUTPUT': 'memory: tronons sans jointure'}
        save_select = processing.run("native:saveselectedfeatures", params)
        out_select = save_select['OUTPUT']  # Variable pour appeler la couche

        feedback.pushInfo("\t- Recalcul des champs rue, ,numero nature dans les tronçons sans jointure")
        exp1 = "NOM_1_D"
        exp2 = "NOM_1_G"
        exp3 = "NUMERO"
        exp4 = "NATURE"
        out_select.startEditing()
        for c in [exp1, exp2, exp3, exp4]:
            exp = '"{}" is null'.format(c)
            for row in out_select.getFeatures(exp):
                idx_id = out_select.fields().lookupField(c)
                new_attri = ''
                out_select.changeAttributeValue(row.id(), idx_id, new_attri)
        out_select.commitChanges()

        # Output 1 du processing  : Tronçons perte jointure (new référentiel)
        output1 = self.parameterAsOutputLayer(parameters, self.OUTPUT_1, context)
        params = {'INPUT': out_select, 'OUTPUT': output1, 'LAYER_NAME': 'Tronçons perte jointure (nouveau référentiel)',
                  'DATASOURCE_OPTIONS': '', 'LAYER_OPTIONS': ''}
        layer_output1 = processing.run("native:savefeatures", params, context=context, feedback=feedback)['OUTPUT']

        # Requête pour selectionner les tronçon qui ont perdu la jointure (référentiel actuel)
        feedback.pushInfo("\t- Création couche perte jointure (référentiel actuel)")
        exp_old = '\"id_2\" is null and \"LIB_ROUTE_GESTION_CD94\" = \'Val-de-Marne\''
        filter_old = jointure_2.setSubsetString(exp_old)
        # Output 2 du processing  : Tronçons perte jointure (référentiel actuel)
        output2 = self.parameterAsOutputLayer(parameters, self.OUTPUT_2, context)
        params = {'INPUT': jointure_2, 'OUTPUT': output2, 'LAYER_NAME': 'Tronçons perte jointure (référentiel actuel)',
                  'DATASOURCE_OPTIONS': '', 'LAYER_OPTIONS': ''}
        layer_output2 = processing.run("native:savefeatures", params, context=context, feedback=feedback)['OUTPUT']

        # _______________________Génération point longueur/2 sur la selection
        feedback.pushInfo("4- Génération des points au centre des tronçons")

        # Création de la couche en mémoire pour accueillir les points
        temp = QgsVectorLayer("Point?crs=epsg:2154", "point_milieu_troncon", "memory")
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
        feedback.pushInfo("\t - Ajout du champ qualie_maj")
        field_quali = 'qualite_maj'
        new_field = QgsField(field_quali, QVariant.Int)
        temp_prov.addAttributes([new_field])
        temp.updateFields()
        # Ecriture dans la donnée temp créée au dessus (points au centre des tronçons)
        temp.commitChanges()

        # _______________________Projection des points sur l'ancien référentiel
        #                       (tentative de récupération des attributs CD94)
        feedback.pushInfo("5- Récupération attributs CD94")
        # -------- Création de la couche en mémoire pour accueillir les points projetés
        # Création des liste des tronçons à filtrer (rd,rn, autoroute)
        list_rd_temp = [i['numero'] for i in temp.getFeatures()]
        list_rd = []
        for i in list_rd_temp:
            if i not in list_rd and i != '':
                list_rd.append(i)  # Récupération des numéro de route de façon unique
        feedback.pushInfo(str(list_rd))
        # Création de la liste des route autres à filtrer (nom de rue + nature)
        list_other = []
        for i in temp.getFeatures():
            if i['numero'] == '':
                r_g = i['nom_1_g']  # Récupération du nom de rue gauche
                r_d = i['nom_1_d']  # Récupération du nom de rue droite
                nature = i['nature']  # Récupération de la nature du tronçon
                txt = r_g + ',' + r_d + ',' + nature
                attri = txt.split(',')  # création de la sous liste des attributs
                if attri not in list_other:
                    list_other.append(attri)  # ajout de la sous liste dans la liste
        total = len(list_other)

        # Boucle dans les deux listes créées précédemment
        creation_temp_2 = 0
        list_join = []
        for t in ['rd nat aut', 'other']:
            # Projection des points sur les RD, RN et Autoroutes sur l'ancien referentiel
            if t == 'rd nat aut':
                feedback.pushInfo('\t- Maj sur rd,rn,auto')
                for rd in list_rd:
                    creation_temp_2 += 1
                    # Création des filtres pour projeté le point sur le même numero de route
                    feedback.pushInfo("\t\t- {}".format(rd))
                    exp1 = '"NUMERO_ROUTE"= \'{}\''.format(rd)
                    exp2 = '"numero"= \'{}\''.format(rd)
                    filter_1 = ref_old_layer_modif.setSubsetString(exp1)
                    filter_2 = temp.selectByExpression(exp2)
                    temp.selectedFeatures()
                    params = {
                        'INPUT': temp,
                        'OUTPUT': 'memory: projection'}
                    select_temp = processing.run("native:saveselectedfeatures", params)[
                        'OUTPUT']  # Variable pour appeler la couche
                    ##filter_2 = temp.setSubsetString(exp2)
                    # Pojection des points sur les tronçons correspondant (numéro de route)
                    params = {'INPUT': select_temp, 'INPUT_2': ref_old_layer_modif,
                              'FIELDS_TO_COPY': [], 'DISCARD_NONMATCHING': False,
                              'PREFIX': '', 'NEIGHBORS': 1, 'MAX_DISTANCE': 20, 'OUTPUT': 'TEMPORARY_OUTPUT'}
                    process_join_nearest = processing.run("native:joinbynearest", params)
                    join_nearest = process_join_nearest['OUTPUT']
                    feedback.pushInfo(str(exp2))
                    ##len_ref_old = len([feature for feature in ref_old_layer_modif.getFeatures()])
                    ##len_temp = len([feature for feature in temp.getFeatures()])
                    ##feedback.pushInfo ("nb points projetés : "+str(len_temp ))
                    ##feedback.pushInfo (str(process_join_nearest['JOINED_COUNT']))
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
                    ##sys.exit()
            # Projection des points type voirie autre sur l'ancien referentiel
            if t == 'other':
                feedback.pushInfo('\t- Maj sur reste des routes')
                # Remplacement des guillemets (') par une double guillemet ('') pour les filtres
                u = 1
                for o in list_other:
                    feedback.pushInfo('\t\t=> {}/{}'.format(u, total))
                    u += 1
                    step = 0
                    for e in o:
                        if "'" in e:
                            o[step] = e.replace("'", "''")
                        step += 1
                    # Création des filtres pour projeté le point sur l'ancien référentiel
                    # avec les mêmes nom de rue (g et d) et la même nature
                    exp1 = '("NUMERO_ROUTE" is null or "NUMERO_ROUTE" = \'NC\') and "NOM_1_G"= \'{}\' and "NOM_1_D"= \'{}\' and "CODE_ROUTE_NATURE" = \'{}\''.format(
                        o[0], o[1], o[2])
                    exp2 = '"numero" = \'\' and "nom_1_g"= \'{}\' and "nom_1_d"= \'{}\' and "nature" = \'{}\''.format(
                        o[0], o[1], o[2])
                    filter_1 = ref_old_layer_modif.setSubsetString(exp1)
                    filter_2 = temp.selectByExpression(exp2)
                    temp.selectedFeatures()
                    params = {
                        'INPUT': temp,
                        'OUTPUT': 'memory: projection'}
                    select_temp = processing.run("native:saveselectedfeatures", params)[
                        'OUTPUT']  # Variable pour appeler la couche
                    # Pojection des points sur les tronçons correspondant (nom de rue gauche et droite + nature du tronçon)
                    params = {'INPUT': select_temp, 'INPUT_2': ref_old_layer_modif,
                              'FIELDS_TO_COPY': [], 'DISCARD_NONMATCHING': False,
                              'PREFIX': '', 'NEIGHBORS': 1, 'MAX_DISTANCE': 20, 'OUTPUT': 'TEMPORARY_OUTPUT'}
                    process_join_nearest = processing.run("native:joinbynearest", params)
                    join_nearest = process_join_nearest[
                        'OUTPUT']  # résultat du point jointure par attribut le plus proche
                    feedback.pushInfo(str(exp2))
                    ##feedback.pushInfo (str(process_join_nearest['JOINED_COUNT']))
                    ##                  if 'ECOLE' in o[0]:
                    ##                      break
                    # Ecriture dans la donnée temporaire (jointure par attribut le plus proche)
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

        # -------- Contrôle de la qualité des jointures par attaribut le plus proche
        # Ajout du champ contrôle de qualité
        feedback.pushInfo("6- Calcul des champs agglo, rgc et qualite maj")
        field_names = [field.name() for field in temp_2.fields()]
        cur = 0
        for f in field_names:
            feedback.pushInfo("{} id : {}".format(f, cur))
            cur += 1
        # Edition de la couche jointure par attribut le plus proche
        temp_2.startEditing()
        rows = temp_2.getFeatures()
        list_nature = ['Sentier', 'Escalier', 'Chemin', 'Piste cyclable']
        # Boucle dans la donnée pour renseigner le nouveau champ contrôle de qualité
        for row in rows:
            id_tr = row['id_3']
            cd94 = row['cd94']
            numero = row['numero']
            agglo = row['agglo_2']
            rgc = row['rgc_2010_2']
            nature = row['nature']
            quali = row[field_quali]
            idx_id_1 = temp_2.fields().lookupField(field_quali)
            idx_id_2 = temp_2.fields().lookupField('rgc_2010_2')
            idx_id_3 = temp_2.fields().lookupField('agglo_2')
            idx_id_4 = temp_2.fields().lookupField('cd94')
            # Un un tronçon correspondant a été trouvé
            if id_tr != None:
                cd94_att = 1
                new_att = 1
                ##feedback.pushInfo (str(idx_id_1))
                temp_2.changeAttributeValue(row.id(), idx_id_1, new_att)
                temp_2.changeAttributeValue(row.id(), idx_id_4, cd94_att)
            # Aucun tronçon type autre n'a été trouvé mais il s'agit de chemin, sentier, pc ou escalier
            # Les valeurs rgc est forcée en 'Non' et agglo en 'Oui'
            if id_tr == None and nature in list_nature and numero == '':
                quali_att = 2
                rgc_att = 'Non'
                agglo_att = 'Oui'
                cd94_att = 1
                ##feedback.pushInfo (str(idx_id_1))
                temp_2.changeAttributeValue(row.id(), idx_id_1, quali_att)
                temp_2.changeAttributeValue(row.id(), idx_id_2, rgc_att)
                temp_2.changeAttributeValue(row.id(), idx_id_3, agglo_att)
                temp_2.changeAttributeValue(row.id(), idx_id_4, cd94_att)
            # Aucun tronçon type autre n'a été trouvé et les aveurs sont quand même forcées
            # rgc en 'Non' et agglo en 'Oui'
            if id_tr == None and nature not in list_nature and numero == '':
                quali_att = 3
                rgc_att = 'Non'
                agglo_att = 'Oui'
                cd94_att = 1
                ##feedback.pushInfo (str(idx_id_1))
                temp_2.changeAttributeValue(row.id(), idx_id_1, quali_att)
                temp_2.changeAttributeValue(row.id(), idx_id_2, rgc_att)
                temp_2.changeAttributeValue(row.id(), idx_id_3, agglo_att)
                temp_2.changeAttributeValue(row.id(), idx_id_4, cd94_att)
            # Aucun tronçon type RD, RN, NAT ou Autoroute n'a été trouvé
            # Les attributs doivent être renseignés manuellement
            if numero != '' and id_tr == None:
                quali_att = 4
                cd94_att = 1
                temp_2.changeAttributeValue(row.id(), idx_id_1, quali_att)
                temp_2.changeAttributeValue(row.id(), idx_id_4, cd94_att)
        feedback.pushInfo("id qualite_maj =" + str(idx_id_1))
        # Cloture de l'édition
        temp_2.commitChanges()
        
        # Output 3 du processing  : Point qualité mise  à jour
        output3 = self.parameterAsOutputLayer(parameters, self.OUTPUT_3, context)
        params = {'INPUT': temp_2, 'OUTPUT': output3, 'LAYER_NAME': 'Point qualité mise  à jour',
                  'DATASOURCE_OPTIONS': '', 'LAYER_OPTIONS': ''}
        layer_output3 = processing.run("native:savefeatures", params, context=context, feedback=feedback)['OUTPUT']

        # -------- Récupération des nouveaux attributs dans la table cd94
        feedback.pushInfo("7- Récupération des nouveaux attributs dans la nouvelle table CD94")
        # Suppression de la selection sur la couche join_layers
        jointure.removeSelection()
        
        # Création de la liste de champ à joindre issue des projections
        fields_cd94 = [field.name() for field in tab_cd94.fields()]
        fields_join = []
        fields_join.append('cd94')
        fields_join.append(field_quali)  # Ajout manuel du champ qualite rajouté précédemment
        for f in fields_cd94:
            if f != 'ID' and f != 'ogc_fid' and f != 'cd94':
                new = f.upper() + '_2'
                fields_join.append(new)
        feedback.pushInfo(str(fields_join))
        feedback.pushInfo("- Jointure des projection sur le new ref")

        # Jointure des champs issue de la projection sur le new ref
        params = {'DISCARD_NONMATCHING': False, 'FIELD': 'ID',
                  'FIELDS_TO_COPY': fields_join, 'FIELD_2': 'id',
                  'INPUT': jointure, 'INPUT_2': temp_2, 'METHOD': 1, 'OUTPUT': 'memory: new_ref_x_cd_94_final',
                  'PREFIX': ''}
        jointure_2 = processing.run("native:joinattributestable", params)
        join_layers_final = jointure_2['OUTPUT']  # résultat de la jointure
        
        # Écriture des champs joins dans la table cd94 du new ref
        join_layers_final.startEditing()
        feedback.pushInfo("- Ecriture des attributs des projections sur la table cd94 du new ref")
        # Sélection des tronnçon doivent être mis à jour
        req = QgsFeatureRequest().setFilterExpression('"qualite_maj" is not null')
        rows = join_layers_final.getFeatures(req)  # applciation requete pour la boucle

        # Ecriture des mises à jour dans la future table cd94
        for row in rows:
            for f in fields_cd94:
                if f != 'id' and f != 'ID' and f != 'ogc_fid':  # Evite de reecrire dans les champs id (tronçon) et ogc_fid
                    idx_id = join_layers_final.fields().lookupField(f)
                    attri = row[f + '_2']
                    join_layers_final.changeAttributeValue(row.id(), idx_id, attri)
        join_layers_final.commitChanges()# Cloture de l'edtion sur la couche join_layers_final

        # Suppression des champs joins (excepté quali_maj)
        feedback.pushInfo("- Suppression des champs joins (excepté quali_maj)")
        del_fields = []
        field_ids = []
        for d in fields_join:
            if d != field_quali and d != 'cd94':
                del_fields.append(d)
        for field in join_layers_final.fields():
            if field.name() in del_fields:
                field_ids.append(join_layers_final.dataProvider().fieldNameIndex(field.name()))
        join_layers_final.dataProvider().deleteAttributes(field_ids)
        join_layers_final.updateFields()
        feedback.pushInfo("- champs supprimés de la jointure : " + str(del_fields))


        # Transformation de la donnée géographique join_layers_final en table cd94 (csv)
        feedback.pushInfo("- Creation de la table cd94 finale en csv")
        # Selection des tronçons que la DTVD est censé maintenir à jour
        exp_final = '"cd94" is not null'
        filter_tab_cd94 = join_layers_final.setSubsetString(exp_final)
        # Suppression de tous les champs qui ne font pas partie de la table cd94 d'origine
        fields_cd94.append(field_quali)
        field_id_del = []
        del_fields_ign = []
        for field in join_layers_final.fields():
            name = field.name()
            if name not in fields_cd94 and name != 'ID' and name != 'id':
                field_id_del.append(join_layers_final.dataProvider().fieldNameIndex(field.name()))
                del_fields_ign.append(name)
        join_layers_final.dataProvider().deleteAttributes(field_id_del)
        join_layers_final.updateFields()
        feedback.pushInfo("- champs IGN supprimés : " + str(del_fields_ign))
        
        # Création de la table cd94
        # Output 4 : création de la table cd94 en csv
        tab_c94_memory = QgsVectorLayer('None', 'Tab_cd94_new', 'memory')
        CreateMemory(join_layers_final, tab_c94_memory)
        output4 = self.parameterAsOutputLayer(parameters, self.OUTPUT_4, context)
        params = {'INPUT': tab_c94_memory, 'OUTPUT': output4, 'LAYER_NAME': 'TABLE_CD94_new',
                  'DATASOURCE_OPTIONS': '', 'LAYER_OPTIONS': ''}
        layer_output4 = processing.run("native:savefeatures", params, context=context, feedback=feedback)['OUTPUT']
        
        return {self.OUTPUT_1: layer_output1,self.OUTPUT_2: layer_output2,self.OUTPUT_3: layer_output3,self.OUTPUT_4: layer_output4}

