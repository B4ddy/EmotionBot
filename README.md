1. create  models/emotion_classifier and paste contents of
2. https://huggingface.co/tsid7710/distillbert-emotion-model/tree/main

3. # 1. System-Dependencies
sudo apt update
sudo apt install -y python3-pip portaudio19-dev python3-pyaudio

# 2. PyTorch CPU-optimiert
pip3 install torch --index-url https://download.pytorch.org/whl/cpu

# 3. Rest installieren
pip3 install -r requirements.txt

# 4. Überprüfen
pip3 list
