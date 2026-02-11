-- INSTRUCTIONS:
-- 1. Open System Settings -> Privacy & Security -> Accessibility.
-- 2. Ensure "Script Editor" (or the name of this app) is checked/allowed.
-- 3. Run this script.
-- 4. You have 3 seconds to click into the target window (e.g., your game or document).

display notification "Script starting in 3 seconds... Switch window now!"
delay 3

set loopCounter to 0

repeat
	-- Increment counter
	set loopCounter to loopCounter + 1
	
	tell application "System Events"
		-- Press Shift (Key Code 56 is Left Shift)
		key code 56
		
		-- Every 3rd second (iterations 3, 6, 9...), press l and ;
		if loopCounter = 3 then
			keystroke "l"
			keystroke ";"
			set loopCounter to 0
		end if
	end tell
	
	-- Wait 1 second before next loop
	delay 1.0
end repeat
