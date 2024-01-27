import pyaudio
import numpy as np

def test_audio_devices():
    p = pyaudio.PyAudio()
    valid_input_devices = []
    valid_output_devices = []
    invalid_devices = []

    for i in range(p.get_device_count()):
        device_info = p.get_device_info_by_index(i)
        device_name = device_info.get('name')

        # Test input capability
        if device_info.get('maxInputChannels') > 0:
            try:
                stream = p.open(format=pyaudio.paInt16,
                                channels=1,
                                rate=44100,
                                input=True,
                                frames_per_buffer=1024,
                                input_device_index=i)
                stream.close()
                valid_input_devices.append((i, device_name))
            except Exception as e:
                invalid_devices.append((i, device_name, 'Input', str(e)))

        # Test output capability
        if device_info.get('maxOutputChannels') > 0:
            try:
                stream = p.open(format=pyaudio.paInt16,
                                channels=1,
                                rate=44100,
                                output=True,
                                frames_per_buffer=1024,
                                output_device_index=i)
                stream.close()
                valid_output_devices.append((i, device_name))
            except Exception as e:
                # Check if device was already marked as invalid for input
                if not any(d[0] == i for d in invalid_devices):
                    invalid_devices.append((i, device_name, 'Output', str(e)))
    
    p.terminate()

    # Generate report
    print("\n--- Audio Devices Report ---\n")
    print("Invalid Devices:")
    for device in invalid_devices:
        print(f"Device {device[0]}: {device[1]} - {device[2]} Error: {device[3]}")

    print("\nValid Input Devices:")
    for device in valid_input_devices:
        print(f"Device {device[0]}: {device[1]}")

    print("\nValid Output Devices:")
    for device in valid_output_devices:
        print(f"Device {device[0]}: {device[1]}")

if __name__ == "__main__":
    test_audio_devices()
