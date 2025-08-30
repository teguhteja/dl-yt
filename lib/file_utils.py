import os


def get_namefile_code(file_path):
    """Extract code from filename"""
    open_index = file_path.find(' [')
    close_index = file_path.find('].')
    file_code = file_path[open_index+2:close_index]
    return file_code


def get_mp4_m4a(files_combine):
    """Separate MP4 and M4A files from a list"""
    f_mp4 = list(filter(lambda x: '.mp4' in x, files_combine))
    f_m4a = list(filter(lambda x: '.m4a' in x, files_combine))
    return f_mp4, f_m4a


def check_files_with_code_and_ext(files, code, exts):
    """Check for files with specific code and extensions"""
    my_files = []
    my_exts = exts.split(',')
    for file in files:
        for ext in my_exts:
            if file.endswith(ext) and code in get_namefile_code(file):
                my_files.append(file)
    return my_files


def remove_link_yt_in_file(list_yt, link):
    """Comment out a YouTube link in the list"""
    print('Comment out link : ', link)
    index = list_yt.index(link)
    list_yt[index] = f'# {link}'
    return list_yt


def preparation_download(args):
    """Prepare download environment and validate files"""
    my_folder = args.folder
    if my_folder == '.':
        my_folder = './'

    # Set my_folder as directory
    my_folder = os.path.abspath(my_folder)
    print(my_folder)

    file_path = os.path.join(my_folder, args.file)
    if os.path.isfile(file_path):
        print(f"The file {args.file} : {file_path} exists.")
    else:
        print(f"The file {args.file} : {file_path} does not exist. Please add it and insert url youtube links.")
        exit()

    # Get all files in my_folder
    files = os.listdir(my_folder)
    
    # Read the list_yt of the file t-yt-dl.txt
    list_yt = []
    with open(file_path, 'r') as f:
        list_yt = f.read().split('\n')
    
    return files, list_yt, my_folder, file_path