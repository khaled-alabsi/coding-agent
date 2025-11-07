"""Simple sound notification utility."""
import sys
import subprocess


def play_completion_sound():
    """Play a simple sound to indicate completion."""
    try:
        if sys.platform == "darwin":  # macOS
            # Use system beep
            subprocess.run(["afplay", "/System/Library/Sounds/Glass.aiff"],
                         check=False, capture_output=True)
        elif sys.platform == "win32":  # Windows
            import winsound
            # Play Windows default sound
            winsound.MessageBeep(winsound.MB_OK)
        else:  # Linux
            # Try to use beep command or fallback to print bell
            try:
                subprocess.run(["beep"], check=False, capture_output=True)
            except FileNotFoundError:
                # Fallback: print bell character
                print("\a")
    except Exception:
        # Fallback: print bell character
        print("\a")


def play_error_sound():
    """Play a sound to indicate an error."""
    try:
        if sys.platform == "darwin":  # macOS
            subprocess.run(["afplay", "/System/Library/Sounds/Basso.aiff"],
                         check=False, capture_output=True)
        elif sys.platform == "win32":  # Windows
            import winsound
            winsound.MessageBeep(winsound.MB_ICONHAND)
        else:  # Linux
            # Print bell twice for error
            print("\a\a")
    except Exception:
        # Fallback: double bell
        print("\a\a")
