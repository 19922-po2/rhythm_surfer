import keyboard
import time
import pyautogui
from PIL import Image
import win32gui
import win32ui
import win32con

def click_key_simple(key):
    pyautogui.press(key)

def press_keys_simultaneously(keys):
    """
    Press multiple keys at exactly the same time.
    
    Args:
        keys (list): List of keys to press simultaneously
    """
    if not keys:
        return
    
    # Method 1: Use keyboard library for true simultaneous presses
    try:
        # Press all keys down at once
        for key in keys:
            keyboard.press(key)
        
        # Small delay to register the press
        time.sleep(0.01)
        
        # Release all keys at once
        for key in keys:
            keyboard.release(key)
            
    except Exception as e:
        # Fallback: Use pyautogui (slightly less simultaneous but still fast)
        print(f"Keyboard method failed: {e}, using pyautogui fallback")
        for key in keys:
            pyautogui.press(key)

def get_pixel_color_fast(x, y):
    """
    Get pixel color directly from screen using Windows API - much faster than screenshots.
    
    Args:
        x (int): X coordinate
        y (int): Y coordinate
        
    Returns:
        tuple: RGB color values (r, g, b)
    """
    # Get device context for the entire screen
    hdc = win32gui.GetDC(0)
    
    # Get pixel color as a packed RGB value
    pixel = win32gui.GetPixel(hdc, x, y)
    
    # Release the device context
    win32gui.ReleaseDC(0, hdc)
    
    # Unpack RGB values from the pixel
    r = pixel & 0xff
    g = (pixel >> 8) & 0xff
    b = (pixel >> 16) & 0xff
    
    return (r, g, b)

def get_all_pixel_colors_fast(coords_list):
    """
    Get colors for all coordinates directly from screen - no screenshots needed.
    
    Args:
        coords_list (list): List of (x, y) coordinate tuples
        
    Returns:
        dict: Dictionary mapping coordinates to RGB colors
    """
    # Get device context once for all pixels
    hdc = win32gui.GetDC(0)
    
    colors = {}
    for x, y in coords_list:
        pixel = win32gui.GetPixel(hdc, x, y)
        # Unpack RGB values
        r = pixel & 0xff
        g = (pixel >> 8) & 0xff
        b = (pixel >> 16) & 0xff
        colors[(x, y)] = (r, g, b)
    
    # Release the device context
    win32gui.ReleaseDC(0, hdc)
    
    return colors

def is_white(color, tolerance=10):
    """
    Check if a color is white (or close to white within tolerance).
    
    Args:
        color (tuple): RGB color tuple
        tolerance (int): Tolerance for white detection
        
    Returns:
        bool: True if color is white-ish
    """
    r, g, b = color
    return r >= (255 - tolerance) and g >= (255 - tolerance) and b >= (255 - tolerance)

def is_yellow(color, tolerance=50):
    """
    Check if a color is yellow or yellowish (including faded yellow).
    Yellow has high red and green components, low blue.
    
    Args:
        color (tuple): RGB color tuple
        tolerance (int): Tolerance for yellow detection (higher to catch faded yellow)
        
    Returns:
        bool: True if color is yellow-ish
    """
    r, g, b = color
    # Yellow characteristics: high red, high green, low blue
    # More tolerant to catch faded yellows
    return (r >= (200 - tolerance) and 
            g >= (200 - tolerance) and 
            b <= (100 + tolerance) and
            r > b and g > b)  # Ensure red and green are higher than blue

def get_color_type(color):
    """
    Determine the type of color for note handling.
    
    Args:
        color (tuple): RGB color tuple
        
    Returns:
        str: 'white', 'yellow', or 'other'
    """
    if is_white(color):
        return 'white'
    elif is_yellow(color):
        return 'yellow'
    else:
        return 'other'

def monitor_rhythm_game():
    """
    Monitor the rhythm game coordinates and handle different note types:
    - Yellow notes: Hold key until no longer yellow (including faded yellow)
    - Other non-white notes: Quick press
    """
    # Coordinate and key mapping from comments
    coords_map = {
        (277, 893): 's',   # Position 1
        (622, 893): 'd',   # Position 2  
        (959, 893): 'f',   # Position 3
        (1304, 893): 'k',  # Position 4
        (1647, 893): 'l'   # Position 5
    }
    
    # Cooldown system to prevent multiple presses for same note
    last_press_time = {}
    cooldown_ms = 50  # 50ms cooldown between presses for same key
    
    # Track which keys are currently being held for yellow notes
    keys_being_held = {}
    yellow_note_active = {}  # Track if a yellow note is currently active
    
    for coord in coords_map.keys():
        last_press_time[coord] = 0
        keys_being_held[coord] = False
        yellow_note_active[coord] = False
    
    print("Starting rhythm game monitor...")
    print("Yellow notes = Hold until no longer yellow, Other notes = Quick press")
    print("Press Ctrl+C to stop")
    
    try:
        while True:
            # Get all pixel colors directly from screen - no screenshots needed!
            coords_list = list(coords_map.keys())
            all_colors = get_all_pixel_colors_fast(coords_list)
            current_time = time.time() * 1000  # Convert to milliseconds
            
            # Collect keys for quick presses (non-yellow notes)
            keys_to_press_quick = []
            
            for coord, key in coords_map.items():
                current_color = all_colors[coord]
                color_type = get_color_type(current_color)
                
                if color_type == 'yellow':
                    # Yellow note detected
                    if not keys_being_held[coord]:
                        # Start holding the key for yellow note
                        print(f"Yellow note detected at {coord}: {current_color} - Holding '{key}'")
                        keyboard.press(key)
                        keys_being_held[coord] = True
                        yellow_note_active[coord] = True
                    # Continue holding while yellow (including faded yellow)
                    
                elif yellow_note_active[coord] and color_type != 'yellow':
                    # Yellow note ended (no longer yellow)
                    if keys_being_held[coord]:
                        print(f"Yellow note ended at {coord}: {current_color} - Releasing '{key}'")
                        keyboard.release(key)
                        keys_being_held[coord] = False
                        yellow_note_active[coord] = False
                        
                elif color_type == 'other':
                    # Regular note (non-white, non-yellow)
                    if not keys_being_held[coord]:  # Only if not holding a yellow note
                        if current_time - last_press_time[coord] > cooldown_ms:
                            keys_to_press_quick.append((coord, key))
                            last_press_time[coord] = current_time
                
                # If color becomes white and we were holding a yellow note, release it
                elif color_type == 'white' and keys_being_held[coord]:
                    print(f"Note ended (white) at {coord}: {current_color} - Releasing '{key}'")
                    keyboard.release(key)
                    keys_being_held[coord] = False
                    yellow_note_active[coord] = False
            
            # Press all non-yellow keys simultaneously if any were detected
            if keys_to_press_quick:
                coords_detected = [coord for coord, key in keys_to_press_quick]
                keys_detected = [key for coord, key in keys_to_press_quick]
                
                #print(f"Regular notes detected at {coords_detected}")
                press_keys_simultaneously(keys_detected)
                #print(f"Quick pressed keys: {keys_detected}")
            
            # No delay for maximum speed and responsiveness
            
    except KeyboardInterrupt:
        # Release any keys that are still being held
        print("\nReleasing any held keys...")
        for coord, key in coords_map.items():
            if keys_being_held[coord]:
                keyboard.release(key)
                print(f"Released '{key}'")
        print("Monitoring stopped by user")

def test_pixel_colors():
    """
    Test function to check current pixel colors at all coordinates.
    """
    coords_map = {
        (277, 893): 's',   # Position 1
        (622, 893): 'd',   # Position 2  
        (959, 893): 'f',   # Position 3
        (1304, 893): 'k',  # Position 4
        (1647, 893): 'l'   # Position 5
    }
    
    print("Current pixel colors:")
    for coord, key in coords_map.items():
        x, y = coord
        color = get_pixel_color_fast(x, y)
        color_type = get_color_type(color)
        print(f"({x}, {y}) -> Key '{key}': RGB{color} - {color_type.upper()}")
    print()

if __name__ == "__main__":
    # Choose what to run:
    print("Rhythm Game Bot")
    print("1. Test pixel colors at coordinates")
    print("2. Start monitoring and auto-play")
    print("3. Manual key test")
    
    choice = input("Enter choice (1-3): ").strip()
    
    if choice == "1":
        print("Testing pixel colors in 3 seconds...")
        time.sleep(3)
        test_pixel_colors()
        
    elif choice == "2":
        print("Starting auto-play in 5 seconds... Make sure game is focused!")
        time.sleep(5)
        monitor_rhythm_game()
        
    elif choice == "3":
        print("Manual key test in 2 seconds...")
        time.sleep(2)
        click_key_simple('c')
        print("Done testing!")
        
    else:
        print("Invalid choice!")


#python rhythm.py
#python -m mouseinfo
""" coords
277,893 #1-> key: S
622,893 #2-> key: D
959,893 #3-> key: F
1304,893 #4-> key: K
1647,893 #5-> key: L
"""
""" colors
255,255,255 #white

"""
