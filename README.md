# **FOCUS**: An Agentic AI Framework for Helping ADHD Students Learn More Effectively

![SUREPoster_smol](https://github.com/user-attachments/assets/494c5d19-cf56-45af-a053-41dbecce7ee8)

**Installation & Usage**
1. Clone the repo
   ```
   git clone https://github.com/richiii999/AiADHDProject
   cd AiADHDProject/
   ```
2. Setup virtual environment and dependencies with uv
   ```
   pip install uv # If you don't have uv installed
   uv init
   uv python pin 3.11.13
   uv add -r requirements.txt
   chmod +x .venv/bin/activate
   source .venv/bin/activate
   ```
3. Start OpenWebUI server (in separate terminal), OpenWebUI is now accessible on http://localhost:8080/
   ```
   DATA_DIR=./.open-webui WEBUI_AUTH=False uvx --python 3.11.13 open-webui@latest serve
   ```
   To get your admin key: Profile (top right) > Settings > Account > API Keys "show" > JWT Token "copy"

   Enter the key when requested, create/edit the file .webui_admin_key to update your key if needed.
4. If using camera, setup camera output devices & verify they work
   ```
   sudo modprobe v4l2loopback video_nr=8,9 # if you already have device 8/9, use other nums
   v4l2-ctl --list-devices # Verify devices have appeared correctly
   sudo modprobe -r v4l2loopback # Remove if it didnt work / want to change stuff
   ```
   Output of 2nd command should show the following in your device list:
   ```
   ...
   Dummy video device (0x0000) (platform:v4l2loopback-000):
	/dev/video8

   Dummy video device (0x0001) (platform:v4l2loopback-001):
	/dev/video9
   ...
   ```
5. Setup AI models: See the bottom section on setting up models to use with FOCUS
6. Start FOCUS
   ```
   python main.py
   ```

**Setting up models**

Local Models: install ollama to run local models via OpenWebUI
- Manual: curl -fsSL https://ollama.com/install.sh | sh
- Ubuntu (snap): snap install ollama

To download models, run ollama pull \<model name\>, ex. "ollama pull llama3.2:latest" 

FOCUS was tested with llama3.2:1b and llama3.2:8b

Cloud-based Models: go to OpenWebUI (default http://localhost:8080/) and do the following:
- OpenAI Models: Profile > Admin Panel > Settings > Connections > "Manage OpenAI API Connections" set to ON
   - Add the endpoint (ex. "https://api.openai.com/v1") and enter your API Key
- Claude: Download this function: https://openwebui.com/f/justinrahb/anthropic
  - "Import from file" on http://localhost:8080/admin/functions 
  - remove the top / bottom html stuff
  - Once imported, click the gear 'valves' and insert your Anthropic API key, turn it on

**Acknowledgements** This research was conducted as part of the Summer Undergraduate Research Experience (SURE) program at UMD
