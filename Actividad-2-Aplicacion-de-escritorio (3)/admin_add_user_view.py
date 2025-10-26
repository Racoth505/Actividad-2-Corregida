# admin_add_user_view.py
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import os
import shutil
import db_manager # Importa la lógica de la base de datos

def create_admin_add_user_view(parent_frame, user_data):
    """Crea la vista para agregar nuevos usuarios."""
    
    # Frame principal que se adhiere al estilo del parent
    # Usamos ttk.Frame y el estilo "Main.TFrame" que tu app_styles.py define
    main_frame = ttk.Frame(parent_frame, style="Main.TFrame")
    main_frame.pack(fill=tk.BOTH, expand=True)

    ttk.Label(main_frame, text="👤 Agregar Usuarios", font=("Helvetica", 16, "bold"), style="TLabel").pack(pady=10)

    form_frame = ttk.Frame(main_frame, style="Main.TFrame")
    form_frame.pack(pady=10, padx=10)

    # Variables
    rol_var = tk.StringVar(value="profesor") # Usar minúsculas para BBDD
    matricula_var = tk.StringVar()
    password_var = tk.StringVar()
    nombres_var = tk.StringVar()
    apellidos_var = tk.StringVar()
    telefono_var = tk.StringVar()
    direccion_var = tk.StringVar()
    foto_path = tk.StringVar(value="")

    # --- Campos del formulario ---
    ttk.Label(form_frame, text="Rol del Usuario", style="TLabel").grid(row=0, column=0, sticky='w', padx=5, pady=5)
    
    # Usamos Combobox de ttk
    opciones_rol = ["profesor", "alumno"]
    combo_rol = ttk.Combobox(form_frame, textvariable=rol_var, values=opciones_rol, state="readonly", width=37)
    combo_rol.grid(row=0, column=1, sticky='we', padx=5, pady=5)

    campos = [
        ("Matrícula", matricula_var),
        ("Contraseña", password_var),
        ("Nombre(s)", nombres_var),
        ("Apellidos", apellidos_var),
        ("Teléfono", telefono_var),
        ("Dirección", direccion_var)
    ]

    for i, (label_text, var) in enumerate(campos, start=1):
        ttk.Label(form_frame, text=label_text, style="TLabel").grid(row=i, column=0, sticky='w', padx=5, pady=5)
        show_char = '*' if label_text == "Contraseña" else ''
        # Usamos ttk.Entry
        ttk.Entry(form_frame, textvariable=var, width=40, show=show_char).grid(row=i, column=1, sticky='we', padx=5, pady=5)

    # --- Sección de Foto ---
    foto_frame = ttk.Frame(form_frame, style="Main.TFrame")
    foto_frame.grid(row=len(campos)+1, column=0, columnspan=2, pady=10)

    ttk.Label(foto_frame, text="Foto del Usuario:", style="TLabel").pack(side="left", padx=5)

    try:
        default_img = Image.open("assets/default_user.png")
    except FileNotFoundError:
        default_img = Image.new('RGB', (100, 100), color = 'grey')
        
    default_img = default_img.resize((100, 100))
    preview_img = ImageTk.PhotoImage(default_img)
    # Usamos tk.Label normal para la imagen
    img_label = tk.Label(foto_frame, image=preview_img, width=100, height=100, bg="white", relief="solid")
    img_label.image = preview_img
    img_label.pack(side="left", padx=10)

    def seleccionar_foto():
        file_path = filedialog.askopenfilename(
            title="Seleccionar foto",
            filetypes=[("Archivos de imagen", "*.png;*.jpg;*.jpeg;*.gif")]
        )
        if file_path:
            img = Image.open(file_path)
            img = img.resize((100, 100))
            tk_img = ImageTk.PhotoImage(img)
            img_label.config(image=tk_img)
            img_label.image = tk_img
            foto_path.set(file_path)

    # Usamos ttk.Button
    ttk.Button(foto_frame, text="Seleccionar Foto", command=seleccionar_foto, style="Accent.TButton").pack(side="left", padx=5)

    # --- Lógica de Guardar Usuario (actualizada a BBDD) ---
    def guardar_usuario():
        rol = rol_var.get().strip()
        matricula = matricula_var.get().strip()
        password = password_var.get()
        nombres = nombres_var.get().strip()
        apellidos = apellidos_var.get().strip()
        telefono = telefono_var.get().strip() or None
        direccion = direccion_var.get().strip() or None
        ruta_foto_original = foto_path.get()
        ruta_final = None

        if not matricula or not password or not nombres:
            messagebox.showwarning("Campos Requeridos", "Matrícula, Contraseña y Nombre(s) son obligatorios.")
            return

        # Lógica para copiar la foto
        if ruta_foto_original:
            ext = os.path.splitext(ruta_foto_original)[1]
            destino = f"assets/{matricula}{ext}"
            try:
                shutil.copy(ruta_foto_original, destino)
                ruta_final = destino # Guardar ruta relativa
            except Exception as e:
                messagebox.showerror("Error al copiar foto", f"No se pudo guardar la foto: {e}")
                ruta_final = None # Usará el default de la BBDD
        
        # Llamar a db_manager
        new_user_id = db_manager.create_user(
            username=matricula,
            password=password,
            role=rol,
            nombre_completo=nombres,
            apellidos=apellidos,
            telefono=telefono,
            direccion=direccion,
            ruta_foto=ruta_final # Pasa None si no se seleccionó foto, la BBDD usará el default
        )

        if new_user_id:
            messagebox.showinfo("Éxito", f"Usuario '{matricula}' agregado correctamente con ID: {new_user_id}.")
            # Limpiar campos
            for var in [matricula_var, password_var, nombres_var, apellidos_var, telefono_var, direccion_var]:
                var.set("")
            foto_path.set("")
            img_label.config(image=preview_img)
            img_label.image = preview_img
        else:
            messagebox.showerror("Error", f"La matrícula '{matricula}' ya existe o hubo un error al crear el usuario.")

    # Usamos ttk.Button y el estilo "Green.TButton"
    ttk.Button(form_frame, text="Guardar Usuario", command=guardar_usuario, style="Green.TButton").grid(row=len(campos)+2, column=0, columnspan=2, pady=20, sticky='we')

    return main_frame