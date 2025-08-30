import sys
import argparse


def get_arguments():
    """Parse command line arguments"""
    # Create the parser
    parser = argparse.ArgumentParser(description='A script to download and process videos.')

    # Add arguments
    parser.add_argument('--folder', default='.', type=str, help='Current folder work')
    parser.add_argument('-f','--file', default='t-yt-dl.txt', type=str, help='File content link youtube')
    parser.add_argument('-sf', '--sub-format', default='vtt', type=str, help='Type Subformat of the subtitle')
    parser.add_argument('-sl', '--sub-lang', default='id', type=str, help='Language of the subtitle')
    parser.add_argument('-is', '--is-search', type=bool, default=False, help='Is Search using yt-dlp -F ')
    parser.add_argument('-ca', '--code-audio', type=str, default="140", help='The code audio for download file ')
    parser.add_argument('-cv', '--code-video', type=str, default="136", help='The code video for download file')
    parser.add_argument('-ea', '--ext-audio', type=str, default="m4a", help='The ext audio for download file')
    parser.add_argument('-ev', '--ext-video', type=str, default="mp4", help='The ext video for download file')
    parser.add_argument('-ev2', '--ext-video2', type=str, default="mkv,webm", help='The ext full video for download file')
    parser.add_argument('-ia', '--info-audio', type=str, default="720p", help='The info audio for download file')
    parser.add_argument('-iv', '--info-video', type=str, default="en", help='The info video for download file')

    # Parse the arguments
    try:
        args = parser.parse_args()
    except SystemExit as e:
        parser.print_help()
        sys.exit()

    # Print the arguments (for demonstration purposes)
    print(f"Folder: {args.folder}, Sub Format: {args.sub_format}, Sub Lang: {args.sub_lang}, Is Search: {args.is_search}, "
          f"Code Audio: {args.code_audio}, Code Video: {args.code_video}, Ext Audio: {args.ext_audio}, Ext Video : {args.ext_video}, "
          f"Ext Full Video : {args.ext_video2}, Info Audio: {args.info_audio}, Info Vodeo: {args.info_video}"
          )
    
    return args


def build_yt_commands(args):
    """Build yt-dlp command strings based on arguments"""
    yt_cmd_sub = f"--extractor-args 'youtube:player_client=default,-web' --write-auto-subs --sub-format {args.sub_format} --sub-lang {args.sub_lang} --ignore-error --no-playlist "
    yt_cmd_audio = "".join(["-f ", args.code_audio, " --ignore-error --no-playlist"])
    yt_cmd_video = "".join(["-f ", args.code_video, " --ignore-error --no-playlist"])
    
    return yt_cmd_sub, yt_cmd_audio, yt_cmd_video