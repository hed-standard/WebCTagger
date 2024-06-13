FROM python:3.11
COPY . /app
WORKDIR /app
RUN pip install -r /app/requirements.txt
EXPOSE 5000
CMD ["python", "-m", "flask", "--app", "board", "run", "--host", "0.0.0.0"]
