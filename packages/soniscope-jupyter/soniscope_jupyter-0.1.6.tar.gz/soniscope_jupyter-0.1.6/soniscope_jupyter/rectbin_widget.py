#!/usr/bin/env python
# coding: utf-8

# Copyright (c) Alexander Rind & the SoniVis team.
# Distributed under the terms of the MIT License (see LICENSE.txt).

"""
jupyter widget that shows a 2D histogram plot of data binned into rectangles with a lens and fires an event with filtered data whenever the plot is clicked
"""

from ipywidgets import DOMWidget, CallbackDispatcher, register
from traitlets import Unicode, Instance, List, Int, Float, observe, validate, TraitError
from ._frontend import module_name, module_version
import pandas as pd
import numpy as np
from lens_widget import LensWidget


@register
class RectBinWidget(LensWidget):
    """
    jupyter widget that shows a rectbin plot (2D histogram) with a lens and fires an event with filtered data whenever the plot is clicked
    """
    _model_name = Unicode('RectBinModel').tag(sync=True)
    _model_module = Unicode(module_name).tag(sync=True)
    _model_module_version = Unicode(module_version).tag(sync=True)
    _view_name = Unicode('RectBinView').tag(sync=True)
    _view_module = Unicode(module_name).tag(sync=True)
    _view_module_version = Unicode(module_version).tag(sync=True)

    x_bins = Int(8).tag(sync=True)
    """ number of bins along the x axis. """
    y_field = Int(8).tag(sync=True)
    """ number of bins along the x axis. """

    _bins_x = List(Int()).tag(sync=True)
    """ internal data with bins' x positions as column vector """
    _bins_y = List(Int()).tag(sync=True)
    """ internal data with bins' y positions as column vector """
    _bins_count = List(Int()).tag(sync=True)
    """ internal data with  bins' count as column vector """

    def __init__(self, data=None, x_field=None, y_field=None, **kwargs):
        super().__init__(**kwargs)
        # self._lens_click_handlers = CallbackDispatcher()
        # self.on_msg(self._handle_frontend_msg)


    @validate('x_bins')
    def _valid_x_bins(self, proposal):
        print('§§lens§§ check x bins')
        if not (proposal['value'] < 1 ):
            raise TraitError('The x bins must be a positive integer number.')
        return proposal['value']

    # @validate('y_field')
    # def _valid_y_field(self, proposal):
    #     if not (proposal['value'] == '' or proposal['value'] in self.data):
    #         raise TraitError('The y field is not a column of the data frame.')
    #     return proposal['value']


    @observe('data')
    def _observe_data(self, change):
        # print('§§lens§§ update data')
        if super().x_field != '' and super().y_field != '':
            # TODO binning
            self._marks_x = change.new[self.x_field].tolist()
            self._marks_y = change.new[self.y_field].tolist()

    # @observe('x_field', 'y_field')
    # def _observe_fields(self, change):
    #     # print('§§lens§§ update field ' + change.name + ' to ' + change.new)
    #     if change.new != '':
    #         if change.name == 'x_field':
    #             self._marks_x = self.data[change.new].tolist()
    #         else:
    #             self._marks_y = self.data[change.new].tolist()

    # def lens_click(self, event: str, x: float, y: float, edgeX: float, edgeY: float):
    #     """Programmatically trigger a lens click event.
    #     This will call the callbacks registered to the clicked lens
    #     widget instance.
    #     """

    #     if (self.x_field == '') | (self.y_field == ''):
    #         raise TraitError('At least one axis is undefined.')

    #     if self.shape == 'none':
    #         # no event if lens is disabled by 'shape = none'
    #         return

    #     xRel = self.data[self.x_field] - x
    #     xRad = edgeX - x
    #     yRel = self.data[self.y_field] - y
    #     yRad = edgeY - y

    #     if self.shape == 'square':
    #         distances = np.maximum(xRel.abs() / xRad, yRel.abs() / yRad)
    #     elif self.shape == 'circle':
    #         distances = np.sqrt(xRel**2 / xRad**2 + yRel**2 / yRad**2)
    #         # filtered = self.data.loc[distances <= 1]
    #         # self._lens_click_handlers(self, x, y, filtered, distances)
    #     elif self.shape == 'xonly':
    #         distances = xRel.abs() / xRad
    #     elif self.shape == 'yonly':
    #         distances = yRel.abs() / yRad
    #     else:
    #         raise TraitError('Other lens shape not supported yet.')

    #     filtered = self.data.loc[distances <= 1]
    #     self._lens_click_handlers(self, x, y, filtered, distances)

    # def _handle_frontend_msg(self, _widget, payload, _buffers):
    #     """Handle a msg from the front-end.
    #     Parameters
    #     ----------
    #     payload: dict
    #         Content of the msg.
    #     """
    #     if payload.get('event', '') == 'lens':
    #         self.lens_click(**payload)
