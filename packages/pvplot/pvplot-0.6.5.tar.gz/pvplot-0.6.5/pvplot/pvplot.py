#!/usr/bin/env python3
"""Plotting package for EPICS PVs, ADO and LITE parameters.
"""
__version__ = 'v0.6.5 2023-09-14'# unnecessary updates removed
#TODO: if backend times out the gui is not responsive
#TODO: add_curves is not correct for multiple curves
#TODO: move Add Dataset to Dataset options
#TODO: if docks are stripcharts then zooming should be synchronized
#TODO: add dataset arithmetics

import sys, os, time
timer = time.perf_counter
import numpy as np
from qtpy import QtWidgets as QW, QtGui, QtCore
from qtpy.QtWidgets import QApplication, QMainWindow, QGridLayout
import pyqtgraph as pg
from pyqtgraph.graphicsItems.ViewBox.ViewBoxMenu import ViewBoxMenu
from pyqtgraph import dockarea
from functools import partial

#````````````````````````````Constants````````````````````````````````````````
X,Y = 0,1
Scale,Units = 0,1
#````````````````````````````Helper methods```````````````````````````````````
def printTime(): return time.strftime("%m%d:%H%M%S")
def printi(msg): print((f'INFO_PP@{printTime()}: '+msg))
def printw(msg): print((f'WARN_PP@{printTime()}: '+msg))
def printe(msg): print((f'ERR_PP@{printTime()}: '+msg))
def _printv(msg, level=0):
    if PVPlot.pargs.verbose is None:
        return
    if len(PVPlot.pargs.verbose) >= level:
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

try:    from cad_epics import epics as EPICSAccess
except Exception as e:
    EPICSAccess = None 
    printw(f'EPICS devices are not supported on this host: {e}')
try:
    import liteaccess as liteAccess 
    LITEAccess = liteAccess.Access
    print(f'liteAccess {liteAccess.__version__}')
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
    print('cprint:'+msg)

def get_pv(adopar:str, prop='value'):
    #print(f'>get_pv {adopar}')
    adopar, vslice = split_slice(adopar)
    access = PVPlot.access.get(adopar[:2], (ADOAccess,0))
    access,prefixLength = PVPlot.access.get(adopar[:2], (ADOAccess,0))
    if access is None:
        printe(f'No access method for {adopar}')
        sys.exit(1)

    pvTuple = tuple(adopar[prefixLength:].rsplit(':',1))
    rd = access.get(pvTuple)[pvTuple]
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
    return devParSlice[0], vslice
#,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,

def new_dock(dataset):
    docks = [x.split('.')[0] for x in MapOfDatasets.dtsDict]
    i = 0
    while '#'+str(i) in docks: i += 1
    v = '#'+str(i)+' '+dataset
    printv('adding plot: '+str(v))

def close_dock(dname):
    """remove datasets and curves and close the dock widget"""
    print('closing dock '+dname)
    for curveName in MapOfDatasets.dtsDict.keys():
        printv('looking: '+curveName)
        dock = curveName.split('.')[0]
        if dock == dname:
            printv('removing: '+curveName)
            MapOfDatasets.remove(curveName)
    printv('MapOfDatasets.dtsDict: '+str(MapOfDatasets.dtsDict))
    PVPlot.mapOfDocks[dname].close()
    del PVPlot.mapOfPlotWidgets[dname]

def update_data():
    """ called on QtCore.qTimer() event to update plots."""
    tstart = timer()
    tt = round(time.time(),6)
    if tt > PVPlot.lastPlotTime + PVPlot.minPlottingPeriod:
        time2plot = True
        PVPlot.lastPlotTime = tt + PVPlot.minPlottingPeriod
    else:
        time2plot = False

    for dataset in MapOfDatasets.dtsDict.values():
        dataset.update_plot(time2plot)

    if PVPlot.perfmon:
        v = timer()-tstart
        print('update time:'+str(timer()-tstart))

def set_legend(dockName:str, state:bool):
    if state: # legend enabled
        printv('add legend for '+str(dockName))
        widget = PVPlot.mapOfPlotWidgets[dockName]
        listOfItems = widget.getPlotItem().listDataItems()
        l = pg.LegendItem((100,60), offset=(70,30))  # args are (size, offset)
        l.setParentItem(widget.graphicsItem())
        PVPlot.legend[dockName] = l
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
            PVPlot.legend[dockName].scene().removeItem(PVPlot.legend[dockName])
            del PVPlot.legend[dockName]
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
    """ dataset storage, keeps everything what is necessary to plot the curve.
    """
    def __init__(self,name,paramAndCount):
        self.name = name
        self.adoPars = paramAndCount # list of max 2 of (adoPar,count)
        self.plotItem = None # plotting object PlotDataItem
        self.pen = None # current pen
        self.width = 1 # pen width
        self.lastTimePlotted = 0.
        self.lastTimeUpdated = 0.
        self.timestampReported = 0 # time of the last title update
        self.plotWidget = None
        self.viewBox = None
        # members for stripchart plot
        self.viewXSize = 9E9# Wed Mar 14 2255 16:00:00
        self.viewXRange = [0., 9E9]
        self.scrolling = False
        
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
        initialWidth = 16
        self.data = [np.empty(initialWidth),np.empty(initialWidth)]# [X,U] data storage
        self.dataPtr = 0
        count = self.adoPars[0][1] #
        printv(f'adoPars,count: {self.adoPars,count}')

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
        
        # assign the plotwidget
        if dock in PVPlot.mapOfPlotWidgets:
            # dock already exist, use the existing plotwidget
            self.plotWidget = PVPlot.mapOfPlotWidgets[dock]
        else:
            # new dock need to be created
            # create vewBox with plotwidget
            self.viewBox = CustomViewBox(dock, self)
            self.viewBox.setMouseMode(self.viewBox.RectMode)
            self.viewBox.sigRangeChangedManually.connect(self.xrangeChanged)
            printv('adding plotwidget:'+dock)
            title = None
            if count == 1 and not isCorrelationPlot:
                self.plotWidget = pg.PlotWidget(title=title, viewBox=self.viewBox,
                  axisItems={'bottom':DateAxis(orientation='bottom')})
                if dock != '#0':
                	self.plotWidget.setXLink(PVPlot.mapOfPlotWidgets['#0'])
            else: 
                self.plotWidget = pg.PlotWidget(title=title, viewBox=self.viewBox)
            #self.plotWidget.showGrid(True,True)
            PVPlot.mapOfPlotWidgets[dock] = self.plotWidget
            PVPlot.mapOfDocks[dock].addWidget(self.plotWidget)
            if isCorrelationPlot:                        
                self.plotWidget.setLabel('bottom',self.adoPars[1][0])
            elif count == 1:
                self.plotWidget.setLabel('bottom','time', units='date', unitPrefix='')
            else:
                self.plotWidget.setLabel('bottom',PVPlot.scaleUnits[X][Units])

        # set X and Y ranges
        rangeMap = {X: (PVPlot.pargs.xrange, self.plotWidget.setXRange),
                    Y: (PVPlot.pargs.yrange, self.plotWidget.setYRange)}
        for axis,v in rangeMap.items():
            r,func = v
            if r is None:
                continue
            r = [float(i) for i in v[0].split(':')]
            func(*r)

        if self.plotItem:
            self.plotWidget.addItem(self.plotItem)
        self.lastTimePlotted = 0.

    def __str__(self):
        return f'Dataset {self.name}, x: {self.data[X].shape}'

    def xrangeChanged(self):
        viewRange = self.viewBox.viewRange()
        self.viewXRange = viewRange[X]
        viewlimit = self.viewXRange[1]
        self.viewXSize = viewlimit - self.viewXRange[0]
        rstack = self.viewBox.rangestack
        rstack.append(viewRange)
        if len(rstack) > 10:
            rstack.pop(0)
        self.scrolling = (self.viewBox is not None)\
            and viewlimit > self.data[X][self.dataPtr-1]
        #print(f'scrolling: {self.scrolling}')

    def shift_viewXRange(self):
        if self.viewBox.state['autoRange'][X]:
                return
        dx = self.viewXSize*PVPlot.padding
        self.viewXRange[0] += dx
        self.viewXRange[1] += dx
        #print(f'>shift_viewXRange: {self.viewXRange[0], self.viewXRange[1]}')
        self.viewBox.setXRange(self.viewXRange[0], self.viewXRange[1])

    def plot(self, ts):
        # Plot the dataset
        if self.lastTimePlotted == ts:
            return
        self.lastTimePlotted = ts
        #print(f'>plot: {self.name,round(ts,3)}')
        x = self.data[X][:self.dataPtr]
        y = self.data[Y][:self.dataPtr]
        pen = self.pen if self.width else None
        #printvv(f'x:{x}\ny:{y}')
        self.plotItem.setData(x=x, y=y,
            pen = pen,
            #TODO:connect = self.connect,
            #TODO:shadowPen = self.shadowPen,
            #TODO:fillLevel = self.fillLevel,
            #TODO:fillBrush = self.fillBrush,
            #TODO:stepMode = self.stepMode,
            symbol = self.symbol,
            #TODO:symbolPen = self.symbolPen,
            symbolPen = None,
            symbolBrush = self.symbolBrush,
            #TODO:symbolBrush = self.pen.color(),
            symbolSize = self.symbolSize,
            #TODO:pxMode = self.pxMode,
        )

    def update_plot(self, time2plot):
        curvePars = self.adoPars
        #printvv(f'self: {curvePars}')#: {self.data}')
        yd,ts = None,None
        try:
            yd, ts = get_pv(curvePars[0][0])
        except Exception as e:
            #printv('got '+str((yd,ts))+', from:'+str(curvePars[0][0])+', except:'+str(e))
            printw(f'Exception getting {curvePars[0][0]}: {e}')
            return
        if ts:
            if ts == self.lastTimeUpdated:
                #print(f'curve {self.name} did not change {round(ts,3)}')
                if time2plot:
                    self.plot(ts)
                return
        self.lastTimeUpdated = ts
        #print(f'update {self.name, round(ts,3), round(self.lastTimePlotted,3)}')
        try:    
            l = len(yd)
            if l == 1: yd = yd[0]
        except: 
            l = 1

        # Evaluate X and Y arrays
        if l > 1:
            # the plot is array plot
            y = np.array(yd)
            x = np.arange(len(yd))*PVPlot.scaleUnits[X][Scale]
            self.plot(x,y)
            return
        else:
            # the plot is scrolling or correlation plot
            ptr = self.dataPtr
            if ptr >= PVPlot.maxPoints:
                # do not extent the data buffer, roll it over insted
                self.data[X] = np.roll(self.data[X],-1)
                self.data[Y] = np.roll(self.data[Y],-1)
                ptr -= 1
            self.data[Y][ptr] = yd
            if len(curvePars) > 1: 
                #printv(f'correlation plot: {curvePars[1][0]}')
                try:
                    v,*_ = get_pv(curvePars[1][0])
                    try:    v = v[0]
                    except: pass 
                    self.data[X][ptr] = v
                except Exception as e:
                    printe('no data from '+str(curvePars[1][0]))
            else:
                # scrolling plot with time scale
                #print(f'ts: {round(ts,3), round(self.viewXRange[1],3)}')
                if self.scrolling and ts > self.viewXRange[1]:
                    self.shift_viewXRange()
                self.data[X][ptr] = ts
            ptr += 1
            self.dataPtr = ptr
            #print(f'ptr: {ptr,self.data[Y].shape[0]}')
            if (ptr <= PVPlot.maxPoints/2) & (ptr >= self.data[Y].shape[0]):
                tmp = self.data
                self.data = [np.empty(self.data[Y].shape[0] * 2),
                    np.empty(self.data[Y].shape[0] * 2)]
                self.data[Y][:tmp[Y].shape[0]] = tmp[Y]
                self.data[X][:tmp[X].shape[0]] = tmp[X]
                #printi(f'adjust {self.name} from {tmp[X].shape} to {self.data[X].shape}')

            if time2plot:
                self.plot(ts)

class MapOfDatasets():
    """Global dictionary of Datasets, provides safe methods to add and remove 
    the datasets"""
    dtsDict = {}
    
    def add(name, adoPars):
        """add new datasets, the adoPars is the space delimited string of 
        source ado:parameters."""
        printv(f'>MapOfDatasets.add({adoPars})')
        if name in MapOfDatasets.dtsDict:
            printv('Need to remove '+name)
            MapOfDatasets.remove(name)
        for i, token in enumerate(adoPars.split()):
            dname = f'{name}.{i}'
            pnameAndCount = [];
            alist = token.split(',')
            alist = alist[:2] # we cannot handle more than 2 curves in correlation plot
            if len(alist) == 0:
                #MapOfDatasets.dtsDict[dname] = Dataset(dname,[('',0)])
                #print(f'added dataset {str(MapOfDatasets.dtsDict[dname])}')
                print(f'Logic error: MapOfDatasets({adoPars})') 
                sys.exit(1)
            else:
                alist.reverse()
                #print(f'alist: {alist}')
                for adoPar in alist:
                    ap = PVPlot.pargs.prefix+adoPar
                    try:
                        printv(f'check if {ap}, is alive')
                        valts = get_pv(ap) # check if parameter is alive
                        if valts is None:
                            printw('Could not add {ap}')
                            return 2
                    except Exception as e:
                        printw(f'Exception in getting parameter {ap}')
                        return 1
                    val,ts = valts
                    newName = ap
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
#`````````````````````````````````````````````````````````````````````````````
class CustomViewBox(pg.ViewBox):
    """ defines actions, activated on the right mouse click in the dock
    """
    def __init__(self, name, dataset):
        #self.dockName = kwds['name'] # cannot use name due to an issue in demo
        #del kwds['name'] # the name in ViewBox.init fails in demo
        self.dockName = name
        self.dataset = dataset# master dataset, it defines horizontal axis
        #print('CustomViewBox: '+str(self.dockName))

        # call the init method of the parent class
        super(CustomViewBox, self).__init__()
        self.setDefaultPadding(0.)# standard is 0.02

        # IMPORTANT: menu creation is deferred because it is expensive 
        # and often the user will never see the menu anyway.
        self.menu = None
        self.cursors = set()
        self.rangestack = [] #stack of view ranges
           
    #v32#def mouseClickEvent(self, ev) removed, due to blank exports

    def raiseContextMenu(self, ev):
        # Let the scene add on to the end of our context menu
        menuIn = self.getContextMenus()        
        menu = self.scene().addParentContextMenus(self, menuIn, ev)
        menu.popup(ev.screenPos().toPoint())
        return True

    def getContextMenus(self, event=None):
        """ This method will be called when this item's children want to raise
        a context menu that includes their parents' menus.
        """
        if self.menu:
            printv('menu exist')
            return self.menu
        printv('getContextMenus for '+str(self.dockName))
        self.menu = ViewBoxMenu(self)
        self.menu.setTitle(str(self.dockName)+ " options..")

        # unzoom last
        unzoom = self.menu.addAction("&UnZoom")
        unzoom.triggered.connect(lambda: self.unzoom())

        # Datasets options dialog
        setDatasets = self.menu.addAction('Datasets &Options')
        setDatasets.triggered.connect(self.changed_datasetOptions)

        cursorMenu = self.menu.addMenu('Add &Cursor')
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
        runWidget = QW.QCheckBox('&Stop')
        runWidget.setChecked(False)
        runWidget.stateChanged.connect(lambda x: self.set_stop(x))
        runAction.setDefaultWidget(runWidget)
        self.menu.addAction(runAction)
        
        sleepTimeMenu = self.menu.addMenu('Sleep&Time')
        sleepTimeAction = QW.QWidgetAction(sleepTimeMenu)
        sleepTimeWidget = QW.QDoubleSpinBox()
        sleepTimeWidget.setValue(PVPlot.pargs.sleepTime)
        sleepTimeWidget.setRange(0.001,100)
        sleepTimeWidget.setSuffix(' s')
        sleepTimeWidget.setSingleStep(.1)
        sleepTimeWidget.valueChanged.connect(lambda x: self.set_sleepTime(x))
        sleepTimeAction.setDefaultWidget(sleepTimeWidget)
        sleepTimeMenu.addAction(sleepTimeAction)
        return self.menu

    def cursorAction(self, direction):
        angle = {'Vertical':90, 'Horizontal':0}[direction]
        pwidget = PVPlot.mapOfPlotWidgets[self.dockName]
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
        pwidget = PVPlot.mapOfPlotWidgets[self.dockName]
        viewRange = pwidget.getPlotItem().viewRange()[horizontal]
        if pos > viewRange[1]:
            pwidget.removeItem(cursor)
            self.cursors.remove(cursor)
        else:
            cursor.label.setText(str(round(pos,3)))

    def changed_datasetOptions(self):
        """Dialog Plotting Options"""
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

        listOfItems = PVPlot.mapOfPlotWidgets[self.dockName].getPlotItem().listDataItems()
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
            colorButton = pg.ColorButton(color=dataset.pen.color())
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
            symbolColorButton = pg.ColorButton(color=dataset.pen.color())
            symbolColorButton.setObjectName(curveName)
            symbolColorButton.sigColorChanging.connect(lambda x:
              change_plotOption(str(self.sender().objectName()),scolor=x.color()))
            tbl.setCellWidget(row, 5,symbolColorButton)
        dlg.exec_()

    def set_symbol(self, x):
        """ Change symbol of the scatter plot. The size and color are taken
        from the curve setting"""
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
        PVPlot.mapOfPlotWidgets[dock].setLabel(side,label, units='')
        # it might be useful to return the prompt back:
        #labelGui.setText('LabelX' if side=='bottom' else 'LabelY')

    def set_legend(self, state):
        state = (state==QtCore.Qt.Checked)
        print(f'set_legend {state}')
        set_legend(self.dockName, state)

    def set_stop(self, state):
        if state == QtCore.Qt.Checked:
            PVPlot.qTimer.stop()
        else:
            PVPlot.qTimer.start(int(PVPlot.pargs.sleepTime*1000))

    def set_sleepTime(self, itemData):
        #print('setting SleepTime to: '+str(itemData))
        PVPlot.pargs.sleepTime = itemData
        PVPlot.qTimer.stop()
        PVPlot.qTimer.start(int(PVPlot.pargs.sleepTime*1000))

    def unzoom(self):
        self.rangestack.pop()
        try:    viewRange = self.rangestack[-1]
        except:
            return        
        self.setRange(xRange=viewRange[X], yRange=viewRange[Y], padding=None,
            update=True, disableAutoRange=True)
#,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,,

def callback(args):
    #print(f'cb: {args}')
    for hostDev, pardict in args.items():
        for par in pardict:
            try:
                axis,units = PVPlot.subscribedParMap[(hostDev,par)]
            except:
                continue
            scale = pardict[par]['value'][0]
            print(f'axis={axis}, units={units}, scale={scale}')
            PVPlot.scaleUnits[axis][Scale] = scale

def add_curves(dock:str, adopars:str):        
    # if dock name is new then create new dock, otherwise extend the 
    # existing one with new curve
    
    curves = [x for x in MapOfDatasets.dtsDict]
    docks = [x.split('.')[0] for x in curves]
    printv(f'addcurves curves,docks:{curves,docks}')
    if dock in docks:
        printv('extending dock '+str(dock))
        for i in range(MaxCurvesPerPlot):
            newSlot = dock+'.'+str(i+1)
            if newSlot not in curves: break
        dock = newSlot
    else:
        printv('adding new plot '+dock)
        PVPlot.mapOfDocks[dock] = dockarea.Dock(dock, size=(500,200), hideTitle=True)
        if dock == '#0':
            PVPlot.dockArea.addDock(PVPlot.mapOfDocks[dock], 'right', closable=True)
        else:
            PVPlot.dockArea.addDock(PVPlot.mapOfDocks[dock], 
              'top', PVPlot.mapOfDocks['#0'], closable=True) #TODO:closable does not work
    if MapOfDatasets.add(dock, adopars):
            printe('in add_curves: '+str((dock, adopars)))
    printv(f'datasets:{MapOfDatasets.dtsDict.keys()}')

class PVPlot():
    pargs = None
    mapOfDocks = {}
    mapOfPlotWidgets = {}
    padding = 0.1
    scaleUnits = [[1,'Sample'],[1,'Count']]
    subscribedParMap = {}
    perfmon = False # option for performance monitoring
    legend = {}# unfortunately we have to keep track of legends
    access = {'E:':(EPICSAccess,2), 'L:':(LITEAccess,2)}
    qWin = None
    qTimer = QtCore.QTimer()
    dockArea = None
    minPlottingPeriod = 1/10.# the data will not be plotted faster than that limit.
    lastPlotTime = 0.
    maxPoints = 1048576# Max number of data points to store.

    def start():
        pargs = PVPlot.pargs
        print(f'pargs: {PVPlot.pargs}')

        try:    os.environ["QT_SCALE_FACTOR"] = str(pargs.zoomin)
        except: pass
        qApp = QApplication([])
        PVPlot.qWin = QMainWindow()
        PVPlot.dockArea = dockarea.DockArea()
        PVPlot.qWin.setCentralWidget(PVPlot.dockArea)
        PVPlot.qWin.resize(1000,500)
        ## Switch to using white background and black foreground
        pg.setConfigOption('background', 'w')
        pg.setConfigOption('foreground', 'k')

        PVPlot.qWin.setWindowTitle(f'pvplot {pargs.parms}')

        # plots for other docks
        if pargs.dock:
            for par in pargs.dock:
                dock = par[0][0]
                adopar = par[0][1:].lstrip()
                dock = '#'+dock
                add_curves(dock, adopar)
        else:
            # plots for the main dock
            add_curves('#0', pargs.parms)
        if len(MapOfDatasets.dtsDict) == 0:
            printe(f'No datasets created')
            sys.exit(1)

        for dock in PVPlot.mapOfDocks:
            set_legend(str(dock), True)

        # Subscriptions. Only LITE system is supported.
        if pargs.xscale is not None:
            infrastructure = pargs.prefix[:2]
            if infrastructure != 'L:':
                printe(f'The --xcale option is supported only for LITE infrastucture')
                sys.exit(1)
            hostDev = pargs.prefix[2:]
            if hostDev[-1] == ':':
                hostDev = hostDev[:-1]
            par = pargs.xscale
            printv(f'subscribing: {hostDev,par}')
            info = LITEAccess.info((hostDev,par))
            printv(f'info of {hostDev,par}: {info}')
            units = info[par].get('units','')
            PVPlot.scaleUnits[X][1] = units
            LITEAccess.subscribe(callback, (hostDev,par))
            PVPlot.subscribedParMap[(hostDev,par)] = [X, units]

        update_data()

        ## Start a timer to rapidly update the plot in pw
        PVPlot.qTimer.timeout.connect(update_data)
        PVPlot.qTimer.start(int(pargs.sleepTime*1000))

        PVPlot.qWin.show()
        PVPlot.qWin.resize(640,480)

        # start GUI
        qApp.instance().exec_()
        print('Application exit')
