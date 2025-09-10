# Project Anima Simulacrum

*Motore AI per l'analisi di testi narrativi e la creazione di profili di personalità dinamici per LLM.*

---

## 🎯 Obiettivo del Progetto

**Project Anima Simulacrum** è un sistema software progettato per leggere e comprendere testi narrativi (come libri o sceneggiature) al fine di generare un "profilo psicologico-linguistico" dettagliato di un personaggio. Questo profilo viene poi utilizzato come DNA per un Large Language Model (es. Gemini, ChatGPT) per simulare una conversazione con quel personaggio nel modo più fedele possibile.

L'obiettivo è trasformare un personaggio statico su una pagina in un'entità interattiva e dinamica.

## ⚙️ Come Funziona

Il sistema opera in quattro fasi principali:

1.  **Ingestione e Normalizzazione**: Il software legge file in vari formati (PDF, ePub) ed estrae il testo grezzo, pulendolo e standardizzandolo.
2.  **Parsing Strutturale**: Utilizzando modelli di Natural Language Processing, il sistema analizza il testo per identificare le scene, i personaggi e attribuire ogni battuta al suo oratore.
3.  **Analisi Contestuale e Relazionale**: Questa è la fase chiave. Il motore mappa le interazioni tra i personaggi, analizzando come lo stile, il tono e i temi di un personaggio cambiano in base al suo interlocutore.
4.  **Generazione del Profilo**: I risultati dell'analisi vengono distillati in un file JSON strutturato. Questo profilo contiene metriche quantitative (stile linguistico) e qualitative (schemi emotivi, sarcasmo, temi ricorrenti) che costituiscono l'impronta digitale del personaggio.

## 🚀 Stato Attuale

* **Fase attuale**: Sviluppo iniziale dell'architettura e del modulo di parsing.
* **Versione**: 0.1.0 (Alpha)

## 🛠️ Come Iniziare

*(Questa sezione verrà compilata in futuro con le istruzioni per installare e avviare il codice).*