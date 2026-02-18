FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends ffmpeg && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV DJANGO_DEBUG=False
ENV DJANGO_ALLOWED_HOSTS=*

RUN python manage.py collectstatic --noinput

EXPOSE 8000

CMD ["gunicorn", "video_site.wsgi:application", "--bind", "0.0.0.0:8000"]

