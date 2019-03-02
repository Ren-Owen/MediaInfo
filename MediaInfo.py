#!/usr/bin/env python3

# author : renpeng
# github : https://github.com/laodifang
# description : media information
# date : 2015-09-24

import os, sys, re, subprocess, json

class MediaInfo :
    def __init__(self, **kwargs) :
        self.filename = kwargs.get('filename')
        self.cmd      = kwargs.get('cmd')
        self.info     = dict()

        if self.filename == None :
            self.filename = ''

        if self.cmd == None :
            for cmdpath in os.environ['PATH'].split(':') :
                if os.path.isdir(cmdpath) and 'mediainfo' in os.listdir(cmdpath) :
                    self.cmd = cmdpath + '/mediainfo'
                elif os.path.isdir(cmdpath) and 'ffprobe' in os.listdir(cmdpath) :
                    self.cmd = cmdpath + '/ffprobe'
                
            if self.cmd == None :
                self.cmd = ''

    def getInfo(self) :
        if not os.path.exists(self.filename) or not os.path.exists(self.cmd) :
            return None

        cmdName = os.path.basename(self.cmd)

        if cmdName == 'ffprobe' :
            self._ffmpegGetInfo()
        elif cmdName == 'mediainfo' :
            self._mediainfoGetInfo()
        
        return self.info


    def _ffmpegGetInfo(self) :
        cmd         = self.cmd + ' -loglevel quiet -print_format json -show_format -show_streams -show_error -count_frames -i ' + self.filename
        outputBytes = ''

        try :
            outputBytes = subprocess.check_output(cmd, shell = True)
        except subprocess.CalledProcessError as e :
            return ''

        outputText = outputBytes.decode('utf-8')
        self.info  = self._ffmpegGetInfoJson(outputText)

    def _ffmpegGetInfoJson(self, sourceString) :
        mediaInfo = dict()
        infoDict  = dict()

        try :
            infoDict = json.loads(sourceString)
        except json.JSONDecodeError as err :
            return mediaInfo

        mediaInfo['container'] = infoDict.get('format').get('format_name')
        mediaInfo['fileSize']  = infoDict.get('format').get('size')
        mediaInfo['duration']  = infoDict.get('format').get('duration')
        mediaInfo['bitrate']   = infoDict.get('format').get('bit_rate')

        videoStreamIndex = None
        audioStreamIndex = None

        for item in infoDict.get('streams') :
            codec_type = item.get('codec_type')

            if codec_type == 'video' :
                videoStreamIndex       = item.get('index')
                mediaInfo['haveVideo'] = 1
            elif codec_type == 'audio' :
                audioStreamIndex       = item.get('index')
                mediaInfo['haveAudio'] = 1

        if mediaInfo.get('haveVideo') :
            mediaInfo['videoCodec']        = infoDict.get('streams')[videoStreamIndex].get('codec_name')
            mediaInfo['videoCodecProfile'] = infoDict.get('streams')[videoStreamIndex].get('profile')
            mediaInfo['videoDuration']     = infoDict.get('streams')[videoStreamIndex].get('duration')
            mediaInfo['videoBitrate']      = infoDict.get('streams')[videoStreamIndex].get('bit_rate')
            mediaInfo['videoWidth']        = infoDict.get('streams')[videoStreamIndex].get('width')
            mediaInfo['videoHeight']       = infoDict.get('streams')[videoStreamIndex].get('height')
            mediaInfo['videoAspectRatio']  = infoDict.get('streams')[videoStreamIndex].get('display_aspect_ratio')
            mediaInfo['videoFrameRate']    = infoDict.get('streams')[videoStreamIndex].get('r_frame_rate')
            mediaInfo['videoFrameCount']   = infoDict.get('streams')[videoStreamIndex].get('nb_read_frames')

        if mediaInfo.get('haveAudio') : 
            mediaInfo['audioCodec']        = infoDict.get('streams')[audioStreamIndex].get('codec_name')
            mediaInfo['audioCodecProfile'] = infoDict.get('streams')[audioStreamIndex].get('profile')
            mediaInfo['audioDuration']     = infoDict.get('streams')[audioStreamIndex].get('duration')
            mediaInfo['audioBitrate']      = infoDict.get('streams')[audioStreamIndex].get('bit_rate')
            mediaInfo['audioChannel']      = infoDict.get('streams')[audioStreamIndex].get('channels')
            mediaInfo['audioSamplingRate'] = infoDict.get('streams')[audioStreamIndex].get('sample_rate')
            mediaInfo['audioFrameCount']   = infoDict.get('streams')[audioStreamIndex].get('nb_read_frames')

        return mediaInfo

    def _mediainfoGetInfo(self) :
        prevPath    = os.getcwd()
        newPath     = os.path.abspath(os.path.dirname(self.filename))
        file        = os.path.basename(self.filename)

        cmd         = self.cmd + ' -f ' + file
        outputBytes = ''

        try :
            os.chdir(newPath)
            try :
                outputBytes = subprocess.check_output(cmd, shell = True)
            except subprocess.CalledProcessError as e :
                return ''

            outputText = outputBytes.decode('utf-8')
        except IOError :
            os.chdir(prevPath)
            return ''
        finally:
            os.chdir(prevPath)

        self.info  = self._mediainfoGetInfoRegex(outputText)

    def _mediainfoGetInfoRegex(self, sourceString) :
        mediaInfo   = dict()
        
        general     = re.search("(^General\n.*?\n\n)", sourceString, re.S)
        if general :
            generalInfo = general.group(0)
        
            container   = re.search("Format\s*:\s*([\w\_\-\\\/\. ]+)\n",    generalInfo, re.S)
            fileSize    = re.search("File size\s*:\s*(\d+)\.?\d*\n",        generalInfo, re.S)
            duration    = re.search("Duration\s*:\s*(\d+)\.?\d*\n",         generalInfo, re.S)
            bitrate     = re.search("Overall bit rate\s*:\s*(\d+)\.?\d*\n", generalInfo, re.S)

            mediaInfo['container'] = container.group(1)
            mediaInfo['fileSize']  = fileSize.group(1)
            mediaInfo['duration']  = (str)((float)(duration.group(1))/1000)
            mediaInfo['bitrate']   = bitrate.group(1)

        video     = re.search("(\nVideo[\s\#\d]*\n.*?\n\n)", sourceString, re.S)
        if video :
            mediaInfo['haveVideo'] = 1
            videoInfo = video.group(0)

            videoCodec        = re.search("Codec(?:\sID)?\s*:\s*([\w\_\-\\\/\. ]+)\n",  videoInfo, re.S)
            videoCodecProfile = re.search("Codec profile\s*:\s*([\w\_\-\\\/\@\. ]+)\n", videoInfo, re.S)
            videoDuration     = re.search("Duration\s*:\s*(\d+)\.?\d*\n",               videoInfo, re.S)
            videoBitrate      = re.search("Bit rate\s*:\s*(\d+)\n",                     videoInfo, re.S)
            videoWidth        = re.search("Width\s*:\s*(\d+)\n",                        videoInfo, re.S)
            videoHeight       = re.search("Height\s*:\s*(\d+)\n",                       videoInfo, re.S)
            videoAspectRatio  = re.search("Display aspect ratio\s*:\s*([\d\.]+)\n",     videoInfo, re.S)
            videoFrameRate    = re.search("Frame rate\s*:\s*([\d\.]+)\n",               videoInfo, re.S)
            videoFrameCount   = re.search("Frame count\s*:\s*(\d+)\.?\d*\n",            videoInfo, re.S)

            if videoCodec :
                mediaInfo['videoCodec'] = videoCodec.group(1)
            if videoCodecProfile :
                mediaInfo['videoCodecProfile'] = videoCodecProfile.group(1)
            if videoDuration :
                mediaInfo['videoDuration'] = (str)((float)(videoDuration.group(1))/1000)
            if videoBitrate :
                mediaInfo['videoBitrate'] = videoBitrate.group(1)
            if videoWidth :
                mediaInfo['videoWidth'] = (int)(videoWidth.group(1))
            if videoHeight :
                mediaInfo['videoHeight'] = (int)(videoHeight.group(1))
            if videoAspectRatio :
                mediaInfo['videoAspectRatio'] = videoAspectRatio.group(1)
            if videoFrameRate :
                mediaInfo['videoFrameRate'] = videoFrameRate.group(1)
            if videoFrameCount :
                mediaInfo['videoFrameCount'] = videoFrameCount.group(1)

        audio     = re.search("(\nAudio[\s\#\d]*\n.*?\n\n)", sourceString, re.S)
        if audio :
            mediaInfo['haveAudio'] = 1
            audioInfo = audio.group(0)

            tmpAudioCodec     = re.search("Codec(?:\sID)?\s*:\s*([\w\_\-\\\/ ]+)\n",    audioInfo, re.S)
            audioCodec        = re.search("\w+", tmpAudioCodec.group(1), re.S)
            audioCodecProfile = re.search("Codec profile\s*:\s*([\w\_\-\\\/\@\. ]+)\n", audioInfo, re.S)
            if audioCodecProfile is None :
                audioCodecProfile = re.search("Format profile\s*:\s*([\w\_\-\\\/\@\. ]+)\n", audioInfo, re.S)

            audioDuration     = re.search("Duration\s*:\s*(\d+)\.?\d*\n", audioInfo, re.S)
            audioBitrate      = re.search("Bit rate\s*:\s*(\d+)\n",       audioInfo, re.S)
            audioChannel      = re.search("Channel\(s\)\s*:\s*(\d+)\n",   audioInfo, re.S)
            samplingRate      = re.search("Sampling rate\s*:\s*([\w\_\-\\\/\@\. ]+)\n", audioInfo, re.S)
            audioSamplingRate = re.search("\d+", samplingRate.group(1), re.S)
            
            if audioCodec :
                mediaInfo['audioCodec'] = audioCodec.group(0)
            if audioCodecProfile :
                mediaInfo['audioCodecProfile'] = audioCodecProfile.group(1)
            if audioDuration :
                mediaInfo['audioDuration'] = (str)((float)(audioDuration.group(1))/1000)
            if audioBitrate :
                mediaInfo['audioBitrate'] = audioBitrate.group(1)
            if audioChannel :
                mediaInfo['audioChannel'] = audioChannel.group(1)
            if audioSamplingRate :
                mediaInfo['audioSamplingRate'] = audioSamplingRate.group(0)

        return mediaInfo
