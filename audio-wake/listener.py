import sounddevice as sd
import numpy as np
import config

class Listener:
    def __init__(self):
        self.device = config.MIC_DEVICE
        self.sr = config.SAMPLE_RATE
        self.block_size = config.BLOCK_SIZE
        
    def stream_callback(self, indata, frames, time, status):
        """
        Called for each audio block.
        Calculates RMS and passes it to the callback provided in listen().
        """
        if status:
            print(status)
        
        # Calculate RMS amplitude
        # indata is numpy array
        rms = np.sqrt(np.mean(indata**2))
        self.latest_rms = rms

    def listen_loop(self, on_audio_level):
        """
        Blocking loop that listens to audio.
        on_audio_level(rms_value) is called every block.
        """
        print(f"[Sheep] Listening on {self.device}...")
        
        try:
            # We need to explicitly select the ALSA device
            with sd.InputStream(device=self.device, channels=1, callback=None, 
                                samplerate=self.sr, blocksize=self.block_size) as stream:
                while True:
                    # Read chunk
                    data, overflowed = stream.read(self.block_size)
                    if overflowed:
                        print("Audio overflow")
                    
                    # Calculate RMS
                    # Flatten in case of multiple channels (should be 1 though)
                    flat_data = data.flatten()
                    rms = np.sqrt(np.mean(flat_data**2))
                    
                    on_audio_level(rms)
                    
        except Exception as e:
            print(f"[Sheep] Audio Error: {e}")
            # Identify device list if it fails
            print("Available devices:")
            print(sd.query_devices())
