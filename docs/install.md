# Installation and Start-up Procedure

This guide describes how to set up and run **Project Anima Simulacrum** using Docker.

## Prerequisites

Before you start, make sure you have installed on your system:

1.  **Git**: to clone the repository.
2.  **Docker Desktop**: to build and run the container. Make sure the Docker daemon is running.

## Procedure

1.  **Clone the Repository**
    Open a terminal and clone the project to your local machine.
    ```bash
    git clone https://github.com/SOsintOps/Project-Anima-Simulacrum.git
    ```

2.  **Enter the Project Folder**
    ```bash
    cd Project-Anima-Simulacrum
    ```

3.  **Build the Docker Image**
    This command reads the `Dockerfile` and assembles the required software environment. The process may take a few minutes the first time.
    ```bash
    docker build -t project-anima-simulacrum .
    ```

4.  **Run the Container**
    This command starts the container, runs the `ingestion.py` script and, thanks to the "volumes" (`-v`), makes sure that the input files are read from your `/data/raw` folder and the results are written to your `/data/processed` folder.

    ```bash
    docker run --rm \
      -v ./data:/app/data \
      -v ./profiles:/app/profiles \
      project-anima-simulacrum
    ```
    *Note: if you use Windows PowerShell, you may need to replace `./` with `${PWD}/`.*

When the run is complete, the `/data/processed` folder will contain the text files extracted from the PDFs.
