from tkinter import *
from main import select_language, current_language

def show():
    selected_language = clicked.get()
    select_language(selected_language)
    
    
    # Ocultar o destruir el menú desplegable y el botón
    drop.pack_forget()  # Oculta el OptionMenu
    my_button.pack_forget()  # Oculta el botón
    
    # Puedes agregar más widgets o acciones aquí después de seleccionar el idioma
    label = Label(root, text=f'El idioma actual es Español' if selected_language == 'Español' else 'Current language is English')
    label.pack()



root = Tk()
root.title('Chatbot Lucas')
root.geometry('400x400')

languages = ['Español', 'English']

clicked = StringVar()
clicked.set(languages[0])
choosed = clicked.get()

drop = OptionMenu(root, clicked, *languages)
drop.pack()


my_button = Button(root, text='Elegir idioma' if choosed == 'Español' else 'Choose language', command=show)
my_button.pack()



root.mainloop()
