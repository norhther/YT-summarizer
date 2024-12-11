from melo.api import TTS

def generate_audio(text, output_path='output.wav', language='EN', accent='EN-US', speed=1.0, device='auto'):
    """
    Generate audio from text using MeloTTS.
    :param text: The text to convert to audio
    :param output_path: The path to save the generated audio file
    :param language: Language for TTS (default: 'EN')
    :param accent: Accent for TTS (default: 'EN-US')
    :param speed: Speed of the speech
    :param device: Device for inference ('auto', 'cpu', 'cuda', 'cuda:0', 'mps')
    :return: Path to the generated audio file
    """
    try:
        # Initialize TTS model
        model = TTS(language=language, device=device)
        speaker_ids = model.hps.data.spk2id

        # Check if the accent exists
        if accent not in speaker_ids:
            raise ValueError(f"Accent '{accent}' is not available. Available accents: {list(speaker_ids.keys())}")

        # Generate and save the audio
        model.tts_to_file(text, speaker_ids[accent], output_path, speed=speed)
        return output_path
    except Exception as e:
        print(f"Error generating audio: {e}")
        return None
