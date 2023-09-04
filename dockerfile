# Use the official Conda image as the base image
FROM continuumio/miniconda3:latest

# Set the working directory in the container
WORKDIR /app

# Copy the environment.yml file into the container
COPY environment.yml .

# Create a Conda environment and activate it
RUN conda env create -f environment.yml
RUN echo "source activate $(head -1 environment.yml | cut -d' ' -f2)" > ~/.bashrc

# Install any additional dependencies here if needed
# RUN conda install -c some_channel some_package

# Copy the rest of your application code into the container
COPY . .

# Expose the port your FastAPI application will run on
EXPOSE 8000

# Command to activate the Conda environment and run your FastAPI application
CMD [ "bash", "-c", "source activate $(head -1 environment.yml | cut -d' ' -f2) && uvicorn main:app --host 127.0.0.1 --port 8000 --reload" ]
# CMD [ "bash", "-c", "source activate $(head -1 environment.yml | cut -d' ' -f2) && python3 main.py" ]
