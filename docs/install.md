# Procedura di Installazione e Avvio

Questa guida descrive come configurare ed eseguire **Project Anima Simulacrum** utilizzando Docker.

## Prerequisiti

Prima di iniziare, assicurati di avere installato sul tuo sistema:

1.  **Git**: Per clonare il repository.
2.  **Docker Desktop**: Per costruire ed eseguire il container. Assicurati che il demone di Docker sia in esecuzione.

## Procedura

1.  **Clona il Repository**
    Apri un terminale e clona il progetto sulla tua macchina locale.
    ```bash
    git clone [https://github.com/tuo-username/Project-Anima-Simulacrum.git](https://github.com/tuo-username/Project-Anima-Simulacrum.git)
    ```

2.  **Entra nella Cartella del Progetto**
    ```bash
    cd Project-Anima-Simulacrum
    ```

3.  **Costruisci l'Immagine Docker**
    Questo comando legge il `Dockerfile` e assembla l'ambiente software necessario. Il processo potrebbe richiedere qualche minuto la prima volta.
    ```bash
    docker build -t project-anima-simulacrum .
    ```

4.  **Esegui il Container**
    Questo comando avvia il container, esegue lo script `ingestion.py` e, grazie ai "volumi" (`-v`), si assicura che i file di input vengano letti dalla tua cartella `/data/raw` e i risultati vengano scritti nella tua cartella `/data/processed`.

    ```bash
    docker run --rm \
      -v ./data:/app/data \
      -v ./profiles:/app/profiles \
      project-anima-simulacrum
    ```
    *Nota: Se usi Windows PowerShell, potresti dover sostituire `./` con `${PWD}/`.*

Al termine dell'esecuzione, la cartella `/data/processed` conterrà i file di testo estratti dai PDF.