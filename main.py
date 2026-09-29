import os
import sys
import webview
from ursina import *

def main():
    # Path to your HTML file
    html_file = os.path.abspath("DRONE__OPS.html")
    
    if not os.path.exists(html_file):
        print(f"Error: Could not find '{html_file}' in the current directory.")
        sys.exit(1)

    # Launch desktop window
    window = webview.create_window(
        title="DRONE // OPS",
        url=f"file://{html_file}",
        width=1280,
        height=720,
        resizable=True,
        fullscreen=False
    )
    
    # gui='cef' or 'qt' can be specified if needed
    webview.start()

if __name__ == "__main__":
    main()
