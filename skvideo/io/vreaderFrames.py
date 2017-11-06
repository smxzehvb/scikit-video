
from itertools import compress

#from ..utils import *
from .io import vreader
from ..ffprobeFrames import ffprobeFrames
#from .ffmpeg import FFmpegReader
#from .ffmpeg import FFmpegWriter
#from .avconv import LibAVReader
#from .avconv import LibAVWriter
#from .. import _HAS_FFMPEG
#from .. import _HAS_AVCONV



def vreaderFrameTypeSelector(fname, height=0, width=0, num_frames=0, as_grey=False, inputdict=None, outputdict=None, selectIframes = True, selectPframes = False, selectBframes = False, verbosity=0):
    """Load a video through the use of a generator.

    Parameters
    ----------
    fname : string
        Video file name; passed to vreader().

    height : int
        Set the source video height used for decoding; passed to vreader().

    width : int
        Set the source video width used for decoding; passed to vreader().

    num_frames : int
        Only read the first `num_frames` number of frames from video; passed to vreader().

    as_grey : bool
        If true, only load the luminance channel of the input video; passed to vreader().

    inputdict : dict
        Input dictionary parameters, i.e. how to interpret the input file; passed to vreader().

    outputdict : dict
        Output dictionary parameters, i.e. how to encode the data
        between backend and python; passed to vreader().

    selectIframes : bool
        If True, return I frames from video. Default is True.

    selectPframes : bool
        If True, return P frames from video.  Default is False.

    selectBframes : bool
        If True, return B frames from video. Default is False.

    verbosity : int
        Passed to vreader().


    Returns
    -------
    vid_gen : generator
        returns ndarrays, shape (M, N, C) where
        M is frame height, N is frame width, and
        C is number of channels per pixel


    Note
    ----
        The frame selection for each type (selectIframes, selectPframes, selectBframes) 
        must be explicitly set True or False for each of the three types to achieve the
        desired combination of frame types.  


    """

    # raise error if no select*frames True
    if not any([selectIframes, selectPframes, selectBframes]):
        raise ValueError("No frames selected!")

    # call vreader to return a generator
    videogen = vreader(fname=fname, height=height, width=width, num_frames=num_frames, as_grey=as_grey, inputdict=inputdict, outputdict=outputdict, backend='ffmpeg', verbosity=verbosity) 

    # easiest case: return all frame types
    if all([selectIframes, selectPframes, selectBframes]):
        return videogen

    else: # we need more information to select frames
        # use ffprobeFrames to get metadata for all video frames (discard audio frame info)
        _, videoframeinfo = ffprobeFrames(fname)

        # get user's requested frame types
        selecttypes = []

        if selectIframes:
            selecttypes.append('I')
        if selectPframes:
            selecttypes.append('P')
        if selectBframes:
            selecttypes.append('B')

        # create list of bools--whether we want that frame or not
        selectmap = [(vf['@pict_type'].upper() in selecttypes) for idx, vf in enumerate(videoframeinfo)]

        # in some cases, we don't end up filtering, 
        # e.g. if user asked for only I and P, but the video did not have B frames anyway
        if all(selectmap):
            return videogen
        # otherwise use itertools compress to select frames 
        else:
            videogen = compress(videogen, selectmap)
            return videogen

