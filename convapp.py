#!/usr/bin/env python3
import os
import subprocess
import sys
import shutil
import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox

def check_install_pyinstaller():
    """Check if PyInstaller is installed. If not, install it."""
    try:
        result = subprocess.run(["pyinstaller", "--version"],
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if result.returncode != 0:
            raise Exception("PyInstaller not found")
    except Exception:
        if messagebox.askyesno("Install PyInstaller", "PyInstaller is not installed. Install it now?"):
            subprocess.check_call([sys.executable, "-m", "pip", "install", "--user", "pyinstaller"])
        else:
            messagebox.showerror("Error", "PyInstaller is required to convert scripts. Exiting. 😢")
            sys.exit(1)

def convert_python_app():
    root = tk.Tk()
    root.withdraw()

    # 1. Select the Python script to convert.
    py_script = filedialog.askopenfilename(
        title="Select the Python script to convert",
        filetypes=[("Python Files", "*.py")],
        initialdir=os.path.expanduser("~")
    )
    if not py_script:
        messagebox.showinfo("Cancelled", "No Python script selected. Exiting. 😕")
        return

    # 2. Enter the app name.
    app_name = simpledialog.askstring("App Name", "Enter the app name:", parent=root)
    if not app_name:
        messagebox.showinfo("Cancelled", "No app name provided. Exiting. 😕")
        return

    # 3. Optionally choose an icon.
    if messagebox.askyesno("Icon", "Do you want to choose an icon for your app? 🤔"):
        icon_path = filedialog.askopenfilename(
            title="Select an icon image (ICO recommended)",
            filetypes=[("Icon Files", "*.ico"), ("Image Files", "*.png *.jpg *.svg"), ("All Files", "*.*")]
        )
        if not icon_path:
            icon_path = None
    else:
        icon_path = None

    # 4. Choose terminal mode: hide terminal or not.
    use_terminal = messagebox.askyesno("Terminal?", "Should the app run in a terminal window? (No = hidden)")
    # PyInstaller uses --noconsole to hide the terminal
    no_console_flag = "--noconsole" if not use_terminal else ""

    # 5. Check/install PyInstaller.
    check_install_pyinstaller()

    # 6. Run PyInstaller to convert the script.
    # We'll run in a temporary folder to avoid clutter.
    work_dir = os.getcwd()
    pyinstaller_cmd = [
        "pyinstaller",
        "--onefile",
        f"--name={app_name}"
    ]
    if icon_path:
        pyinstaller_cmd.append(f"--icon={icon_path}")
    if no_console_flag:
        pyinstaller_cmd.append(no_console_flag)
    pyinstaller_cmd.append(py_script)

    try:
        subprocess.check_call(pyinstaller_cmd)
    except subprocess.CalledProcessError as e:
        messagebox.showerror("Error", f"PyInstaller failed: {e} 😢")
        return

    # 7. Move the executable to a dedicated folder.
    # The executable is in the "dist" folder.
    dist_dir = os.path.join(work_dir, "dist")
    exe_path = os.path.join(dist_dir, app_name)
    if not os.path.exists(exe_path):
        # Some systems might add an extension, try with .py (or .exe for Windows, but we're targeting Linux)
        exe_path = os.path.join(dist_dir, app_name + ".py")
        if not os.path.exists(exe_path):
            messagebox.showerror("Error", "Executable not found after PyInstaller. 😢")
            return

    # Create destination folder for executables.
    final_dir = os.path.join(os.path.expanduser("~"), ".local", "share", "applications", "py_apps")
    os.makedirs(final_dir, exist_ok=True)
    final_exe_path = os.path.join(final_dir, app_name)
    try:
        shutil.move(exe_path, final_exe_path)
        os.chmod(final_exe_path, 0o755)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to move the executable: {e} 😢")
        return

    # 8. Cleanup PyInstaller generated files and folders.
    for folder in ["build", "dist"]:
        folder_path = os.path.join(work_dir, folder)
        if os.path.exists(folder_path):
            shutil.rmtree(folder_path)
    spec_file = os.path.join(work_dir, f"{app_name}.spec")
    if os.path.exists(spec_file):
        os.remove(spec_file)

    # 9. Create a .desktop file to launch the new app.
    desktop_entry = f"""[Desktop Entry]
Type=Application
Name={app_name}
Exec="{final_exe_path}"
Icon={icon_path if icon_path else "utilities-terminal"}
Terminal=false
Categories=Utility;
"""
    applications_dir = os.path.join(os.path.expanduser("~"), ".local", "share", "applications")
    os.makedirs(applications_dir, exist_ok=True)
    desktop_file_path = os.path.join(applications_dir, f"{app_name}.desktop")
    try:
        with open(desktop_file_path, "w") as f:
            f.write(desktop_entry)
        os.chmod(desktop_file_path, 0o755)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to create .desktop file: {e} 😢")
        return

    messagebox.showinfo("Success", f"App '{app_name}' created successfully!\nExecutable at:\n{final_exe_path}\nDesktop entry created.")
    root.destroy()

def create_app():
    """Existing function to create a .desktop file for an existing file."""
    root = tk.Tk()
    root.withdraw()

    file_path = filedialog.askopenfilename(
        title="Select the file to launch",
        initialdir=os.path.expanduser("~")
    )
    if not file_path:
        messagebox.showinfo("Cancelled", "No file selected. Exiting. 😕")
        return

    if messagebox.askyesno("Icon", "Do you want to choose an icon for your app? 🤔"):
        icon_path = filedialog.askopenfilename(
            title="Select an icon image",
            filetypes=[("Image Files", "*.png *.jpg *.svg *.ico"), ("All Files", "*.*")]
        )
        if not icon_path:
            icon_path = "utilities-terminal"
    else:
        icon_path = "utilities-terminal"

    app_name = simpledialog.askstring("App Name", "Enter the app name:", parent=root)
    if not app_name:
        messagebox.showinfo("Cancelled", "No app name provided. Exiting. 😕")
        return

    desktop_entry = f"""[Desktop Entry]
Type=Application
Name={app_name}
Exec="{file_path}"
Icon={icon_path}
Terminal=false
Categories=Utility;
"""
    applications_dir = os.path.join(os.path.expanduser("~"), ".local", "share", "applications")
    os.makedirs(applications_dir, exist_ok=True)
    desktop_file_path = os.path.join(applications_dir, f"{app_name}.desktop")

    try:
        with open(desktop_file_path, "w") as f:
            f.write(desktop_entry)
        os.chmod(desktop_file_path, 0o755)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to create desktop app: {e} 😢")
        return

    if messagebox.askyesno("Terminal Variant", "Do you want a terminal version as well? 💻"):
        term_app_name = simpledialog.askstring("Terminal App Name",
                                                 f"Enter name for terminal version (default: {app_name} Terminal):",
                                                 parent=root)
        if not term_app_name:
            term_app_name = f"{app_name} Terminal"
        term_entry = f"""[Desktop Entry]
Type=Application
Name={term_app_name}
Exec="{file_path}"
Icon={icon_path}
Terminal=true
Categories=Utility;
"""
        term_desktop_file_path = os.path.join(applications_dir, f"{term_app_name}.desktop")
        try:
            with open(term_desktop_file_path, "w") as f:
                f.write(term_entry)
            os.chmod(term_desktop_file_path, 0o755)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create terminal desktop app: {e} 😢")
            return

    messagebox.showinfo("Success", f"App(s) '{app_name}' created and added to your app menu! 🚀")
    root.destroy()

def delete_app():
    applications_dir = os.path.join(os.path.expanduser("~"), ".local", "share", "applications")
    if not os.path.isdir(applications_dir):
        messagebox.showinfo("Info", "Applications folder not found. 😕")
        return

    root = tk.Tk()
    root.withdraw()
    selected_file = filedialog.askopenfilename(
        title="Select a .desktop file to delete",
        initialdir=applications_dir,
        filetypes=[("Desktop Files", "*.desktop")]
    )
    if not selected_file:
        messagebox.showinfo("Cancelled", "No file selected. 😕")
        return

    if not messagebox.askyesno("Confirm", f"Delete the file:\n{os.path.basename(selected_file)}? This action cannot be undone."):
        return

    try:
        os.remove(selected_file)
        messagebox.showinfo("Deleted", f"File '{os.path.basename(selected_file)}' deleted successfully! 🚮")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to delete the file: {e} 😢")
    root.destroy()

def main_menu():
    menu = tk.Tk()
    menu.title("Custom App Manager")
    tk.Label(menu, text="Choose an operation:", font=("Arial", 12)).pack(padx=10, pady=10)

    tk.Button(menu, text="Create New App", width=25, command=lambda: [menu.destroy(), create_app()]).pack(pady=5)
    tk.Button(menu, text="Convert Python Script to App", width=25, command=lambda: [menu.destroy(), convert_python_app()]).pack(pady=5)
    tk.Button(menu, text="Delete Existing App", width=25, command=lambda: [menu.destroy(), delete_app()]).pack(pady=5)

    menu.mainloop()

if __name__ == "__main__":
    main_menu()
