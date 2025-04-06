FROM python:3.12

RUN apt-get update && apt-get install -y ca-certificates
COPY your_certificate.crt /usr/local/share/ca-certificates/
RUN update-ca-certificates

WORKDIR /usr/src/app
COPY . .

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8000

CMD ["python", "-m", "patient_generator.manage", "runserver", "0.0.0.0:8000"] 