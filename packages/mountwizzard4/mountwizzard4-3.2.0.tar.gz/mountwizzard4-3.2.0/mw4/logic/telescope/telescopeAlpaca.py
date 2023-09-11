############################################################
# -*- coding: utf-8 -*-
#
#       #   #  #   #   #    #
#      ##  ##  #  ##  #    #
#     # # # #  # # # #    #  #
#    #  ##  #  ##  ##    ######
#   #   #   #  #   #       #
#
# Python-based Tool for interaction with the 10micron mounts
# GUI with PyQT5 for python
#
# written in python3, (c) 2019-2023 by mworion
# Licence APL2.0
#
###########################################################
# standard libraries

# external packages

# local imports
from base.alpacaClass import AlpacaClass


class TelescopeAlpaca(AlpacaClass):
    """
    """

    __all__ = ['TelescopeAlpaca']

    def __init__(self, app=None, signals=None, data=None):
        super().__init__(app=app, data=data)

        self.signals = signals
        self.data = data

    def workerGetInitialConfig(self):
        """
        :return: true for test purpose
        """
        super().workerGetInitialConfig()
        self.getAndStoreAlpacaProperty('aperturediameter',
                                       'TELESCOPE_INFO.TELESCOPE_APERTURE')
        self.getAndStoreAlpacaProperty('focallength',
                                       'TELESCOPE_INFO.TELESCOPE_FOCAL_LENGTH')
        return True
