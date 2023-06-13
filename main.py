import ai

video_file = r"C:\Users\anwar\Nextcloud\Meeting Personal\InfoImage\infoimage leads\Zoom Meeting 2023-06-10 00-09-01_optimized.m4a"
# audio_file = os.path.splitext(video_file)[0] + ".m4a"
#
# # seperate the audio from the video with copy mode
# command = f'ffmpeg -i "{video_file}" -vn -acodec copy "{audio_file}"'
# os.system(command)

audio_file = open(video_file, "rb")

# breakdown the audio into 25mb chunks and transcribe each chunk
for chunk in openai.Audio.chunk(audio_file):
    print(openai.Audio.transcribe("whisper-1", chunk).text)

transcript = openai.Audio.transcribe("whisper-1", audio_file)

# write the transcript to a file
with open("transcript.txt", "w") as f:
    f.write(transcript.text)
