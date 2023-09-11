def update_data_old():
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
                printv(f're-range {dataset.name}')
                tmp = dataset.data
                dataset.data = [np.empty(dataset.data[0].shape[0] * 2),
                    np.empty(dataset.data[0].shape[0] * 2)]
                dataset.data[0][:tmp[0].shape[0]] = tmp[0]
                dataset.data[1][:tmp[1].shape[0]] = tmp[1]
            x = dataset.data[1][:ptr]
            y = dataset.data[0][:ptr]
        #print(f'symbolSize: {curveName,dataset.symbol,dataset.symbolSize}')
        pen = dataset.pen if dataset.width else None
        #printvv(f'x:{x}\ny:{y}')

        #print(f'dataBounds: {dataset.plotItem.dataBounds(0)[1]}, x:{x.max()}')
        vrect = dataset.plotWidget.visibleRange()
        if x.max() > vrect.right():#+vrect.width()*0.001:
            print(f'visual rect: {repr(vrect.right())}, x:{x.max()}')

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
        print(f'update time: {round(timer()-tstart,6)}')
