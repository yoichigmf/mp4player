# -*- coding: utf-8 -*-
"""
/***************************************************************************
 MP4player
                                 A QGIS plugin
 play MP4 movie with gps log
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                              -------------------
        begin                : 2022-03-12
        git sha              : $Format:%H$
        copyright            : (C) 2022 by Yoichi Kayama/aeroasahi corporation
        email                : yoichi.kayama@gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
from tracemalloc import start
from qgis.PyQt.QtCore import QSettings, QTranslator, QCoreApplication, QDateTime
from qgis.PyQt.QtGui import QIcon, QColor
from qgis.PyQt.QtWidgets import QAction
from qgis.core   import (QgsMapLayerProxyModel,QgsProject, QgsFeature, QgsPointXY,
    QgsFieldProxyModel, QgsProcessing,  QgsWkbTypes, QgsFeatureRequest, QgsProject,
    QgsCoordinateReferenceSystem,  QgsCoordinateTransform)

from qgis import processing

from qgis.gui  import QgsMapToolEmitPoint, QgsMapToolIdentifyFeature, QgsVertexMarker

from qgis.PyQt.QtCore import QDir, Qt, QUrl
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer
from PyQt5.QtMultimediaWidgets import QVideoWidget
from qgis.PyQt.QtWidgets import (QApplication, QFileDialog, QHBoxLayout, QLabel,
        QPushButton, QSizePolicy, QSlider, QStyle, QVBoxLayout, QWidget)
from qgis.PyQt.QtWidgets import QMainWindow,QWidget, QPushButton, QAction


# Initialize Qt resources from file resources.py
from .resources import *
# Import the code for the dialog
from .MP4player_dialog import MP4playerDialog
import os.path

from  .videowindow import VideoWindow



class MP4player:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """

        self.debug = True

        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'MP4player_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)
            QCoreApplication.installTranslator(self.translator)

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&MP4player')

        # Check if plugin was started the first time in current QGIS session
        # Must be set in initGui() to survive plugin reloads
        self.first_start = None

        self.Timelist = []



        self.canvas = iface.mapCanvas()


        self.mapToolIdent = QgsMapToolIdentifyFeature(self.canvas)
        #self.mapToolIdent.featureIdentified.connect(self.mapToolFeatureIdentified)
        #self.mapToolIdent.canvasClicked.connect(self.identmouseClick)


        self.toolexec = False
        self.identtoolexec= False
        
        self.loglayer = None  
        self.timefield = None
        self.mp4layer = None

        self.PointLogLayer = None

        self.TimeList = None

        self.StartTime = None
        self.EndTime = None

        self.lastx = None
        self.lasty = None

        self.lastPlotTime = None
        self.ploted = False

        self.last_vertex = None

        project = QgsProject.instance()
        project.crsChanged.connect(self.changecrs)


        self.transformcontext =  project.transformContext()

        self.projectcrs = project.crs()


    def changecrs(self):

        project = QgsProject.instance()
        self.projectcrs = project.crs()

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('MP4player', message)


    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            # Adds plugin icon to Plugins toolbar
            self.iface.addToolBarIcon(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/MP4player/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'動画再生'),
            callback=self.run,
            parent=self.iface.mainWindow())


        self.add_action(
            icon_path,
            text=self.tr(u'設定'),
            callback=self.runAdm,
            parent=self.iface.mainWindow())

        # will be set False in run()
        self.first_start = True
        self.admfirst_start = True

    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&MP4player'),
                action)
            self.iface.removeToolBarIcon(action)


    def select_layer( self, vlayer ):


        self.dlg.dateTimeComboBox.setLayer( vlayer )




 
    def mapToolEdit(self):
        #print("in edit")
        if self.identtoolexec:
            print("out edit")
            self.recoverIdentMaptool()
            #self.toolexec = False
            #self.canvas.setMapTool(self.previousMapTool)  # このツール実行前に戻す
        else:
            print("in edit")     
            self.identtoolexec= True
            self.previousIdentMapTool = self.canvas.mapTool() 

            #print( "layer " + self.mp4layer.name())
            #self.iface.setactivelayer
  
            self.mapToolIdent.featureIdentified.connect(self.mapToolFeatureIdentified)

            self.mapToolIdent.setLayer(self.mp4layer )
            #self.maptooIdent.canvasClicked.connect(self.identmouseClick)
            self.canvas.setMapTool( self.mapToolIdent )


    def  loadlayerinfo( self ):
        proj = QgsProject.instance()

        log_id = proj.readEntry("MP4Player",  
                                            "loglayer_id",
                                            None)

            #        proj.writeEntry("MP4Player", "loglayer_id", self.loglayer_id)
            #proj.writeEntry("MP4Player", "timefield", self.timefield)
            #proj.writeEntry("MP4Player", "mp4layer_id", self.mp4layer_id )


        if log_id is not None:
            print( log_id )
            self.loglayer_id= log_id[0]
            self.loglayer = proj.mapLayer(self.loglayer_id)

        mp4_id = proj.readEntry("MP4Player",  
                                            "mp4layer_id",
                                            None)

        if mp4_id is not None:
                print( mp4_id )
                self.mp4layer_id= mp4_id[0]
                self.mp4layer  = proj.mapLayer(self.mp4layer_id)       


        time_field_l  = proj.readEntry("MP4Player",  
                                            "timefield",
                                            None)

        if time_field_l is not None:
            self.timefield = time_field_l[0]       

    def runAdm(self):
        if self.admfirst_start== True:
            self.admfirst_start= False   

            self.loglayer = None  
            self.timefield = None
            self.mp4layer = None

            self.loadlayerinfo()
        


            self.dlg = MP4playerDialog()
            self.dlg.logLayerComboBox.setFilters(QgsMapLayerProxyModel.PointLayer)

            self.dlg.logLayerComboBox.layerChanged.connect(self.select_layer)

            self.dlg.mp4LayerComboBox.setFilters(QgsMapLayerProxyModel.PointLayer) 

            self.dlg.dateTimeComboBox.setFilters(QgsFieldProxyModel.DateTime) 

        if self.loglayer is not None:

            try:

                self.dlg.logLayerComboBox.setLayer(self.loglayer)
            except:
                self.loglayer = None

            #self.configdlg.mMapLayerHenjyo.setLayer(self.marklayer )

        if self.timefield  is not None:
            try:
                self.dlg.dateTimeComboBox.setField( self.timefield  )
            except:
                self.timefield = None
      
            #print(" log1")

        if self.mp4layer is not None:
            try:
                self.dlg.mp4LayerComboBox.setLayer(self.mp4layer) 
            except:
                self.mp4layer = None
        
        # show the dialog
        self.dlg.show()
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:
            # Do something useful here - delete the line containing pass and
            # substitute with your code.

            self.loglayer = self.dlg.logLayerComboBox.currentLayer()
            self.loglayer_id = self.loglayer.id()

            self.timefield = self.dlg.dateTimeComboBox.currentField()

            self.mp4layer = self.dlg.mp4LayerComboBox.currentLayer()

            self.mp4layer_id = self.mp4layer.id()
            proj = QgsProject.instance()

            proj.writeEntry("MP4Player", "loglayer_id", self.loglayer_id)
            proj.writeEntry("MP4Player", "timefield", self.timefield)
            proj.writeEntry("MP4Player", "mp4layer_id", self.mp4layer_id )

            #print( self.loglayer )

            #print( self.loglayer.id() )

            #pass
    def recoverIdentMaptool( self ):

        self.identtoolexec = False
        self.mapToolIdent.featureIdentified.disconnect(self.mapToolFeatureIdentified)
        self.canvas.setMapTool(self.previousIdentMapTool )  # このツール実行前に戻す


    def mapToolFeatureIdentified(self, feature):

        print("ident in")
        qfeature = QgsFeature(feature)


        
        #print( qfeature)

        tgfname = qfeature["filename"]

        print( tgfname )

        self.playfilename = tgfname

        self.starttime = qfeature["filetime"]
        self.logtime =   qfeature["logtime"]
        self.vsec  =  qfeature["vsec"]

        self.framecount = qfeature["frame_count"]
        self.fps = qfeature["fps"]



        self.recoverIdentMaptool()


        fmt ="yyyy-MM-dd HH:mm:ss"

        startTime  = QDateTime.fromString(self.starttime , fmt )

        ofmt = "yyyy/MM/dd HH:mm:ss"
        start_str = startTime.toString(ofmt)

        endTime = startTime.addSecs( self.vsec )

        end_str  = endTime.toString(ofmt)

        print("start "+ start_str)
        print("end "+ end_str)

     



        self.vdlg.setFile( tgfname )

        self.SetPointLog( startTime, endTime)


        self.vdlg.play()


    #  経過時刻で移動ポイントを更新する
    def  upDateMovePoint( self, ctinfo, ctstr ):

        print( "upfdate =" + ctstr )

        ctime = self.StartTime.addMSecs( ctinfo.msecsSinceStartOfDay() )
        ofmt = "yyyy/MM/dd HH:mm:ss"
        ntime = ctime.toString( ofmt )
        print( "now =" + ntime )

        #  前回のプロット時刻と同じ時刻の場合処理しない
        if self.lastPlotTime is not None:
            if ctime == self.lastPlotTime:
                return

        # 一番時刻がちかい点を探す
        prec = self.SerchNealistTimeRec( ctime )

        if  prec is None:
            return

        print( "find = " + prec["time"].toString(ofmt) + " x " + str(prec["x"]) + " y " + str(prec["y"])) 

        self.lastPlotTime = prec["time"]
        self.ploted = True
        self.lastx = prec["x"]
        self.lasty = prec["y"]

        if self.last_vertex is not None:
                self.iface.mapCanvas().scene().removeItem(self.last_vertex  )

        self.last_vertex = QgsVertexMarker(self.iface.mapCanvas())
        self.last_vertex.setIconType(QgsVertexMarker.ICON_CROSS)
        self.last_vertex.setColor(QColor(255,0, 0)) #(R,G,B)
        self.last_vertex.setIconSize(20)
        #self.last_vertex.setIconType(QgsVertexMarker.ICON_X)
        self.last_vertex.setPenWidth(3)

        crsDest =  self.projectcrs
        transformContext = self.transformcontext

        crsSrc = QgsCoordinateReferenceSystem("EPSG:4326")  
        xform = QgsCoordinateTransform(crsSrc, crsDest, transformContext)

        pt1 = xform.transform(QgsPointXY(self.lastx,self.lasty))
        self.last_vertex.setCenter(QgsPointXY(pt1 ))


        
    def SerchNealistTimeRec( self, ctime ):

        if self.TimeList is None:
            return None


        if  self.EndTime  < self.TimeList[0]["time"]:
                return
            
        tgrec = self.TimeList[0]
        tdiff = abs( ctime.toMSecsSinceEpoch()  - tgrec["time"].toMSecsSinceEpoch() )

        for  nrec in self.TimeList:

            if  self.EndTime  < nrec["time"]:
                break

            ndiff = abs( ctime.toMSecsSinceEpoch() - nrec["time"].toMSecsSinceEpoch())
            if ndiff < tdiff:
                tdiff = ndiff
                tgrec = nrec

        return tgrec

    def  SetPointLog( self, starttime, endtime ):

        #print( "set point log")


        #inputstr = 'C:\\work\\gpx2\\TrackLog_2021_06_11.gpkg|layername=TrackLog_2021_06_11'
        expstr =  '(\"DateTimeG\" <= to_datetime( \'2021/06/11 01:19:13\', \'yyyy/MM/dd HH:mm:ss\')) and (\"DateTimeG\" >= to_datetime( \'2021/06/11 01:17:50\', \'yyyy/MM/dd HH:mm:ss\'))'
        expstr =  '\"DateTimeG\" <= to_datetime( \'2021/06/11 01:19:13\', \'yyyy/MM/dd HH:mm:ss\')'
        # and (\"DateTimeG\" >= to_datetime( \'2021/06/11 01:17:50\', \'yyyy/MM/dd HH:mm:ss\'))'

        #print( inputstr )
        #print(expstr)

        ofmt = "yyyy/MM/dd HH:mm:ss"
        ststring = starttime.toString(ofmt)

        #expstr2 =  '\"DateTimeG\" >= to_datetime( \'2021/06/11 01:17:50\', \'yyyy/MM/dd HH:mm:ss\')'

        tgt_field = self.timefield 
        tglayer = self.loglayer 

        expstr2 =  '\"' + tgt_field + '\" >= to_datetime( \'' + ststring +'\', \'yyyy/MM/dd HH:mm:ss\')'

        result = processing.run("qgis:extractbyexpression", {'INPUT': tglayer,
              'EXPRESSION': expstr2,
              'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT})
        #print( inputstr )
        print(expstr)

        result1_layer = result['OUTPUT']

        #expstr2 =  '\"DateTimeG\" >= to_datetime( \'2021/06/11 01:17:50\', \'yyyy/MM/dd HH:mm:ss\')'



        #param2 ={'INPUT': result1_layer,
        #      'EXPRESSION': expstr,
        #      'OUTPUT': QgsProcessing.TEMPORARY_OUTPUT}
        
        #result2 = processing.run("qgis:extractbyexpression", param2,is_child_algorithm=True)

        self.PointLogLayer = result1_layer

        self.createTimeList( self.PointLogLayer, tgt_field, starttime, endtime )

        self.StartTime = starttime
        self.EndTime = endtime


        #print(result2['OUTPUT'])
        #QgsProject.instance().addMapLayer(self.PointLogLayer)
        #if self.debug:
            #QgsProject.instance().addMapLayer(result1_layer )

    def  createTimeList( self, tgLayer, tgt_field, starttime, endtime ):
        
        retarray = []
        
        #print(tgField)
    
        #features = source.getFeatures()

        request=QgsFeatureRequest().addOrderBy(tgt_field)
        

        for  feature in tgLayer.getFeatures(request):
            tgTime = feature[tgt_field]
            
            #print(type(tgTime) )
              #   型判定
            #if isinstance(tgTime, str):
                  #print( tgTime )
             #     if  tgTime =='0:00:00':
                         #print("continue")
              #           continue
                         
              #    dt = datetime.datetime.strptime(tgTime, '%Y/%m/%d %H:%M:%S')
              #    file_update_unix_time = dt.timestamp()
            #else:
            
                  #file_update_unix_time = tgTime.toSecsSinceEpoch()
                 # dt = datetime.datetime.fromtimestamp(file_update_unix_time)
            #print(tgTime.toSecsSinceEpoch())
            #print( dt )
 
            geom = feature.geometry()
          #  print(QgsWkbTypes.displayString(geom.wkbType()))             マルチポイントとかの場合の対応が必要
            if geom.wkbType() == QgsWkbTypes.Point or geom.wkbType() == QgsWkbTypes.PointZ or geom.wkbType() == QgsWkbTypes.Point25D  :
                  #print("point ")
                  
                  ptg =  geom.asPoint();
                  
                  pt = {"time": tgTime, "x": ptg.x(), "y": ptg.y(), "geom": geom}
                  
                  retarray.append( pt );
            
        
            # Stop the algorithm if cancel button has been clicked
           # if feedback.isCanceled():
           #     break

        self.TimeList = retarray
    
        #return retarray


    def  identmouseClick(self, currentPos, clickedButton ):

        if clickedButton == QtCore.Qt.LeftButton: 
            print('左クリック!' + str(QgsPointXY(currentPos)))

            
            #getmeshID(qgis.core.QgsPointXY(currentPos).y(), qgis.core.QgsPointXY(currentPos).x())
            self.recoverIdentMaptool()

            #self.insertNewRec(QgsPointXY(currentPos))

        if clickedButton == QtCore.Qt.RightButton:
            print('右クリック!' + str(QgsPointXY(currentPos)))
            self.recoverIdentMaptool()        


    def run(self):
        """Run method that performs all the real work"""

        # Create the dialog with elements (after translation) and keep reference
        # Only create GUI ONCE in callback, so that it will only load when the plugin is started
        if self.first_start == True:
            self.first_start = False

            self.vdlg = VideoWindow()
            self.vdlg.setModel( self )
            self.vdlg.setWindowFlags(Qt.WindowStaysOnTopHint)
            self.vdlg.resize(640, 480)
            #self.initVideo()

        self.loadlayerinfo()

        # show the dialog
        self.vdlg.show()
        # Run the dialog event loop
        #result = self.vdlg.exec_()
        # See if OK was pressed
        #if result:
            # Do something useful here - delete the line containing pass and
            # substitute with your code.
        #    pass
