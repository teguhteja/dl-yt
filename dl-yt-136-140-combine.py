import sys
import os
import subprocess

YT_DLP = '~/Videos/_/yt-dlp'
YT_CMD = '--write-auto-subs --sub-format vtt --sub-lang id -f 136,140 --ignore-error --no-playlist -a'
# YT_CMD = '-f 136,140 --ignore-error --no-playlist -a'


def get_namefile_code(file_path):
    open_index = file_path.find(' [')
    close_index =file_path.find('].')
    file_code = file_path[open_index+2:close_index]
    return file_code

def get_mp4_m4a(files_combine):
    f_mp4 = list(filter(lambda x: '.mp4' in x, files_combine))
    f_m4a = list(filter(lambda x: '.m4a' in x, files_combine))
    return f_mp4, f_m4a

def delete_line(list_yt, code):
    new_list = []
    for yt in list_yt:
        if code in yt:
            continue
        new_list.append(yt)
    return new_list

# Get input from command line argument
if len(sys.argv) == 1:
    print("add argument as folder", )
    exit()
    
my_folder = sys.argv[1]
if my_folder == '.':
    my_folder = './'

# Set my_folder as directory
my_folder = os.path.abspath(my_folder)
print(my_folder)

file_path = os.path.join(my_folder, 't-yt-dl.txt')
if os.path.isfile(file_path):
    print(f"The file t-yt-dl.txt : {file_path} exists.")
    os.system(f"python3 {YT_DLP} {YT_CMD} {file_path}")
else:
    print(f"The file t-yt-dl.txt : {file_path} does not exist. Please add it and insert url youtube links.")
    exit()

# Get all files in my_folder
files = os.listdir(my_folder)
 
# Read the list_yt of the file t-yt-dl.txt
list_yt = []
with open(file_path, 'r') as f:
    list_yt = f.read().split('\n')

# Print the list of files
list_files_code = []
for my_file in files:
    if my_file.find(' [') == -1:
        continue
    
    code_file = get_namefile_code(my_file) 
    if code_file in list_files_code:
        continue
    
    my_files_combine = list(filter(lambda x: code_file in x, files))
    f_mp4, f_m4a = get_mp4_m4a(my_files_combine)
    if not f_mp4 or not f_m4a:
        continue
    
    new_file = f'temp_{f_mp4[0]}'
    f_mp4 = os.path.join(my_folder, f_mp4[0])
    f_m4a = os.path.join(my_folder, f_m4a[0])
    new_file = os.path.join(my_folder, new_file)
    # os.system(f"ffmpeg -i {f_mp4} -i {f_m4a} -c:v copy -c:a aac {new_file}" )
    command = ["ffmpeg", "-i", f_mp4, "-i", f_m4a, "-c:v", "copy", "-c:a", "aac", new_file]
    subprocess.run(command, check=True)
    
    if not os.path.exists(new_file):
        continue
        
    os.remove(f_mp4)
    print(f"Delete file {f_mp4}")
    os.remove(f_m4a)
    print(f"Delete file {f_m4a}")
    list_files_code.append(code_file)
    os.rename(new_file,f_mp4)
    print(f"Rename file {new_file}")
    list_yt = delete_line(list_yt, code_file)
    # Write list_yt into t-yt-dl.txt
with open(file_path, 'w') as f:
    f.write('\n'.join(list_yt))
