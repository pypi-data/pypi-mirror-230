
# cd /home/lutzray/SyncQUO/Dev/AtomicSync/Sources/PostProduction/tictacsync/tictacsync
# while inotifywait --recursive -e close_write . ; do python entry.py  tests/multi2/; done
# above for linux


av_file_extensions = \
"""webm mkv flv flv vob ogv ogg drc gif gifv mng avi MTS M2TS TS mov qt
wmv yuv rm rmvb viv asf amv mp4 m4p m4v mpg mp2 mpeg mpe mpv mpg mpeg m2v
m4v svi 3gp 3g2 mxf roq nsv flv f4v f4p f4a f4b 3gp aa aac aax act aiff alac
amr ape au awb dss dvf flac gsm iklax ivs m4a m4b m4p mmf mp3 mpc msv nmf
ogg oga mogg opus ra rm raw rf64 sln tta voc vox wav wma wv webm 8svx cda MOV AVI
WEBM MKV FLV FLV VOB OGV OGG DRC GIF GIFV MNG AVI MTS M2TS TS MOV QT
WMV YUV RM RMVB VIV ASF AMV MP4 M4P M4V MPG MP2 MPEG MPE MPV MPG MPEG M2V
M4V SVI 3GP 3G2 MXF ROQ NSV FLV F4V F4P F4A F4B 3GP AA AAC AAX ACT AIFF ALAC
AMR APE AU AWB DSS DVF FLAC GSM IKLAX IVS M4A M4B M4P MMF MP3 MPC MSV NMF
OGG OGA MOGG OPUS RA RM RAW RF64 SLN TTA VOC VOX WAV WMA WV WEBM 8SVX CDA MOV AVI BWF""".split()

import ffmpeg
from pathlib import Path
from pprint import pformat 
# from collections import defaultdict
from loguru import logger
# import pathlib, os.path
import sox, tempfile
# from functools import reduce
from rich import print
from itertools import groupby
# from sklearn.cluster import AffinityPropagation
# import distance

# utility for accessing pathnames
def _pathname(tempfile_or_path):
    if isinstance(tempfile_or_path, str):
        return tempfile_or_path
    if isinstance(tempfile_or_path, Path):
        return str(tempfile_or_path)
    if isinstance(tempfile_or_path, tempfile._TemporaryFileWrapper):
        return tempfile_or_path.name
    else:
        raise Exception('%s should be Path or tempfile...'%tempfile_or_path)

def print_grby(grby):
    for key, keylist in grby:
        print('\ngrouped by %s:'%key)
        for e in keylist:
            print(' ', e)

def media_dict_from_path(p):
        probe = ffmpeg.probe(p)
        dev_UID, dev_type = get_device_ffprobe_UID(p)
        time_base = eval(probe['streams'][0]['time_base'])
        duration_in_secondes = float(probe['format']['duration'])
        sample_length = duration_in_secondes/time_base
        return {
            'path' : p,
            'device type' : dev_type,
            'sample length' : sample_length,
            'dev UID' : dev_UID
            }

def get_device_ffprobe_UID(file):
    """
    Tries to find an unique integer identifying the device that produced
    the file based on the string inside ffprobe metadata  without any
    reference to date nor length nor time. Find out with ffprobe the type
    of device: CAM or REC for videocamera or audio recorder.

    Device UIDs are used later in Montage._get_concatenated_audiofile_for()
    for grouping each audio or video clip along its own timeline track.
    
    Returns a tuple: (UID, string of device type)
    
    If an ffmpeg.Error occurs, returns (None, None)
    if no UID is found, but device type is identified, returns (None, device)

    """
    file = Path(file)
    # logger.debug('trying to find UID probe for %s'%file)
    try:
        probe = ffmpeg.probe(file)
    except ffmpeg.Error as e:
        print('ffmpeg.probe error')
        print(e.stderr, file)
        return None, None
        # fall back to folder name
    # print(file)
    # pprint(probe)
    streams = probe['streams']
    codecs = [stream['codec_type'] for stream in streams]
    device_type = 'CAM' if 'video' in codecs else 'REC'
    format_dict = probe['format'] # all files should have this
    if 'tags' in format_dict:
        probe_string = pformat(format_dict['tags'])
        probe_lines = [l for l in probe_string.split('\n') 
                if '_time' not in l 
                and 'time_' not in l 
                and 'date' not in l ]
        # this removes any metadata related to the file
        # but keeps metadata related to the device
        UID = hash(''.join(probe_lines))
    else:
        UID = None
        # print('no ffprobe UID for %s'%file)
    # UID += ' type: ' + device_type
    # logger.debug('ffprobe_UID is: %s'%UID)
    return UID, device_type

class Scanner:
    """
    Scan self.top_directory trying to detect the set of devices used for the shooting.
    Info collected by Scanner is later used to instanciate Recordings.

    Attributes:
        top_directory : string
            String of path of where to start searching for media files.
        media_paths : list of tuples (pathlib.Path, nice_file_alias)
            all found files with known extensions listed in av_file_extensions,
            populated after a call to _regroup_multifiles_if_any().
            If multifile recordings are found, they are merged into a
            tempfile.NamedTemporaryFile poly wav.
        devices_names : dict of str
            more evocative names for each device, keys are same as
            self.devices_UID_count
        media_dev_names : dict of str
            keys are elements of self.media_paths and values are
            values of self.devices_names

        found_media_files: list of dicts {
                'path' : as is ,
                'device type' : REC or CAM,
                'sample length' : as is
                'dev UID' : see get_device_ffprobe_UID()
                }
    """

    def __init__(self, top_directory):
        """
        Initialises Scanner

        """
        self.top_directory = top_directory
        # self.devices_UID_counts = defaultdict(int)
        # self.devices_names = {}
        # self.media_paths = []
        # self.media_dev_names = {}
        self.found_media_files = []
        self.found_multifiles = []


    def get_devices_number(self):
        return len(set([m['dev UID'] for m in self.found_media_files]))

    def _check_for_multifile_rec(self):
        """        
        Populates Scanner.found_multifiles using Scanner.found_media_files

        Modifies Scanner.found_media_files: only unique file recordings 
        will remains in the list.

        Returns nothing
        """
        sample_length_key = lambda m: m['sample length']
        medias = sorted(self.found_media_files, key=sample_length_key)
        # build lists from iterators for multiple reference
        media_grouped_by_length = [ (k, list(iterator)) for k, iterator
                        in groupby(medias, sample_length_key)]
        # print_grby(media_grouped_by_length)
        logger.debug('media_grouped_by_length %s'%media_grouped_by_length)
        unifile_recordings = []
        for length_in_sample, media_same_length in media_grouped_by_length:
            if len(media_same_length) == 1:
                unifile_recordings.append(media_same_length[0])
                continue
            devices = [m['dev UID'] for m in media_same_length]
            if len(set(devices)) !=1:
                print('files with same length but diff device?')
                for media in media_same_length:
                    print(' %s'%media['path'])
                print('put the offending file in its own folder and')
                print('rerun. Quitting...')
                quit()
            self.found_multifiles.append(media_same_length)
        self.found_media_files = unifile_recordings
        logger.debug('Scanner.found_media_files (unique): %s'%self.found_media_files)
        logger.debug('Scanner.found_multifiles: %s'%self.found_multifiles)
        if len(self.found_multifiles) !=0:
            print('\nFound those multifile recordings. If any error, move them into an exclusive folder and rerun:')
            # for mf in self.found_multifiles:
            #     print('\nIn folder [gold1]%s[/gold1]:'%mf[0]['path'].parent, end=' ')
            #     for f in mf:
            #         print('[gold1]%s[/gold1]; '%f['path'].name, end='')

            # print()
        return

    def _build_poly_WAV(self):
        """
        if any files in Scanner.found_multifiles, merge them into poly WAV
        and add them to Scanner.found_media_files

        """
        def _build_name(media_list):
            # if len(media_list) == 1:
            #     return path_list[0].stem
            s1 = str(media_list[0]['path'].stem)
            s2 = str(media_list[1]['path'].stem)
            # max_length = max([len(m['path'].stem) for m in media_list])
            first_diff_char_index = [c1==c2 for c1, c2 in
                zip(s1,s2)].index(False)
            # XXX_string = '_'*(max_length - first_diff_char_index)
            return s1[:first_diff_char_index] + '.WAV'
        for multi_files in self.found_multifiles:
            logger.debug('will merge %s'%[m['path'].name for m in multi_files])
            cbn = sox.Combiner()
            # output_fh = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
            # output_dir = tempfile.TemporaryDirectory()
            poly_dir = Path(self.top_directory)/Path('tictacsynced/polywav')
            # out_dir_path = Path(poly_dir.name)
            poly_dir.mkdir(exist_ok=True)
            out_path = poly_dir / Path(_build_name(multi_files))
            logger.debug('merge into %s'%out_path)
            # flattened_paths.append(out_path)
            new_WAV = {'path' : out_path, 'device type': 'REC'}
            new_WAV['sample length'] = multi_files[0]['sample length']
            new_WAV['dev UID'] = multi_files[0]['dev UID']
            self.found_media_files.append(new_WAV)
            multi = ' + '.join([pp['path'].name for pp in multi_files])
            filenames = [str(pp['path']) for pp in multi_files]
            logger.debug('sox.build args: %s %s'%(
                filenames,
                _pathname(out_path)))
            status = cbn.build(
                filenames,
                _pathname(out_path),
                combine_type='merge')
            logger.debug('sox.build status: %s'%status)
            print('Merged poly WAV [gold1]%s [/gold1]from [gold1]%s[/gold1]'%(
                _pathname(out_path), multi))
        logger.debug('new Scanner.found_media_files: %s'%self.found_media_files)



    def scan_media_and_build_devices_UID(self, recursive=True):
        """
        Scans self.top_directory recursively for files with known audio-video
        extensions. For each file found, a device fingerprint is obtained from
        their ffprobe result to ID the device used.


        Also looked for are multifile recordings: files with the exact same
        length. When done, calls

        Returns nothing

        Populates Scanner.found_media_files, a list of dict as
                {
                'path' : # as is,
                'device type' : 'CAM' or 'REC',
                'sample length' : # in samples
                'dev UID' : dev_UID or None
                }

        """
        # devices_UID_counts = defaultdict(int)
        files = Path(self.top_directory).rglob('*.*')
        paths = [
            p
            for p in files
            if p.suffix[1:] in av_file_extensions
            and 'tictacsynced' not in p.parts
        ]
        for p in paths:
            new_media = media_dict_from_path(p)
            self.found_media_files.append(new_media)
        logger.debug('Scanner.found_media_files = %s'%self.found_media_files)
        # logger.debug('all devices, Scanner.media_dev_names = %s'%self.media_dev_names)
        self._check_mixed_folders()
        self._use_folder_as_device_ID()
        self._check_for_multifile_rec()
        self._build_poly_WAV()
        logger.debug('before _regroup_multifiles_if_any()')
        logger.debug('scanner.found_media_files = %s'%self.found_media_files)
        # self._regroup_multifiles_if_any(paths)
        logger.debug('_regroup_multifiles_if_any() done,')
        # logger.debug('scanner.media_paths = %s'%self.media_paths)
        # logger.debug('all devices, Scanner.media_dev_names = %s'%self.media_dev_names)
        # self._flatten_multifile_to_poly()
        logger.debug('_flatten_multifile_to_poly() done,')
        # logger.debug('scanner.media_paths = %s'%self.media_paths)
        # self._make_device_names_from_UIDs(devices_UID_counts)
        # logger.debug('Scanner.media_dev_names = %s'%self.media_dev_names)
        # logger.debug('Scanner.media_paths = %s'%self.media_paths)
        # self._media_are_sorted_by_folders()

    def _use_folder_as_device_ID(self):
        """
        For each media in self.found_media_files replace existing dev_UID by
        folder name.

        Returns nothing
        """
        for m in self.found_media_files:
            folder_name = m['path'].parent.name
            # known_folder_name = [media['dev UID'] for media
            #     in self.found_media_files]
            # if folder_name not in known_folder_name:
            m['dev UID'] = folder_name
            # else:
            #     print('already existing folder name: [gold1]%s[/gold1] please change it and rerun'%m['path'].parent)
            #     quit()
        logger.debug(self.found_media_files)

    def _check_mixed_folders(self):
        """

        Checks for files in self.found_media_files for structure as following.

        Warns user and quit program for:
          A- folders with mix of video and audio
          B- folders with mix of uniquely identified devices and unUIDied ones
          C- folders with mixed audio (or video) devices
        
        Warns user but proceeds for:
          D- folder with only unUIDied files (overlaps will be check later)
        
        Proceeds silently if 
          E- all files in the folder are from the same device

        Returns nothing
        """
        folder_key = lambda m: m['path'].parent
        medias = sorted(self.found_media_files, key=folder_key)
        # build lists for multiple reference of iterators
        media_grouped_by_folder = [ (k, list(iterator)) for k, iterator
                        in groupby(medias, folder_key)]
        complete_path_folders = [e[0] for e in media_grouped_by_folder]
        name_of_folders = [p.name for p in complete_path_folders]
        logger.debug('complete_path_folders with media files %s'%complete_path_folders)
        logger.debug('name_of_folders with media files %s'%name_of_folders)
        unique_folder_names = set(name_of_folders)
        if len(unique_folder_names) != len(name_of_folders):
            print('There is conflicts for some folder names:')
            for f in [str(p) for p in complete_path_folders]:
                print(' [gold1]%s[/gold1]'%f)
            print('please rename and rerun. Quitting..')
            quit()
        # print(media_grouped_by_folder)
        for folder, list_of_medias_in_folder in media_grouped_by_folder:
            # list_of_medias_in_folder = list(media_files_same_folder_iterator)
            # check all medias are either video or audio recordings in folder
            # if not, warn user and quit.
            dev_types = set([m['device type'] for m in list_of_medias_in_folder])
            if len(dev_types) != 1:
                print('\nProblem while scanning for media files. In [gold1]%s[/gold1]:'%folder)
                print('There is a mix of video and audio files:')
                [print('[gold1]%s[/gold1]'%m['path'].name, end =', ')
                    for m in list_of_medias_in_folder]
                print('\nplease move them in exclusive folders and rerun.\n')
                quit()
            # dev_UID come from  Montage.get_device_ffprobe_UID().
            unidentified = [m for m in list_of_medias_in_folder
                if m['dev UID'] == None]
            UIDed = [m for m in list_of_medias_in_folder
                if m['dev UID'] != None]
            logger.debug('devices in folder %s:'%folder)
            logger.debug('  media with unknown devices %s'%unidentified)
            logger.debug('  media with UIDed devices %s'%UIDed)
            if False and len(unidentified) != 0 and len(UIDed) != 0:
                print('\nProblem while grouping files in [gold1]%s[/gold1]:'%folder)
                print('There is a mix of unidentifiable and identified devices.')
                print('Is this file:')
                for m in unidentified:
                    print(' [gold1]%s[/gold1]'%m['path'].name)
                answer = input("In the right folder?")
                if answer.upper() in ["Y", "YES"]:
                    continue
                elif answer.upper() in ["N", "NO"]:
                    # Do action you need
                    print('please move the following files in a folder named appropriately:\n')
                    quit()
            # if, in a folder, there's a mix of different identified devices,
            # Warn user and quit.
            # devices = set([m['dev UID'] for m in list_of_medias_in_folder])
            if len(dev_types) != 1:
                print('\nProblem while scanning for media files. In [gold1]%s[/gold1]:'%folder)
                print('There is a mix of files from different devices:')
                [print('[gold1]%s[/gold1]'%m['path'].name, end =', ')
                    for m in list_of_medias_in_folder]
                print('\nplease move them in exclusive folders and rerun.\n')
                quit()
            if len(unidentified) == len(list_of_medias_in_folder):
                # all unidentified
                if len(unidentified) > 1:
                    print('Assuming those files are from the same device:')
                    [print('[gold1]%s[/gold1]'%m['path'].name, end =', ')
                        for m in unidentified]
                    print('\nIf not, there\'s a risk of error: put them in exclusive folders and rerun.')
            # if we are here, the check is done: either 
            #   all files in folder are from unidentified device or
            #   all files in folder are from the same identified device
            return





