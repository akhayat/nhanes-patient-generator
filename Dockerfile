FROM python:3.12

RUN apt-get update && apt-get upgrade -y

WORKDIR /app
COPY . .

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8000

CMD ["python", "-m", "patient_generator.manage", "runserver_plus", "--cert-file", "/certs/simpat.pem", "--key-file", "/certs/simpat-key.pem", "0.0.0.0:8000"] 
