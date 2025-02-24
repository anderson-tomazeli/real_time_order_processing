FROM python:3.9-slim-buster

RUN apt-get update && apt-get install -y iputils-ping
# Create a new user and group
RUN useradd -ms /bin/bash anderson_tomazeli

# Set working directory and copy files as the new user
USER anderson_tomazeli

WORKDIR /app

COPY src/utils.py /app/src/utils.py
COPY config.ini .

COPY ./order_processor/requirements.txt .
RUN pip install --upgrade pip                                                                                                                                                                                                 
RUN pip install --no-cache-dir -r requirements.txt                                                                                                                                                                                                                                                                                                                                                                                                          
#COPY . .
COPY ./order_processor/app.py .

CMD ["python", "app.py"]
