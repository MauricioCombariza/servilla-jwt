FROM tiangolo/uvicorn-gunicorn-fastapi:python3.9
ENV PIP_DISBLE_PIP_VERSION_CHECK=1
ENV PYTHONUNBUFFERED=1

WORKDIR /APP
COPY requirements.txt .
RUN python -m venv venv
RUN /bin/bash -c "source venv/bin/activate"
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8000
CMD [ "uvicorn", "main:app", "--reload", "--host", "127.0.0.1", "--port", "8000" ]
