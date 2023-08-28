FROM tiangolo/uvicorn-gunicorn-fastapi:python3.9
ENV PIP_DISBLE_PIP_VERSION_CHECK=1
ENV PYTHONUNBUFFERED=1
ENV SECRET_KEY = c91a8b9e4203f9764cb97792062c59f3a40cca45
ENV ALGORITHM = HS256
ENV ACCESS_TOKEN_EXPIRE_MINUTES = 2500
ENV DB_USER="servilla_remoto"
ENV DB_PASS="Servilla123"
ENV DB_HOST="192.160.30.15"
# ENV DB_HOST = "179.32.43.106"
# ENV DB_PORT = 12539
ENV DB_PORT=3307
ENV DB_NAME="bases_web"
WORKDIR /APP
COPY requirements.txt .
RUN python -m venv venv
RUN /bin/bash -c "source venv/bin/activate"
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8000
CMD [ "uvicorn", "main:app", "--reload", "--host", "127.0.0.1", "--port", "8000" ]
