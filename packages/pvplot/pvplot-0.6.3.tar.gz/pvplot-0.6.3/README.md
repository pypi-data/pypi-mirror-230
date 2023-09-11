# pvplot
Plotting tool for EPICS PVs, ADO and [liteServer](https://github.com/ASukhanov/liteServer) parameters.

![Stripchart example](docs/pvplot_stripchart.png)

![Example of an array plot](docs/pvplot_arrays.png)

## Examples
- Sliced array plot of an EPICS PV: ```pvplot -s0.01 -a'E:testAPD:scope1:' 'Waveform_RBV[1:500]'```
- Strip chart of analog inputs of a LabJack U3-HV instrument, served by liteLabjack:<br>
```pvplot -a'L:localhost:dev1' 'tempU3 ADC_HV[0] ADC_HV[1] ADC_HV[2] ADC_HV[3] ADC_LV'```
- Fast correlation plot of a litePeakSimulator ```pvplot -s.01 -a'L:localhost:dev1' 'x,y'```
- Multiple docks. For example, to plot two scrolling plots in lower dock and a 
correlation plot in upper dock:
```pvplot -a'L:localhost:dev1:' -#0'yMax yMin' -#1'yMax,yMin'```
- To change properties of curves: right click on a plot and select 'DataSets Options'
