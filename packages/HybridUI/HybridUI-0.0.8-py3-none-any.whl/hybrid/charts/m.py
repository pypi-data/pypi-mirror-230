import json

class ConfigGenerator:
    def __init__(self):
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

    def generate_json(self):
        return json.dumps(self.config, indent=2)

# Instanz der ConfigGenerator-Klasse erstellen
config_generator = ConfigGenerator()

# JSON-Konfiguration generieren und ausgeben
generated_config = config_generator.generate_json()
print(generated_config)
