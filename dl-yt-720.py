import sys
import os
import subprocess
import asyncio
import argparse
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter, SRTFormatter

# Get script directory for relative paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
YT_DLP = os.path.join(SCRIPT_DIR, 'yt-dlp')
COOKIES = os.path.join(SCRIPT_DIR, 'cookies.txt')
SUB_LANG = 'en'
YT_CMD = f'-f 136,140 --ignore-error --no-playlist -a --cookies {COOKIES}'
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
        # os.system(f"{YT_DLP} {YT_CMD} {file_path}")
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
        
            
        audio_files = check_files_with_code_and_ext(files, code, '.m4a')
        if not audio_files:
            command = f"{YT_DLP} {YT_CMD_AUDIO} '{link}'"
            await download_file(command)
            files = os.listdir(MY_FOLDER)
            audio_files = check_files_with_code_and_ext(files, code, '.m4a')
        
        video_files = check_files_with_code_and_ext(files, code, '.mp4')
        if not video_files:
            command = f"{YT_DLP} {YT_CMD_VIDEO} '{link}'"
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
    global YT_CMD_AUDIO, YT_CMD_VIDEO
    # Create the parser
    parser = argparse.ArgumentParser(description='A script to download and process videos.')

    # Add arguments
    parser.add_argument('--folder', default='.', type=str, help='Current folder work')
    parser.add_argument('-f','--file', default='t-yt-dl.txt', type=str, help='File content link youtube')
    parser.add_argument('-sl', '--sub-lang', default='en', type=str, help='Language of the subtitle')
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
    parser.add_argument('-c', '--cookies', default=os.path.join(SCRIPT_DIR, 'cookies.txt'), type=str, help='Path to cookies file')

    # Parse the arguments
    try:
        args = parser.parse_args()
    except SystemExit:
        parser.print_help()
        sys.exit()

    # Print the arguments (for demonstration purposes)
    print(f"Folder: {args.folder}, Sub Lang: {args.sub_lang}, Is Search: {args.is_search}, "
          f"Code Audio: {args.code_audio}, Code Video: {args.code_video}, Ext Audio: {args.ext_audio}, Ext Video : {args.ext_video}, "
          f"Ext Full Video : {args.ext_video2}, Info Audio: {args.info_audio}, Info Video: {args.info_video}, "
          f"Download TXT: {args.download_txt}, Download SRT: {args.download_srt}, Cookies: {args.cookies}"
          )
    
    global SUB_LANG, COOKIES
    SUB_LANG = args.sub_lang
    COOKIES = args.cookies
    YT_CMD_AUDIO = "".join(["-f ", args.code_audio, " --ignore-error --no-playlist"])
    YT_CMD_AUDIO = "".join(["-f ", args.code_audio, " --ignore-error --no-playlist"])
    YT_CMD_VIDEO = "".join(["-f ", args.code_video, " --ignore-error --no-playlist"])
    
    return args
    
def parse_formats_and_select_codes(output_lines):
    """Parse yt-dlp --list-formats output and select best audio/video codes"""
    audio_candidates = []
    video_candidates = []
    
    for line in output_lines:
        line = line.strip()
        if not line or line.startswith('─') or line.startswith('[') or line.startswith('ID'):
            continue
        
        parts = line.split()
        if len(parts) < 4:
            continue
            
        format_id = parts[0]
        ext = parts[1] if len(parts) > 1 else ''
        resolution = parts[2] if len(parts) > 2 else ''
        
        # Skip storyboard formats
        if 'sb' in format_id or 'mhtml' in ext:
            continue
        
        # Collect audio only mp4 formats
        if 'audio only' in line and 'mp4' in ext:
            try:
                audio_candidates.append(int(format_id))
            except ValueError:
                continue
        
        # Collect 720p60 mp4_dash video formats
        if '720p60' in line and 'mp4_dash' in line:
            try:
                video_candidates.append(int(format_id))
            except ValueError:
                continue
        # Fallback: collect regular 720p mp4 formats if no 720p60 found
        elif '720p' in line and 'mp4' in ext and not any('720p60' in l for l in output_lines):
            try:
                video_candidates.append(int(format_id))
            except ValueError:
                continue
        # Fallback: collect 480p mp4 formats if no 720p found  
        elif '480p' in line and 'mp4' in ext and not any('720p' in l for l in output_lines):
            try:
                video_candidates.append(int(format_id))
            except ValueError:
                continue
    
    # Select highest code number for audio (prefer 234 over 140)
    audio_code = str(max(audio_candidates)) if audio_candidates else None
    
    # Select highest code number for video (prefer 398 over 298)
    video_code = str(max(video_candidates)) if video_candidates else None
    
    return audio_code, video_code

def run_download_command(command, description=""):
    """Run download command and check for HTTP 403 errors"""
    print(f"Running: {command}")
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    
    # Check for HTTP 403 Forbidden errors in output
    if "HTTP Error 403: Forbidden" in result.stderr or "HTTP Error 403: Forbidden" in result.stdout:
        print(f"HTTP 403 Forbidden error detected for {description}. Skipping this download.")
        return False
    
    # Check for other critical errors that should stop download
    if "ERROR:" in result.stderr and "fragment" in result.stderr and "403" in result.stderr:
        print(f"Fragment download failed with 403 error for {description}. Skipping this download.")
        return False
    
    return result.returncode == 0

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
    
    
    files = os.listdir(MY_FOLDER)
    full_video_files = check_files_with_code_and_ext(files, code, args.ext_video2)
    if full_video_files:
        return False, False
    
    # Download audio with code 140
    audio_files = check_files_with_code_and_ext(files, code, args.ext_audio)
    audio_success = False
    if not audio_files:
        command = f"{YT_DLP} -f 140 --ignore-error --no-playlist --cookies {COOKIES} '{link}'"
        if run_download_command(command, "Audio (140)"):
            files = os.listdir(MY_FOLDER)
            audio_files = check_files_with_code_and_ext(files, code, args.ext_audio)
            if audio_files:
                audio_success = True
        
        # If 140 failed and no 403 error, try fallback for audio
        if not audio_success and not audio_files:
            print("Audio 140 failed, trying fallback with --list-formats...")
            command = f"{YT_DLP} --list-formats '{link}' --ignore-error --no-playlist --cookies {COOKIES}"
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            
            if result.returncode == 0:
                output_lines = result.stdout.split('\n')
                fallback_audio_code, _ = parse_formats_and_select_codes(output_lines)
                
                if fallback_audio_code:
                    print(f"Selected fallback audio code: {fallback_audio_code}")
                    command = f"{YT_DLP} -f {fallback_audio_code} --ignore-error --no-playlist --cookies {COOKIES} '{link}'"
                    if run_download_command(command, f"Audio ({fallback_audio_code})"):
                        files = os.listdir(MY_FOLDER)
                        audio_files = check_files_with_code_and_ext(files, code, args.ext_audio)
                        if audio_files:
                            audio_success = True
                        else:
                            print(f"Fallback audio download with code {fallback_audio_code} completed but no files found.")
                    else:
                        print(f"Fallback audio download with code {fallback_audio_code} failed.")
                else:
                    print("No suitable fallback audio code found.")
            else:
                print(f"Failed to get formats list for audio fallback: {result.stderr}")
    else:
        audio_success = True
    
    # Download video with code 136
    video_files = check_files_with_code_and_ext(files, code, args.ext_video)
    video_success = False
    if not video_files:
        command = f"{YT_DLP} -f 136 --ignore-error --no-playlist --cookies {COOKIES} '{link}'"
        if run_download_command(command, "Video (136)"):
            files = os.listdir(MY_FOLDER)
            video_files = check_files_with_code_and_ext(files, code, args.ext_video)
            if video_files:
                video_success = True
        
        # If 136 failed and no 403 error, try fallback for video
        if not video_success and not video_files:
            print("Video 136 failed, trying fallback with --list-formats...")
            command = f"{YT_DLP} --list-formats '{link}' --ignore-error --no-playlist --cookies {COOKIES}"
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            
            if result.returncode == 0:
                output_lines = result.stdout.split('\n')
                _, fallback_video_code = parse_formats_and_select_codes(output_lines)
                
                if fallback_video_code:
                    print(f"Selected fallback video code: {fallback_video_code}")
                    command = f"{YT_DLP} -f {fallback_video_code} --ignore-error --no-playlist --cookies {COOKIES} '{link}'"
                    if run_download_command(command, f"Video ({fallback_video_code})"):
                        files = os.listdir(MY_FOLDER)
                        video_files = check_files_with_code_and_ext(files, code, args.ext_video)
                        if video_files:
                            video_success = True
                        else:
                            print(f"Fallback video download with code {fallback_video_code} completed but no files found.")
                    else:
                        print(f"Fallback video download with code {fallback_video_code} failed.")
                else:
                    print("No suitable fallback video code found.")
            else:
                print(f"Failed to get formats list for video fallback: {result.stderr}")
    else:
        video_success = True
    
    # Report final status
    if not audio_success:
        print(f"FAILED: Could not download audio for video {code}")
    if not video_success:
        print(f"FAILED: Could not download video for video {code}")
    
    return audio_files, video_files

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
        
        audio_files, video_files = sync_download_file(args, files, code, link)
        
        if audio_files and video_files:
            list_yt = remove_link_yt_in_file(list_yt, link)
        else:
            print(f"Failed to download both audio and video for: {link}")
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
        
        command = f"{YT_DLP} -F '{link}' --ignore-error --no-playlist --cookies {COOKIES}"
        ca, cv = await get_code_audio_video(command,args)
        if ca is None :
            ca = args.code_audio
        if cv is None :
            cv = args.code_video
        
        YT_CMD_AUDIO = "".join(["-f ", ca, " --ignore-error --no-playlist"])
        YT_CMD_VIDEO = "".join(["-f ", cv, " --ignore-error --no-playlist"])
        
        audio_files, video_files = sync_download_file(args, files, code, link)
        
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
