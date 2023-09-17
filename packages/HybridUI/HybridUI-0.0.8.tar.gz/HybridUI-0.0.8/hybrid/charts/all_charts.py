from typing import List, Dict, Any
from ..element import Element

"""




  


  RaderChart
  DecompositionTreeGraphChart
  RingProgressChart
  RoseChart
  AlipaySankeyChart
  BulletChart
  ScatterRegressionLineChart
  ColorMappingScatterChart
  CustomGaugeIndicatorChart
  GaugeChart
  GaugeCustomColorChart
  GaugeGradientChart
  RangeGauge
  LiqdChart
  MeterGaugeChart
  MeterGaugeCustomStepsAndStepRatio


"""

class AreaChart(Element):
    def __init__(
        self,
        data: List[Dict[str, Any]]  = None
    ):
        super().__init__(component='AreaChart')
        self.children = []
        if data is not None:
            self._props["data"]= data




class BarChart(Element):
    def __init__(
        self,
        data: List[Dict[str, Any]]  = None
    ):
        super().__init__(component='BarChart')
        self.children = []
        if data is not None:
            self._props["data"]= data





class ViolinChart(Element):
    def __init__(
        self,
        data: List[Dict[str, Any]]  = None
    ):
        super().__init__(component='ViolinChart')
        self.children = []
        if data is not None:
            self._props["data"]= data







class DonutChart(Element):
    def __init__(
        self,
        data: List[Dict[str, Any]]  = None
    ):
        super().__init__(component='DonutChart')
        self.children = []
        if data is not None:
            self._props["data"]= data







class GeographicHeatmap(Element):
    def __init__(
        self,
        data: List[Dict[str, Any]]  = None
    ):
        super().__init__(component='GeographicHeatmap')
        self.children = []
        if data is not None:
            self._props["data"]= data






class ColumnChart(Element):
    def __init__(
        self,
        data: List[Dict[str, Any]]  = None
    ):
        super().__init__(component='ColumnChart')
        self.children = []
        if data is not None:
            self._props["data"]= data






class DualmultilineChart(Element):
    def __init__(
        self,
        data: List[Dict[str, Any]]  = None
    ):
        super().__init__(component='DualmultilineChart')
        self.children = []
        if data is not None:
            self._props["data"]= data






class DualAxesChart(Element):
    def __init__(
        self,
        data: List[Dict[str, Any]]  = None
    ):
        super().__init__(component='DualAxesChart')
        self.children = []
        if data is not None:
            self._props["data"]= data






class legendChart(Element):
    def __init__(
        self,
        data: List[Dict[str, Any]]  = None
    ):
        super().__init__(component='legendChart')
        self.children = []
        if data is not None:
            self._props["data"]= data





class FunnelChart(Element):
    def __init__(
        self,
        data: List[Dict[str, Any]]  = None
    ):
        super().__init__(component='FunnelChart')
        self.children = []
        if data is not None:
            self._props["data"]= data





class LineChart(Element):
    def __init__(
        self,
        data: List[Dict[str, Any]]  = None,
        style = None,
        realtime = False
    ):
        super().__init__(component='LineChart')
        self.children = []
        if data is not None:
            self._props["data"]= data

        if style is not None:
            self._props["style"]= style
        
        if realtime is not None:
            self._props["realtime"]= realtime
            





class PieChart(Element):
    def __init__(
        self,
        data: List[Dict[str, Any]]  = None
    ):
        super().__init__(component='PieChart')
        self.children = []
        if data is not None:
            self._props["data"]= data


"""




  



  MeterGaugeChart
  MeterGaugeCustomStepsAndStepRatio


"""


class RaderChart(Element):
    def __init__(
        self,
        data: List[Dict[str, Any]]  = None
    ):
        super().__init__(component='RaderChart')
        self.children = []
        if data is not None:
            self._props["data"]= data





class DecompositionTreeGraphChart(Element):
    def __init__(
        self,
        data: List[Dict[str, Any]]  = None
    ):
        super().__init__(component='DecompositionTreeGraphChart')
        self.children = []
        if data is not None:
            self._props["data"]= data





class RingProgressChart(Element):
    def __init__(
        self,
        data: List[Dict[str, Any]]  = None
    ):
        super().__init__(component='RingProgressChart')
        self.children = []
        if data is not None:
            self._props["data"]= data





class RoseChart(Element):
    def __init__(
        self,
        data: List[Dict[str, Any]]  = None
    ):
        super().__init__(component='RoseChart')
        self.children = []
        if data is not None:
            self._props["data"]= data










class BulletChart(Element):
    def __init__(
        self,
        data: List[Dict[str, Any]]  = None
    ):
        super().__init__(component='BulletChart')
        self.children = []
        if data is not None:
            self._props["data"]= data




class ScatterRegressionLineChart(Element):
    def __init__(
        self,
        data: List[Dict[str, Any]]  = None
    ):
        super().__init__(component='ScatterRegressionLineChart')
        self.children = []
        if data is not None:
            self._props["data"]= data




class AlipaySankeyChart(Element):
    def __init__(
        self,
        data: List[Dict[str, Any]]  = None
    ):
        super().__init__(component='AlipaySankeyChart')
        self.children = []
        if data is not None:
            self._props["data"]= data




class ColorMappingScatterChart(Element):
    def __init__(
        self,
        data: List[Dict[str, Any]]  = None
    ):
        super().__init__(component='ColorMappingScatterChart')
        self.children = []
        if data is not None:
            self._props["data"]= data




class CustomGaugeIndicatorChart(Element):
    def __init__(
        self,
        data: List[Dict[str, Any]]  = None
    ):
        super().__init__(component='CustomGaugeIndicatorChart')
        self.children = []
        if data is not None:
            self._props["data"]= data




class GaugeChart(Element):
    def __init__(
        self,
        data: List[Dict[str, Any]]  = None
    ):
        super().__init__(component='GaugeChart')
        self.children = []
        if data is not None:
            self._props["data"]= data



class GaugeCustomColorChart(Element):
    def __init__(
        self,
        data: List[Dict[str, Any]]  = None
    ):
        super().__init__(component='GaugeCustomColorChart')
        self.children = []
        if data is not None:
            self._props["data"]= data




class GaugeGradientChart(Element):
    def __init__(
        self,
        data: List[Dict[str, Any]]  = None
    ):
        super().__init__(component='GaugeGradientChart')
        self.children = []
        if data is not None:
            self._props["data"]= data




class RangeGauge(Element):
    def __init__(
        self,
        data: List[Dict[str, Any]]  = None
    ):
        super().__init__(component='RangeGauge')
        self.children = []
        if data is not None:
            self._props["data"]= data




class LiqdChart(Element):
    def __init__(
        self,
        data: List[Dict[str, Any]]  = None
    ):
        super().__init__(component='LiqdChart')
        self.children = []
        if data is not None:
            self._props["data"]= data




class MeterGaugeChart(Element):
    def __init__(
        self,
        data: List[Dict[str, Any]]  = None
    ):
        super().__init__(component='MeterGaugeChart')
        self.children = []
        if data is not None:
            self._props["data"]= data




class MeterGaugeCustomStepsAndStepRatio(Element):
    def __init__(
        self,
        data: List[Dict[str, Any]]  = None
    ):
        super().__init__(component='MeterGaugeCustomStepsAndStepRatio')
        self.children = []
        if data is not None:
            self._props["data"]= data






class ConfigGenerator(Element):
    def __init__(self):
        super().__init__("config")
        self.data = None
        self.measureField = 'measures'
        self.rangeField = 'ranges'
        self.targetField = 'target'
        self.xField = 'title'
        self.rangeColor = '#f0efff'
        self.measureColor = '#5B8FF9'
        self.targetColor = '#3D76DD'
        self.xAxisLine = None
        self.yAxis = False
        self.layout = 'vertical'
        self.measureLabelPosition = 'middle'
        self.measureLabelFill = '#fff'
        self.legendCustom = True
        self.legendPosition = 'bottom'
        self.measureLegendValue = '实际值'
        self.measureLegendName = '实际值'
        self.measureLegendMarkerSymbol = 'square'
        self.measureLegendMarkerFill = '#5B8FF9'
        self.measureLegendMarkerR = 5
        self.targetLegendValue = '目标值'
        self.targetLegendName = '目标值'
        self.targetLegendMarkerSymbol = 'line'
        self.targetLegendMarkerStroke = '#3D76DD'
        self.targetLegendMarkerR = 5
        
        self.config = {
            'data': self.data,
            'measureField': self.measureField,
            'rangeField': self.rangeField,
            'targetField': self.targetField,
            'xField': self.xField,
            'color': {
                'range': self.rangeColor,
                'measure': self.measureColor,
                'target': self.targetColor,
            },
            'xAxis': {
                'line': self.xAxisLine,
            },
            'yAxis': self.yAxis,
            'layout': self.layout,
            'label': {
                'measure': {
                    'position': self.measureLabelPosition,
                    'style': {
                        'fill': self.measureLabelFill,
                    },
                },
            },
            'legend': {
                'custom': self.legendCustom,
                'position': self.legendPosition,
                'items': [
                    {
                        'value': self.measureLegendValue,
                        'name': self.measureLegendName,
                        'marker': {
                            'symbol': self.measureLegendMarkerSymbol,
                            'style': {
                                'fill': self.measureLegendMarkerFill,
                                'r': self.measureLegendMarkerR,
                            },
                        },
                    },
                    {
                        'value': self.targetLegendValue,
                        'name': self.targetLegendName,
                        'marker': {
                            'symbol': self.targetLegendMarkerSymbol,
                            'style': {
                                'stroke': self.targetLegendMarkerStroke,
                                'r': self.targetLegendMarkerR,
                            },
                        },
                    },
                ],
            },
        }