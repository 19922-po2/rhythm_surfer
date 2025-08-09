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

def monitor_rhythm_game():
    """
    Monitor the rhythm game coordinates and press keys when pixels are not white.
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
    
    for coord in coords_map.keys():
        last_press_time[coord] = 0
    
    print("Starting rhythm game monitor...")
    print("Press Ctrl+C to stop")
    
    try:
        while True:
            # Get all pixel colors directly from screen - no screenshots needed!
            coords_list = list(coords_map.keys())
            all_colors = get_all_pixel_colors_fast(coords_list)
            current_time = time.time() * 1000  # Convert to milliseconds
            
            # Collect all keys that need to be pressed simultaneously
            keys_to_press = []
            
            for coord, key in coords_map.items():
                current_color = all_colors[coord]
                
                # Check if key should be pressed (not white and cooldown passed)
                if not is_white(current_color):
                    if current_time - last_press_time[coord] > cooldown_ms:
                        keys_to_press.append((coord, key))
                        last_press_time[coord] = current_time
            
            # Press all keys simultaneously if any were detected
            if keys_to_press:
                coords_detected = [coord for coord, key in keys_to_press]
                keys_detected = [key for coord, key in keys_to_press]
                
                print(f"Non-white colors detected at {coords_detected}")
                
                # Press all keys at the same time
                press_keys_simultaneously(keys_detected)
                
                print(f"Pressed keys simultaneously: {keys_detected}")
            
            # No delay for maximum speed and responsiveness
            
    except KeyboardInterrupt:
        print("\nMonitoring stopped by user")

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
        is_white_color = is_white(color)
        print(f"({x}, {y}) -> Key '{key}': RGB{color} - {'WHITE' if is_white_color else 'NOT WHITE'}")
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
