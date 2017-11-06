import subprocess as sp

from ..utils import *
from .. import _HAS_FFMPEG
from .. import _FFMPEG_PATH
from .. import _FFPROBE_APPLICATION

def ffprobeFrames(filename):
    """Get frame-level metadata by using ffprobe.

    Checks the output of ffprobe on the desired video
    file. MetaData is then parsed into two lists of 
    dictionaries--one list for audio frames, and one for  
    video frames.

    Parameters
    ----------
    filename : string
        Path to the video file.

    Returns
    -------
    audioDicts : list of dict
       List of dictionaries containing all audio frame information 
       (one dict per audio frame) about the passed-in source video.
    videoDicts : list of dict
       List of dictionaries containing all video frame information 
       (one dict per video frame) about the passed-in source video.


    """
    # check if FFMPEG exists in the path
    assert _HAS_FFMPEG, "Cannot find installation of real FFmpeg (which comes with ffprobe)."

    try:
        command = [_FFMPEG_PATH + "/" + _FFPROBE_APPLICATION, "-v", "error", "-show_frames", "-print_format", "xml", filename]

        # simply get std output
        xml = check_output(command)

        d = xmltodictparser(xml)["ffprobe"]

        d = d["frames"]


        # filter by frame media_type
        audioframes = list(filter(lambda f: f["@media_type"].lower() in ["audio"], d["frame"]))

        videoframes = list(filter(lambda f: f["@media_type"].lower() in ["video"], d["frame"]))


        return audioframes, videoframes

    except:
        return [], []
