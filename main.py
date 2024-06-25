import sqlite3
import json
from difflib import get_close_matches
from langdetect import detect

# Conecta o crea(Si no existe) a una base de datos, en este caso una sql
def connect_to_sqlite(data_base: str):
    conn = sqlite3.connect(data_base)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS knowledge_base (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question TEXT,
            answer TEXT
        )
    ''')
    conn.commit()
    return conn

# Hace que todos los mensajes sean en minuzcula, los normaliza
def normalize_text(text: str) -> str:
    return text.strip().lower()

# Encuentra la mejor opcion de respuesta a un mensaje
def find_best_match(user_question: str, cursor) -> str | None:
    cursor.execute('SELECT question FROM knowledge_base')
    questions = [normalize_text(row[0]) for row in cursor.fetchall()]
    matches = get_close_matches(normalize_text(user_question), questions, n=1, cutoff=0.7)
    return matches[0] if matches else None

# Seleccion de respuesta a un mensaje
def get_answer_for_question(question: str, cursor) -> str | None:
    cursor.execute('SELECT answer FROM knowledge_base WHERE question = ?', (question,))
    result = cursor.fetchone()
    return result[0] if result else None

# Funcion para leer el archivo Json
def load_predefined_qa(json_file: str, cursor, conn):
    with open(json_file, 'r', encoding='utf-8-sig') as file:
        predefined_qa = json.load(file)
        for qa in predefined_qa:
            question = normalize_text(qa['question'])
            if 'answers' in qa:
                # Si hay múltiples respuestas, iterar y agregar cada una
                for answer in qa['answers']:
                    cursor.execute('INSERT INTO knowledge_base (question, answer) VALUES (?, ?)', (question, answer))
            else:
                # Si es una respuesta única, agregarla directamente
                answer = qa['answer']
                cursor.execute('INSERT INTO knowledge_base (question, answer) VALUES (?, ?)', (question, answer))
                
        conn.commit()

def chat_bot():
    conn = connect_to_sqlite('knowledge_base.db')
    cursor = conn.cursor()

    # Precarga a la base de datos de las cosas en el archivo json
    load_predefined_qa('predefined_qa.json', cursor, conn)

    while True:
        user_input = input('You: ')

    # Cerrar el archivo en consola
        if user_input.lower() == 'quit':
            break

        best_match = find_best_match(user_input, cursor)

        if best_match:
            answer = get_answer_for_question(best_match, cursor)
            if answer:
                print(f'Bot: {answer}')
            else:
                # Esto ocurre cuando no sabe la respuesta
                print('Bot: I don\'t know the answer. Can you teach me?')
                new_answer = input('Type the answer or "skip" to skip: ')

                if new_answer.lower() != 'skip':
                    cursor.execute('INSERT INTO knowledge_base (question, answer) VALUES (?, ?)', (normalize_text(user_input), new_answer))
                    conn.commit()
                    print('Bot: Thank you! I learned a new response.')
        else:
            # Entra nueva info
            print('Bot: I don\'t know the answer. Can you teach me?')
            new_answer = input('Type the answer or "skip" to skip: ')

            if new_answer.lower() != 'skip':
                cursor.execute('INSERT INTO knowledge_base (question, answer) VALUES (?, ?)', (normalize_text(user_input), new_answer))
                conn.commit()
                print('Bot: Thank you! I learned a new response.')

    conn.close()

if __name__ == '__main__':
    chat_bot()
