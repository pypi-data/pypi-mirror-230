from pyfrigel_report_tool.consts import DEFAULT_STROKE_COLOR, WORKING_MODES_COLORS, DEFAULT_FONT, DEFAULT_ON_COLOR, DEFAULT_NEGATIVE_COLOR

from reportlab.graphics.shapes import Drawing, _DrawingEditorMixin, Polygon
from reportlab.graphics.charts.legends import Legend
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics.charts.barcharts import VerticalBarChart, HorizontalBarChart
from reportlab.lib.colors import PCMYKColor
from reportlab.lib.formatters import DecimalFormatter

class ChartPieWithLegend(_DrawingEditorMixin, Drawing):
    '''
        creates a pie chart with a legend
    '''
    def __init__(self, data: list, seriesNames: list, colors: list=list(), width: int=270, height: int=100, *args, **kw):
        Drawing.__init__(self, width, height, *args, **kw)
        self._add(self, Pie(), name='pie', validate=None, desc=None)
        self.pie.data = data
        if colors:
            self._colors = colors
        self.pie.height = 100
        self.pie.width = 100
        self.pie.x = 0
        self.pie.strokeWidth = 1
        self.pie.slices.strokeColor = DEFAULT_STROKE_COLOR
        self.pie.slices.strokeWidth = 0
        self._seriesNames = seriesNames
        self._add(self, Legend(), name='legend', validate=None, desc=None)
        self.legend.columnMaximum  = 3
        self.legend.y = self.height/2 +10
        self.legend.x = 140
        self.legend.fontName = DEFAULT_FONT
        self.legend.strokeWidth = 0
        self.legend.strokeColor = DEFAULT_STROKE_COLOR
        self.legend.fontSize = 14
        self.legend.alignment='right'
        self.legend.subCols.rpad = 40
        for i, _ in enumerate(self.pie.data): self.pie.slices[i].fillColor = self._colors[i]
        self.legend.colorNamePairs = list(zip(self._colors, list(zip(self._seriesNames, map(lambda x: "{}{}".format(round(x,2), '%'), self.pie.data)))))
        
        
class ChartBar(_DrawingEditorMixin,Drawing):
    """
        creates a chart bar
        
        input:
            data (list)
            category_names (list): x axys names
            colors (list): bar colors
            width (float)
            height (float)
            
    """
    def __init__(self, data: list, category_names: list, colors: list, width=400, height=200, style='stacked', legend = False, series_names=None, *args, **kw):
        Drawing.__init__(self,width,height,*args,**kw)
        self._add(self,VerticalBarChart(),name='chart',validate=None,desc=None)
        self.chart.x = 30
        self.chart.y = 20
        self.chart.width=self.width - self.chart.x -10
        self.chart.height=self.height - self.chart.y -10
        self.chart.reversePlotOrder = 0
        
        self.chart.valueAxis.strokeWidth = 0.5
        self.chart.categoryAxis.strokeWidth = 0.5
        self.chart.categoryAxis.style = style
        self.chart.valueAxis.valueMin = 0
        self.chart.valueAxis.valueMax = 24
        self.chart.valueAxis.valueStep= 6
        self.chart.valueAxis.labelTextFormat= '%0.0f h'
        self.chart.valueAxis.labels.fontName = DEFAULT_FONT
        self.chart.categoryAxis.labels.fontName = DEFAULT_FONT
        self.chart.data = data
        for index, color in enumerate(colors): self.chart.bars[index].fillColor = color 
        if legend:
            self._colors = WORKING_MODES_COLORS
            self._add(self, Legend(), name='legend', validate=None, desc=None)
            self.legend.x = 392
            self.legend.y = 180
            self.legend.fontSize = 10
            self.legend.fontName = DEFAULT_FONT
            self.legend.dx = 8
            self.legend.dy = 8
            self.legend.dxTextSpace = 10
            self.legend.yGap = 0
            self.legend.deltay = 24
            self.legend.strokeColor = PCMYKColor(0,0,0,0)
            self.legend.strokeWidth = 0
            self.legend.columnMaximum = 99
            self.legend.alignment = 'right'
            self.legend.variColumn = 0
            self.legend.dividerDashArray = None
            self.legend.dividerWidth = 0.25
            self.legend.subCols[0].align = 'left'
            self.legend.subCols[0].minWidth = 200
            self.legend.subCols[1].align = 'right'
            self.legend.subCols[1].align='numeric'
            self.legend.subCols[1].dx = -30
            self.legend.subCols[1].minWidth = 80
            self.legend.subCols[2].align = 'right'
            self.legend.subCols[2].align='numeric'
            self.legend.subCols[2].dx = -10
            self.legend.subCols[2].minWidth = 16
            self._seriesNames = series_names
            names = list(zip(self._seriesNames))
            self.legend.colorNamePairs = list(zip(self._colors, names))
        self.chart.bars.strokeWidth = 0.25
        self.chart.bars.strokeColor = DEFAULT_STROKE_COLOR
        self.chart.categoryAxis.categoryNames = category_names


class PieChartWorkingModes(_DrawingEditorMixin,Drawing):
    """
        creates a chart bar
        
        input:
            data (list)
            category_names (list): x axys names
            colors (list): bar colors
            width (float)
            height (float)
            
    """
    def __init__(self, data, label_percentage, data_trend, header_names: tuple, series_names: tuple, width=400, height=125, *args, **kw):
        Drawing.__init__(self,width,height,*args,**kw)
        self._colors = WORKING_MODES_COLORS
        # font
        fontSize = 12
        fontName = DEFAULT_FONT
        self._add(self, Pie(), name='chart', validate=None, desc=None)
        # pie
        self.chart.y = 0
        self.chart.x = 30
        self.chart.height = 100
        self.chart.width = 100
        self.chart.slices.strokeColor = DEFAULT_STROKE_COLOR
        self.chart.slices.strokeWidth = 0.5
        self._add(self, Legend(), name='legend', validate=None, desc=None)
        self._add(self, Legend(), name='legendHeader', validate=None, desc=None)
        self.legendHeader.x = 180
        self.legendHeader.y = self.height -25
        self.legendHeader.fontSize = fontSize
        self.legendHeader.fontName = fontName
        self.legendHeader.subCols[0].minWidth = 130
        self.legendHeader.subCols[0].align = 'left'
        self.legendHeader.subCols[1].minWidth = 75
        self.legendHeader.subCols[1].align = 'right'
        self.legendHeader.subCols[2].minWidth = 123
        self.legendHeader.subCols[2].align = 'right'
        self.legendHeader.subCols[3].minWidth = 1000 # needed to remove black rectangle
        black = PCMYKColor(0, 0, 0, 100)
        self.legendHeader.colorNamePairs = [(black, header_names + ('', ))]
        self.legend.x = 180
        self.legend.y = self.height -50
        self.legend.fontSize = fontSize
        self.legend.fontName = fontName
        self.legend.dx = 8
        self.legend.dy = 8
        self.legend.dxTextSpace = 10
        self.legend.yGap = 0
        self.legend.deltay = 24
        self.legend.strokeColor = PCMYKColor(0,0,0,0)
        self.legend.strokeWidth = 0
        self.legend.columnMaximum = 99
        self.legend.alignment = 'right'
        self.legend.variColumn = 0
        self.legend.dividerDashArray = None
        self.legend.dividerWidth = 0.5
        self.legend.dividerOffsX = (0, 0)
        self.legend.dividerLines = 7
        self.legend.dividerOffsY = 12
        self.legend.subCols[0].align = 'left'
        self.legend.subCols[0].minWidth = 180
        self.legend.subCols[1].align = 'right'
        self.legend.subCols[1].align='numeric'
        self.legend.subCols[1].dx = -15
        self.legend.subCols[1].minWidth = 62
        self.legend.subCols[2].align = 'right'
        self.legend.subCols[2].align='numeric'
        self.legend.subCols[2].dx = -4
        self.legend.subCols[2].minWidth = 110
        # sample data
        self._seriesNames = series_names
        self._seriesData1 = data
        self._seriesData2 = data_trend
        # up = Drawing(3,3).add(Polygon(
        #             strokeColor = DEFAULT_ON_COLOR,
        #             fillColor = DEFAULT_ON_COLOR,
        #             points=[4, 6+(5/2), 4-(5/2), 6-(5/2), 4+(5/2), 6-(5/2), 4, 6+(5/2)] #Structure [(x1,y1),(x2,y2),...]
        #         ))
        # down = Drawing(3,3).add(Polygon(
        #             strokeColor = DEFAULT_NEGATIVE_COLOR,
        #             fillColor = DEFAULT_NEGATIVE_COLOR,
        #             points=[4, 6-(5/2), 4+(5/2), 6+(5/2), 4-(5/2), 6+(5/2), 4, 6-(5/2)] 
        #         ))


        formatter_time = lambda x: '{} h  {} min'.format(int(x), int((x-int(x))*60))
        formatter_trend = lambda x: x if x is None else \
            DecimalFormatter(places=0, thousandSep=',', decimalSep='.', suffix=' %').format(x) if x <= 100 else \
                '>100 %'
        sign_adder = lambda x: '-' if x== None else x if x.startswith('-') or x.startswith('>') else '+{}'.format(x)
        names = list(zip(self._seriesNames,
        map(formatter_time, self._seriesData1),
        map(sign_adder, map(formatter_trend, self._seriesData2))))
        self.legend.colorNamePairs = list(zip(self._colors, names))
        self.chart.data  = self._seriesData1
        self.chart.labels = label_percentage
        self.chart.slices.fontName = DEFAULT_FONT
        self.chart.sideLabels = 1
        # apply colors to slices
        for i, _ in enumerate(self.chart.data): self.chart.slices[i].fillColor = self._colors[i]
        self.legend.deltax = 75
        self.legendHeader.subCols[0].minWidth = 100
        self.legend.subCols[0].minWidth = 100

class HBarChartValueAxisNegLabels(_DrawingEditorMixin,Drawing):
    
    '''
Chart Features
--------------
This is a simple horizontal barchart whose XVAlueAxis is modified to make the negative tick labels turn red.

        - The xValueAxis has negative tick labels coloured red. That is accomplished by changing the Label attribute customDrawChanger to be an instance of
        reportlab.graphics.charts.textlabels.RedNegativeChanger.

        This chart was built with our [Diagra](http://www.reportlab.com/software/diagra/) solution.

        Not the kind of chart you looking for? Go [up](..) for more charts, or to see different types of charts click on [ReportLab Charts Gallery](/chartgallery/).
    '''
    def __init__(self, data: list, category_names: list, width=500, height=200, style='parallel', *args, **kw):
        Drawing.__init__(self,width,height,*args,**kw)
        self._add(self,HorizontalBarChart(),name='chart',validate=None,desc=None)
        self.chart.x = 30
        self.chart.y = 20
        self.chart.width=self.width - self.chart.x -10
        self.chart.height=self.height - self.chart.y -10
        self.chart.reversePlotOrder = 0
        self.chart.valueAxis.strokeWidth = 0.5
        self.chart.categoryAxis.strokeWidth = 0.5
        self.chart.valueAxis.valueMin = -500
        self.chart.valueAxis.valueMax = 500
        self.chart.valueAxis.valueStep= 50
        self.chart.valueAxis.labels.fontName = DEFAULT_FONT
        self.chart.categoryAxis.labels.fontName = DEFAULT_FONT
        self.chart.data = data
        self.chart.bars.strokeWidth = 0.25
        self.chart.categoryAxis.style = style
        self.chart.categoryAxis.categoryNames = category_names
        self.chart.valueAxis.labelTextFormat= '%0.0f sec'
        self.chart.valueAxis.labels.angle = -45
        self.chart.valueAxis.labels.boxAnchor ='autox'
        for index, value in enumerate(data[0]):
            if value >0:
                self.chart.bars[(0, index)].fillColor = DEFAULT_ON_COLOR
                self.chart.categoryAxis.labels[index].dx = -8
                self.chart.categoryAxis.labels[index].dy = -2
            else:
                self.chart.bars[(0, index)].fillColor = DEFAULT_NEGATIVE_COLOR             
                self.chart.categoryAxis.labels[index].dx = 10 + len(category_names[index])*4
                self.chart.categoryAxis.labels[index].dy = -2