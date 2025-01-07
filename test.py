from gtts import gTTS
from playsound import playsound

def test_tts():
    try:
        tts = gTTS("Testing text-to-speech", lang='en')
        tts.save("test.mp3")
        playsound("test.mp3")
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"Error in text-to-speech: {e}")

test_tts()
