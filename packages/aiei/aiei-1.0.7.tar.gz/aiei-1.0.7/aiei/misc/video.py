import cv2
try:
    from moviepy.editor import VideoFileClip
except Exception as e:
    print(e)


def get_video_data(path_video, skip_frames=0, writer_fps=None):
    capture = cv2.VideoCapture()
    capture.open(path_video)
    w = int(capture.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = capture.get(cv2.CAP_PROP_FPS)
    total_frame = int(capture.get(cv2.CAP_PROP_FRAME_COUNT))
    print(w, h, fps, total_frame)
    capture.set(cv2.CAP_PROP_POS_FRAMES, skip_frames)
    writer = None
    if writer_fps is not None:
        writer = cv2.VideoWriter()
        # fourcc = cv2.VideoWriter_fourcc(*'vp80')  # *.webm, can play in h5 player(browser), generate slowly
        fourcc = cv2.VideoWriter_fourcc(*'DIVX')  # *.mp4/avi, couldn't play in browser
        writer.open(f'{path_video.split(".")[0]}_demo.mp4', fourcc, writer_fps, (w, h))
    meta = {'w': w, 'h': h, 'fps': fps, 'total_frame': int(total_frame)}
    return capture, writer, meta


def get_audio_from_video(path_video):
    video = VideoFileClip(path_video)
    audio = video.audio
    return audio


def save_video_audio(path_video):
    video = VideoFileClip(path_video)
    audio = video.audio
    audio.write_audiofile(path_video.split('.')[0] + '.mp3')


def add_audio_to_video(src_audio, dst_video_path):
    video = VideoFileClip(dst_video_path)
    video_clip = video.set_audio(src_audio)
    video_clip.write_videofile(dst_video_path.split('.')[0] + '_out.mp4')
