import os
import PyPDF2

# --- CONFIGURAZIONE DEI PERCORSI ---
# Definiamo i percorsi relativi alle cartelle di input e output.
# Questo rende lo script eseguibile da qualsiasi punto del progetto.
RAW_DATA_PATH = 'data/raw'
PROCESSED_DATA_PATH = 'data/processed'

def extract_text_from_pdfs():
    """
    Legge tutti i file PDF nella cartella RAW_DATA_PATH, estrae il testo
    e lo salva in file .txt nella cartella PROCESSED_DATA_PATH.
    """
    print("--- Inizio del processo di ingestione dei PDF ---")

    # Assicurati che la cartella di output esista, altrimenti creala
    if not os.path.exists(PROCESSED_DATA_PATH):
        os.makedirs(PROCESSED_DATA_PATH)
        print(f"Cartella '{PROCESSED_DATA_PATH}' creata.")

    # Elenca tutti i file nella cartella di input
    files_in_raw = os.listdir(RAW_DATA_PATH)
    
    for filename in files_in_raw:
        # Processa solo i file che finiscono con .pdf
        if filename.lower().endswith('.pdf'):
            input_pdf_path = os.path.join(RAW_DATA_PATH, filename)
            
            print(f"\nProcessing file: {filename}...")
            
            try:
                with open(input_pdf_path, 'rb') as pdf_file:
                    reader = PyPDF2.PdfReader(pdf_file)
                    full_text = ""
                    
                    # Estrai il testo da ogni pagina
                    for page_num in range(len(reader.pages)):
                        page = reader.pages[page_num]
                        full_text += page.extract_text()
                    
                    # Salva il testo estratto in un nuovo file .txt
                    output_txt_filename = os.path.splitext(filename)[0] + '.txt'
                    output_txt_path = os.path.join(PROCESSED_DATA_PATH, output_txt_filename)
                    
                    with open(output_txt_path, 'w', encoding='utf-8') as txt_file:
                        txt_file.write(full_text)
                    
                    print(f"-> Successo! Testo estratto e salvato in: {output_txt_path}")

            except Exception as e:
                print(f"-> ERRORE durante l'elaborazione di {filename}: {e}")

    print("\n--- Processo di ingestione completato. ---")

if __name__ == '__main__':
    extract_text_from_pdfs()