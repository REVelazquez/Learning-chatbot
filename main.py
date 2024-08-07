import sqlite3
import json
import random
from difflib import get_close_matches

# Declarar globalmente la variable current_language
current_language = 'es'

# Conecta o crea(Si no existe) a una base de datos, en este caso una sql
def connect_to_sqlite(data_base: str):
    conn = sqlite3.connect(data_base)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS knowledge_base (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question TEXT,
            answer TEXT, 
            language TEXT
        )
    ''')
    conn.commit()
    return conn

# Hace que todos los mensajes sean en minúscula, los normaliza
def normalize_text(text: str) -> str:
    return text.strip().lower()

def select_language(language: str):
    global current_language 
    if language == 'Español':
        current_language = 'es'
    elif language == 'English':
        current_language = 'en'

# Encuentra la mejor opción de respuesta a un mensaje
def find_best_match(user_question: str, cursor) -> str | None:
    cursor.execute('SELECT question FROM knowledge_base')
    questions = [normalize_text(row[0]) for row in cursor.fetchall()]
    matches = get_close_matches(normalize_text(user_question), questions, n=1, cutoff=0.7)
    return matches[0] if matches else None

# Selección de respuesta a un mensaje
def get_answer_for_question(question: str, cursor) -> str | None:
    cursor.execute('SELECT answer, language FROM knowledge_base WHERE question = ?', (question,))
    result = cursor.fetchone()
    if result:
        answers = json.loads(result[0])  # Convertir de cadena JSON a lista de respuestas
        selected_answer = random.choice(answers)  # Devolver una respuesta aleatoria de la lista
        answer_lang = result[1]
        full_answer = [selected_answer, answer_lang]
        return full_answer
    return None

# Función para leer el archivo JSON
def load_predefined_qa(json_file: str, cursor, conn):
    with open(json_file, 'r', encoding='utf-8-sig') as file:
        predefined_qa = json.load(file)
        for qa in predefined_qa:
            question = normalize_text(qa['question'])
            language = normalize_text(qa.get('language', 'en'))
            if 'answers' in qa:
                # Convertir la lista de respuestas a una cadena JSON
                answers = json.dumps(qa['answers'])
                cursor.execute('INSERT INTO knowledge_base (question, answer, language) VALUES (?, ?, ?)', (question, answers, language))
            else:
                # Si es una respuesta única, guardarla como una lista JSON con un solo elemento
                answer = json.dumps([qa['answer']])
                cursor.execute('INSERT INTO knowledge_base (question, answer, language) VALUES (?, ?, ?)', (question, answer, language))
                
        conn.commit()

def chat_bot():
    conn = connect_to_sqlite('knowledge_base.db')
    cursor = conn.cursor()

    # Precarga a la base de datos de las cosas en el archivo JSON
    load_predefined_qa('predefined_qa.json', cursor, conn)

    while True:
        user_input = input('You: ').strip()

        # Cerrar el archivo en consola
        if user_input.lower() == 'quit':
            break

        if user_input.lower() == 'change language':
            if current_language == 'es':
                language = 'English'
                select_language(language)
                print('Language changed to English.')
            elif current_language == 'en':
                language = 'Español'
                select_language(language)
                print('El idioma se cambió a Español.')
            continue

        best_match = find_best_match(user_input, cursor)

        if best_match:
            answer = get_answer_for_question(best_match, cursor)
            if answer:
                if answer[1] == current_language:
                    print (f'Bot: {answer[0]}')
                else:
                    if current_language == 'en':
                        print('Bot: I can\'t answer in that language right now, if you want to change it type "change language" ')
                    if current_language == 'es':
                        print('Bot: No puedo responder en ese idioma en este momento, si quieres cambiar de idioma escribe "change language" ')
            else:
                # Esto ocurre cuando no sabe la respuesta
                print('Bot: I don\'t know the answer. Can you teach me?')
                if current_language == 'en':
                    new_answer = input('Type the answer or "skip" to skip: ')
                elif current_language == 'es':
                    new_answer = input('Escribe la respuesta o "skip" para saltear: ')

                if new_answer.lower() != 'skip':
                    cursor.execute('INSERT INTO knowledge_base (question, answer, language) VALUES (?, ?, ?)', (normalize_text(user_input), new_answer, current_language))
                    conn.commit()
                    print('Bot: Thank you! I learned a new response.')
        else:
            # Entra nueva info
            print('Bot: I don\'t know the answer. Can you teach me?')
            if current_language == 'en':
                new_answer = input('Type the answer or "skip" to skip: ')
            elif current_language == 'es':
                new_answer = input('Escribe la respuesta o "skip" para saltear: ')

            if new_answer.lower() != 'skip':
                cursor.execute('INSERT INTO knowledge_base (question, answer, language) VALUES (?, ?, ?)', (normalize_text(user_input), new_answer, current_language))
                conn.commit()
                print('Bot: Thank you! I learned a new response.')

    conn.close()

if __name__ == '__main__':
    chat_bot()
