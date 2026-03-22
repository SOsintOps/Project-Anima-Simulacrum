# Project Anima Simulacrum

*Motore AI per l'analisi di testi narrativi e la creazione di profili di personalità dinamici per LLM.*

---

## 🎯 Obiettivo del Progetto

**Project Anima Simulacrum** è un sistema software progettato per leggere e comprendere testi narrativi (come libri o sceneggiature) al fine di generare un "profilo psicologico-linguistico" dettagliato di un personaggio. Questo profilo viene poi utilizzato come DNA per un Large Language Model (es. Gemini, ChatGPT) per simulare una conversazione con quel personaggio nel modo più fedele possibile.

## 🚀 Stato Attuale

* **Versione**: 0.1.0 (Alpha)
* **Fase attuale**: Setup del progetto e sviluppo del modulo di ingestione dati.

## 🛠️ Come Avviare

Il progetto è interamente containerizzato con Docker per garantire la massima portabilità.

**>> [Vedi la procedura di installazione e avvio completa](./docs/install.md) <<**

## 📂 Struttura del Progetto

* **/data/**: Contiene i dati grezzi (input) e processati (output).
* **/docs/**: Tutta la documentazione del progetto.
* **/src/**: Il codice sorgente Python del motore di analisi.
* **/profiles/**: I profili finali dei personaggi in formato JSON.
* `Dockerfile`: La ricetta per costruire l'ambiente di esecuzione.

## ❓ Domande Frequenti

Hai una domanda?

**>> [Leggi le nostre FAQ](./docs/faq.md) <<**

## 📜 Licenza

Questo progetto è rilasciato sotto la **Licenza MIT**. Vedi il file `LICENSE` per maggiori dettagli.