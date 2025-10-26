# admin_edit_subjects_view.py
import tkinter as tk
from tkinter import ttk, messagebox
import db_manager # Importa la lógica de la BBDD

# --- Helper function: Get user by USERNAME ---
# (Necesario si se permite buscar profesor por matrícula en el futuro)
def get_user_by_username(username):
    """Función helper para buscar un usuario por su username."""
    conn = db_manager.get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Usuarios WHERE username = ?", (username,))
    user = cursor.fetchone()
    conn.close()
    if user: return dict(user)
    return None

def create_edit_subjects_view(parent_frame):
    """Crea la vista para editar materias existentes."""

    main_frame = ttk.Frame(parent_frame, style="Main.TFrame")
    main_frame.pack(fill=tk.BOTH, expand=True)

    current_subject_id = None # Guardar el ID (int) de la materia cargada

    ttk.Label(main_frame, text="📝 Editar Materias", font=("Helvetica", 16, "bold"), style="TLabel").pack(pady=10)

    search_frame = ttk.Frame(main_frame, style="Main.TFrame", padding=(10, 10))
    search_frame.pack(pady=10)

    ttk.Label(search_frame, text="ID de la Materia a editar:", style="TLabel").grid(row=0, column=0, sticky='w', padx=5)
    materia_id_search_var = tk.StringVar()
    entry_search = ttk.Entry(search_frame, textvariable=materia_id_search_var, width=30)
    entry_search.grid(row=0, column=1, padx=5)

    edit_frame = ttk.Frame(main_frame, style="Main.TFrame", padding=(10, 10))
    edit_frame.pack(pady=10)

    # --- Variables ---
    nombre_var = tk.StringVar()
    profesor_id_var = tk.StringVar() # Guardará el ID numérico como string
    horas_var = tk.StringVar()
    salon_var = tk.StringVar()
    fecha_inicio_var = tk.StringVar()
    fecha_fin_var = tk.StringVar()

    # Definir el Label fuera de cargar_materia
    nombre_profesor_display = ttk.Label(edit_frame, text="Profesor: ", style="TLabel", foreground='gray')
    # (Se colocará en el grid dentro de cargar_materia)

    def actualizar_nombre_profesor_edit(*args):
        profesor_id_str = profesor_id_var.get().strip()
        # Asegurarse de que el widget exista antes de configurarlo
        if not nombre_profesor_display.winfo_exists():
            return # No hacer nada si la etiqueta no existe

        if not profesor_id_str:
            nombre_profesor_display.config(text="Profesor: ", foreground='gray')
            return

        try:
            # Convertir a número ANTES de llamar a db_manager
            prof_id = int(profesor_id_str)
            user = db_manager.get_user_by_id(prof_id) # Llamar con el número

            if user and user['role'] == 'profesor':
                nombre = user.get('nombre_completo', '')
                ap = user.get('apellidos', '')
                nombre_profesor_display.config(text=f"Nombre: {nombre} {ap}".strip(), foreground='green')
            else:
                 # Si el ID es numérico pero no es profesor o no existe
                 nombre_profesor_display.config(text="✗ ID no es de un profesor válido", foreground='red')

        except ValueError:
            # Si el texto no es un número válido
            nombre_profesor_display.config(text="✗ ID debe ser numérico", foreground='red')
        except Exception as e:
            # Otros posibles errores de base de datos
            print(f"Error validando ID de profesor {profesor_id_str}: {e}")
            nombre_profesor_display.config(text="Error", foreground='red')

    profesor_id_var.trace_add("write", actualizar_nombre_profesor_edit)

    def cargar_materia():
        nonlocal current_subject_id
        materia_id_str = materia_id_search_var.get().strip()

        # Limpiar frame anterior (esto NO destruye nombre_profesor_display ahora)
        for widget in edit_frame.winfo_children():
            widget.destroy()

        # Re-crear la etiqueta nombre_profesor_display dentro del edit_frame limpio
        # Esto es necesario porque el grid() necesita un widget padre válido
        nombre_profesor_display = ttk.Label(edit_frame, text="Profesor: ", style="TLabel", foreground='gray')


        if not materia_id_str.isdigit():
             ttk.Label(edit_frame, text="ID de la materia debe ser numérico.", foreground='red', style="TLabel").pack()
             current_subject_id = None
             return

        try:
            mat_id = int(materia_id_str)
            materia_data = db_manager.get_subject_details(mat_id)
        except ValueError:
             ttk.Label(edit_frame, text="ID de la materia debe ser numérico.", foreground='red', style="TLabel").pack()
             current_subject_id = None
             return

        if not materia_data:
            ttk.Label(edit_frame, text=f"Materia con ID '{mat_id}' no encontrada.", foreground='red', style="TLabel").pack()
            current_subject_id = None
            return

        current_subject_id = materia_data['id'] # Guardar ID

        ttk.Label(edit_frame, text=f"Editando: {materia_data.get('nombre', '')} (ID: {materia_data.get('id')})",
                  font=("Arial", 12, "bold"), style="TLabel").grid(row=0, column=0, columnspan=3, pady=(0, 15))

        nombre_var.set(materia_data.get('nombre', ''))

        # Manejar None al establecer la variable
        prof_id_principal = materia_data.get('id_profesor_principal')
        profesor_id_var.set(str(prof_id_principal) if prof_id_principal is not None else "") # Poner "" si es None

        horas_val = materia_data.get('horas_semanales')
        horas_var.set(str(horas_val) if horas_val is not None else "")

        salon_var.set(materia_data.get('salon', '') or "") # Asegurar string
        fecha_inicio_var.set(materia_data.get('fecha_inicio', '') or "") # Asegurar string
        fecha_fin_var.set(materia_data.get('fecha_fin', '') or "") # Asegurar string

        # actualizar_nombre_profesor_edit() # El trace lo hará

        campos = [
            ("Nombre de la Materia", nombre_var),
            ("ID Profesor Principal", profesor_id_var),
            ("Horas Semanales", horas_var),
            ("Salón", salon_var),
            ("Fecha Inicio (YYYY-MM-DD)", fecha_inicio_var),
            ("Fecha Fin (YYYY-MM-DD)", fecha_fin_var)
        ]

        for i, (label_text, var) in enumerate(campos):
            row = i + 1
            ttk.Label(edit_frame, text=label_text, style="TLabel").grid(row=row, column=0, sticky='w', padx=5, pady=5)
            entry = ttk.Entry(edit_frame, textvariable=var, width=40)
            entry.grid(row=row, column=1, sticky='we', padx=5, pady=5)
            if var == profesor_id_var:
                # Colocar el label existente en el grid
                nombre_profesor_display.grid(row=row, column=2, sticky='w', padx=10)

        # --- Lógica de guardar (ya estaba bien, usa ID numérico) ---
        def guardar_cambios_materia():
            if current_subject_id is None: return

            profesor_id_str = profesor_id_var.get().strip()
            horas_str = horas_var.get().strip()
            prof_id = None
            horas = None

            if profesor_id_str: # Solo validar si no está vacío
                if not profesor_id_str.isdigit():
                    messagebox.showerror("Error", "ID de Profesor debe ser un número.")
                    return
                prof_id = int(profesor_id_str)
                user = db_manager.get_user_by_id(prof_id)
                if not (user and user['role'] == 'profesor'):
                    messagebox.showerror("Error", "ID de Profesor no es válido.")
                    return
            # Si profesor_id_str está vacío, prof_id se queda como None (permitido en BBDD)

            if horas_str:
                if not horas_str.isdigit():
                    messagebox.showerror("Error", "Horas Semanales debe ser un número.")
                    return
                horas = int(horas_str)
            # Si horas_str está vacío, horas se queda como None (permitido en BBDD)

            success = db_manager.update_subject_details(
                subject_id=current_subject_id,
                nombre=nombre_var.get().strip(),
                id_profesor=prof_id,
                horas=horas,
                salon=salon_var.get().strip() or None,
                inicio=fecha_inicio_var.get().strip() or None,
                fin=fecha_fin_var.get().strip() or None
            )
            if success:
                messagebox.showinfo("Éxito", f"Materia '{current_subject_id}' actualizada.")
                cargar_materia() # Recargar para ver cambios (si los hubo)
            else:
                 messagebox.showerror("Error", "No se pudo actualizar la materia.")

        def delete_materia():
            if current_subject_id is None: return
            if messagebox.askyesno(
                "Confirmar",
                f"¿Seguro que quieres eliminar la materia (ID: {current_subject_id})?\n"
                "Esto borrará todas las inscripciones y calificaciones asociadas."
            ):
                if db_manager.delete_subject(current_subject_id):
                    messagebox.showinfo("Eliminado", "Materia eliminada.")
                    materia_id_search_var.set("")
                    # Limpiar frame después de eliminar
                    for w in edit_frame.winfo_children(): w.destroy()
                else:
                    messagebox.showerror("Error", "No se pudo eliminar la materia.")

        # Botones de acción
        btn_frame = ttk.Frame(edit_frame, style="Main.TFrame")
        btn_frame.grid(row=len(campos) + 1, column=0, columnspan=3, pady=20, sticky='ew')
        btn_frame.columnconfigure((0,1), weight=1)

        ttk.Button(btn_frame, text="Guardar Cambios", command=guardar_cambios_materia, style="Green.TButton").grid(row=0, column=0, padx=5, sticky='ew')
        ttk.Button(btn_frame, text="Eliminar Materia", command=delete_materia, style="Danger.TButton").grid(row=0, column=1, padx=5, sticky='ew')


    ttk.Button(search_frame, text="Buscar", command=cargar_materia, style="Accent.TButton").grid(row=0, column=2, padx=5)
    entry_search.bind("<Return>", lambda event: cargar_materia())

    return main_frame