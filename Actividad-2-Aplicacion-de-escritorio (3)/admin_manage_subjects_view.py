# admin_manage_subjects_view.py
import tkinter as tk
from tkinter import messagebox, ttk
import db_manager

def create_manage_subjects_view(parent):
    """Vista del Admin para agregar nuevas materias con detalles."""
    view_frame = ttk.Frame(parent, style="Main.TFrame")

    # --- Configuración Responsiva ---
    view_frame.columnconfigure(0, weight=1)  # Columna única se expande
    view_frame.rowconfigure(1, weight=1)  # Fila del form se expande

    # --- Título ---
    title_frame = ttk.Frame(view_frame, style="Main.TFrame")
    title_frame.grid(row=0, column=0, sticky="w", padx=20, pady=(0, 20))
    try:
        from admin_main_view import _icon_images
        icon = _icon_images.get("icon_add_subject.png")
        if icon:
            ttk.Label(title_frame, image=icon, style="TLabel").pack(side=tk.LEFT, padx=(0, 10))
    except:
        pass
    ttk.Label(title_frame, text="Agregar Materias", font=("Helvetica", 18, "bold"), style="TLabel").pack(side=tk.LEFT)

    # --- Frame principal para el formulario ---
    form_area = ttk.Frame(view_frame, style="Main.TFrame")
    form_area.grid(row=1, column=0, sticky="n", padx=20, pady=0)
    form_area.columnconfigure(1, weight=1, minsize=350)
    form_area.columnconfigure(2, weight=0)

    # Helper
    def create_labeled_entry(parent_frame, label_text, row, show=None, placeholder=None):
        ttk.Label(parent_frame, text=label_text, style="TLabel").grid(row=row, column=0, sticky="w", pady=5, padx=5)
        entry = ttk.Entry(parent_frame, show=show, font=("Helvetica", 10))
        entry.grid(row=row, column=1, columnspan=2, sticky="ew", pady=5, padx=5, ipady=4)
        if placeholder:
            entry.insert(0, placeholder)
        return entry

    # Campos
    row_idx = 0
    entry_name = create_labeled_entry(form_area, "Nombre de la Materia", row_idx)
    row_idx += 1

    # Profesor Principal
    ttk.Label(form_area, text="Profesor Principal", style="TLabel").grid(row=row_idx, column=0, sticky="w", pady=5, padx=5)
    combo_prof = ttk.Combobox(form_area, state="readonly", font=("Helvetica", 10))
    combo_prof.grid(row=row_idx, column=1, sticky="ew", pady=5, padx=5)  # Combo ocupa columna 1
    row_idx += 1

    entry_hours = create_labeled_entry(form_area, "Horas Semanales", row_idx)
    row_idx += 1
    entry_salon = create_labeled_entry(form_area, "Salon", row_idx)
    row_idx += 1
    entry_start_date = create_labeled_entry(form_area, "Fecha de Inicio", row_idx, placeholder="YYYY-MM-DD")
    row_idx += 1
    entry_end_date = create_labeled_entry(form_area, "Fecha de Fin", row_idx, placeholder="YYYY-MM-DD")
    row_idx += 1

    # --- Botón Guardar ---
    btn_save = ttk.Button(form_area, text="Guardar Materia", style="Green.TButton", command=lambda: save_new_subject())
    btn_save.grid(row=row_idx, column=0, columnspan=3, pady=30, ipady=5, sticky="ew", padx=5)

    # --- Mapas ---
    prof_map_display_to_id = {}  # Mapa de "Nombre (username)" a ID

    # --- Lógica ---
    def refresh_professor_list():
        combo_prof.set("(Opcional)")
        prof_map_display_to_id.clear()
        professors = db_manager.get_users_by_role("profesor")
        prof_display_list = ["(Ninguno)"]
        prof_map_display_to_id["(Ninguno)"] = None
        for prof in professors:
            display_text = f"{prof['nombre_completo']} ({prof['username']})"  # Mostrar nombre y username
            prof_display_list.append(display_text)
            prof_map_display_to_id[display_text] = prof["id"]
        combo_prof['values'] = prof_display_list

    def on_prof_select(event):
        combo_prof.selection_clear()

    combo_prof.bind("<<ComboboxSelected>>", on_prof_select)

    def clear_form():
        entry_name.delete(0, tk.END)
        combo_prof.set("(Opcional)")
        entry_hours.delete(0, tk.END)
        entry_salon.delete(0, tk.END)
        entry_start_date.delete(0, tk.END)
        entry_start_date.insert(0, "YYYY-MM-DD")
        entry_end_date.delete(0, tk.END)
        entry_end_date.insert(0, "YYYY-MM-DD")

    def save_new_subject():
        name = entry_name.get().strip()
        prof_display = combo_prof.get()
        hours_str = entry_hours.get().strip()
        salon = entry_salon.get().strip()
        start_date = entry_start_date.get().strip()
        end_date = entry_end_date.get().strip()

        if not name:
            messagebox.showwarning("Nombre Requerido", "El nombre de la materia es obligatorio.")
            return

        # Handle "(Ninguno)" or "(Opcional)" selection for professor
        prof_id = None
        if prof_display and prof_display not in ["(Ninguno)", "(Opcional)"]:
            prof_id = prof_map_display_to_id.get(prof_display)

        hours = None
        if hours_str:
            try:
                hours = int(hours_str)
            except ValueError:
                messagebox.showerror("Error", "Horas Semanales debe ser un número entero.")
                return

        if start_date == "YYYY-MM-DD":
            start_date = None
        if end_date == "YYYY-MM-DD":
            end_date = None

        success = db_manager.add_subject_with_details(name, prof_id, hours, salon, start_date, end_date)

        if success:
            messagebox.showinfo("Éxito", f"Materia '{name}' agregada correctamente.")
            clear_form()
        else:
            messagebox.showerror("Error", f"No se pudo agregar la materia '{name}'. ¿Ya existe?")

    # Carga inicial
    refresh_professor_list()
    clear_form()  # Poner placeholders

    return view_frame