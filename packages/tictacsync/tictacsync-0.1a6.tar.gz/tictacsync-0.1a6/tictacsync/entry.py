"""
cd /Users/lutzray/SyncQUO/Dev/AtomicSync/Sources/PostProduction/tictacsync/tictacsync
while true; do fswatch . | python3 entry.py tests/mcam2; done

cd /Users/lutzray/SyncQUO/Dev/AtomicSync/Sources/PostProduction/tictacsync
while true; do fswatch -r . | python entry.py tests/data/timeline/mid2raw; done
while true; do fswatch -r . | python entry.py tests/data/timeline/1audio_pad; done

"""
print('Loading modules...', end='')

# I know, this is ugly, but I need those try's to
# run the command in my dev setting AND from
# a deployment set-up... surely I'm setting
# things wrong [TODO] find why and clean up this mess
try:
    from . import yaltc
except:
    import yaltc
try:
    from . import device_scanner
except:
    import device_scanner
try:
    from . import timeline
except:
    import timeline

import argparse
from loguru import logger
from pathlib import Path
# import os, sys
import os, sys
from rich.progress import track
# from pprint import pprint
from rich.console import Console
# from rich.text import Text
from rich.table import Table
from rich import print
# import itertools
# from datetime import timedelta

print(' done')


av_file_extensions = \
"""MOV webm mkv flv flv vob ogv ogg drc gif gifv mng avi MTS M2TS TS mov qt
wmv yuv rm rmvb viv asf amv mp4 m4p m4v mpg mp2 mpeg mpe mpv mpg mpeg m2v
m4v svi 3gp 3g2 mxf roq nsv flv f4v f4p f4a f4b 3gp aa aac aax act aiff alac
amr ape au awb dss dvf flac gsm iklax ivs m4a m4b m4p mmf mp3 mpc msv nmf
ogg oga mogg opus ra rm raw rf64 sln tta voc vox wav wma wv webm 8svx cda""".split()

logger.level("DEBUG", color="<yellow>")


def process_files_with_progress_bars(medias):
    recordings = []
    rec_with_yaltc = []
    times = []
    for m in track(medias,
            description="1/4 Initializing Recording objects:"):
        # file_alias = 'dummy'
        recordings.append(yaltc.Recording(m))
    for r in track(recordings,
            description="2/4   Checking if files have YaLTC:"):
        if r.seems_to_have_YaLTC_at_beginning():
            rec_with_yaltc.append(r)
    for r in track(rec_with_yaltc,
            description="3/4            Finding start times:"):
        times.append(r.get_start_time())
    return recordings, rec_with_yaltc, times

def process_files(medias):
    recordings = []
    rec_with_yaltc = []
    times = []
    for m in medias:
        recordings.append(yaltc.Recording(m))
    for r in recordings:
        print('%s duration %.2fs'%(r.AVpath.name, r.get_duration()))
        if r.seems_to_have_YaLTC_at_beginning():
            rec_with_yaltc.append(r)
    for r in rec_with_yaltc:
        times.append(r.get_start_time())
    return recordings, rec_with_yaltc, times

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
                "directory",
                type=str,
                nargs="+",
                help="path of media directory"
                )
    # parser.add_argument("directory", nargs="?", help="path of media directory")
    parser.add_argument('-v', action='store_true')
    args = parser.parse_args()
    # logger.info('arguments: %s'%args)
    # logger.remove()
    if not args.v:
        yaltc.logger.remove()
    # logger.add(sys.stdout, filter="__main__")
    # logger.add(sys.stdout, filter="device_scanner")
    # logger.add(sys.stdout, filter="yaltc")
    # logger.add(sys.stdout, filter="timeline")
    # logger.add(sys.stdout, filter=lambda r: r["function"] == "shrink_gaps_between_takes")
    # logger.add(sys.stdout, filter=lambda r: r["function"] == "get_timecode")
    # logger.add(sys.stdout, filter=lambda r: r["function"] == "_get_BFSK_symbols_boundaries")
    # logger.add(sys.stdout, filter=lambda r: r["function"] == "_get_BFSK_word_boundaries")
    top_dir = args.directory[0]
    if os.path.isfile(top_dir):
        # argumnent is a single file: do plots
        m = device_scanner.media_dict_from_path(Path(top_dir))
        a_rec = yaltc.Recording(m)
        a_rec._read_sound_find_YaLTC(0.5, 1.56)
        a_rec.decoder.make_silence_analysis_plot(
            title='word detection for\n%s'%(top_dir))
        time = a_rec.get_start_time(plot_slicing=True)
        if time != None:
            print('recording started at [gold1]%s[/gold1]'%time)
            print('true sample rate [gold1]%.3f Hz[/gold1]'%a_rec.true_samplerate)
            print('first sync at [gold1]%i[/gold1] samples'%a_rec.sync_position)
        else:
            print('Start time couldnt be determined')
        quit()
    if not os.path.isdir(top_dir):
        print('%s is not a directory or doesnt exist.'%top_dir)
        quit()
    scanner = device_scanner.Scanner(top_dir)
    (Path(top_dir)/Path('tictacsynced')).mkdir(exist_ok=True)
    # scanner.cluster_media_files_by_name()
    scanner.scan_media_and_build_devices_UID(recursive=False)
    print('\n\nFound [gold1]%i[/gold1] media files from [gold1]%i[/gold1] devices'%(
        len(scanner.found_media_files),
        scanner.get_devices_number()), end='')
    # print( ' devices: [gold1]%s[/gold1]'%(
    #             ' '.join(list(scanner.devices_names.values())),
    #             ))
    print('\nThese recordings will be analysed for timestamps:\n')
    for m in (scanner.found_media_files):
        # if len(p) > 1:
        #     continue
        # print('   ', '[gold1]%s[/gold1]'%file_alias)
        print('   ', '[gold1]%s[/gold1]'%m['path'].name)
    print()
    if not args.v:
        rez = process_files_with_progress_bars(scanner.found_media_files)
    else: # verbose, so no progress bars
        rez = process_files(scanner.found_media_files)
    recordings, rec_with_yaltc, times = rez
    print('\n\n')
    table = Table(title="tictacsync results")
    table.add_column("Recording\n", justify="center", style='gold1')
    table.add_column("YaLTC\nChannel", justify="center", style='gold1')
    # table.add_column("Device\n", justify="center", style='gold1')
    table.add_column("UTC times\nstart:end", justify="center", style='gold1')
    table.add_column("Clock drift\n(ppm)", justify="right", style='gold1')
    table.add_column("SN ratio\n(dB)", justify="center", style='gold1')
    recordings_with_time =  [
        rec 
        for rec in rec_with_yaltc
        if rec.get_start_time() != 'Failed'
        ]
    for r in recordings_with_time:
        start_HHMMSS = r.get_start_time().strftime("%Hh%Mm%Ss")
        end_MMSS = r.get_end_time().strftime("%Mm%Ss")
        times_range = start_HHMMSS + ':' + end_MMSS
        table.add_row(
            str(r.AVpath.name),
            str(r.YaLTC_channel),
            # r.device,
            times_range,
            # '%.6f'%(r.true_samplerate/1e3),
            '%2i'%(r.get_samplerate_drift()),
            '%.0f'%r.decoder.SN_ratio,
            )
    console = Console()
    console.print(table)
    n_devices = scanner.get_devices_number()
    # if n_devices > 2:
    #     print('\nMerging for more than 2 devices is not implemented yet, quitting...')
    #     quit()
    matcher = timeline.Matcher(recordings_with_time)
    matcher.scan_audio_for_each_ref_rec()
    print()
    for stitcher in track(matcher.video_mergers,
        description="4/4                  Merging videos:"):
        stitcher.build_audio_and_write_video(top_dir)

    # [stitcher.build_audio_and_write_video(top_dir) for stitcher in matcher.video_mergers]
    print()
    for stitcher in matcher.video_mergers:
        print('[gold1]%s[/gold1]'%stitcher.ref_recording.AVpath.name, end='')
        for audio in stitcher.matched_audio_recordings:
            print(' + [gold1]%s[/gold1]'%audio.AVpath.name, end='')
        print(' became [gold1]%s[/gold1]'%stitcher.ref_recording.final_synced_file.name)
    # matcher._build_otio_tracks_for_cam()
    matcher.shrink_gaps_between_takes()
    

if __name__ == '__main__':
    main()






