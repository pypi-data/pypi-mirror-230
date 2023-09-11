# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file './mw4/gui/widgets/satellite.ui'
#
# Created by: PyQt5 UI code generator 5.15.9
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_SatelliteDialog(object):
    def setupUi(self, SatelliteDialog):
        SatelliteDialog.setObjectName("SatelliteDialog")
        SatelliteDialog.resize(800, 600)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(SatelliteDialog.sizePolicy().hasHeightForWidth())
        SatelliteDialog.setSizePolicy(sizePolicy)
        SatelliteDialog.setMinimumSize(QtCore.QSize(800, 285))
        SatelliteDialog.setMaximumSize(QtCore.QSize(1600, 600))
        SatelliteDialog.setSizeIncrement(QtCore.QSize(10, 10))
        SatelliteDialog.setBaseSize(QtCore.QSize(10, 10))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(10)
        SatelliteDialog.setFont(font)
        self.gridLayout = QtWidgets.QGridLayout(SatelliteDialog)
        self.gridLayout.setContentsMargins(4, 8, 4, 4)
        self.gridLayout.setSpacing(4)
        self.gridLayout.setObjectName("gridLayout")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setContentsMargins(4, 4, 4, 4)
        self.verticalLayout.setSpacing(4)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout_5 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.label_273 = QtWidgets.QLabel(SatelliteDialog)
        self.label_273.setMinimumSize(QtCore.QSize(0, 25))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(10)
        font.setBold(False)
        self.label_273.setFont(font)
        self.label_273.setObjectName("label_273")
        self.horizontalLayout_5.addWidget(self.label_273)
        self.satLatitude = QtWidgets.QLineEdit(SatelliteDialog)
        self.satLatitude.setEnabled(True)
        self.satLatitude.setMinimumSize(QtCore.QSize(0, 25))
        self.satLatitude.setMaximumSize(QtCore.QSize(60, 16777215))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(10)
        font.setBold(False)
        self.satLatitude.setFont(font)
        self.satLatitude.setMouseTracking(False)
        self.satLatitude.setAcceptDrops(False)
        self.satLatitude.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.satLatitude.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.satLatitude.setReadOnly(True)
        self.satLatitude.setObjectName("satLatitude")
        self.horizontalLayout_5.addWidget(self.satLatitude)
        self.label_330 = QtWidgets.QLabel(SatelliteDialog)
        self.label_330.setMinimumSize(QtCore.QSize(0, 25))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(10)
        font.setBold(False)
        self.label_330.setFont(font)
        self.label_330.setAlignment(QtCore.Qt.AlignCenter)
        self.label_330.setWordWrap(False)
        self.label_330.setObjectName("label_330")
        self.horizontalLayout_5.addWidget(self.label_330)
        spacerItem = QtWidgets.QSpacerItem(20, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_5.addItem(spacerItem)
        self.label_333 = QtWidgets.QLabel(SatelliteDialog)
        self.label_333.setMinimumSize(QtCore.QSize(0, 25))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(10)
        font.setBold(False)
        self.label_333.setFont(font)
        self.label_333.setObjectName("label_333")
        self.horizontalLayout_5.addWidget(self.label_333)
        self.satLongitude = QtWidgets.QLineEdit(SatelliteDialog)
        self.satLongitude.setEnabled(True)
        self.satLongitude.setMinimumSize(QtCore.QSize(0, 25))
        self.satLongitude.setMaximumSize(QtCore.QSize(60, 16777215))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(10)
        font.setBold(False)
        self.satLongitude.setFont(font)
        self.satLongitude.setMouseTracking(False)
        self.satLongitude.setAcceptDrops(False)
        self.satLongitude.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.satLongitude.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.satLongitude.setReadOnly(True)
        self.satLongitude.setObjectName("satLongitude")
        self.horizontalLayout_5.addWidget(self.satLongitude)
        self.label_205 = QtWidgets.QLabel(SatelliteDialog)
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(10)
        font.setBold(False)
        self.label_205.setFont(font)
        self.label_205.setAlignment(QtCore.Qt.AlignCenter)
        self.label_205.setWordWrap(False)
        self.label_205.setObjectName("label_205")
        self.horizontalLayout_5.addWidget(self.label_205)
        spacerItem1 = QtWidgets.QSpacerItem(20, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_5.addItem(spacerItem1)
        self.label_238 = QtWidgets.QLabel(SatelliteDialog)
        self.label_238.setMinimumSize(QtCore.QSize(0, 25))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(10)
        font.setBold(False)
        self.label_238.setFont(font)
        self.label_238.setObjectName("label_238")
        self.horizontalLayout_5.addWidget(self.label_238)
        self.satAzimuth = QtWidgets.QLineEdit(SatelliteDialog)
        self.satAzimuth.setEnabled(True)
        self.satAzimuth.setMinimumSize(QtCore.QSize(0, 25))
        self.satAzimuth.setMaximumSize(QtCore.QSize(60, 16777215))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(10)
        font.setBold(False)
        self.satAzimuth.setFont(font)
        self.satAzimuth.setMouseTracking(False)
        self.satAzimuth.setAcceptDrops(False)
        self.satAzimuth.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.satAzimuth.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.satAzimuth.setReadOnly(True)
        self.satAzimuth.setObjectName("satAzimuth")
        self.horizontalLayout_5.addWidget(self.satAzimuth)
        self.label_208 = QtWidgets.QLabel(SatelliteDialog)
        self.label_208.setMinimumSize(QtCore.QSize(0, 25))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(10)
        font.setBold(False)
        self.label_208.setFont(font)
        self.label_208.setAlignment(QtCore.Qt.AlignCenter)
        self.label_208.setWordWrap(False)
        self.label_208.setObjectName("label_208")
        self.horizontalLayout_5.addWidget(self.label_208)
        spacerItem2 = QtWidgets.QSpacerItem(20, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_5.addItem(spacerItem2)
        self.label_297 = QtWidgets.QLabel(SatelliteDialog)
        self.label_297.setMinimumSize(QtCore.QSize(0, 25))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(10)
        font.setBold(False)
        self.label_297.setFont(font)
        self.label_297.setObjectName("label_297")
        self.horizontalLayout_5.addWidget(self.label_297)
        self.satAltitude = QtWidgets.QLineEdit(SatelliteDialog)
        self.satAltitude.setEnabled(True)
        self.satAltitude.setMinimumSize(QtCore.QSize(0, 25))
        self.satAltitude.setMaximumSize(QtCore.QSize(60, 16777215))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(10)
        font.setBold(False)
        self.satAltitude.setFont(font)
        self.satAltitude.setMouseTracking(False)
        self.satAltitude.setAcceptDrops(False)
        self.satAltitude.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.satAltitude.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.satAltitude.setReadOnly(True)
        self.satAltitude.setObjectName("satAltitude")
        self.horizontalLayout_5.addWidget(self.satAltitude)
        self.label_331 = QtWidgets.QLabel(SatelliteDialog)
        self.label_331.setMinimumSize(QtCore.QSize(0, 25))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(10)
        font.setBold(False)
        self.label_331.setFont(font)
        self.label_331.setAlignment(QtCore.Qt.AlignCenter)
        self.label_331.setWordWrap(False)
        self.label_331.setObjectName("label_331")
        self.horizontalLayout_5.addWidget(self.label_331)
        spacerItem3 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_5.addItem(spacerItem3)
        self.horizontalLayout_5.setStretch(7, 1)
        self.horizontalLayout_5.setStretch(15, 1)
        self.verticalLayout.addLayout(self.horizontalLayout_5)
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.groupEarth = QtWidgets.QGroupBox(SatelliteDialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.groupEarth.sizePolicy().hasHeightForWidth())
        self.groupEarth.setSizePolicy(sizePolicy)
        self.groupEarth.setProperty("large", True)
        self.groupEarth.setObjectName("groupEarth")
        self.gridLayout_5 = QtWidgets.QGridLayout(self.groupEarth)
        self.gridLayout_5.setContentsMargins(4, 12, 8, 4)
        self.gridLayout_5.setSpacing(0)
        self.gridLayout_5.setObjectName("gridLayout_5")
        self.satEarth = PlotBase(self.groupEarth)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.satEarth.sizePolicy().hasHeightForWidth())
        self.satEarth.setSizePolicy(sizePolicy)
        self.satEarth.setToolTip("")
        self.satEarth.setObjectName("satEarth")
        self.gridLayout_5.addWidget(self.satEarth, 0, 0, 1, 1)
        self.horizontalLayout_4.addWidget(self.groupEarth)
        self.groupHorizon = QtWidgets.QGroupBox(SatelliteDialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.groupHorizon.sizePolicy().hasHeightForWidth())
        self.groupHorizon.setSizePolicy(sizePolicy)
        self.groupHorizon.setProperty("large", True)
        self.groupHorizon.setObjectName("groupHorizon")
        self.gridLayout_4 = QtWidgets.QGridLayout(self.groupHorizon)
        self.gridLayout_4.setContentsMargins(4, 12, 8, 4)
        self.gridLayout_4.setSpacing(0)
        self.gridLayout_4.setObjectName("gridLayout_4")
        self.satHorizon = PlotBase(self.groupHorizon)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.satHorizon.sizePolicy().hasHeightForWidth())
        self.satHorizon.setSizePolicy(sizePolicy)
        self.satHorizon.setToolTip("")
        self.satHorizon.setObjectName("satHorizon")
        self.gridLayout_4.addWidget(self.satHorizon, 0, 0, 1, 1)
        self.horizontalLayout_4.addWidget(self.groupHorizon)
        self.verticalLayout.addLayout(self.horizontalLayout_4)
        self.gridLayout.addLayout(self.verticalLayout, 0, 0, 1, 1)

        self.retranslateUi(SatelliteDialog)
        QtCore.QMetaObject.connectSlotsByName(SatelliteDialog)

    def retranslateUi(self, SatelliteDialog):
        _translate = QtCore.QCoreApplication.translate
        SatelliteDialog.setWindowTitle(_translate("SatelliteDialog", "Satellite"))
        self.label_273.setText(_translate("SatelliteDialog", "Latitude"))
        self.satLatitude.setToolTip(_translate("SatelliteDialog", "Actual latitude where the satellite could be seen in zenith."))
        self.satLatitude.setText(_translate("SatelliteDialog", "-"))
        self.label_330.setText(_translate("SatelliteDialog", "°"))
        self.label_333.setText(_translate("SatelliteDialog", "Longitude"))
        self.satLongitude.setToolTip(_translate("SatelliteDialog", "Actual longitude where the satellite could be seen in zenith."))
        self.satLongitude.setText(_translate("SatelliteDialog", "-"))
        self.label_205.setText(_translate("SatelliteDialog", "°"))
        self.label_238.setText(_translate("SatelliteDialog", "Azimuth"))
        self.satAzimuth.setToolTip(_translate("SatelliteDialog", "Actual azimuth of the satelite from observers position."))
        self.satAzimuth.setText(_translate("SatelliteDialog", "-"))
        self.label_208.setText(_translate("SatelliteDialog", "°"))
        self.label_297.setText(_translate("SatelliteDialog", "Altitude"))
        self.satAltitude.setToolTip(_translate("SatelliteDialog", "Actual altitude of the satelite from observers position."))
        self.satAltitude.setText(_translate("SatelliteDialog", "-"))
        self.label_331.setText(_translate("SatelliteDialog", "°"))
        self.groupEarth.setToolTip(_translate("SatelliteDialog", "<html><head/><body><p>Shows the satellite path vertical over ground.</p></body></html>"))
        self.groupEarth.setTitle(_translate("SatelliteDialog", "Satellite path over earth surface"))
        self.groupHorizon.setToolTip(_translate("SatelliteDialog", "Shows the visible track of the satellite when being observed from the position of the mount. "))
        self.groupHorizon.setTitle(_translate("SatelliteDialog", "Satellite path over horizon from observer location"))
from gui.utilities.tools4pyqtgraph import PlotBase


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    SatelliteDialog = QtWidgets.QWidget()
    ui = Ui_SatelliteDialog()
    ui.setupUi(SatelliteDialog)
    SatelliteDialog.show()
    sys.exit(app.exec_())
