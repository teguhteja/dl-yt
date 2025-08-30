#!/usr/bin/env python3

import os
import asyncio
from lib.config import get_arguments, build_yt_commands
from lib.url_utils import get_code_from_url
from lib.file_utils import preparation_download, remove_link_yt_in_file
from lib.download_utils import sync_download_file, get_code_audio_video, YT_DLP
from lib.video_utils import combine_audio_video, remove_file


def sync_task_download(args):
    """Main synchronous download task"""
    files, list_yt, my_folder, file_path = preparation_download(args)
    yt_cmd_sub, yt_cmd_audio, yt_cmd_video = build_yt_commands(args)
    
    for link in list_yt:
        code = get_code_from_url(link)
        if not code or link.startswith('#'):
            continue
        
        _, audio_files, video_files = sync_download_file(
            args, files, code, link, my_folder, yt_cmd_sub, yt_cmd_audio, yt_cmd_video
        )
        list_yt = remove_link_yt_in_file(list_yt, link)
        
        if not audio_files or not video_files:
            continue
            
        new_file, f_mp4, f_m4a = combine_audio_video(video_files, audio_files, my_folder)
        
        if not os.path.exists(new_file):
            continue
        
        remove_file(f_mp4, f_m4a, new_file)
    
    with open(file_path, 'w') as f:
        f.write('\n'.join(list_yt))


async def search_yt_dlp(args):
    """Search and download with format detection"""
    files, list_yt, my_folder, file_path = preparation_download(args)
    yt_cmd_sub, yt_cmd_audio_base, yt_cmd_video_base = build_yt_commands(args)
    
    for link in list_yt:
        code = get_code_from_url(link)
        if not code or link.startswith('#'):
            continue
        
        command = f"python3 {YT_DLP} -F '{link}' --ignore-error --no-playlist "
        ca, cv = await get_code_audio_video(command, args)
        if ca is None:
            ca = args.code_audio
        if cv is None:
            cv = args.code_video
        
        yt_cmd_audio = "".join(["-f ", ca, " --ignore-error --no-playlist"])
        yt_cmd_video = "".join(["-f ", cv, " --ignore-error --no-playlist"])
        
        _, audio_files, video_files = sync_download_file(
            args, files, code, link, my_folder, yt_cmd_sub, yt_cmd_audio, yt_cmd_video
        )
        
        if not audio_files or not video_files:
            continue
            
        new_file, f_mp4, f_m4a = combine_audio_video(video_files, audio_files, my_folder)
        
        if not os.path.exists(new_file):
            continue
        
        list_yt = remove_link_yt_in_file(list_yt, link)
        remove_file(f_mp4, f_m4a, new_file)
    
    with open(file_path, 'w') as f:
        f.write('\n'.join(list_yt))


if __name__ == '__main__':
    args = get_arguments()
    if args.is_search:
        asyncio.run(search_yt_dlp(args))
    else:
        sync_task_download(args)