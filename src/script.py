#!/usr/bin/env python3
import os

path = os.path.dirname(os.path.abspath(__file__))

all_folder = os.path.join(path)
for folder in os.listdir(all_folder):
    try:
        open(os.path.join(all_folder, folder, "domain", "__init__.py"), "w").close()
        open(os.path.join(all_folder, folder,
                          "application", "__init__.py"), "w").close()
        open(os.path.join(all_folder, folder,
                          "infrastructure", "__init__.py"), "w").close()
        open(os.path.join(all_folder, folder,
                          "interfaces", "__init__.py"), "w").close()
    except FileNotFoundError:
        pass
    except FileExistsError:
        pass
    except NotADirectoryError:
        pass
