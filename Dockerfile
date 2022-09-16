FROM python:3.9

LABEL MAINTAINER = "Vijay Ram"

############################################
# update apt-get & install basic deps
############################################
RUN apt-get update --fix-missing
RUN apt-get install software-properties-common wget -y

# install Target Cert
WORKDIR /opt
RUN wget http://browserconfig.target.com/tgt-certs/tgt-ca-bundle.crt --no-check-certificate -nv
ENV REQUESTS_CA_BUNDLE=/opt/tgt-ca-bundle.crt
ENV SSL_CERT_FILE=/opt/tgt-ca-bundle.crt

############################################
# install tap connector
############################################
ENV RUNTIME_VERSION=v2.4.3
RUN curl -sk "https://binrepo.target.com/artifactory/platform/runtime-connector/${RUNTIME_VERSION}/runtime-connector-linux-amd64-${RUNTIME_VERSION}.tgz" -o /runtime-connector.tgz && tar xvzf /runtime-connector.tgz -C / && rm /runtime-connector.tgz


############################################
# install code base
############################################
RUN mkdir /code
COPY . /code/
WORKDIR /code/

# Install dependencies
RUN python -m pip install \
    --extra-index-url https://binrepo.target.com/artifactory/api/pypi/tgt-python/simple \
    -r requirements.txt

# Open port for health endpoint
EXPOSE 8080

# Start Container
CMD ["/runtime-connector", "--", "python", "app.py"]
