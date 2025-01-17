import os
import subprocess
import sys


def create_virtual_environment():
    print("Создание виртуального окружения...")
    if not os.path.exists("venv"):
        subprocess.run([sys.executable, "-m", "venv", "venv"])
        print("Виртуальное окружение создано.")
    else:
        print("Виртуальное окружение уже существует.")


def activate_virtual_environment():
    """Активирует виртуальное окружение."""
    if os.name == "nt":  # Windows
        return os.path.join("venv", "Scripts", "python.exe")
    else:  # macOS/Linux
        return os.path.join("venv", "bin", "python")


def install_dependencies(python_path):
    print("Установка зависимостей...")
    if not os.path.exists("requirements.txt"):
        with open("requirements.txt", "w") as f:
            f.write("fastapi\nuvicorn\nhttpx\npydantic\npytest\n")
    subprocess.run([python_path, "-m", "pip", "install", "--upgrade", "pip"])
    subprocess.run([python_path, "-m", "pip", "install", "-r", "requirements.txt"])
    print("Все зависимости установлены.")


def run_server(python_path):
    print("Запуск сервера FastAPI...")
    subprocess.run([python_path, "-m", "uvicorn", "main:app", "--reload"])


if __name__ == "__main__":
    create_virtual_environment()
    python_path = activate_virtual_environment()
    install_dependencies(python_path)
    print("Инициализация базы данных...")
    subprocess.run([python_path, "main.py"])

    run_server(python_path)
