FROM python:3.12.1

# Add image info
LABEL org.opencontainers.image.source https://github.com/biostat821/ehr-api

# Normal requirements
ADD requirements.txt .
RUN pip install -r requirements.txt

# Copy in files
ADD src/api ./api
ADD src/dao ./dao
ADD src/database.py .

# Set up database
RUN python database.py

# Set up server
CMD ["uvicorn", "--host", "0.0.0.0", "--port", "34491", "api.api:app"]
EXPOSE 34491