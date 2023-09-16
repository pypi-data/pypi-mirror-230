# AUTO GENERATED FILE - DO NOT EDIT

from dash.development.base_component import Component, _explicitize_args


class Minichart(Component):
    """A Minichart component.


Keyword arguments:

- id (string; optional):
    Unique ID to identify this component in Dash callbacks.

- colors (list of strings; optional):
    Array of colors. If its length is less than the length of data,
    colors are recycled.

- data (list of numbers; optional):
    Data values the chart has to represent.

- height (number; optional):
    Maximal height of barcharts.

- labelColor (string; optional):
    Color to apply to labels. If \"auto\", text will be black or white
    depending on the background color.

- labelMaxSize (number; optional):
    Maximal height of labels in pixels.

- labelMinSize (number; optional):
    Labels are automatically hidden if the label height is less than
    this number.

- labelPadding (number; optional):
    Padding to apply to labels.

- labelStyle (string; optional):
    CSS style to apply to labels.

- labels (list of strings; optional):
    Labels to display on the chart. If it equals to \"auto\" then data
    values are displayed in a compact way.

- lat (number; required):
    Latitude of the minichart.

- loading_state (dict; optional):
    Dash loading state information.

- lon (number; required):
    Latitude of the minichart.

- maxValues (number | list of numbers; optional):
    Maximal absolute value the data could take. It can be a single
    numeric value or an array of values with same length as data. In
    the first case, all values will be represented with the same scale
    while in the second case, each value will have its own scale. This
    is useful when one wants to represent multiple variables that are
    not comparable. If it equals to \"auto\" (the default) then the
    maximum absolute value in data is used.

- transitionTime (number; optional):
    Duration in milliseconds of transitions.

- type (a value equal to: 'bar', 'pie', 'polar-radius', 'polar-area'; optional):
    Type of chart to create.

- width (number; optional):
    Width of the chart when `type` equals 'bar' or maximal diameter of
    the chart for all other types."""
    _children_props = []
    _base_nodes = ['children']
    _namespace = 'dash_leaflet'
    _type = 'Minichart'
    @_explicitize_args
    def __init__(self, lat=Component.REQUIRED, lon=Component.REQUIRED, type=Component.UNDEFINED, data=Component.UNDEFINED, maxValues=Component.UNDEFINED, colors=Component.UNDEFINED, width=Component.UNDEFINED, height=Component.UNDEFINED, labels=Component.UNDEFINED, labelMinSize=Component.UNDEFINED, labelMaxSize=Component.UNDEFINED, labelPadding=Component.UNDEFINED, labelStyle=Component.UNDEFINED, labelColor=Component.UNDEFINED, transitionTime=Component.UNDEFINED, id=Component.UNDEFINED, loading_state=Component.UNDEFINED, **kwargs):
        self._prop_names = ['id', 'colors', 'data', 'height', 'labelColor', 'labelMaxSize', 'labelMinSize', 'labelPadding', 'labelStyle', 'labels', 'lat', 'loading_state', 'lon', 'maxValues', 'transitionTime', 'type', 'width']
        self._valid_wildcard_attributes =            []
        self.available_properties = ['id', 'colors', 'data', 'height', 'labelColor', 'labelMaxSize', 'labelMinSize', 'labelPadding', 'labelStyle', 'labels', 'lat', 'loading_state', 'lon', 'maxValues', 'transitionTime', 'type', 'width']
        self.available_wildcard_properties =            []
        _explicit_args = kwargs.pop('_explicit_args')
        _locals = locals()
        _locals.update(kwargs)  # For wildcard attrs and excess named props
        args = {k: _locals[k] for k in _explicit_args}

        for k in ['lat', 'lon']:
            if k not in args:
                raise TypeError(
                    'Required argument `' + k + '` was not specified.')

        super(Minichart, self).__init__(**args)
