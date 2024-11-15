import subprocess
import threading
import os

# Function to install Python dependencies
def install_python_dependencies():
    if os.path.exists('../requirements.txt'):
        print("Installing Python dependencies...")
        subprocess.run(["pip", "install", "-r", "../requirements.txt"])
    else:
        print("No 'requirements.txt' file found, skipping Python dependency installation.")

# Function to install Next.js dependencies
def install_nextjs_dependencies():
    client_path = "../client"  # Adjust the path to reflect relative position
    if os.path.exists(os.path.join(client_path, 'package.json')):
        print("Installing Next.js dependencies...")
        subprocess.run(["npm", "install"], cwd=client_path, check=True)  # Use "npm" for cross-platform
    else:
        print("No 'package.json' found, skipping Next.js dependency installation.")

# Function to run model_save.py
def run_model_save():
    try:
        print("Running model_save.py...")
        subprocess.run(["python3", "./server/model_save.py"], check=True)  # Adjust path to correct sub-directory
    except subprocess.CalledProcessError as e:
        print(f"Error occurred while running model_save.py: {e}")

# Function to run the Flask server
def run_flask():
    try:
        print("Running Flask server...")
        subprocess.run(["python3", "./server/server.py"], check=True)  # Correct the path to server.py
    except subprocess.CalledProcessError as e:
        print(f"Error occurred while running Flask: {e}")

# Function to run the Next.js app using "npm run dev"
def run_nextjs():
    client_path = "../client"  # Adjust the path to reflect relative position
    try:
        subprocess.run(["npm", "run", "dev"], cwd=client_path, check=True)  # Use "npm" for cross-platform
    except subprocess.CalledProcessError as e:
        print(f"Error occurred while running Next.js: {e}")

if __name__ == '__main__':
    # Step 1: Install dependencies
    install_python_dependencies()
    install_nextjs_dependencies()

    # Step 2: Run model_save.py
    run_model_save()

    # Step 3: Start Flask server in a separate thread
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.start()

    # Step 4: Start Next.js frontend in the main thread
    run_nextjs()