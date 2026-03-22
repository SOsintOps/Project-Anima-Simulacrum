# Domande Frequenti (FAQ)

### 1. Perché usiamo Docker invece di un ambiente virtuale?
Docker garantisce un ambiente di esecuzione **identico** su qualsiasi macchina, eliminando problemi di compatibilità tra sistemi operativi o versioni delle librerie. Rende il progetto più robusto, portabile e pronto per un'eventuale distribuzione futura.

### 2. Cosa fa esattamente lo script `ingestion.py`?
Questo script è la prima fase del nostro processo. Legge tutti i file `.pdf` presenti nella cartella `/data/raw`, estrae il loro contenuto testuale pagina per pagina e salva il risultato in file `.txt` con lo stesso nome all'interno della cartella `/data/processed`.

### 3. Come posso processare nuovi file PDF?
Semplice:
1.  Aggiungi i nuovi file `.pdf` alla tua cartella `/data/raw`.
2.  Esegui nuovamente il comando `docker run` come descritto nella guida di installazione. Lo script processerà solo i file che non ha già elaborato (o li sovrascriverà se hanno lo stesso nome).

### 4. Il comando `docker run` sembra complesso. Cosa significa `-v`?
Il flag `-v` sta per **volume**. È il modo in cui colleghiamo una cartella del nostro computer (es. `./data`) a una cartella all'interno del container isolato (es. `/app/data`). Questo permette al codice dentro il container di leggere e scrivere file sul nostro computer, rendendo i risultati permanenti.