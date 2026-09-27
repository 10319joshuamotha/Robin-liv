# Robin browser bridge

Robin can enumerate all **normal** tabs in Chromium/Edge-compatible browsers and inspect page text through the included extension. Incognito/InPrivate tabs are deliberately filtered out.

## Install

1. Start Robin once so the local bridge is running.
2. Open your browser's extensions page.
3. Enable Developer Mode.
4. Choose **Load unpacked** and select this `browser_extension` folder.
5. Repeat for each Chromium-based browser profile you want Robin to see.

The extension only talks to `127.0.0.1:8765`. It does not send tab data to a remote server.
