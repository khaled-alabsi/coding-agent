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
    """Play a sound to indicate a critical error."""
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


def play_warning_sound():
    """Play a sound to indicate a warning (non-critical)."""
    try:
        if sys.platform == "darwin":  # macOS
            subprocess.run(["afplay", "/System/Library/Sounds/Ping.aiff"],
                         check=False, capture_output=True)
        elif sys.platform == "win32":  # Windows
            import winsound
            winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)
        else:  # Linux
            # Single bell for warning
            print("\a")
    except Exception:
        # Fallback: single bell
        print("\a")


def play_truncation_sound():
    """Play a sound to indicate response truncation detected."""
    try:
        if sys.platform == "darwin":  # macOS
            subprocess.run(["afplay", "/System/Library/Sounds/Funk.aiff"],
                         check=False, capture_output=True)
        elif sys.platform == "win32":  # Windows
            import winsound
            winsound.MessageBeep(winsound.MB_ICONASTERISK)
        else:  # Linux
            # Three short beeps for truncation
            print("\a", end="", flush=True)
            import time
            time.sleep(0.1)
            print("\a", end="", flush=True)
            time.sleep(0.1)
            print("\a")
    except Exception:
        # Fallback: triple bell
        print("\a\a\a")


def play_validation_failed_sound():
    """Play a sound to indicate validation failed."""
    try:
        if sys.platform == "darwin":  # macOS
            subprocess.run(["afplay", "/System/Library/Sounds/Sosumi.aiff"],
                         check=False, capture_output=True)
        elif sys.platform == "win32":  # Windows
            import winsound
            winsound.MessageBeep(winsound.MB_ICONQUESTION)
        else:  # Linux
            # Two beeps with pause
            print("\a", end="", flush=True)
            import time
            time.sleep(0.2)
            print("\a")
    except Exception:
        # Fallback: double bell with spacing
        print("\a \a")


def play_fix_attempt_sound():
    """Play a sound to indicate auto-fix attempt."""
    try:
        if sys.platform == "darwin":  # macOS
            subprocess.run(["afplay", "/System/Library/Sounds/Blow.aiff"],
                         check=False, capture_output=True)
        elif sys.platform == "win32":  # Windows
            import winsound
            # Play system default
            winsound.MessageBeep()
        else:  # Linux
            # Quick beep
            print("\a")
    except Exception:
        # Fallback
        print("\a")
