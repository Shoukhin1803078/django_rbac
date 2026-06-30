FROM python:3.12-alpine
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
WORKDIR /app
RUN apk update && apk add --no-cache postgresql-client                 # This is for psql use in container machine
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
# CMD ["tail", "-f", "/dev/null"]   
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]