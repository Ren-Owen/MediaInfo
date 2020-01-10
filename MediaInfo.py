#!/usr/bin/env python3

# author: renpeng
# github: https://github.com/laodifang
# description: media information
# date: 2015-09-24

import os, sys, re, json
import subprocess
from shutil import which

def _internal_search(obj, name, pattern, string, group, permille=False, integral=False):
    m = re.search(pattern, string, re.S)
    if m:
        res = m.group(group)
        if permille:
            res = str(float(res)/1000.)
        if integral:
            res = int(res)
        obj[name] = res

class MediaInfo:
    def __init__(self, filename=None, cmd=None):
        self.filename = '' if filename is None else filename
        self.cmd      = cmd
        self.info     = {}
        if self.cmd is None:
            self.cmd = which("mediainfo")
            if self.cmd is None:
                self.cmd = which("ffprobe")
                if self.cmd == None:
                    self.cmd = ""
    def getInfo(self):
        if not all((os.path.isfile(sc) for sc in (self.filename, self.cmd))):
            return None
        cmdName = os.path.basename(self.cmd)
        if cmdName == 'ffprobe':
            self._ffmpegGetInfo()
        elif cmdName == 'mediainfo':
            self._mediainfoGetInfo()
        return self.info

    def _ffmpegGetInfo(self):
        try:
            outputBytes = subprocess.check_output([self.cmd, "-loglevel", "quiet", "-print_format", "json", "-show_format", "-show_streams", "-show_error", "-count_frames", "-i", self.filename])
        except Exception:
            return ''
        outputText = outputBytes.decode('utf-8')
        self.info  = self._ffmpegGetInfoJson(outputText)

    def _ffmpegGetInfoJson(self, sourceString):
        try:
            infoDict = json.loads(sourceString)
        except json.JSONDecodeError as err:
            return {}
        mediaInfo = {
            "container": infoDict['format'].get('format_name'),
            "fileSize": infoDict['format'].get('size'),
            "duration": infoDict['format'].get('duration'),
            "bitrate": infoDict['format'].get('bit_rate')
        }
        if infoDict['streams']:
            videoStreamIndex = None
            audioStreamIndex = None
            for stream in infoDict['streams']:
                codec_type = stream.get('codec_type')
                if codec_type == 'video':
                    videoStreamIndex       = stream.get('index')
                    mediaInfo['haveVideo'] = True
                elif codec_type == 'audio':
                    audioStreamIndex       = stream.get('index')
                    mediaInfo['haveAudio'] = True
            if videoStreamIndex is not None:
                mediaInfo['videoCodec']        = infoDict['streams'][videoStreamIndex].get('codec_name')
                mediaInfo['videoCodecProfile'] = infoDict['streams'][videoStreamIndex].get('profile')
                mediaInfo['videoDuration']     = infoDict['streams'][videoStreamIndex].get('duration')
                mediaInfo['videoBitrate']      = infoDict['streams'][videoStreamIndex].get('bit_rate')
                mediaInfo['videoWidth']        = infoDict['streams'][videoStreamIndex].get('width')
                mediaInfo['videoHeight']       = infoDict['streams'][videoStreamIndex].get('height')
                mediaInfo['videoAspectRatio']  = infoDict['streams'][videoStreamIndex].get('display_aspect_ratio')
                mediaInfo['videoFrameRate']    = infoDict['streams'][videoStreamIndex].get('r_frame_rate')
                mediaInfo['videoFrameCount']   = infoDict['streams'][videoStreamIndex].get('nb_read_frames')
            if audioStreamIndex is not None: 
                mediaInfo['audioCodec']        = infoDict['streams'][audioStreamIndex].get('codec_name')
                mediaInfo['audioCodecProfile'] = infoDict['streams'][audioStreamIndex].get('profile')
                mediaInfo['audioDuration']     = infoDict['streams'][audioStreamIndex].get('duration')
                mediaInfo['audioBitrate']      = infoDict['streams'][audioStreamIndex].get('bit_rate')
                mediaInfo['audioChannel']      = infoDict['streams'][audioStreamIndex].get('channels')
                mediaInfo['audioSamplingRate'] = infoDict['streams'][audioStreamIndex].get('sample_rate')
                mediaInfo['audioFrameCount']   = infoDict['streams'][audioStreamIndex].get('nb_read_frames')
        return mediaInfo

    def _mediainfoGetInfo(self):
        try:
            outputBytes = subprocess.check_output([self.cmd, "-f", self.filename])
        except Exception:
            return ''
        outputText = outputBytes.decode('utf-8')
        self.info  = self._mediainfoGetInfoRegex(outputText)

    def _mediainfoGetInfoRegex(self, sourceString):
        mediaInfo = {}
        general = re.search("^General\n.*?\n\n", sourceString, re.S)
        if general:
            generalInfo = general.group(0)
            _internal_search(mediaInfo, 'container', "Format\s*:\s*([\w\_\-\\\/\. ]+)\n",  generalInfo, 1)
            _internal_search(mediaInfo, 'fileSize', "File size\s*:\s*(\d+)\.?\d*\n",       generalInfo, 1)
            _internal_search(mediaInfo, 'duration', "Duration\s*:\s*(\d+)\.?\d*\n",        generalInfo, 1, permille=True)
            _internal_search(mediaInfo, 'bitrate', "Overall bit rate\s*:\s*(\d+)\.?\d*\n", generalInfo, 1)
        video = re.search("\nVideo[\s\#\d]*\n.*?\n\n", sourceString, re.S)
        if video:
            mediaInfo['haveVideo'] = 1
            videoInfo = video.group(0)
            _internal_search(mediaInfo, 'videoCodec', "Codec\s*:\s*([\w\_\-\\\/\. ]+)\n",                  videoInfo, 1)
            _internal_search(mediaInfo, 'videoCodecProfile', "Codec profile\s*:\s*([\w\_\-\\\/\@\. ]+)\n", videoInfo, 1)
            _internal_search(mediaInfo, 'videoDuration', "Duration\s*:\s*(\d+)\.?\d*\n",                   videoInfo, 1, permille=True)
            _internal_search(mediaInfo, 'videoBitrate', "Bit rate\s*:\s*(\d+)\n",                          videoInfo, 1)
            _internal_search(mediaInfo, 'videoWidth', "Width\s*:\s*(\d+)\n",                               videoInfo, 1, integral=True)
            _internal_search(mediaInfo, 'videoHeight', "Height\s*:\s*(\d+)\n",                             videoInfo, 1, integral=True)
            _internal_search(mediaInfo, 'videoAspectRatio', "Display aspect ratio\s*:\s*([\d\.]+)\n",      videoInfo, 1)
            _internal_search(mediaInfo, 'videoFrameRate', "Frame rate\s*:\s*([\d\.]+)\n",                  videoInfo, 1)
            _internal_search(mediaInfo, 'videoFrameCount', "Frame count\s*:\s*(\d+)\.?\d*\n",              videoInfo, 1)
        audio = re.search("(\nAudio[\s\#\d]*\n.*?\n\n)", sourceString, re.S)
        if audio:
            mediaInfo['haveAudio'] = 1
            audioInfo = audio.group(0)
            audioCodec = re.search("Codec\s*:\s*([\w\_\-\\\/ ]+)\n",                         audioInfo, re.S)
            if audioCodec:
                _internal_search(mediaInfo, 'audioCodec', "\w+",                             audioCodec.group(1), 0)
            audioCodecProfile = re.search("Codec profile\s*:\s*([\w\_\-\\\/\@\. ]+)\n",      audioInfo, re.S)
            if audioCodecProfile is None:
                audioCodecProfile = re.search("Format profile\s*:\s*([\w\_\-\\\/\@\. ]+)\n", audioInfo, re.S)
            if audioCodecProfile:
                mediaInfo['audioCodecProfile'] = audioCodecProfile.group(1)
            _internal_search(mediaInfo, 'audioDuration', "Duration\s*:\s*(\d+)\.?\d*\n",     audioInfo, 1, permille=True)
            _internal_search(mediaInfo, 'audioBitrate', "Bit rate\s*:\s*(\d+)\n",            audioInfo, 1)
            _internal_search(mediaInfo, 'audioChannel', "Channel\(s\)\s*:\s*(\d+)\n",        audioInfo, 1)
            audioSamplingRate = re.search("Sampling rate\s*:\s*([\w\_\-\\\/\@\. ]+)\n",      audioInfo, re.S)
            if audioSamplingRate:
                _internal_search(mediaInfo, 'audioSamplingRate', "\d+",                      audioSamplingRate.group(1), 0)
        return mediaInfo
