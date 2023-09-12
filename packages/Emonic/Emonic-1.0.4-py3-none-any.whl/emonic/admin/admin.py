import os
import argparse
import subprocess
from colorama import Fore, Style  # Import colorama for colored output

def create_project(project_name, use_database, setup_routing, setup_engine):
    # Create a folder for the project
    os.makedirs(project_name, exist_ok=True)

    # Create settings.py
    with open(os.path.join(project_name, 'settings.py'), 'w') as settings_file:
        settings_file.write(f"HOST = 'localhost'\n")
        settings_file.write(f"PORT = 8000\n")
        settings_file.write(f"DEBUG = True\n")
        settings_file.write(f"SECRET_KEY = 'your_secret_key'\n")
        settings_file.write(f"STATIC_FOLDER = 'static'\n")

        settings_file.write("\nTEMPLATES = [\n")
        settings_file.write("    {\n")
        settings_file.write("        'BACKEND': 'emonic.backends.EmonicTemplates',\n")
        settings_file.write("        'DIRS': ['views'],\n")
        settings_file.write("    }\n")
        settings_file.write("]\n")

        if use_database:
            settings_file.write("\nDATABASES = {\n")
            settings_file.write("    'default': {\n")
            settings_file.write("        'ENGINE': 'emonic.db.backends.electrus',\n")
            settings_file.write("        'HOST': 'localhost',\n")
            settings_file.write("        'PORT': 37017,\n")
            settings_file.write("        'USER': 'root',\n")
            settings_file.write("        'PASSWORD': 'root',\n")
            settings_file.write("    }\n")
            settings_file.write("}\n")

        settings_file.write("\nMAILER = [\n")
        settings_file.write("    {\n")
        settings_file.write("        \"SMTP\": \"VALUE\",\n")
        settings_file.write("        \"PORT\": \"VALUE\",\n")
        settings_file.write("        \"USERNAME\": \"VALUE\",\n")
        settings_file.write("        \"PASSWORD\": \"VALUE\",\n")
        settings_file.write("        \"SSL\": True,\n")
        settings_file.write("        \"DEFAULT_SENDER\": \"VALUE\",\n")
        settings_file.write("    }\n")
        settings_file.write("]\n")

        settings_file.write("\nSCRIPT = [\n")
        settings_file.write("    {\n")
        settings_file.write("        \"config\": {\n")
        settings_file.write("            \"wsgi\": \"emonic.wsgi.http\",\n")
        settings_file.write("            \"host\": \"localhost\",\n")
        settings_file.write("            \"port\": \"8000\",\n")
        settings_file.write("            \"debug\": \"True\",\n")
        settings_file.write("        },\n")
        settings_file.write("        \"apps\": {\n")
        settings_file.write("            \"emonic\",\n")
        settings_file.write("            \"emonic-admin\"\n")
        settings_file.write("            # add more emonic apps for e.g, electrus nexusdb etc...\n")
        settings_file.write("        }\n")
        settings_file.write("    }\n")
        settings_file.write("]\n")

    if setup_routing:
        # Create Router folder
        os.makedirs(os.path.join(project_name, 'Routes'), exist_ok=True)

        # Create clust.py inside Routes folder
        clust_py_content = """from emonic.components.blueprint import Blueprint

home = Blueprint('Home', __name__, url_prefix='/home')

@home.route('/')
def BlueprintHomeRoute(request):
    return home.text_response('hello')
    """

        routes_folder = os.path.join(project_name, 'Routes')
        os.makedirs(routes_folder, exist_ok=True)

        with open(os.path.join(routes_folder, 'clust.py'), 'w') as clust_file:
            clust_file.write(clust_py_content)

    else:
        # Create app folder
        os.makedirs(os.path.join(project_name, 'app'), exist_ok=True)

    if setup_engine:
        # Create views and static folders
        os.makedirs(os.path.join(project_name, 'views'), exist_ok=True)
        os.makedirs(os.path.join(project_name, 'static'), exist_ok=True)

    if use_database:
        # Install Electrus package
        subprocess.run(['pip', 'install', 'electrus'])

    # Create main.py
    main_py_content = """from emonic.core import Emonic

app = Emonic(__name__)

@app.route('/<name: str>', methods=['GET', 'POST'])
def emonicHomeRoute(request, name):
    return f"Welcome, {name} to Emonic Web server"

if __name__ == "__main__":
    app.run()
    """
    with open(os.path.join(project_name, 'main.py'), 'w') as main_file:
        main_file.write(main_py_content)

    # Create config.ini outside the project folder
    project_path = os.path.abspath(project_name)
    config_ini_content = f"""[PROJECT]
SERVER = "Emonic"
HOST = "localhost"
PORT = 8000
ALIAS = "Keep-Active-2.1"
ROOT = {project_path}
NAME = {project_name}
"""
    with open('config.ini', 'w') as config_file:
        config_file.write(config_ini_content)

def main():
    parser = argparse.ArgumentParser(description='Build a project')
    parser.add_argument('command', choices=['buildproject'], help='The command to execute')
    args = parser.parse_args()

    if args.command == 'buildproject':
        project_name = input(f"{Fore.BLUE}Enter the project name: {Style.RESET_ALL}")
        use_database = input(f"{Fore.BLUE}Would you like to use Electrus Database? (Y/N): {Style.RESET_ALL}").strip().lower() in ['y', 'yes']
        setup_routing = input(f"{Fore.BLUE}Would you like to setup Routing? (Y/N): {Style.RESET_ALL}").strip().lower() in ['y', 'yes']
        setup_engine = input(f"{Fore.BLUE}Would you like to setup the Emonic Template & Static engine? (Y/N): {Style.RESET_ALL}").strip().lower() in ['y', 'yes']

        create_project(project_name, use_database, setup_routing, setup_engine)
        print(f"Project '{project_name}' created successfully!")

if __name__ == "__main__":
    main()
