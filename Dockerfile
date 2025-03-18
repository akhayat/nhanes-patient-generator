FROM python:3.12

WORKDIR /usr/src/app
COPY . .

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8000

CMD ["python", "-m", "patient_generator.manage", "runserver", "0.0.0.0:8000"] 