import cv2
import os
import requests
import yt_dlp

from pytube import YouTube

num_frames  = 50

def download_video(video_url, temp_file="temp_video.mp4"):
    """Downloads a video from a URL."""
    if "youtube.com" in video_url or "youtu.be" in video_url or "instagram.com" in video_url:
        try:
            ydl_opts = {
                'format': 'best[ext=mp4]',
                'outtmpl': temp_file,
                'quiet': True,
                'no_warnings': True,
                'extract_flat': False,
                'ignoreerrors': True,
                # Remove cookie dependency
                'cookiesfrombrowser': None,
                # Add user agent to avoid blocks
                'http_headers': {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                }
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([video_url])
        except Exception as e:
            raise Exception(f"Failed to download video: {str(e)}")
    else:
        response = requests.get(video_url, stream=True)
        if response.status_code == 200:
            with open(temp_file, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
        else:
            raise Exception(f"Failed to download video: {response.status_code}")


def extract_frames(video_path, output_dir, num_frames=num_frames):
    """Extracts frames from a video, dividing it equally."""
    os.makedirs(output_dir, exist_ok=True)
    video = cv2.VideoCapture(video_path)
    total_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
    frame_interval = max(1, total_frames // num_frames)
    extracted_frames = 0
    for i in range(0, total_frames, frame_interval):
        video.set(cv2.CAP_PROP_POS_FRAMES, i)
        ret, frame = video.read()
        if ret:
            output_path = os.path.join(output_dir, f"frame_{extracted_frames:04d}.jpg")
            cv2.imwrite(output_path, frame)
            extracted_frames += 1
            if extracted_frames >= num_frames:
                break
    video.release()
    print(f"Extracted {extracted_frames} frames to {output_dir}")

if __name__ == "__main__":
    video_url = input("Enter the video URL: ")
    output_directory = "frames"
    
    # Download the video
    try:
        download_video(video_url)
        extract_frames("temp_video.mp4", output_directory)
    finally:
        # Clean up the temporary video file
        if os.path.exists("temp_video.mp4"):
            os.remove("temp_video.mp4")
