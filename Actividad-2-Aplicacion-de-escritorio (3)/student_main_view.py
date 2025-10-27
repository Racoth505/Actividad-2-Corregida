# student_main_view.py
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import os
import db_manager  # Import DB manager

# Importar las vistas
from student_subjects_view import create_student_subjects_view
from tab_profile import create_profile_tab  # Reutilizar lógica de perfil

# Placeholders globales
_logout_func = None
_update_header_func = None
student_lbl_photo_header = None


def show_view(content_frame, user_data, view_name):
    """Limpia el frame de contenido y muestra la vista seleccionada."""
    for widget in content_frame.winfo_children():
        widget.destroy()

    if view_name == "subjects":
        create_student_subjects_view(content_frame, user_data)
    elif view_name == "profile":
        view_frame = create_profile_tab(content_frame, user_data, _update_header_func)
        view_frame.pack(fill=tk.BOTH, expand=True)


def create_student_main_view(root, user_data, logout_func, update_header_func):
    """Crea el dashboard principal del alumno con sidebar y área de contenido."""
    global _logout_func, _update_header_func, student_lbl_photo_header
    _logout_func = logout_func
    _update_header_func = update_header_func

    # --- Configurar grid principal ---
    sidebar_width = 220
    root.columnconfigure(0, weight=0, minsize=sidebar_width)
    root.columnconfigure(1, weight=1)
    root.rowconfigure(0, weight=1)

    # --- Sidebar ---
    sidebar_frame = tk.Frame(root, bg="#28a745", width=sidebar_width)
    sidebar_frame.grid(row=0, column=0, sticky="nsew")
    sidebar_frame.rowconfigure(1, weight=1)

    # --- Banner ---
    try:
        banner_img_path = "assets/banner.png"
        original_img = Image.open(banner_img_path)
        img_w, img_h = original_img.size
        target_w = sidebar_width - 20
        ratio = target_w / img_w
        target_h = int(img_h * ratio)
        banner_img = original_img.resize((target_w, target_h), Image.Resampling.LANCZOS)
        banner_photo = ImageTk.PhotoImage(banner_img)
        lbl_banner = tk.Label(sidebar_frame, image=banner_photo, bg="#28a745")
        lbl_banner.image = banner_photo
        lbl_banner.grid(row=0, column=0, pady=20, padx=10, sticky="ew")
    except Exception as e:
        print(f"Error cargando banner.png: {e}")
        lbl_banner = tk.Label(
            sidebar_frame, text="[BANNER]", bg="#28a745", fg="white",
            font=("Helvetica", 16, "bold")
        )
        lbl_banner.grid(row=0, column=0, pady=20, padx=10, sticky="ew")

    # --- Navegación ---
    nav_frame = tk.Frame(sidebar_frame, bg="#28a745")
    nav_frame.grid(row=1, column=0, sticky="new", pady=10, padx=10)
    nav_frame.columnconfigure(1, weight=1)

    btn_materias = ttk.Button(
        nav_frame, text="📁 Materias",
        command=lambda: show_view(content_frame, user_data, "subjects")
    )
    btn_materias.grid(row=0, column=1, sticky="ew", pady=(10, 5))

    # --- Parte inferior ---
    bottom_frame = tk.Frame(sidebar_frame, bg="#28a745")
    bottom_frame.grid(row=2, column=0, sticky="sew", pady=20, padx=10)
    bottom_frame.columnconfigure(0, weight=1)

    btn_perfil = ttk.Button(
        bottom_frame, text="👤 Perfil",
        command=lambda: show_view(content_frame, user_data, "profile")
    )
    btn_perfil.grid(row=0, column=0, sticky="ew", pady=(0, 5))

    btn_salir = ttk.Button(bottom_frame, text="➔ Salir", command=_logout_func)
    btn_salir.grid(row=1, column=0, sticky="ew", pady=(5, 0))

    # --- Área de contenido ---
    content_area = ttk.Frame(root, padding=(20, 10))
    content_area.grid(row=0, column=1, sticky="nsew")
    content_area.rowconfigure(1, weight=1)
    content_area.columnconfigure(0, weight=1)

    # Header
    header_frame = ttk.Frame(content_area)
    header_frame.grid(row=0, column=0, sticky="ew", pady=(10, 20))

    student_lbl_photo_header = ttk.Label(header_frame)
    student_lbl_photo_header.pack(side=tk.RIGHT, padx=(0, 10))

    _update_header_func()  # Carga inicial

    header_text = f"{user_data['nombre_completo']} ({user_data['role'].capitalize()})"
    ttk.Label(header_frame, text=header_text, font=("Helvetica", 14)).pack(side=tk.RIGHT, padx=(0, 10))

    # Frame para las vistas dinámicas
    content_frame = ttk.Frame(content_area)
    content_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))

    # Mostrar vista inicial
    show_view(content_frame, user_data, "subjects")