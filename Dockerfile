FROM ubuntu:jammy

WORKDIR /app

RUN apt-get update \ 
	&& apt-get install --no-install-recommends python3-pip -y \
	&& apt-get clean \
	&& rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN python3 -m pip install --no-cache-dir -r requirements.txt
RUN playwright install firefox && playwright install-deps

COPY . .

ENV OUTLOOK_EMAIL=''
ENV OUTLOOK_PASSWORD=''
ENV RECEIVERS=''

CMD ["python3", "script.py"]
