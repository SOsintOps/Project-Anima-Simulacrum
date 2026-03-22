# Usiamo un'immagine ufficiale Python come base
FROM python:3.9-slim

# Impostiamo la cartella di lavoro all'interno del container
WORKDIR /app

# Copiamo il file dei requisiti e installiamo le dipendenze
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiamo tutto il resto del nostro progetto nella cartella di lavoro
COPY . .

# Definiamo il comando di default da eseguire quando il container parte
# In questo caso, esegue il nostro script di ingestione
CMD ["python", "src/ingestion.py"]