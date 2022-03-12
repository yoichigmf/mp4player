# -*- coding: utf-8 -*-
"""
/***************************************************************************
 MP4player
                                 A QGIS plugin
 play MP4 movie with gps log
 Generated by Plugin Builder: http://g-sherman.github.io/Qgis-Plugin-Builder/
                             -------------------
        begin                : 2022-03-12
        copyright            : (C) 2022 by Yoichi Kayama/aeroasahi corporation
        email                : yoichi.kayama@gmail.com
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load MP4player class from file MP4player.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .MP4player import MP4player
    return MP4player(iface)
