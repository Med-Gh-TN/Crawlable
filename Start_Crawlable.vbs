' @file Start_Crawlable.vbs
' @description Invisible Windows Launcher. Bypasses Defender SmartScreen by using native WScript to trigger the Python headless bootstrapper.

Set WshShell = CreateObject("WScript.Shell")

' 1. Provide instant visceral feedback to the user so they don't click it multiple times
WshShell.Popup "Booting Crawlable SOTA Engine. Your Web Dashboard will open shortly...", 3, "Crawlable AI", 64

' 2. Launch the Python Bootstrapper completely invisibly (0) and do not block (False)
WshShell.Run "cmd /c python main.py --headless", 0, False