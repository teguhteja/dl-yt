import sys
import os
import subprocess
import asyncio
import argparse
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter, SRTFormatter

YT_DLP = '~/Videos/_/yt-dlp --cookies ~/Videos/_/cookies.txt'
YT_CMD = '--write-auto-subs --sub-format vtt --sub-lang id -f 136,140 --ignore-error --no-playlist -a --cookies ~/Videos/_/cookies.txt'
YT_CMD_SUB_1 = '--write-auto-subs --sub-format vtt --sub-lang id --ignore-error --no-playlist --cookies ~/Videos/_/cookies.txt'
YT_CMD_SUB = '--write-auto-subs --ignore-error --no-playlist --cookies ~/Videos/_/cookies.txt'
YT_CMD_AUDIO = '-f 140 --ignore-error --no-playlist '
YT_CMD_AUDIO = '-f 140 --ignore-error --no-playlist '
YT_CMD_VIDEO = '-f 136 --ignore-error --no-playlist '
MY_FOLDER = ''
FILE_PATH = ''
# YT_CMD = '-f 136,140 --ignore-error --no-playlist -a'


def get_code_from_url(url):
    n = 11
    s_st = 'v='
    index = url.find(s_st)
    if index > -1:
        code = url[index+len(s_st):index+n+len(s_st)]
        return code
    s_st = 'be/'
    index = url.find(s_st)
    if index > -1:
        code = url[index+len(s_st):index+n+len(s_st)]
        return code
    return None


def get_namefile_code(file_path):
    open_index = file_path.find(' [')
    close_index =file_path.find('].')
    file_code = file_path[open_index+2:close_index]
    return file_code


def get_mp4_m4a(files_combine):
    f_mp4 = list(filter(lambda x: '.mp4' in x, files_combine))
    f_m4a = list(filter(lambda x: '.m4a' in x, files_combine))
    return f_mp4, f_m4a


def check_files_with_code_and_ext(files, code, exts):
    #my_files = list(filter(lambda x: x.endswith(ext) and code in get_namefile_code(x), files))
    my_files = []
    my_exts = exts.split(',')
    for file in files:
        for ext in my_exts:
            if file.endswith(ext) and code in get_namefile_code(file):
                my_files.append(file)
    return my_files


def download_transcript_as_txt(video_code, language='id'):
    try:
        ytt_api = YouTubeTranscriptApi()
        transcript = ytt_api.fetch(video_code, languages=[language, 'en'])
        
        formatter = TextFormatter()
        txt_content = formatter.format_transcript(transcript)
        
        # Create filename with video code
        txt_filename = f"transcript_{video_code}.txt"
        txt_filepath = os.path.join(MY_FOLDER, txt_filename)
        
        with open(txt_filepath, 'w', encoding='utf-8') as f:
            f.write(txt_content)
        
        print(f"Downloaded transcript as TXT: {txt_filename}")
        return txt_filepath
    except Exception as e:
        print(f"Failed to download transcript as TXT for {video_code}: {str(e)}")
        return None


def download_transcript_as_srt(video_code, language='id'):
    try:
        ytt_api = YouTubeTranscriptApi()
        transcript = ytt_api.fetch(video_code, languages=[language, 'en'])
        
        formatter = SRTFormatter()
        srt_content = formatter.format_transcript(transcript)
        
        # Create filename with video code
        srt_filename = f"transcript_{video_code}.srt"
        srt_filepath = os.path.join(MY_FOLDER, srt_filename)
        
        with open(srt_filepath, 'w', encoding='utf-8') as f:
            f.write(srt_content)
        
        print(f"Downloaded transcript as SRT: {srt_filename}")
        return srt_filepath
    except Exception as e:
        print(f"Failed to download transcript as SRT for {video_code}: {str(e)}")
        return None


async def download_file(command):
    process = await asyncio.create_subprocess_shell(
        command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )

    stdout, stderr = await process.communicate()
    
    if process.returncode == 0:
        list_out = stdout.splitlines()
        out = [item.decode() for item in list_out if 'downloaded' in item.decode()] 
        if out:
            print(f"{out[0]}")
        else : 
            print(f"File Downloaded : {list_out}") 
    else:
        print(f"Error downloading file: {stderr.decode()}")
        

async def get_code_audio_video(command,args):
    os.system(command)
    process = await asyncio.create_subprocess_shell(
        command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    ca, cv = None, None
    stdout, stderr = await process.communicate()
    ext_audio = args.ext_audio
    ext_video = args.ext_video
    info_video = args.info_video
    info_audio = args.info_audio
    if process.returncode != 0:
        print(f"Error downloading file: {stderr.decode()}")
        return ca, cv
        
    list_out = stdout.splitlines()
    for item in list_out:
        item = item.decode()
        if ext_audio in item and info_audio in item:
            ca_list = item.split(' ')
            ca = ca_list[0]
        if ext_video in item and info_video in item:
            cv_list = item.split(' ')
            cv = cv_list[0]
    
    return ca, cv


def preparation_download(args):
    global MY_FOLDER, FILE_PATH
        
    MY_FOLDER = args.folder
    if MY_FOLDER == '.':
        MY_FOLDER = './'

    # Set my_folder as directory
    MY_FOLDER = os.path.abspath(MY_FOLDER)
    print(MY_FOLDER)

    FILE_PATH = os.path.join(MY_FOLDER, args.file)
    if os.path.isfile(FILE_PATH):
        print(f"The file {args.file} : {FILE_PATH} exists.")
        # os.system(f"python3 {YT_DLP} {YT_CMD} {file_path}")
    else:
        print(f"The file {args.file} : {FILE_PATH} does not exist. Please add it and insert url youtube links.")
        exit()

    # Get all files in my_folder
    files = os.listdir(MY_FOLDER)
    
    # Read the list_yt of the file t-yt-dl.txt
    list_yt = []
    with open(FILE_PATH, 'r') as f:
        list_yt = f.read().split('\n')
    
    return files, list_yt


async def main():
    files, list_yt = preparation_download()    
    for link in list_yt:
        code = get_code_from_url(link)
        
        if not code:
            continue
        
        vtt_files = check_files_with_code_and_ext(files, code, '.vtt')
        if not vtt_files:
            command = f"python3 {YT_DLP} {YT_CMD_SUB} '{link}'"
            await download_file(command)
            
        audio_files = check_files_with_code_and_ext(files, code, '.m4a')
        if not audio_files:
            command = f"python3 {YT_DLP} {YT_CMD_AUDIO} '{link}'"
            await download_file(command)
            files = os.listdir(MY_FOLDER)
            audio_files = check_files_with_code_and_ext(files, code, '.m4a')
        
        video_files = check_files_with_code_and_ext(files, code, '.mp4')
        if not video_files:
            command = f"python3 {YT_DLP} {YT_CMD_VIDEO} '{link}'"
            await download_file(command)
            files = os.listdir(MY_FOLDER)
            video_files = check_files_with_code_and_ext(files, code, '.mp4')
        
        if not audio_files or not video_files:
            continue
        
        new_file = f'temp_{video_files[0]}'
        f_mp4 = os.path.join(MY_FOLDER, video_files[0])
        f_m4a = os.path.join(MY_FOLDER, audio_files[0])
        new_file = os.path.join(MY_FOLDER, new_file)
        command = ["ffmpeg", "-i", f_mp4, "-i", f_m4a, "-c:v", "copy", "-c:a", "aac", new_file]
        subprocess.run(command, check=True)

        if not os.path.exists(new_file):
            continue
            
        os.remove(f_mp4)
        print(f"Delete file {f_mp4}")
        os.remove(f_m4a)
        print(f"Delete file {f_m4a}")
        os.rename(new_file,f_mp4)
        print(f"Rename file {new_file}")
        # Write list_yt into t-yt-dl.txt
        list_yt.remove(link)
    
    with open(FILE_PATH, 'w') as f:
        f.write('\n'.join(list_yt))


def get_arguments():
    global YT_CMD_AUDIO, YT_CMD_VIDEO, YT_CMD_SUB
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
    parser.add_argument('--download-txt', action='store_true', help='Download subtitles as TXT format using youtube-transcript-api')
    parser.add_argument('--download-srt', action='store_true', help='Download subtitles as SRT format using youtube-transcript-api')

    # Parse the arguments
    try:
        args = parser.parse_args()
    except SystemExit as e:
        parser.print_help()
        sys.exit()

    # Print the arguments (for demonstration purposes)
    print(f"Folder: {args.folder}, Sub Format: {args.sub_format}, Sub Lang: {args.sub_lang}, Is Search: {args.is_search}, "
          f"Code Audio: {args.code_audio}, Code Video: {args.code_video}, Ext Audio: {args.ext_audio}, Ext Video : {args.ext_video}, "
          f"Ext Full Video : {args.ext_video2}, Info Audio: {args.info_audio}, Info Video: {args.info_video}, "
          f"Download TXT: {args.download_txt}, Download SRT: {args.download_srt}"
          )
    
    YT_CMD_SUB = f"--extractor-args 'youtube:player_client=default,-web' --write-auto-subs --sub-format {args.sub_format} --sub-lang {args.sub_lang} --ignore-error --no-playlist "
    YT_CMD_SUB_0 = f"--write-auto-subs --ignore-error --no-playlist "
    YT_CMD_AUDIO = "".join(["-f ", args.code_audio, " --ignore-error --no-playlist"])
    YT_CMD_AUDIO = "".join(["-f ", args.code_audio, " --ignore-error --no-playlist"])
    YT_CMD_VIDEO = "".join(["-f ", args.code_video, " --ignore-error --no-playlist"])
    
    return args
    
def sync_download_file(args, files, code, link):
    # Download subtitles using youtube-transcript-api for TXT and SRT formats
    if hasattr(args, 'download_txt') and args.download_txt:
        txt_files = check_files_with_code_and_ext(files, code, '.txt')
        if not txt_files:
            download_transcript_as_txt(code, args.sub_lang)
    
    if hasattr(args, 'download_srt') and args.download_srt:
        srt_files = check_files_with_code_and_ext(files, code, '.srt')
        if not srt_files:
            download_transcript_as_srt(code, args.sub_lang)
    
    # Keep original VTT download functionality
    vtt_files = check_files_with_code_and_ext(files, code, args.sub_format)
    if not vtt_files:
        command = f"python3 {YT_DLP} {YT_CMD_SUB} '{link}'"
        print("Download Full : ",command)
        os.system(command)
    
    files = os.listdir(MY_FOLDER)
    full_video_files = check_files_with_code_and_ext(files, code, args.ext_video2)
    if full_video_files:
        return vtt_files, False, False
    
    audio_files = check_files_with_code_and_ext(files, code, args.ext_audio)
    if not audio_files:
        command = f"python3 {YT_DLP} {YT_CMD_AUDIO} '{link}'"
        print("Download Audio : ", command)
        os.system(command)
        files = os.listdir(MY_FOLDER)
        audio_files = check_files_with_code_and_ext(files, code, args.ext_audio)
    
    video_files = check_files_with_code_and_ext(files, code, args.ext_video)
    if not video_files:
        command = f"python3 {YT_DLP} {YT_CMD_VIDEO} '{link}'"
        print('Download Video : ', command)
        os.system(command)
        files = os.listdir(MY_FOLDER)
        video_files = check_files_with_code_and_ext(files, code, args.ext_video)
    
    return vtt_files, audio_files, video_files

def combine_audio_video(video_files, audio_files):
    new_file = f'temp_{video_files[0]}'
    f_mp4 = os.path.join(MY_FOLDER, video_files[0])
    f_m4a = os.path.join(MY_FOLDER, audio_files[0])
    new_file = os.path.join(MY_FOLDER, new_file)
    command = ["ffmpeg", "-i", f_mp4, "-i", f_m4a, "-c:v", "copy", "-c:a", "aac", new_file]
    print(f'combine : {command}')
    subprocess.run(command, check=True)
    return new_file, f_mp4, f_m4a

def remove_file(f_mp4, f_m4a, new_file,):
    os.remove(f_mp4)
    print(f"Delete file {f_mp4}")
    os.remove(f_m4a)
    print(f"Delete file {f_m4a}")
    os.rename(new_file,f_mp4)
    print(f"Rename file {new_file}")

def remove_link_yt_in_file(list_yt, link):
    print('Comment out link : ', link)
    index = list_yt.index(link)
    list_yt[index] = f'# {link}'
    return list_yt

def sync_task_download(args):
    # my_folder, file_path, 
    files, list_yt = preparation_download(args)
    for link in list_yt:
        
        code = get_code_from_url(link)
        if not code or link.startswith('#'):
            continue
        
        _, audio_files, video_files = sync_download_file(args, files, code, link)
        list_yt = remove_link_yt_in_file(list_yt, link)
        
        if not audio_files or not video_files:
            continue
            
        new_file, f_mp4, f_m4a = combine_audio_video(video_files, audio_files)
        
        if not os.path.exists(new_file):
            continue
        
        remove_file(f_mp4, f_m4a, new_file,)
    
    with open(FILE_PATH, 'w') as f:
        f.write('\n'.join(list_yt))

async def search_yt_dlp(args):
    global YT_CMD_AUDIO, YT_CMD_VIDEO 
    files, list_yt = preparation_download(args)
    for link in list_yt:
        code = get_code_from_url(link)
        if not code or link.startswith('#'):
            continue
        
        command = f"python3 {YT_DLP} -F '{link}' --ignore-error --no-playlist "
        ca, cv = await get_code_audio_video(command,args)
        if ca is None :
            ca = args.code_audio
        if cv is None :
            cv = args.code_video
        
        YT_CMD_AUDIO = "".join(["-f ", ca, " --ignore-error --no-playlist"])
        YT_CMD_VIDEO = "".join(["-f ", cv, " --ignore-error --no-playlist"])
        
        _, audio_files, video_files = sync_download_file(args, files, code, link)
        
        if not audio_files or not video_files:
            continue
            
        new_file, f_mp4, f_m4a = combine_audio_video(video_files, audio_files)
        
        if not os.path.exists(new_file):
            continue
        
        list_yt = remove_file(f_mp4, f_m4a, new_file, list_yt, link)
    
    with open(FILE_PATH, 'w') as f:
        f.write('\n'.join(list_yt))

if __name__ == '__main__':
    args = get_arguments()
    if args.is_search:
        asyncio.run(search_yt_dlp(args))
    else : 
        sync_task_download(args)
        # asyncio.run(main())
