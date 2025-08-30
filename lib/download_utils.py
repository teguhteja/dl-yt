import os
import asyncio
from .file_utils import check_files_with_code_and_ext

YT_DLP = '~/Videos/_/yt-dlp --cookies ~/Videos/_/cookies.txt'


async def download_file(command):
    """Download file using yt-dlp asynchronously"""
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


async def get_code_audio_video(command, args):
    """Get audio and video codes from yt-dlp format listing"""
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


def sync_download_file(args, files, code, link, my_folder, yt_cmd_sub, yt_cmd_audio, yt_cmd_video):
    """Synchronously download subtitle, audio, and video files"""
    vtt_files = check_files_with_code_and_ext(files, code, args.sub_format)
    if not vtt_files:
        command = f"python3 {YT_DLP} {yt_cmd_sub} '{link}'"
        print("Download Full : ", command)
        os.system(command)
    
    files = os.listdir(my_folder)
    full_video_files = check_files_with_code_and_ext(files, code, args.ext_video2)
    if full_video_files:
        return vtt_files, False, False
    
    audio_files = check_files_with_code_and_ext(files, code, args.ext_audio)
    if not audio_files:
        command = f"python3 {YT_DLP} {yt_cmd_audio} '{link}'"
        print("Download Audio : ", command)
        os.system(command)
        files = os.listdir(my_folder)
        audio_files = check_files_with_code_and_ext(files, code, args.ext_audio)
    
    video_files = check_files_with_code_and_ext(files, code, args.ext_video)
    if not video_files:
        command = f"python3 {YT_DLP} {yt_cmd_video} '{link}'"
        print('Download Video : ', command)
        os.system(command)
        files = os.listdir(my_folder)
        video_files = check_files_with_code_and_ext(files, code, args.ext_video)
    
    return vtt_files, audio_files, video_files