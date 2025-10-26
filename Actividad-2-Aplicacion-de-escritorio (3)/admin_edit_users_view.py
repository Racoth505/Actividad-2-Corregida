# admin_edit_users_view.py
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import db_manager # Importa la lógica de la BBDD

def create_edit_users_view(parent_frame):
    """Crea la vista para editar usuarios existentes."""
    
    main_frame = ttk.Frame(parent_frame, style="Main.TFrame")
    main_frame.pack(fill=tk.BOTH, expand=True)
    
    current_user_id = None # Guardar el ID (int) del usuario cargado
    
    ttk.Label(main_frame, text="✏️ Editar Usuarios", font=("Helvetica", 16, "bold"), style="TLabel").pack(pady=10)
    
    search_frame = ttk.Frame(main_frame, style="Main.TFrame", padding=(10, 10))
    search_frame.pack(pady=10)
    
    ttk.Label(search_frame, text="Matrícula (username) a editar:", style="TLabel").grid(row=0, column=0, sticky='w', padx=5)
    matricula_search_var = tk.StringVar()
    entry_search = ttk.Entry(search_frame, textvariable=matricula_search_var, width=30)
    entry_search.grid(row=0, column=1, padx=5)
    
    edit_frame = ttk.Frame(main_frame, style="Main.TFrame", padding=(10, 10))
    edit_frame.pack(pady=10)
    
    # Variables para los campos de edición
    nombres_var = tk.StringVar()
    apellidos_var = tk.StringVar()
    telefono_var = tk.StringVar()
    direccion_var = tk.StringVar()

    def get_user_by_username(username):
        """Función helper para buscar por username ya que db_manager no la tiene."""
        conn = db_manager.get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Usuarios WHERE username = ?", (username,))
        user = cursor.fetchone()
        conn.close()
        if user: return dict(user)
        return None

    def cargar_usuario():
        nonlocal current_user_id
        username = matricula_search_var.get().strip()
        user_data = get_user_by_username(username)
        
        for widget in edit_frame.winfo_children():
            widget.destroy()
            
        if not user_data:
            ttk.Label(edit_frame, text=f"Usuario '{username}' no encontrado.", foreground='red', style="TLabel").pack()
            current_user_id = None
            return
        
        current_user_id = user_data['id'] # Guardar el ID (int)
            
        ttk.Label(edit_frame, text=f"Editando: {user_data.get('username')} ({user_data.get('role')})", 
                  font=("Arial", 12, "bold"), style="TLabel").grid(row=0, column=0, columnspan=2, pady=(0, 15))
                  
        nombres_var.set(user_data.get('nombre_completo', ''))
        apellidos_var.set(user_data.get('apellidos', ''))
        telefono_var.set(user_data.get('telefono', ''))
        direccion_var.set(user_data.get('direccion', ''))
        
        campos = [("Nombre(s)", nombres_var), ("Apellidos", apellidos_var), ("Teléfono", telefono_var), ("Dirección", direccion_var)]
        
        for i, (label_text, var) in enumerate(campos):
            row = i + 1
            ttk.Label(edit_frame, text=label_text, style="TLabel").grid(row=row, column=0, sticky='w', padx=5, pady=5)
            ttk.Entry(edit_frame, textvariable=var, width=40).grid(row=row, column=1, sticky='we', padx=5, pady=5)
            
        def guardar_cambios():
            if current_user_id is None:
                messagebox.showerror("Error", "No hay ningún usuario cargado.")
                return

            success = db_manager.update_user_profile_details(
                user_id=current_user_id,
                nombre_completo=nombres_var.get().strip(),
                apellidos=apellidos_var.get().strip(),
                telefono=telefono_var.get().strip() or None,
                direccion=direccion_var.get().strip() or None
            )
            if success:
                messagebox.showinfo("Éxito", f"Datos de '{username}' actualizados.")
                cargar_usuario() # Recargar
            else:
                messagebox.showerror("Error", "No se pudieron guardar los cambios.")
        
        def reset_password():
            if current_user_id is None: return
            new_pass = simpledialog.askstring("Resetear Contraseña", f"Ingrese la nueva contraseña para {username}:", show='*')
            if new_pass:
                db_manager.update_user_password(current_user_id, new_pass)
                messagebox.showinfo("Éxito", "Contraseña actualizada.")

        def delete_user():
            if current_user_id is None: return
            if messagebox.askyesno("Confirmar", f"¿Seguro que quieres eliminar a {username}?\nEsta acción es irreversible y borrará sus asignaciones y calificaciones."):
                if db_manager.delete_user(current_user_id):
                    messagebox.showinfo("Eliminado", f"Usuario {username} ha sido eliminado.")
                    matricula_search_var.set("")
                    for w in edit_frame.winfo_children(): w.destroy()
                else:
                    messagebox.showerror("Error", "No se pudo eliminar al usuario.")

        # Botones de acción
        btn_frame = ttk.Frame(edit_frame, style="Main.TFrame")
        btn_frame.grid(row=len(campos) + 1, column=0, columnspan=2, pady=20, sticky='ew')
        btn_frame.columnconfigure((0,1,2), weight=1)

        ttk.Button(btn_frame, text="Guardar Cambios", command=guardar_cambios, style="Green.TButton").grid(row=0, column=0, padx=5, sticky='ew')
        ttk.Button(btn_frame, text="Resetear Contraseña", command=reset_password, style="Accent.TButton").grid(row=0, column=1, padx=5, sticky='ew')
        ttk.Button(btn_frame, text="Eliminar Usuario", command=delete_user, style="Danger.TButton").grid(row=0, column=2, padx=5, sticky='ew')

    
    ttk.Button(search_frame, text="Buscar", command=cargar_usuario, style="Accent.TButton").grid(row=0, column=2, padx=5)
    entry_search.bind("<Return>", lambda event: cargar_usuario())
    
    return main_frame