import os
from gnani.stt import GnaniSTTClient
from gnani.tts import GnaniTTSClient

class VoiceSupportAgent:
    def __init__(self, agent_swarm_instance):
        self.agent = agent_swarm_instance
        # Reads GNANI_API_KEY from environment variables
        self.stt = GnaniSTTClient()
        self.tts = GnaniTTSClient()

    def process_voice_turn(self, audio_file_path: str, customer_payload: dict) -> tuple:
        try:
            # 1. Speech to Text via Gnani API[cite: 15, 18]
            stt_result = self.stt.transcribe(audio_file_path, language_code="en-IN")
            heard_text = stt_result.get("transcript", "").strip()
            
            if not heard_text:
                reply_text = "Sorry, I didn't catch that. Could you say it again?"
            else:
                # 2. Agent Swarm Brain[cite: 15]
                reply_text = self.agent.process_support_ticket(customer_payload, heard_text)
            
            # 3. Text to Speech via Gnani API[cite: 15, 18]
            output_audio_path = "reply_output.wav"
            self.tts.synthesize(
                text=reply_text,
                voice="Kaveri",
                model="timbre-v2.5",
                language_code="en-IN",
                output_file=output_audio_path
            )
            
            return heard_text, reply_text, output_audio_path
            
        except Exception as e:
            fallback_reply = "An error occurred while processing your voice request."
            return "", fallback_reply, None
