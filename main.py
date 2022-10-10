import socks
import socket
import shutil
from pytube import YouTube
import ffmpeg, subprocess
import os, json

class color:
    PURPLE = '\033[95m'
    GREEN = '\033[92m'
    BOLD = '\033[1m'
    CWHITE = '\33[37m'

# Load Config parameters
try:
    load_config = open(os.getcwd()+ "config.json", 'r')
    json_data = json.load(load_config)
    default_res = json_data["default_res"]
    second_res = json_data["second_res"]
    retries_nbr = json_data["retries"]
    video_size_allowed = json_data["video_size_allowed"]
except:
    print(color.PURPLE + "[x]" + color.CWHITE + "Parameters not load correctly!" )

def convert_bytes(num):
    """
    this function will convert bytes to MB.... GB... etc
    """
    for x in ['bytes', 'KB', 'MB', 'GB', 'TB']:
        if num < 1024.0:
            return "%3.1f %s" % (num, x)
        num /= 1024.0

def file_size(file_path):
    """
    this function will return the file size
    """
    if os.path.isfile(file_path):
        file_info = os.stat(file_path)
        return convert_bytes(file_info.st_size)

proxy_handler = {
    "http": "127.0.0.1:20304",
    'https': '127.0.0.1:20304'
}

with open(os.getcwd() + '/test.txt','r') as test_file:
    for line in test_file:
        video_id = line.strip()
        yout_link = "https://www.youtube.com/watch?v=" + video_id
        print(yout_link)
        try:
            # object creation using YouTube
            # which was imported in the beginning
            yt = YouTube(yout_link, use_oauth=True, allow_oauth_cache=True)
            print(color.GREEN+ '[!]' + color.CWHITE + 'Video sucessfully initialized...')
        except:
            # to handle exception
            print(color.PURPLE +"[x]" + color.CWHITE +  "Connection Error")

        video_name =  "ViD-" + video_id + '.mp4'
        filename = os.getcwd() + '/raw/' + video_name       # Raw vids
        output = os.getcwd() + '/output/' + video_name      # Compressed vids
        oversize = os.getcwd() + '/oversize' + video_name   # Oversized vids
        # filters out all the files with "mp4" extension
        mp4files = yt.streams.filter(file_extension='mp4')
        try:

            # Split video and audio
            yt.streams.filter(res=default_res, progressive=False).first().download(filename=filename)

            res = default_res

            #print(stream.filesize_mb())

            print(color.GREEN + '[!]' + color.CWHITE + "{} resolution get!".format(res))
        except:
            yt.streams.filter(res=second_res, progressive=False).first().download(filename='filename')
            res = second_res

            print(color.PURPLE +'[x]' + color.CWHITE +"{} resolution get, instead!".format(res))

        video = ffmpeg.input('video.mp4')

        video_size_no_compression = file_size(filename)

        #Compression start
        result = subprocess.run('ffmpeg -i {} -c:v libx265 -tune zerolatency -preset ultrafast -crf 40 -c:a aac -b:a 10k {}'.format(filename, output))

        video_size_compression = file_size(output)

        try: # Compare if file is larger than video_size_allowed(see Config.json file)
            if video_size_compression < float(video_size_allowed.replace("MB",'')):
                shutil.copy(output, oversize)   #Copy on oversize/
                os.remove(output)   #Remove from output/ Put it on
            else:
                ratio = (float(video_size_compression.replace("MB", '').replace("KB", '')) / float(
                    video_size_no_compression.replace("MB", '').replace("KB", ''))) * 100

                print(result)

                print(color.GREEN + '[{}]'.format(
                    res) + color.CWHITE + ' video has been download sucessfully!  \nID: ' + color.PURPLE + '{}'.format(
                    video_id)
                      + color.CWHITE + '\nSize(Before): ' + '{}'.format(
                    video_size_no_compression) + color.CWHITE + '\nSize(After): ' + '{}'.format(video_size_compression)
                      + color.CWHITE + '\nCompression ratio: ' + '{} %'.format(100 - ratio))
        except:
            print(color.PURPLE + "[x]" + color.CWHITE + "Something messed up see upper.........")

    print(color.GREEN + '[!]' + color.CWHITE + ' Task Completed!')
