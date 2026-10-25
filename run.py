import os
import sys
import pandas as pd

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from src.agent_swarm import SupportGenSwarm
from src.voice_agent import VoiceSupportAgent

def run_batch_evaluation(audio_input_dir: str):
    print("Initializing ZentroMart Support Agent Swarm...")
    swarm = SupportGenSwarm()
    voice_agent = VoiceSupportAgent(swarm)
    
    output_dir = os.path.join(ROOT_DIR, "sample_outputs")
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"Processing audio files from: {audio_input_dir}")
    
    mock_payload = {
        "customer_id": "C100000",
        "name": "Valued Customer",
        "email": "customer@zentromart.com"
    }
    
    if not os.path.exists(audio_input_dir):
        print(f"Audio directory {audio_input_dir} not found.")
        return

    for file_name in os.listdir(audio_input_dir):
        if file_name.endswith(('.wav', '.mp3', '.m4a')):
            audio_path = os.path.join(audio_input_dir, file_name)
            print(f"Running turn for: {file_name}")
            heard, reply, out_audio = voice_agent.process_voice_turn(audio_path, mock_payload)
            print(f"Heard: {heard}")
            print(f"Reply: {reply}")
            print("-" * 40)

if __name__ == "__main__":
    input_folder = sys.argv[1] if len(sys.argv) > 1 else "practice/audio"
    run_batch_evaluation(input_folder)
