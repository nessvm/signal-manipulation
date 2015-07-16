import sys
import wave

__author__ = 'Nestor Velazquez'

def main():
    wave_obj = wave.open(sys.argv[1], mode='rb')
    samples = get_samples(wave_obj)

    output_samples = {
        'invert': invert
    }.get(sys.argv[2])(samples)

    params = wave_obj.getparams()
    wave_obj.close()

    output_wave = wave.open("output.wav", mode='wb')
    output_wave.setparams(params)
    output_wave.writeframes(output_samples)
    output_wave.close()

def get_samples(wave_obj):
    return wave_obj.readframes(
        wave_obj.getnframes()
    )

def get_frames(samples):
    sample_list = list(samples)
    frame_list = list()
    for i in range(0, len(sample_list) - 1, 2):
        frame_list.append(sample_list[i:i+2])

    return frame_list

def frames_to_bytes(frame_list):
    output_samples = list()

    for li in frame_list:
        for sample in li:
            output_samples.append(sample)

    return bytes(output_samples)

def invert(samples):
    frame_list = get_frames(samples)
    frame_list.reverse()

    return frames_to_bytes(frame_list)

if __name__ == '__main__':
    main()
