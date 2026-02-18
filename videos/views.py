from django.shortcuts import render, get_object_or_404
from .models import Video
from django.conf import settings
import os
from datetime import timedelta
import subprocess
from pathlib import Path

def _get_video_duration_seconds(file_path):
    try:
        result = subprocess.run(
            ['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', file_path],
            capture_output=True, text=True, check=True
        )
        val = result.stdout.strip()
        return float(val) if val else None
    except Exception:
        return None

def _generate_thumbnail(file_path, thumb_path):
    try:
        # Ensure directory exists
        os.makedirs(os.path.dirname(thumb_path), exist_ok=True)
        # Take a frame at 1s
        subprocess.run(
            ['ffmpeg', '-y', '-ss', '00:00:01', '-i', file_path, '-vframes', '1', '-q:v', '2', thumb_path],
            capture_output=True, check=True
        )
        return os.path.isfile(thumb_path)
    except Exception:
        return False

def _sync_media_videos_to_db():
    media_videos_dir = os.path.join(settings.MEDIA_ROOT, 'videos')
    if not os.path.isdir(media_videos_dir):
        return
    allowed_exts = {'.mp4', '.webm', '.mkv', '.mov'}
    for name in os.listdir(media_videos_dir):
        path = os.path.join(media_videos_dir, name)
        _, ext = os.path.splitext(name.lower())
        if not os.path.isfile(path) or ext not in allowed_exts:
            continue
        rel_name = f'videos/{name}'
        title = os.path.splitext(name)[0]
        thumb_rel = f"thumbnails/{Path(name).stem}.jpg"
        thumb_abs = os.path.join(settings.MEDIA_ROOT, thumb_rel)

        # Create or update record
        video = Video.objects.filter(video_file=rel_name).first()
        if not video:
            video = Video.objects.create(
                title=title,
                description='',
                video_file=rel_name,
                duration=timedelta(seconds=0),
            )

        # Duration
        if not video.duration or video.duration.total_seconds() == 0:
            secs = _get_video_duration_seconds(path)
            if secs and secs > 0:
                video.duration = timedelta(seconds=int(secs))

        # Thumbnail
        if not video.thumbnail or not os.path.isfile(os.path.join(settings.MEDIA_ROOT, str(video.thumbnail))):
            if _generate_thumbnail(path, thumb_abs):
                video.thumbnail = thumb_rel

        video.save()

def video_list(request):
    _sync_media_videos_to_db()
    videos = Video.objects.all().order_by('-created_at')
    return render(request, 'videos/video_list.html', {'videos': videos})

def video_detail(request, video_id):
    video = get_object_or_404(Video, pk=video_id)
    return render(request, 'videos/video_detail.html', {'video': video})
