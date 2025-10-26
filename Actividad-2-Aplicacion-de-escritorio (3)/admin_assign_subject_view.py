# admin_assign_subject_view.py
import tkinter as tk
from tkinter import ttk, messagebox
import db_manager # Importa la lógica de la BBDD

def create_assign_subject_view(parent_frame):
    """Crea la vista para asignar materias a alumnos (Inscripciones)."""
    
    main_frame = ttk.Frame(parent_frame, style="Main.TFrame")
    main_frame.pack(fill=tk.BOTH, expand=True)

    ttk.Label(main_frame, text="✅ Asignar Materias a Alumnos", font=("Helvetica", 16, "bold"), style="TLabel").pack(pady=10)

    form_frame = ttk.Frame(main_frame, style="Main.TFrame", padding=(10, 10))
    form_frame.pack(pady=10)
    
    matricula_alumno_var = tk.StringVar()
    materia_id_var = tk.StringVar()
    
    nombre_alumno_display = ttk.Label(form_frame, text="Nombre del Alumno: ", style="TLabel", foreground='gray')
    nombre_materia_display = ttk.Label(form_frame, text="Nombre de la Materia: ", style="TLabel", foreground='gray')

    # Guardar IDs (int) validados
    validated_student_id = None
    validated_subject_id = None

    def get_user_by_username(username):
        """Función helper para buscar por username."""
        conn = db_manager.get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Usuarios WHERE username = ?", (username,))
        user = cursor.fetchone()
        conn.close()
        if user: return dict(user)
        return None

    def validar_alumno_y_materia(*args):
        nonlocal validated_student_id, validated_subject_id
        
        alumno_username = matricula_alumno_var.get().strip()
        materia_id_str = materia_id_var.get().strip()
        
        # Validar Alumno
        if alumno_username:
            alumno_data = get_user_by_username(alumno_username)
            if alumno_data and alumno_data.get('role', '').lower() == 'alumno':
                nombre_completo = f"{alumno_data['nombre_completo'] or ''} {alumno_data['apellidos'] or ''}".strip()
                nombre_alumno_display.config(text=f"Alumno: {nombre_completo}", foreground='green')
                validated_student_id = alumno_data['id'] # Guardar ID (int)
            else:
                nombre_alumno_display.config(text="✗ Matrícula no es de Alumno o no existe", foreground='red')
                validated_student_id = None
        else:
            nombre_alumno_display.config(text="Nombre del Alumno: ", foreground='gray')
            validated_student_id = None

        # Validar Materia
        if materia_id_str:
            if not materia_id_str.isdigit():
                nombre_materia_display.config(text="✗ ID de Materia debe ser numérico", foreground='red')
                validated_subject_id = None
            else:
                try:
                    mat_id = int(materia_id_str)
                    materia = db_manager.get_subject_details(mat_id)
                    if materia:
                        nombre_materia_display.config(text=f"Materia: {materia['nombre']}", foreground='green')
                        validated_subject_id = materia['id'] # Guardar ID (int)
                    else:
                        nombre_materia_display.config(text="✗ ID de Materia no encontrado", foreground='red')
                        validated_subject_id = None
                except ValueError:
                     nombre_materia_display.config(text="✗ ID de Materia debe ser numérico", foreground='red')
                     validated_subject_id = None
        else:
            nombre_materia_display.config(text="Nombre de la Materia: ", foreground='gray')
            validated_subject_id = None

    matricula_alumno_var.trace_add("write", validar_alumno_y_materia)
    materia_id_var.trace_add("write", validar_alumno_y_materia)
    
    ttk.Label(form_frame, text="Matrícula del Alumno:", style="TLabel").grid(row=0, column=0, sticky='w', padx=5, pady=5)
    ttk.Entry(form_frame, textvariable=matricula_alumno_var, width=30).grid(row=0, column=1, sticky='we', padx=5, pady=5)
    
    ttk.Label(form_frame, text="ID de la Materia:", style="TLabel").grid(row=2, column=0, sticky='w', padx=5, pady=5)
    ttk.Entry(form_frame, textvariable=materia_id_var, width=30).grid(row=2, column=1, sticky='we', padx=5, pady=5)
    
    nombre_alumno_display.grid(row=1, column=0, columnspan=2, sticky='w', padx=5, pady=5)
    nombre_materia_display.grid(row=3, column=0, columnspan=2, sticky='w', padx=5, pady=5)

    def asignar_materia_a_alumno():
        """Inscribe al alumno usando los IDs validados."""
        
        if not validated_student_id or not validated_subject_id:
            messagebox.showwarning("Advertencia", "Debe ingresar una matrícula de alumno y un ID de materia válidos.")
            return

        # Llamar a db_manager
        success = db_manager.enroll_student(validated_student_id, validated_subject_id)

        if success:
            messagebox.showinfo("Éxito", "Alumno inscrito en la materia correctamente.")
            matricula_alumno_var.set("")
            materia_id_var.set("")
            validar_alumno_y_materia() # Refrescar displays
        else:
             messagebox.showwarning("Advertencia", "El alumno ya estaba inscrito en esta materia.")

    ttk.Button(form_frame, text="Asignar Materia", command=asignar_materia_a_alumno, style="Green.TButton").grid(row=4, column=0, columnspan=2, pady=20, sticky='we')
    
    return main_frame