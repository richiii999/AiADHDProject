# **FOCUS**: An Agentic AI Framework for Helping ADHD Students Learn More Effectively

<img width="1803" height="1436" alt="image" src="https://github.com/user-attachments/assets/8f1c171e-f154-495f-a787-d632e45876a2" />

**Installation & Usage**
1. Clone the repo
   ```
   git clone https://github.com/richiii999/AiADHDProject
   cd AiADHDProject/
   ```
2. Setup virtual environment and dependencies with uv
   ```
   uv init
   uv python pin 3.11.13
   uv add -r requirements.txt
   chmod +x .venv/bin/activate
   source .venv/bin/activate
   ```
3. Start OpenWebUI server (in bkg or separate terminal), OpenWebUI is now accessible on http://localhost:8080/
   ```
   DATA_DIR=./.open-webui uvx --python 3.11.13 open-webui@latest serve
   ```
   To get your admin token, login / create an acc (dont need to use real email, this is local).

   Navigate to: Profile (bottom left) > Settings > Account > API Keys "show" > JWT Token "copy"

   Enter this when requested, or create / edit the file .webui_admin_key and paste it in
5. If using camera, setup camera output devices & verify they work

   Output of 2nd command should show "Dummy video device (0x0000) (platform:v4l2loopback-000): /dev/video8 ..."
   ```
   sudo modprobe v4l2loopback video_nr=8,9 # if you already have device 8/9, use other nums
   v4l2-ctl --list-devices # Verify devices have appeared correctly
   sudo modprobe -r v4l2loopback # Remove if it didnt work / want to change stuff
   ```
7. Start FOCUS
   ```
   python main.py
   ```

To enable cloud-based models, go to OpenWebUI (default http://localhost:8080/) and do the following:
- OpenAI Models: Profile > Admin Panel > Settings > Connections > "Manage OpenAI API Connections" set to ON,
   - Add the endpoint (ex. "https://api.openai.com/v1") and enter your API Key
- Claude: Download this function: https://openwebui.com/f/justinrahb/anthropic
  - "Import from file" on http://localhost:8080/admin/functions 
  - remove the top / bottom html stuff
  - Once imported, click the gear 'valves' and insert your Anthropic API key, turn it on

**Acknowledgements** This research was conducted as part of the SURE program at UMD, which is paid (todo copy their ack here)
