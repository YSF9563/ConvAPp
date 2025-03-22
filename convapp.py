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
        if messagebox.askyesno("Install PyInstaller", "PyInstaller is not installed. Install it now? 🤔"):
            subprocess.check_call([sys.executable, "-m", "pip", "install", "--user", "pyinstaller"])
        else:
            messagebox.showerror("Error", "PyInstaller is required to convert scripts. Exiting. 😢")
            sys.exit(1)

def check_linuxdeploy():
    """Check if linuxdeploy is installed for AppImage packaging."""
    try:
        result = subprocess.run(["linuxdeploy", "--version"],
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if result.returncode != 0:
            raise Exception("linuxdeploy not found")
    except Exception:
        messagebox.showerror("Error", "linuxdeploy is required for AppImage creation. Install it from https://github.com/linuxdeploy/linuxdeploy 😢")
        sys.exit(1)

def convert_python_app():
    """Convert a Python script into an executable and create a desktop entry."""
    root = tk.Tk()
    root.withdraw()

    py_script = filedialog.askopenfilename(
        title="Select the Python script to convert",
        filetypes=[("Python Files", "*.py")],
        initialdir=os.path.expanduser("~")
    )
    if not py_script:
        messagebox.showinfo("Cancelled", "No Python script selected. Exiting. 😕")
        return

    app_name = simpledialog.askstring("App Name", "Enter the app name:", parent=root)
    if not app_name:
        messagebox.showinfo("Cancelled", "No app name provided. Exiting. 😕")
        return

    icon_path = None
    if messagebox.askyesno("Icon", "Do you want to choose an icon for your app? 🤔"):
        icon_path = filedialog.askopenfilename(
            title="Select an icon image (ICO recommended)",
            filetypes=[("Icon Files", "*.ico"), ("Image Files", "*.png *.jpg *.svg"), ("All Files", "*.*")]
        )
        if not icon_path:
            icon_path = None

    use_terminal = messagebox.askyesno("Terminal?", "Should the app run in a terminal window? (No = hidden)")
    no_console_flag = "--noconsole" if not use_terminal else ""

    check_install_pyinstaller()

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

    dist_dir = os.path.join(work_dir, "dist")
    exe_path = os.path.join(dist_dir, app_name)
    if not os.path.exists(exe_path):
        # Try with extension (if on Windows)
        exe_path = os.path.join(dist_dir, app_name + ".exe")
        if not os.path.exists(exe_path):
            messagebox.showerror("Error", "Executable not found after PyInstaller. 😢")
            return

    final_dir = os.path.join(os.path.expanduser("~"), ".local", "share", "applications", "py_apps")
    os.makedirs(final_dir, exist_ok=True)
    final_exe_path = os.path.join(final_dir, app_name)
    try:
        shutil.move(exe_path, final_exe_path)
        os.chmod(final_exe_path, 0o755)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to move the executable: {e} 😢")
        return

    # Cleanup build files
    for folder in ["build", "dist"]:
        folder_path = os.path.join(work_dir, folder)
        if os.path.exists(folder_path):
            shutil.rmtree(folder_path)
    spec_file = os.path.join(work_dir, f"{app_name}.spec")
    if os.path.exists(spec_file):
        os.remove(spec_file)

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

    messagebox.showinfo("Success", f"App '{app_name}' created successfully!\nExecutable at:\n{final_exe_path}\nDesktop entry created. 🚀")
    root.destroy()

def convert_python_appimage():
    """Convert a Python script into an AppImage using PyInstaller and linuxdeploy."""
    root = tk.Tk()
    root.withdraw()

    py_script = filedialog.askopenfilename(
        title="Select the Python script to convert for AppImage",
        filetypes=[("Python Files", "*.py")],
        initialdir=os.path.expanduser("~")
    )
    if not py_script:
        messagebox.showinfo("Cancelled", "No Python script selected. Exiting. 😕")
        return

    app_name = simpledialog.askstring("App Name", "Enter the app name:", parent=root)
    if not app_name:
        messagebox.showinfo("Cancelled", "No app name provided. Exiting. 😕")
        return

    icon_path = None
    if messagebox.askyesno("Icon", "Do you want to choose an icon for your app? 🤔"):
        icon_path = filedialog.askopenfilename(
            title="Select an icon image (ICO recommended)",
            filetypes=[("Icon Files", "*.ico"), ("Image Files", "*.png *.jpg *.svg"), ("All Files", "*.*")]
        )
        if not icon_path:
            icon_path = None

    use_terminal = messagebox.askyesno("Terminal?", "Should the app run in a terminal window? (No = hidden)")
    no_console_flag = "--noconsole" if not use_terminal else ""

    check_install_pyinstaller()
    check_linuxdeploy()

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

    dist_dir = os.path.join(work_dir, "dist")
    exe_path = os.path.join(dist_dir, app_name)
    if not os.path.exists(exe_path):
        exe_path = os.path.join(dist_dir, app_name + ".exe")
        if not os.path.exists(exe_path):
            messagebox.showerror("Error", "Executable not found after PyInstaller. 😢")
            return

    # Create AppDir structure
    appdir = os.path.join(work_dir, f"{app_name}.AppDir")
    usr_bin = os.path.join(appdir, "usr", "bin")
    os.makedirs(usr_bin, exist_ok=True)
    final_exe_path = os.path.join(usr_bin, app_name)
    try:
        shutil.move(exe_path, final_exe_path)
        os.chmod(final_exe_path, 0o755)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to move the executable: {e} 😢")
        return

    # Create a .desktop file inside AppDir
    desktop_entry = f"""[Desktop Entry]
Type=Application
Name={app_name}
Exec={app_name}
Icon={icon_path if icon_path else "utilities-terminal"}
Terminal=false
Categories=Utility;
"""
    desktop_file_dir = os.path.join(appdir, "usr", "share", "applications")
    os.makedirs(desktop_file_dir, exist_ok=True)
    desktop_file_path = os.path.join(desktop_file_dir, f"{app_name}.desktop")
    try:
        with open(desktop_file_path, "w") as f:
            f.write(desktop_entry)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to create .desktop file in AppDir: {e} 😢")
        return

    # Run linuxdeploy to package the AppDir into an AppImage.
    try:
        subprocess.check_call(["linuxdeploy", "--appdir", appdir, "--output", "appimage"])
    except subprocess.CalledProcessError as e:
        messagebox.showerror("Error", f"linuxdeploy failed: {e} 😢")
        return

    messagebox.showinfo("Success", f"AppImage for '{app_name}' created successfully in {work_dir}! 🚀")
    # Cleanup temporary files
    for folder in ["build", "dist"]:
        folder_path = os.path.join(work_dir, folder)
        if os.path.exists(folder_path):
            shutil.rmtree(folder_path)
    spec_file = os.path.join(work_dir, f"{app_name}.spec")
    if os.path.exists(spec_file):
        os.remove(spec_file)
    root.destroy()

def create_bash_app():
    """Create a desktop entry for a Bash script."""
    root = tk.Tk()
    root.withdraw()

    bash_script = filedialog.askopenfilename(
        title="Select the Bash script",
        filetypes=[("Bash Scripts", "*.sh"), ("All Files", "*.*")],
        initialdir=os.path.expanduser("~")
    )
    if not bash_script:
        messagebox.showinfo("Cancelled", "No Bash script selected. Exiting. 😕")
        return

    app_name = simpledialog.askstring("App Name", "Enter the app name:", parent=root)
    if not app_name:
        messagebox.showinfo("Cancelled", "No app name provided. Exiting. 😕")
        return

    icon_path = "utilities-terminal"
    if messagebox.askyesno("Icon", "Do you want to choose an icon for your app? 🤔"):
        chosen_icon = filedialog.askopenfilename(
            title="Select an icon image",
            filetypes=[("Image Files", "*.png *.jpg *.svg *.ico"), ("All Files", "*.*")]
        )
        if chosen_icon:
            icon_path = chosen_icon

    # Ensure the bash script is executable.
    try:
        os.chmod(bash_script, 0o755)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to set executable permission: {e} 😢")
        return

    desktop_entry = f"""[Desktop Entry]
Type=Application
Name={app_name}
Exec="{bash_script}"
Icon={icon_path}
Terminal=true
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
        messagebox.showerror("Error", f"Failed to create desktop entry: {e} 😢")
        return

    messagebox.showinfo("Success", f"Bash app '{app_name}' created successfully! 🚀")
    root.destroy()

def create_jar_app():
    """Create a desktop entry to launch a Java JAR file."""
    root = tk.Tk()
    root.withdraw()

    jar_file = filedialog.askopenfilename(
        title="Select the JAR file",
        filetypes=[("JAR Files", "*.jar"), ("All Files", "*.*")],
        initialdir=os.path.expanduser("~")
    )
    if not jar_file:
        messagebox.showinfo("Cancelled", "No JAR file selected. Exiting. 😕")
        return

    app_name = simpledialog.askstring("App Name", "Enter the app name:", parent=root)
    if not app_name:
        messagebox.showinfo("Cancelled", "No app name provided. Exiting. 😕")
        return

    icon_path = "utilities-terminal"
    if messagebox.askyesno("Icon", "Do you want to choose an icon for your app? 🤔"):
        chosen_icon = filedialog.askopenfilename(
            title="Select an icon image",
            filetypes=[("Image Files", "*.png *.jpg *.svg *.ico"), ("All Files", "*.*")]
        )
        if chosen_icon:
            icon_path = chosen_icon

    desktop_entry = f"""[Desktop Entry]
Type=Application
Name={app_name}
Exec=java -jar "{jar_file}"
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
        messagebox.showerror("Error", f"Failed to create desktop entry: {e} 😢")
        return

    messagebox.showinfo("Success", f"Java app '{app_name}' created successfully! 🚀")
    root.destroy()

def convert_appimage_to_app():
    """Convert an existing AppImage into a desktop application entry."""
    root = tk.Tk()
    root.withdraw()

    appimage_file = filedialog.askopenfilename(
        title="Select the AppImage file",
        filetypes=[("AppImage Files", "*.AppImage"), ("All Files", "*.*")],
        initialdir=os.path.expanduser("~")
    )
    if not appimage_file:
        messagebox.showinfo("Cancelled", "No AppImage selected. Exiting. 😕")
        return

    app_name = simpledialog.askstring("App Name", "Enter the app name for the AppImage:", parent=root)
    if not app_name:
        messagebox.showinfo("Cancelled", "No app name provided. Exiting. 😕")
        return

    icon_path = None
    if messagebox.askyesno("Icon", "Do you want to choose an icon for your AppImage app? 🤔"):
        icon_path = filedialog.askopenfilename(
            title="Select an icon image",
            filetypes=[("Icon Files", "*.ico"), ("Image Files", "*.png *.jpg *.svg"), ("All Files", "*.*")]
        )
        if not icon_path:
            icon_path = None

    # Ensure the AppImage is executable
    try:
        os.chmod(appimage_file, 0o755)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to set executable permission: {e} 😢")
        return

    # Move the AppImage to a dedicated folder
    final_dir = os.path.join(os.path.expanduser("~"), ".local", "share", "applications", "appimages")
    os.makedirs(final_dir, exist_ok=True)
    final_appimage_path = os.path.join(final_dir, os.path.basename(appimage_file))
    try:
        shutil.copy(appimage_file, final_appimage_path)
        os.chmod(final_appimage_path, 0o755)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to copy the AppImage: {e} 😢")
        return

    # Create a desktop entry for the AppImage
    desktop_entry = f"""[Desktop Entry]
Type=Application
Name={app_name}
Exec="{final_appimage_path}"
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
        messagebox.showerror("Error", f"Failed to create desktop entry: {e} 😢")
        return

    messagebox.showinfo("Success", f"AppImage '{app_name}' converted to an application successfully! 🚀")
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

    tk.Button(menu, text="Convert Python Script to App", width=40, command=lambda: [menu.destroy(), convert_python_app()]).pack(pady=5)
    tk.Button(menu, text="Convert Python Script to AppImage", width=40, command=lambda: [menu.destroy(), convert_python_appimage()]).pack(pady=5)
    tk.Button(menu, text="Create Bash Script App", width=40, command=lambda: [menu.destroy(), create_bash_app()]).pack(pady=5)
    tk.Button(menu, text="Create Java App (JAR)", width=40, command=lambda: [menu.destroy(), create_jar_app()]).pack(pady=5)
    tk.Button(menu, text="Convert AppImage to Application", width=40, command=lambda: [menu.destroy(), convert_appimage_to_app()]).pack(pady=5)
    tk.Button(menu, text="Delete Existing App", width=40, command=lambda: [menu.destroy(), delete_app()]).pack(pady=5)

    menu.mainloop()

if __name__ == "__main__":
    main_menu()
