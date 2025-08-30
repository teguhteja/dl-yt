import os
import subprocess


def combine_audio_video(video_files, audio_files, my_folder):
    """Combine audio and video files using ffmpeg"""
    new_file = f'temp_{video_files[0]}'
    f_mp4 = os.path.join(my_folder, video_files[0])
    f_m4a = os.path.join(my_folder, audio_files[0])
    new_file = os.path.join(my_folder, new_file)
    command = ["ffmpeg", "-i", f_mp4, "-i", f_m4a, "-c:v", "copy", "-c:a", "aac", new_file]
    print(f'combine : {command}')
    subprocess.run(command, check=True)
    return new_file, f_mp4, f_m4a


def remove_file(f_mp4, f_m4a, new_file):
    """Remove original files and rename the combined file"""
    os.remove(f_mp4)
    print(f"Delete file {f_mp4}")
    os.remove(f_m4a)
    print(f"Delete file {f_m4a}")
    os.rename(new_file, f_mp4)
    print(f"Rename file {new_file}")