#!/usr/bin/env python3
"""Plotting tool for EPICS PVs, ADO and LITE parameters.
"""
__version__ = 'v0.4.1 2023-03-16'# Using qtpy, Compliant with liteserver 2.0.0

#TODO: add_curves is not correct for multiple curves
#TODO: move Add Dataset to Dataset options
#TODO: if docks are stripcharts then zooming should be synchronized
#TODO: add dataset arithmetics

import sys, time, os
import numpy as np
from timeit import default_timer as timer
from qtpy import QtWidgets as QW, QtGui, QtCore
from qtpy.QtWidgets import QApplication, QMainWindow, QGridLayout
#, QFileDialog
import pyqtgraph as pg
from pyqtgraph.graphicsItems.ViewBox.ViewBoxMenu import ViewBoxMenu
from pyqtgraph import dockarea
from functools import partial

#````````````````````````````Globals``````````````````````````````````````````
MaxCurvesPerPlot = 10
gMapOfDocks = {}
pargs = None
gMapOfPlotWidgets = {}

# the --zoom should be handled prior to QtWidgets.QApplication
for i,argv in enumerate(sys.argv):
    if argv.startswith('-z'):
        zoom = argv[2:]
        if zoom == '':
            zoom = sys.argv[i+1]
        print(f'zoom: `{zoom}`')
        os.environ["QT_SCALE_FACTOR"] = zoom
        break
qApp = QApplication([])

gTimer = QtCore.QTimer()
gWin = QMainWindow()
gArea = dockarea.DockArea()
X,Y = 0,1
Scale,Units = 0,1
gScaleUnits = [[1,'Sample'],[1,'Count']]
subscribedParMap = {}
# temporary globals
#gTimestamp = True # option for plot title timestamping
gPerfmon = False # option for performance monitoring
programStartTime = time.time()
#,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,
#````````````````````````````Helper methods```````````````````````````````````
def printTime(): return time.strftime("%m%d:%H%M%S")
def printi(msg): print((f'INF_PP@{printTime()}: '+msg))
def printw(msg): print((f'WRN_PP@{printTime()}: '+msg))
def printe(msg): print((f'ERR_PP@{printTime()}: '+msg))
def _printv(msg, level=0):
    if pargs.verbose is None:
        return
    if len(pargs.verbose) >= level:
        print((f'DBG{level}_PP@{printTime()}: '+msg))
def printv(msg):   _printv(msg, 0)
def printvv(msg):  _printv(msg, 1)

def croppedText(txt, limit=200):
    if len(txt) > limit:
        txt = txt[:limit]+'...'
    return txt
def prettyDict(rDict, lineLimit=75):
    r=''
    for dev,devVals in rDict.items():
        r += dev+'\n'
        for par, parVals in devVals.items():
            r += '  '+par+':'
            if isinstance(parVals,dict):
                r += '\n'
                for attr, attrVal in parVals.items():
                    r += croppedText(f'    {attr}: {attrVal}',lineLimit)+'\n'
            else:
                r += croppedText(f' {parVals}',lineLimit)+'\n'
    return r

try:    from cad_io import epicsAccess_caproto as EPICSAccess
except:
    EPICSAccess = None 
    printw('EPICS devices are not supported on this host')
try:
    #from cad_io.liteAccess import Access as LITEAccess
    #try:
    #    from liteserver import liteAccess
    #except:
    #    printe(f'The github module liteserver is not available, trying to import local module liteserv')
    #    from liteserv import liteAccess
    import liteaccess as liteAccess 
    LITEAccess = liteAccess.Access
except Exception as e:
    printw(f'LITE devices are not supported on this host: {e}')
    LITEAccess = None
try:    
    from cad_io import adoaccess
    ADOAccess = adoaccess.IORequest()
except Exception as e:
    printw(f'ADO devices are not supported on this host: {e}')
    ADOAccess = None

def cprint(msg): 
    #gWidgetConsole.write('#'+msg+'\n')
    print('cprint:'+msg)

gAccess = {'E:':(EPICSAccess,2), 'L:':(LITEAccess,2)}
def get_pv(adopar:str, prop='value'):
    #printvv(f'>get_pv {adopar}')
    adopar, vslice = split_slice(adopar)
    access = gAccess.get(adopar[:2], (ADOAccess,0))
    access,prefixLength = gAccess.get(adopar[:2], (ADOAccess,0))
    if access is None:
        printe(f'No access metod for {adopar}')
        sys.exit(1)
    try:
        pvTuple = tuple(adopar[prefixLength:].rsplit(':',1))
        rd = access.get(pvTuple)[pvTuple]
        #print(f'rd:{val}')
        val = rd['value']
        try:
            shape = val.shape
            if len(shape) > 2:
                printe(f'2+dimensional arrays not supported for {dev,par}')
                return None
        except:
            # val does not have attribute shape
            pass
        try:
            ts = rd['timestamp']# EPICS and LITE
        except: # ADO
            ts = rd['timestampSeconds'] + rd['timestampNanoSeconds']*1.e-9
        
        #printv(f"get_pv {adopar}: {rd['value']} {vslice}")
        if vslice is not None:
            val = val[vslice[0]:vslice[1]]
        return val, ts
    except Exception as e:
        printe(f'Cannot get({pvTuple}): {e}')
        #sys.exit(1)
        return None

def change_plotOption(curveName,color=None,width=None,symbolSize=None,scolor=None):
    printv('change_plotOption color,width,size,color: '+str((color,width,symbolSize,scolor)))
    dataset = MapOfDatasets.dtsDict[curveName]
    if color != None:
        prop = 'color'
        dataset.pen.setColor(color)
    if width != None:
        prop = 'width'
        dataset.width = width
        dataset.pen.setWidth(width)
    elif symbolSize!=None:
        dataset.symbolSize = symbolSize
    elif scolor!=None:
        dataset.symbolBrush = scolor
    else: return
    try:
        dataset.plotItem.setPen(
          dataset.pen)
    except: cprint('could not set '+prop+' for '+str(curveName))

def split_slice(parNameSlice):
    """Decode 'name[n1:n2]' to 'name',[n1:n2]"""
    devParSlice = parNameSlice.split('[',1)
    if len(devParSlice) < 2:
        return devParSlice[0], None
    sliceStr = devParSlice[1].replace(']','')
    vrange = sliceStr.split(':',1)
    r0 = int(vrange[0])
    if len(vrange) == 1:
        vslice = (r0, r0+1)
    else:
        vslice = (r0, int(vrange[1]))
    #print(f'vslice: {vslice}')
    return devParSlice[0], vslice
#,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,

def new_dock(dataset):
    docks = [x.split('.')[0] for x in MapOfDatasets.dtsDict]
    i = 0
    while '#'+str(i) in docks: i += 1
    v = '#'+str(i)+' '+dataset
    printv('adding plot: '+str(v))

def close_dock(dname):
    '''remove datasets and curves and close the dock widget'''
    print('closing dock '+dname)
    for curveName in MapOfDatasets.dtsDict.keys():
        printv('looking: '+curveName)
        dock = curveName.split('.')[0]
        if dock == dname:
            printv('removing: '+curveName)
            MapOfDatasets.remove(curveName)
    printv('MapOfDatasets.dtsDict: '+str(MapOfDatasets.dtsDict))
    gMapOfDocks[dname].close()
    del gMapOfPlotWidgets[dname]

def update_data():
    ''' called on QtCore.QTimer() event to update plots.'''
    tstart = timer()
    for curveName,dataset in MapOfDatasets.dtsDict.items():
        curvePars = dataset.adoPars
        #printvv(f'dataset: {curvePars}')#: {dataset.data}')
        dock = curveName.split('.')[0]
        yd,ts = None,None
        try:
            yd, ts = get_pv(curvePars[0][0])
        except Exception as e:
            #printv('got '+str((yd,ts))+', from:'+str(curvePars[0][0])+', except:'+str(e))
            printw(f'Exception getting {curvePars[0][0]}: {e}')
            continue
        if ts:
            if ts == dataset.timestamp:
                printv('curve '+curveName+'did not change')
                continue
            else:
                dataset.timestamp = ts
            # if gTimestamp:
                # # update the timestamp only for primary curve
                # if '.' not in curveName:
                    # if tstart - dataset.timestampReported > 0.99:
                        # txt = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(ts))
                        # dataset.plotWidget.setTitle(txt+'\t'+curvePars[0][0])
                        # dataset.timestampReported = tstart
        try:    
            l = len(yd)
            if l == 1: yd = yd[0]
        except: 
            l = 1
            
        #if isinstance(yd,(list,tuple,np.ndarray)):
        if l > 1:
            # array plot
            y = np.array(yd)
            x = np.arange(len(yd))*gScaleUnits[X][Scale]
        else: # scrolling or correlation plot
            ptr = dataset.dataPtr
            dataset.data[0][ptr] = yd
            if len(curvePars) > 1: 
                #printv(f'correlation plot: {curvePars[1][0]}')
                try:
                    v,*_ = get_pv(curvePars[1][0])
                    try:    v = v[0]
                    except: pass 
                    dataset.data[1][ptr] = v
                except Exception as e:
                    printe('no data from '+str(curvePars[1][0]))
            else:
                # scrolling plot with time scale
                dataset.data[1][ptr] = ts
            ptr += 1
            dataset.dataPtr = ptr
            #printv(f'ptr: {ptr,dataset.data[0].shape[0]}')
            if ptr >= dataset.data[0].shape[0]:
                tmp = dataset.data
                dataset.data = [np.empty(dataset.data[0].shape[0] * 2),
                    np.empty(dataset.data[0].shape[0] * 2)]
                dataset.data[0][:tmp[0].shape[0]] = tmp[0]
                dataset.data[1][:tmp[1].shape[0]] = tmp[1]
                print(f'adjust x from {tmp[1].shape} to {dataset.data[1].shape}')
            x = dataset.data[1][:ptr]
            y = dataset.data[0][:ptr]
        #print(f'symbolSize: {curveName,dataset.symbol,dataset.symbolSize}')
        pen = dataset.pen if dataset.width else None
        #printvv(f'x:{x}\ny:{y}')
        dataset.plotItem.setData(x=x, y=y,
            pen = pen,
            #TODO:connect = dataset.connect,
            #TODO:shadowPen = dataset.shadowPen,
            #TODO:fillLevel = dataset.fillLevel,
            #TODO:fillBrush = dataset.fillBrush,
            #TODO:stepMode = dataset.stepMode,
            symbol = dataset.symbol,
            #TODO:symbolPen = dataset.symbolPen,
            symbolPen = None,
            symbolBrush = dataset.symbolBrush,
            #TODO:symbolBrush = dataset.pen.color(),
            symbolSize = dataset.symbolSize,
            #TODO:pxMode = dataset.pxMode,
        )
    if gPerfmon:
        v = timer()-tstart
        print('update time:'+str(timer()-tstart))

gLegend = {}# unfortunately we have to keep track of legends
def set_legend(dockName:str, state:bool):
    if state: # legend enabled
        printv('add legend for '+str(dockName))
        widget = gMapOfPlotWidgets[dockName]
        listOfItems = widget.getPlotItem().listDataItems()
        l = pg.LegendItem((100,60), offset=(70,30))  # args are (size, offset)
        l.setParentItem(widget.graphicsItem())
        gLegend[dockName] = l
        '''# it should be a better way to iterate for curves in the widget
        for curveName,dataset in MapOfDatasets.dtsDict.items():
            if dockName in curveName:
                printv('set_legend: '+curveName)
                l.addItem(dataset.plotItem, curveName)'''
        for item in listOfItems:
            iname = item.name()
            txt = MapOfDatasets.dtsDict[iname].adoPars[0][0]
            # show only parameter name
            ltxt = txt.rsplit(':',1)[-1]
            if '[' in txt:
               ltxt = ':'.join(txt.rsplit(':',2)[-2:])
            printv('set_legend: '+iname+' par: '+ltxt)
            l.addItem(item, ltxt)
    else: # legend disabled
        printv('remove legend from '+dockName)
        try:    
            gLegend[dockName].scene().removeItem(gLegend[dockName])
            del gLegend[dockName]
        except Exception as e:
            printe('failed to remove legend '+dockName+':'+str(e))
#,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,
#```````````````````````````DateAxis class: time scale for bottom plot scale``
class DateAxis(pg.AxisItem):
    def tickStrings(self, values, scale, spacing):
        strns = []
        if len(values) == 0: 
            return ''
        rng = max(values)-min(values)
        #if rng < 120:
        #    return pg.AxisItem.tickStrings(self, values, scale, spacing)
        if rng < 3600*24:
            string = '%H:%M:%S'
        elif rng >= 3600*24 and rng < 3600*24*30:
            string = '%d'
        elif rng >= 3600*24*30 and rng < 3600*24*30*24:
            string = '%b'
        elif rng >=3600*24*30*24:
            string = '%Y'
        for x in values:
            try:
                strns.append(time.strftime(string, time.localtime(x)))
            except ValueError:  ## Windows can't handle dates before 1970
                strns.append('')
        return strns
#,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,
#````````````````````````````Datasets`````````````````````````````````````````
class Dataset():
    ''' dataset storage, keeps everything what is necessary to plot the curve.
    '''
    def __init__(self,name,paramAndCount):
        self.name = name
        self.adoPars = paramAndCount # list of max 2 of (adoPar,count)
        self.plotItem = None # plotting object PlotDataItem
        self.pen = None # current pen
        self.width = 1 # pen width
        self.timestamp = 0 # latest timestamp
        self.timestampReported = 0 # time of the last title update
        self.plotWidget = None
        self.viewBox = None
        
        # plotting options, described in 
        # http://www.pyqtgraph.org/documentation/graphicsItems/plotdataitem.html#pyqtgraph.PlotDataItem
        self.connect = None
        self.shadowPen = None
        self.fillLevel = None
        self.fillBrush = None
        self.stepMode = None
        self.symbol = None
        self.symbolPen = None
        self.symbolBrush = None
        self.symbolSize = None
        self.pxMode = None

        # ``````````````````` Add plotItem ``````````````````````````````````````
        dock = name.split('.')[0]
        printv('plotItem for: '+str([s for s in self.adoPars])+', name:'+str(dock))
        ScrolLength = 10
        self.data = [np.empty(ScrolLength),np.empty(ScrolLength)]# [X,U] data storage
        self.dataPtr = 0
        count = self.adoPars[0][1] #
        print(f'adoPars,count: {self.adoPars,count}')

        # create plotItem with proper pen
        lineNumber = 0
        try: lineNumber = int(name.split('.')[1])
        except: pass
        isCorrelationPlot = len(self.adoPars) == 2
        self.pen = pg.mkPen(lineNumber)                
        if self.adoPars[0][0] == '':
            printv('no dataset - no plotItem')
        else:
            self.plotItem = pg.PlotDataItem(name=name, pen=self.pen)
            #self.plotItem = pg.PlotCurveItem(name=name, pen=self.pen)
        
        # assign the plotwidget if it exist, if not, create new dock and widget
        if dock in gMapOfPlotWidgets:
            self.plotWidget = gMapOfPlotWidgets[dock]
        else:
            self.viewBox = CustomViewBox(name=dock)
            self.viewBox.setMouseMode(self.viewBox.RectMode)
            printv('adding plotwidget:'+dock)
            #title = self.adoPars[0][0]
            title = None
            if count == 1 and not isCorrelationPlot:
                self.plotWidget = pg.PlotWidget(title=title, viewBox=self.viewBox,
                  axisItems={'bottom':DateAxis(orientation='bottom')})
                if dock != '#0':
                	self.plotWidget.setXLink(gMapOfPlotWidgets['#0'])
            else: 
                self.plotWidget = pg.PlotWidget(title=title, viewBox=self.viewBox)
            #self.plotWidget.showGrid(True,True)
            gMapOfPlotWidgets[dock] = self.plotWidget
            gMapOfDocks[dock].addWidget(self.plotWidget)
            if isCorrelationPlot:                        
                self.plotWidget.setLabel('bottom',self.adoPars[1][0])
            elif count == 1:
                self.plotWidget.setLabel('bottom','time', units='date', unitPrefix='')
            else:
                self.plotWidget.setLabel('bottom',gScaleUnits[X][Units])

        rangeMap = {X: (pargs.xrange, self.plotWidget.setXRange),
                    Y: (pargs.yrange, self.plotWidget.setYRange)}
        for axis,v in rangeMap.items():
            r,func = v
            if r is None:
                continue
            r = [float(i) for i in v[0].split(':')]
            func(*r)

        if self.plotItem:
            self.plotWidget.addItem(self.plotItem)
            self.viewBox.sigRangeChangedManually.connect(self.xrangeChanged)

        self.timestamp = 0.

    def __str__(self):
        return f'Dataset {self.name}, x: {self.data[1].shape}'

    def xrangeChanged(self):
        #self.viewBox.enableAutoRange(axis='x', enable=0.1)
        print(f'viewRange: {self.viewBox.viewRange()[X]}')

class MapOfDatasets():
    '''Global dictionary of Datasets, provides safe methods to add and remove 
    the datasets '''
    dtsDict = {}
    
    def add(name, adoPars):
        '''add new datasets, the adoPars is the space delimited string of 
        source ado:parameters.'''
        if name in MapOfDatasets.dtsDict:
            printv('Need to remove '+name)
            MapOfDatasets.remove(name)
        printv('MapOfDatasets.add '+str((name, adoPars)))
        for i, token in enumerate(adoPars.split()):
            token = pargs.ado+token
            dname = f'{name}.{i}'
            pnameAndCount = [];
            alist = token.split(',')
            alist = alist[:2] # we cannot handle more than 2 curves in correlation plot
            if len(alist) == 0:
                MapOfDatasets.dtsDict[dname] = Dataset(dname,[('',0)])
                print(f'added dataset {str(MapOfDatasets.dtsDict[dname])}')
            else:
                alist.reverse()
                for adoPar in alist:
                    try:
                        val,ts = get_pv(adoPar) # check if parameter is alive
                    #if val is None:
                    #    return 1
                    except Exception as e:
                        printw(f'could not get parameter {adoPar}: {e}')
                        return 1
                    newName = adoPar
                    try:    count = len(val)
                    except: count = 1
                    pnameAndCount.append((newName,count))
                #printv('adding '+str(pnameAndCount)+' to datasets['+dname+']')
                MapOfDatasets.dtsDict[dname] = Dataset(dname,pnameAndCount)
        printv(f'MapOfDatasets: {[(k,v.name) for k,v in  MapOfDatasets.dtsDict.items()]}')
        return 0
    
    def remove(name):
        printv('MapOfDatasets.remove '+name)
        dataset = MapOfDatasets.dtsDict[name]
        dataset.plotWidget.removeItem(dataset.plotItem)
        del MapOfDatasets.dtsDict[dataset.name]
#,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,
#'''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
class CustomViewBox(pg.ViewBox):
    ''' defines actions, activated on the right mouse click in the dock
    '''
    def __init__(self, **kwds):
        self.dockName = kwds['name'] # cannot use name due to an issue in demo
        del kwds['name'] # the name in ViewBox.init fails in demo
        printv('CustomViewBox: '+str(self.dockName)+', '+str(kwds))

        # call the init method of the parent class
        super(CustomViewBox, self).__init__()
        # the above is equivalent to:#pg.ViewBox.__init__(self, **kwds)

        # IMPORTANT: menu creation is deferred because it is expensive 
        # and often the user will never see the menu anyway.
        self.menu = None
        self.cursors = set()
           
    #v32#def mouseClickEvent(self, ev) removed, due to blank exports

    def raiseContextMenu(self, ev):
        # Let the scene add on to the end of our context menu
        menuIn = self.getContextMenus()        
        menu = self.scene().addParentContextMenus(self, menuIn, ev)
        menu.popup(ev.screenPos().toPoint())
        return True

    def getContextMenus(self, event=None):
        ''' This method will be called when this item's children want to raise
        a context menu that includes their parents' menus.
        '''
        if self.menu:
            printv('menu exist')
            return self.menu
        printv('getContextMenus for '+str(self.dockName))
        self.menu = ViewBoxMenu(self)
        self.menu.setTitle(str(self.dockName)+ " options..")

        # reset zoom
        #resetzoom = self.menu.addAction("&Reset Zoom")
        #resetzoom.triggered.connect(lambda: self.autoRange())

        # Datasets options dialog
        setDatasets = self.menu.addAction('Datasets &Options')
        setDatasets.triggered.connect(self.changed_datasetOptions)

        cursorMenu = self.menu.addMenu('Add Cursor')
        for cursor in ['Vertical','Horizontal']:
            action = cursorMenu.addAction(cursor)
            action.triggered.connect(partial(self.cursorAction,cursor))
        
        labelX = QW.QWidgetAction(self.menu)
        self.labelXGui = QW.QLineEdit('LabelX')
        self.labelXGui.returnPressed.connect(
            lambda: self.set_label('bottom',self.labelXGui))
        labelX.setDefaultWidget(self.labelXGui)
        self.menu.addAction(labelX)
        labelY = QW.QWidgetAction(self.menu)
        self.labelYGui = QW.QLineEdit('LabelY')
        self.labelYGui.returnPressed.connect(
            lambda: self.set_label('left',self.labelYGui))
        labelY.setDefaultWidget(self.labelYGui)
        self.menu.addAction(labelY)
                   
        backgroundAction = QW.QWidgetAction(self.menu)
        backgroundGui = QW.QCheckBox('&Black background')
        backgroundGui.stateChanged.connect(
          lambda x: self.setBackgroundColor(\
          'k' if x == QtCore.Qt.Checked else 'w'))
        backgroundAction.setDefaultWidget(backgroundGui)
        self.menu.addAction(backgroundAction)

        legenAction = QW.QWidgetAction(self.menu)
        legendGui = QW.QCheckBox('&Legend')
        legendGui.setChecked(True)
        legendGui.stateChanged.connect(lambda x: self.set_legend(x))
        legenAction.setDefaultWidget(legendGui)
        self.menu.addAction(legenAction)
        
        runAction = QW.QWidgetAction(self.menu)
        runWidget = QW.QCheckBox('&Run')
        runWidget.setChecked(True)
        runWidget.stateChanged.connect(lambda x: self.set_run(x))
        runAction.setDefaultWidget(runWidget)
        self.menu.addAction(runAction)
        
        sleepTimeMenu = self.menu.addMenu('&SleepTime')
        sleepTimeAction = QW.QWidgetAction(sleepTimeMenu)
        sleepTimeWidget = QW.QDoubleSpinBox()
        sleepTimeWidget.setValue(pargs.sleepTime)
        sleepTimeWidget.setRange(0.001,100)
        sleepTimeWidget.setSuffix(' s')
        sleepTimeWidget.setSingleStep(.1)
        sleepTimeWidget.valueChanged.connect(lambda x: self.set_sleepTime(x))
        sleepTimeAction.setDefaultWidget(sleepTimeWidget)
        sleepTimeMenu.addAction(sleepTimeAction)
        return self.menu

    def cursorAction(self, direction):
        angle = {'Vertical':90, 'Horizontal':0}[direction]
        pwidget = gMapOfPlotWidgets[self.dockName]
        vid = {'Vertical':0, 'Horizontal':1}[direction]
        vr = pwidget.getPlotItem().viewRange()
        #print(f'vid: {vid,vr[vid]}')
        pos = (vr[vid][1] + vr[vid][0])/2.
        pen = pg.mkPen(color='b', width=1, style=QtCore.Qt.DotLine)
        cursor = pg.InfiniteLine(pos=pos, pen=pen, movable=True, angle=angle
        , label=str(round(pos,3)))
        cursor.sigPositionChangeFinished.connect(\
        (partial(self.cursorPositionChanged,cursor)))
        self.cursors.add(cursor)
        pwidget.addItem(cursor)

    def cursorPositionChanged(self, cursor):
        pos = cursor.value()
        horizontal = cursor.angle == 0.
        pwidget = gMapOfPlotWidgets[self.dockName]
        viewRange = pwidget.getPlotItem().viewRange()[horizontal]
        if pos > viewRange[1]:
            pwidget.removeItem(cursor)
            self.cursors.remove(cursor)
        else:
            cursor.label.setText(str(round(pos,3)))

    def changed_datasetOptions(self):
        '''Dialog Plotting Options'''
        dlg = QW.QDialog()
        dlg.setWindowTitle("Dataset plotting config")
        dlg.setWindowModality(QtCore.Qt.ApplicationModal)
        dlgSize = 500,200
        dlg.setMinimumSize(*dlgSize)
        rowCount,columnCount = 0,6
        tbl = QW.QTableWidget(rowCount, columnCount, dlg)
        tbl.setHorizontalHeaderLabels(['Dataset','Color','Width','Symbol','Size','Color'])
        for column,width in ((1,30),(3,50),(5,30)): # change column widths
            tbl.setColumnWidth(column, width)
        tbl.setShowGrid(False)
        tbl.setSizeAdjustPolicy(
            QW.QAbstractScrollArea.AdjustToContents)
        tbl.resize(*dlgSize)

        listOfItems = gMapOfPlotWidgets[self.dockName].getPlotItem().listDataItems()
        for row,dataitem in enumerate(listOfItems):
            tbl.insertRow(row)
            curveName = dataitem.name()
            printv(f'curveName:{curveName}')
            dataset = MapOfDatasets.dtsDict[curveName]
            adoparName = dataset.adoPars[0][0]
            printv(f'dataset:{adoparName}')
            item = QW.QTableWidgetItem(adoparName.rsplit(':',1)[1])
            #DNW#item.setTextAlignment(QtCore.Qt.AlignRight)
            tbl.setItem(row, 0, item)

            # color button for line
            colorButton = pg.ColorButton(color=MapOfDatasets.dtsDict[curveName].pen.color())
            colorButton.setObjectName(curveName)
            colorButton.sigColorChanging.connect(lambda x:
              change_plotOption(str(self.sender().objectName()),color=x.color()))
            tbl.setCellWidget(row, 1, colorButton)

            # slider for changing the line width
            widthSlider = QW.QSlider()
            widthSlider.setObjectName(curveName)
            widthSlider.setOrientation(QtCore.Qt.Horizontal)
            widthSlider.setMaximum(10)
            widthSlider.setValue(1)
            widthSlider.valueChanged.connect(lambda x:
              change_plotOption(str(self.sender().objectName()),width=x))
            tbl.setCellWidget(row, 2, widthSlider)
            
            # symbol, selected from a comboBox
            self.symbol = QW.QComboBox() # TODO: why self?
            for symbol in ' ostd+x': self.symbol.addItem(symbol)
            self.symbol.setObjectName(curveName)
            self.symbol.currentIndexChanged.connect(self.set_symbol)
            tbl.setCellWidget(row, 3, self.symbol)

            # slider for changing the line width
            symbolSizeSlider = QW.QSlider()
            symbolSizeSlider.setObjectName(curveName)
            symbolSizeSlider.setOrientation(QtCore.Qt.Horizontal)
            symbolSizeSlider.setMaximum(10)
            symbolSizeSlider.setValue(1)
            symbolSizeSlider.valueChanged.connect(lambda x:
              change_plotOption(str(self.sender().objectName()),symbolSize=x))
            tbl.setCellWidget(row, 4, symbolSizeSlider)

            # color button for symbol
            symbolColorButton = pg.ColorButton(color=MapOfDatasets.dtsDict[curveName].pen.color())
            symbolColorButton.setObjectName(curveName)
            symbolColorButton.sigColorChanging.connect(lambda x:
              change_plotOption(str(self.sender().objectName()),scolor=x.color()))
            tbl.setCellWidget(row, 5,symbolColorButton)
        dlg.exec_()

    def set_symbol(self, x):
        ''' Change symbol of the scatter plot. The size and color are taken
        from the curve setting'''
        dtsetName = str(self.sender().objectName())
        symbol = str(self.sender().itemText(x))
        printv('set_symbol for '+dtsetName+' to '+symbol)
        dataset = MapOfDatasets.dtsDict[dtsetName]
        if symbol != ' ':
            dataset.symbol = symbol
            if not dataset.symbolSize:
                dataset.symbolSize = 4 # default size
            if not dataset.symbolBrush:
                dataset.symbolBrush = dataset.pen.color() # symbol color = line color
        else:
            # no symbols - remove the scatter plot
            dataset.symbol = None
            pass
            
    def set_label(self,side,labelGui):
        dock,label = self.dockName,str(labelGui.text())
        printv('changed_label '+side+': '+str((dock,label)))
        gMapOfPlotWidgets[dock].setLabel(side,label, units='')
        # it might be useful to return the prompt back:
        #labelGui.setText('LabelX' if side=='bottom' else 'LabelY')

    def set_legend(self, state):
        state = (state==QtCore.Qt.Checked)
        print(f'set_legend {state}')
        set_legend(self.dockName, state)

    def set_run(self, state):
        if state == QtCore.Qt.Checked:
            gTimer.start(int(pargs.sleepTime*1000))
        else:
            gTimer.stop()    

    def set_sleepTime(self, itemData):
        #print('setting SleepTime to: '+str(itemData))
        pargs.sleepTime = itemData
        gTimer.stop()
        gTimer.start(int(pargs.sleepTime*1000))

#,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,

def callback(args):
    #print(f'cb: {args}')
    for hostDev, pardict in args.items():
        for par in pardict:
            try:
                axis,units = subscribedParMap[(hostDev,par)]
            except:
                continue
            scale = pardict[par]['value'][0]
            print(f'axis={axis}, units={units}, scale={scale}')
            gScaleUnits[axis][Scale] = scale

def add_curves(dock:str, adopars:str):        
    # if dock name is new then create new dock, otherwise extend the 
    # existing one with new curve
    
    #print('adding plot '+str(dock))
    curves = [x for x in MapOfDatasets.dtsDict]
    docks = [x.split('.')[0] for x in curves]
    #printv(f'curves,docks:{curves,docks}')
    if dock in docks:
        #print('extending dock '+str(dock))
        for i in range(MaxCurvesPerPlot):
            newSlot = dock+'.'+str(i+1)
            if newSlot not in curves: break
        dock = newSlot
        #print(f'adding new curve {dock}')
    else:
        #print('adding new plot '+dock)
        gMapOfDocks[dock] = dockarea.Dock(dock, size=(500,200), hideTitle=True)
        if dock == '#0':
            gArea.addDock(gMapOfDocks[dock], 'right', closable=True)
        else:
            gArea.addDock(gMapOfDocks[dock], 
              'top', gMapOfDocks['#0'], closable=True) #TODO:closable does not work
    if MapOfDatasets.add(dock, adopars):
            printe('in add_curves: '+str((dock, adopars)))
    #printv(f'datasets:{MapOfDatasets.dtsDict.keys()}')
                        
def main():
    import argparse
    global pargs
    parser = argparse.ArgumentParser(description=__doc__
    ,formatter_class=argparse.ArgumentDefaultsHelpFormatter
    ,epilog=(f'pvplot: {__version__}'))
    parser.add_argument('-a', '--ado', default='', help=\
      'Default Device/ADO name. Useful for plotting parameters from single device.')
    parser.add_argument('-s', '--sleepTime', type=float, default=1,
      help='sleep time between data delivery [s]')
    parser.add_argument('-v', '--verbose', nargs='*', help=\
      'Show more log messages (-vv: show even more).')
    parser.add_argument('-x', '--xscale', help=\
     'Parameter, which provides dynamic scale for X-axis')
    parser.add_argument('-X', '--xrange', help=\
     'Fixed range of X axis, e.g: -x10:20')
    parser.add_argument('-y', '--yscale', help=\
     'Parameter, which provides dynamic scale for Y-axis')
    parser.add_argument('-Y', '--yrange', help=\
     'Fixed range of Y axis, e.g: -y1000:4095')
    parser.add_argument('-z', '--zoomin', help=\
      'Zoom the application window by a factor')
    parser.add_argument('-#','--dock', action='append', nargs='*', 
      help='''plot the ADO parameter in a specified dock, i.e: to plot the 
        scrolling plot in dock#1 and correlation plot in dock#2:
        -#0simple.test:sinM  -#1simple.test:degM,simple.test:sinM ''')
    parser.add_argument('parms', nargs = '?',#nargs='*',
      default='simple.test:sinM am_simple.0:sinM simple.test:degM',
      help='''String with space-separated parameters, e.g.
      'simple.test:sinM am_simple.0:sinM simple.test:degM' ''')
    pargs = parser.parse_args()
    #print(f'pargs:{pargs}')
    if pargs.ado != '':
       pargs.ado += ':'

    #``````````````arrange keyboard interrupt to kill the program
    import signal
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    #````````````````````````````Initialize Gui```````````````````````````````````
    gWin.setCentralWidget(gArea)
    gWin.resize(1000,500)
    gWin.setWindowTitle(f'pvplot {pargs.parms}')
    ## Switch to using white background and black foreground
    pg.setConfigOption('background', 'w')
    pg.setConfigOption('foreground', 'k')
    layout = QGridLayout()
 
    # Subscriptions. Only LITE system is supported.
    if pargs.xscale is not None:
        hostDev,par = (pargs.ado[2:-1],pargs.xscale)
        print(f'subscribing: {hostDev,par}')
        info = LITEAccess.info((hostDev,par))
        print(f'info of {hostDev,par}: {info}')
        units = info[par]['units']
        gScaleUnits[X] = [info[par]['value'][0], units]
        LITEAccess.subscribe(callback, (hostDev,par))
        subscribedParMap[(hostDev,par)] = [X, units]
    print(f'SubParMap: {subscribedParMap}')

    # plots for other docks
    if pargs.dock:
        #print(f'dock:{pargs.dock}')
        for par in pargs.dock:
            dock = par[0][0]
            adopar = par[0][1:].lstrip()
            dock = '#'+dock
            add_curves(dock, adopar)
    else:
        # plots for the main dock
        #for par in pargs.parms:
        add_curves('#0', pargs.parms)

    for dock in gMapOfDocks:
        set_legend(str(dock), True)

    update_data()

    ## Start a timer to rapidly update the plot in pw
    gTimer.timeout.connect(update_data)
    gTimer.start(int(pargs.sleepTime*1000))

    gWin.show()
    gWin.resize(640,480)

    # start GUI
    qApp.instance().exec_()
    print('Application exit')

if __name__ == "__main__":
    main()
