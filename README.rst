|

NAME
====

    A Python wrapper around the MediaInfo command line utility


|

SYNOPSIS
========

.. code-block::


    from MediaInfo import MediaInfo

    info     = MediaInfo(filename = '/media/test.ts')
    infoData = info.getInfo()

    info     = MediaInfo(filename = '/media/test.ts', cmd = '/usr/bin/ffprobe')
    infoData = info.getInfo()

    info     = MediaInfo(filename = '/media/test.ts', cmd = '/usr/bin/mediainfo')
    infoData = info.getInfo()


|

DESCRIPTION
===========
    MediaInfo gets information of media through ffprobe by default. Alternatively, ffprobe and mediainfo are also supported in configuration.
