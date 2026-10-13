# Frequently Asked Questions (FAQ)

Frequently asked questions about Project Anima Simulacrum — Docker, the ingestion script, volumes and related projects.

## Table of Contents

* [Why do we use Docker instead of a virtual environment?](#why-do-we-use-docker-instead-of-a-virtual-environment)
* [What exactly does the `ingestion.py` script do?](#what-exactly-does-the-ingestionpy-script-do)
* [How can I process new PDF files?](#how-can-i-process-new-pdf-files)
* [The `docker run` command looks complicated. What does `-v` mean?](#the-docker-run-command-looks-complicated-what-does--v-mean)
* [Which development framework does the project follow?](#which-development-framework-does-the-project-follow)
* [Are there related projects?](#are-there-related-projects)

---

## Docker and the pipeline

### Why do we use Docker instead of a virtual environment?

Docker guarantees an **identical** runtime environment on any machine, eliminating compatibility problems between operating systems or library versions. It makes the project more robust, portable and ready for possible distribution in the future.

### What exactly does the `ingestion.py` script do?

This script is the first stage of our process. It reads all the `.pdf` files in the `/data/raw` folder, extracts their text content page by page and saves the result as `.txt` files with the same name in the `/data/processed` folder.

### How can I process new PDF files?

Simple:
1. Add the new `.pdf` files to your `/data/raw` folder.
2. Run the `docker run` command again as described in the [installation guide](install.md). The script will process only the files it has not already processed (or will overwrite them if they have the same name).

### The `docker run` command looks complicated. What does `-v` mean?

The `-v` flag stands for **volume**. It is how we connect a folder on our computer (e.g. `./data`) to a folder inside the isolated container (e.g. `/app/data`). This lets the code inside the container read and write files on our computer, making the results permanent.

---

## Framework and related projects

### Which development framework does the project follow?

[Codex Machinae](https://github.com/SOsintOps/codex-machinae), the SOsintOps playbook for building software with LLM collaborators (Solo profile, D5 ML/Data Pipeline domain). The repository keeps a vendored copy in [`codex-machinae.md`](../codex-machinae.md); it is an early draft (version 2.0.0 of 15 April 2026), so the GitHub repository is the current reference.

### Are there related projects?

Yes:
- [Codex Machinae](https://github.com/SOsintOps/codex-machinae): the development playbook this project follows.
- [Il Conclave](https://github.com/SOsintOps/il-conclave): another project that makes a language model work through several procedures and personas, here analytic ones (ACH, a premortem, a steelman) followed by an anonymous peer review and a synthesis; it is a Claude Code skill, in Italian.
- [Intelligence Field Notes](https://github.com/SOsintOps/intelligence-field-notes): the intelligence method of the other SOsintOps projects; its note on profiling applies here too: a profile drawn from what someone writes describes the writing, not the person.
