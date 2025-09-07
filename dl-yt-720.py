import sys
import os
import subprocess
import asyncio
import argparse
import configparser
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter, SRTFormatter

# Get script directory for relative paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
YT_DLP = os.path.join(SCRIPT_DIR, 'yt-dlp')
COOKIES = os.path.join(SCRIPT_DIR, 'cookies.txt')
CODE_CONF = os.path.join(SCRIPT_DIR, 'code.conf')
SUB_LANG = 'en'
YT_CMD = f'-f 136,140 --ignore-error --no-playlist -a --cookies {COOKIES}'
YT_CMD_AUDIO = '-f 140 --ignore-error --no-playlist '
YT_CMD_AUDIO = '-f 140 --ignore-error --no-playlist '
YT_CMD_VIDEO = '-f 136 --ignore-error --no-playlist '
MY_FOLDER = ''
FILE_PATH = ''
# YT_CMD = '-f 136,140 --ignore-error --no-playlist -a'


def load_config_codes():
    """Load audio and video codes from code.conf file"""
    if not os.path.exists(CODE_CONF):
        print(f"Config file {CODE_CONF} not found, using default codes")
        return ["140"], ["136"]
    
    try:
        config = configparser.ConfigParser()
        config.read(CODE_CONF)
        
        audio_code = config.get('option', 'audio-code', fallback='140')
        video_code = config.get('option', 'video-code', fallback='136')
        
        # Handle multiple codes separated by comma
        audio_codes = [code.strip() for code in audio_code.split(',')]
        video_codes = [code.strip() for code in video_code.split(',')]
            
        print(f"Loaded from config - Audio codes: {audio_codes}, Video codes: {video_codes}")
        return audio_codes, video_codes
        
    except Exception as e:
        print(f"Error reading config file: {e}, using default codes")
        return ["140"], ["136"]


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


def get_base_filename_from_video(video_filename):
    """Extract base filename from video file to use for transcripts"""
    # Remove the extension (.mp4, .mkv, etc.)
    base_name = os.path.splitext(video_filename)[0]
    return base_name


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


def download_transcript_as_txt(video_code, languages=None, base_filename=None):
    if languages is None:
        languages = ['en', 'id', 'es', 'fr', 'de', 'ja', 'ko', 'zh', 'pt', 'ru']
    
    try:
        print(f"🔍 Searching for TXT transcript for video {video_code}...")
        ytt_api = YouTubeTranscriptApi()
        
        # Try to get available transcripts first
        transcript_list = ytt_api.list(video_code)
        available_languages = []
        for transcript in transcript_list:
            available_languages.append(transcript.language_code)
        
        print(f"📋 Available transcript languages: {available_languages}")
        
        # Find the best available language
        selected_language = None
        for lang in languages:
            if lang in available_languages:
                selected_language = lang
                break
        
        if not selected_language and available_languages:
            selected_language = available_languages[0]
        
        if selected_language:
            print(f"🌐 Using language: {selected_language}")
            transcript = ytt_api.fetch(video_code, languages=[selected_language])
        else:
            print(f"⚠️  No transcript available for video {video_code}")
            return None
        
        formatter = TextFormatter()
        txt_content = formatter.format_transcript(transcript)
        
        # Create filename using base filename if provided, otherwise use video code
        if base_filename:
            txt_filename = f"{base_filename}_{selected_language}.txt"
        else:
            txt_filename = f"transcript_{video_code}_{selected_language}.txt"
        txt_filepath = os.path.join(MY_FOLDER, txt_filename)
        
        with open(txt_filepath, 'w', encoding='utf-8') as f:
            f.write(txt_content)
        
        print(f"✅ Downloaded TXT transcript: {txt_filename}")
        return txt_filepath, selected_language
    except Exception as e:
        print(f"❌ Failed to download TXT transcript for {video_code}: {str(e)}")
        return None


def download_transcript_as_srt(video_code, selected_language, base_filename=None):
    try:
        print(f"🔍 Downloading SRT transcript for video {video_code} in {selected_language}...")
        ytt_api = YouTubeTranscriptApi()
        transcript = ytt_api.fetch(video_code, languages=[selected_language])
        
        formatter = SRTFormatter()
        srt_content = formatter.format_transcript(transcript)
        
        # Create filename using base filename if provided, otherwise use video code
        if base_filename:
            srt_filename = f"{base_filename}_{selected_language}.srt"
        else:
            srt_filename = f"transcript_{video_code}_{selected_language}.srt"
        srt_filepath = os.path.join(MY_FOLDER, srt_filename)
        
        with open(srt_filepath, 'w', encoding='utf-8') as f:
            f.write(srt_content)
        
        print(f"✅ Downloaded SRT transcript: {srt_filename}")
        return srt_filepath
    except Exception as e:
        print(f"❌ Failed to download SRT transcript for {video_code}: {str(e)}")
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
    
    # Load default codes from config file
    config_audio_codes, config_video_codes = load_config_codes()
    
    # Create the parser
    parser = argparse.ArgumentParser(description='A script to download and process videos.')

    # Add arguments with config file defaults
    parser.add_argument('--folder', default='.', type=str, help='Current folder work')
    parser.add_argument('-f','--file', default='t-yt-dl.txt', type=str, help='File content link youtube')
    parser.add_argument('-sl', '--sub-lang', default='en', type=str, help='Language of the subtitle')
    parser.add_argument('-is', '--is-search', type=bool, default=False, help='Is Search using yt-dlp -F ')
    parser.add_argument('-ca', '--code-audio', type=str, default=config_audio_codes[0], help='The code audio for download file ')
    parser.add_argument('-cv', '--code-video', type=str, default=config_video_codes[0], help='The code video for download file')
    parser.add_argument('-ea', '--ext-audio', type=str, default="m4a", help='The ext audio for download file')
    parser.add_argument('-ev', '--ext-video', type=str, default="mp4", help='The ext video for download file')
    parser.add_argument('-ev2', '--ext-video2', type=str, default="mkv,webm", help='The ext full video for download file')
    parser.add_argument('-ia', '--info-audio', type=str, default="720p", help='The info audio for download file')
    parser.add_argument('-iv', '--info-video', type=str, default="en", help='The info video for download file')
    parser.add_argument('--download-txt', action='store_true', help='Download subtitles as TXT format using youtube-transcript-api (Note: Subtitles are now downloaded by default)')
    parser.add_argument('--download-srt', action='store_true', help='Download subtitles as SRT format using youtube-transcript-api (Note: Subtitles are now downloaded by default)')
    parser.add_argument('--no-subtitles', action='store_true', help='Skip subtitle download (disable default subtitle download)')
    parser.add_argument('-c', '--cookies', default=os.path.join(SCRIPT_DIR, 'cookies.txt'), type=str, help='Path to cookies file')

    # Parse the arguments
    try:
        args = parser.parse_args()
    except SystemExit:
        parser.print_help()
        sys.exit()

    # Store all config codes in args for later use
    args.config_audio_codes = config_audio_codes
    args.config_video_codes = config_video_codes

    # Print the arguments (for demonstration purposes)
    subtitle_status = "Disabled" if args.no_subtitles else "Enabled (default)"
    print(f"Folder: {args.folder}, Sub Lang: {args.sub_lang}, Is Search: {args.is_search}, "
          f"Code Audio: {args.code_audio}, Code Video: {args.code_video}, Ext Audio: {args.ext_audio}, Ext Video : {args.ext_video}, "
          f"Ext Full Video : {args.ext_video2}, Info Audio: {args.info_audio}, Info Video: {args.info_video}, "
          f"Subtitles: {subtitle_status}, Cookies: {args.cookies}"
          )
    
    global SUB_LANG, COOKIES
    SUB_LANG = args.sub_lang
    COOKIES = args.cookies
    YT_CMD_AUDIO = "".join(["-f ", args.code_audio, " --ignore-error --no-playlist"])
    YT_CMD_AUDIO = "".join(["-f ", args.code_audio, " --ignore-error --no-playlist"])
    YT_CMD_VIDEO = "".join(["-f ", args.code_video, " --ignore-error --no-playlist"])
    
    return args
    

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

def download_subtitles_for_video(args, files, code, video_files):
    """Download subtitles using video filename as base"""
    if args.no_subtitles:
        print(f"⏭️  Skipping subtitle download for video {code} (disabled by --no-subtitles)")
        return
        
    print(f"📝 Starting subtitle download for video {code}...")
    
    # Get base filename from video file
    base_filename = None
    if video_files:
        base_filename = get_base_filename_from_video(video_files[0])
        print(f"📁 Using video filename for transcripts: {base_filename}")
    
    # Check if transcript files already exist (check both old and new naming patterns)
    txt_files = check_files_with_code_and_ext(files, code, '.txt')
    srt_files = check_files_with_code_and_ext(files, code, '.srt')
    
    # Also check for files with video filename pattern if base_filename exists
    if base_filename:
        txt_files.extend([f for f in files if f.startswith(base_filename) and f.endswith('.txt')])
        srt_files.extend([f for f in files if f.startswith(base_filename) and f.endswith('.srt')])
    
    if not txt_files and not srt_files:
        # Download TXT first to detect language (use preferred language from args)
        preferred_languages = None
        if hasattr(args, 'sub_lang') and args.sub_lang:
            preferred_languages = [args.sub_lang, 'en', 'id', 'es', 'fr', 'de', 'ja', 'ko', 'zh', 'pt', 'ru']
        
        txt_result = download_transcript_as_txt(code, languages=preferred_languages, base_filename=base_filename)
        
        if txt_result:
            _, selected_language = txt_result
            print(f"🎯 Transcript language detected: {selected_language}")
            
            # Download SRT using the same language and base filename
            srt_result = download_transcript_as_srt(code, selected_language, base_filename=base_filename)
            
            if srt_result:
                print(f"🎉 Both TXT and SRT subtitles downloaded successfully for {code}")
            else:
                print(f"⚠️  TXT downloaded but SRT failed for {code}")
        else:
            print(f"📵 No subtitles available for video {code}")
    else:
        existing_files = []
        if txt_files:
            existing_files.append("TXT")
        if srt_files:
            existing_files.append("SRT")
        print(f"✅ Subtitle files already exist for {code}: {', '.join(existing_files)}")


def sync_download_file(args, files, code, link):
    
    
    files = os.listdir(MY_FOLDER)
    full_video_files = check_files_with_code_and_ext(files, code, args.ext_video2)
    if full_video_files:
        print(f"✅ Full video already exists for {code}")
        return False, False
    
    # Download audio - try all codes from config sequentially
    audio_files = check_files_with_code_and_ext(files, code, args.ext_audio)
    audio_success = False
    successful_audio_code = None
    
    if not audio_files:
        for audio_code in args.config_audio_codes:
            print(f"Trying audio code: {audio_code}")
            command = f"{YT_DLP} -f {audio_code} --ignore-error --no-playlist --cookies {COOKIES} '{link}'"
            if run_download_command(command, f"Audio ({audio_code})"):
                files = os.listdir(MY_FOLDER)
                audio_files = check_files_with_code_and_ext(files, code, args.ext_audio)
                if audio_files:
                    audio_success = True
                    successful_audio_code = audio_code
                    print(f"✅ Audio download successful with code {audio_code}")
                    break
            print(f"❌ Audio code {audio_code} failed, trying next...")
    else:
        audio_success = True
        print(f"✅ Audio file already exists for {code}")
    
    # Download video - try all codes from config sequentially
    video_files = check_files_with_code_and_ext(files, code, args.ext_video)
    video_success = False
    successful_video_code = None
    
    if not video_files:
        for video_code in args.config_video_codes:
            print(f"Trying video code: {video_code}")
            command = f"{YT_DLP} -f {video_code} --ignore-error --no-playlist --cookies {COOKIES} '{link}'"
            if run_download_command(command, f"Video ({video_code})"):
                files = os.listdir(MY_FOLDER)
                video_files = check_files_with_code_and_ext(files, code, args.ext_video)
                if video_files:
                    video_success = True
                    successful_video_code = video_code
                    print(f"✅ Video download successful with code {video_code}")
                    break
            print(f"❌ Video code {video_code} failed, trying next...")
    else:
        video_success = True
        print(f"✅ Video file already exists for {code}")
    
    # Download subtitles after video is successfully downloaded or already exists
    if video_success and video_files:
        files = os.listdir(MY_FOLDER)  # Refresh file list
        download_subtitles_for_video(args, files, code, video_files)
    
    # Report final status
    if audio_success and video_success:
        if successful_audio_code or successful_video_code:
            success_msg = f"🎉 Download completed for video {code}"
            if successful_audio_code:
                success_msg += f" (Audio: {successful_audio_code}"
                if successful_video_code:
                    success_msg += f", Video: {successful_video_code})"
                else:
                    success_msg += ")"
            elif successful_video_code:
                success_msg += f" (Video: {successful_video_code})"
            print(success_msg)
        else:
            print(f"✅ Both audio and video files already exist for {code}")
    else:
        if not audio_success:
            print(f"❌ FAILED: Could not download audio for video {code} with any available codes")
        if not video_success:
            print(f"❌ FAILED: Could not download video for video {code} with any available codes")
    
    return audio_files, video_files

def combine_audio_video(video_files, audio_files):
    new_file = f'temp_{video_files[0]}'
    f_mp4 = os.path.join(MY_FOLDER, video_files[0])
    f_m4a = os.path.join(MY_FOLDER, audio_files[0])
    new_file = os.path.join(MY_FOLDER, new_file)
    command = ["ffmpeg", "-i", f_mp4, "-i", f_m4a, "-c:v", "copy", "-c:a", "aac", new_file]
    print(f'🔄 Combining audio and video: {command}')
    subprocess.run(command, check=True)
    print(f'✅ Successfully combined audio and video into {new_file}')
    return new_file, f_mp4, f_m4a

def remove_file(f_mp4, f_m4a, new_file,):
    os.remove(f_mp4)
    print(f"🗑️  Deleted file {f_mp4}")
    os.remove(f_m4a)
    print(f"🗑️  Deleted file {f_m4a}")
    os.rename(new_file,f_mp4)
    print(f"📁 Renamed {new_file} to {f_mp4}")
    print(f"🎬 Final video ready: {f_mp4}")

def remove_link_yt_in_file(list_yt, link):
    print(f'📝 Commenting out processed link: {link}')
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
