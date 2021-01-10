FROM python:slim-stretch

WORKDIR /srv

# UPDATE APK CACHE AND INSTALL PACKAGES
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    tzdata \
    gcc \
    g++ \
    ca-certificates \
    wget && \
    update-ca-certificates \
    && rm -rf /var/lib/apt/lists/*

RUN cp /usr/share/zoneinfo/America/Sao_Paulo /etc/localtime && \
    echo "America/Sao_Paulo" > /etc/timezone

# ADD Pipefiles
ADD Pipfile Pipfile.lock ./

# INSTALL FROM Pipefile.lock FILE
RUN pip install --no-cache -U pip pipenv && pipenv install --system

RUN apt-get remove --purge -y \
    gcc \
    g++ \
    wget && rm -rf /var/lib/apt/lists/* \
    && apt-get autoremove -y

# ADD APP
ADD . .

EXPOSE 80

# ENTRYPOINT
ENTRYPOINT ["gunicorn", "src.app:app", "-c", "./src/gunicorn.py"]