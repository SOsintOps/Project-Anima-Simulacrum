import os
import re
import json

# --- CONFIGURAZIONE DEI PERCORSI ---
PROCESSED_DATA_PATH = 'data/processed'
STRUCTURED_DATA_PATH = 'data/structured' # Nuova cartella per l'output

def parse_script_text(text):
    """
    Analizza il testo di uno script e lo trasforma in una lista strutturata di dialoghi.
    
    Questa versione iniziale si concentra su un pattern comune:
    NOME_PERSONAGGIO (tutto in maiuscolo)
    dialogo...
    """
    
    dialogues = []
    
    # Espressione Regolare per identificare un personaggio e la sua battuta.
    # Cerca un nome in maiuscolo (con spazi, es. 'NICK FURY') che si trova su una riga a sé.
    # Poi cattura tutto il testo che segue fino a una riga vuota.
    pattern = re.compile(r'^\s*([A-Z][A-Z\s0-9]+(?:\(.*\))?)\s*\n(.*?)(?=\n\s*[A-Z][A-Z\s0-9]+(?:\(.*\))?\s*\n|\n\s*$)', re.MULTILINE | re.DOTALL)

    for match in pattern.finditer(text):
        character = match.group(1).strip()
        dialogue_text = match.group(2).strip()

        # Pulizia del dialogo da eventuali note di regia tra parentesi
        dialogue_text = re.sub(r'\(\s*.*?\s*\)', '', dialogue_text)
        # Sostituisce interruzioni di riga multiple con un singolo spazio
        dialogue_text = re.sub(r'\s+', ' ', dialogue_text).strip()

        if character and dialogue_text:
            dialogues.append({
                "character": character,
                "dialogue": dialogue_text
            })
            
    return dialogues

def process_all_scripts():
    """
    Esegue il parsing su tutti i file .txt nella cartella dei dati processati.
    """
    print("--- Inizio del processo di Parsing Strutturale ---")

    if not os.path.exists(STRUCTURED_DATA_PATH):
        os.makedirs(STRUCTURED_DATA_PATH)
        print(f"Cartella '{STRUCTURED_DATA_PATH}' creata.")

    files_in_processed = os.listdir(PROCESSED_DATA_PATH)
    
    for filename in files_in_processed:
        if filename.lower().endswith('.txt'):
            input_txt_path = os.path.join(PROCESSED_DATA_PATH, filename)
            
            # Escludiamo per ora lo script mal formattato
            if 'Iron-Man-2' in filename:
                print(f"\nSkipping file (mal formattato): {filename}")
                continue

            print(f"\nParsing file: {filename}...")
            
            try:
                with open(input_txt_path, 'r', encoding='utf-8') as f:
                    text = f.read()
                
                structured_data = parse_script_text(text)
                
                output_json_filename = os.path.splitext(filename)[0] + '.json'
                output_json_path = os.path.join(STRUCTURED_DATA_PATH, output_json_filename)
                
                with open(output_json_path, 'w', encoding='utf-8') as f:
                    json.dump(structured_data, f, indent=2, ensure_ascii=False)
                
                print(f"-> Successo! {len(structured_data)} dialoghi estratti e salvati in: {output_json_path}")

            except Exception as e:
                print(f"-> ERRORE durante il parsing di {filename}: {e}")

    print("\n--- Processo di Parsing completato. ---")

if __name__ == '__main__':
    process_all_scripts()
