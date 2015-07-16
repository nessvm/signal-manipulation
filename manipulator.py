from collections import namedtuple
import sys
import wave
from numpy import interp

__author__ = 'Nestor Velazquez'

def main():
    wave_obj = wave.open(sys.argv[1], mode='rb')
    try:
        factor = int(sys.argv[3])
    except IndexError:
        factor = None

    {
        'invert': invert,
        'decimate': decimate
    }.get(sys.argv[2])(wave_obj, factor=factor)

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

def get_channel_frames(samples, channel, total_channels):
    sample_list = list(samples)
    channel_sample_list = list()

    for i in range(channel-1, len(sample_list), total_channels):
        channel_sample_list.append(sample_list[i])

    return bytes(channel_sample_list)

def get_channels(wave_obj):
    samples = wave_obj.readframes(wave_obj.getnframes())

    channels = list()
    for i in range(wave_obj.getnchannels()):
        channels.append(
            list(get_channel_frames(samples, i+1, wave_obj.getnchannels()))
        )

    return channels

def build_sample(channels):
    sample = list()

    for i in range(len(channels[0]) - 1):
        for channel in channels:
            sample.append(channel[i])

    return bytes(sample)

def frames_to_bytes(frame_list):
    output_samples = list()

    for li in frame_list:
        for sample in li:
            output_samples.append(sample)

    return bytes(output_samples)

def invert(wave_obj, **kwargs):
    channels = get_channels(wave_obj)
    for channel in channels:
        channel.reverse()

    frames = build_sample(channels)
    params = wave_obj.getparams()
    wave_obj.close()

    output_wave = wave.open('inverted.wav', 'wb')
    output_wave.setparams(params)
    output_wave.writeframes(frames)
    output_wave.close()

def decimate(wave_obj, **kwargs):
    channels = get_channels(wave_obj)
    factor = kwargs.get('factor')

    decimated_channels = list()
    j = 0
    for channel in channels:
        decimated_channels.append([])
        for i in range(0, len(channel) - 1, factor):
            decimated_channels[j].append(channel[i])
        j += 1

    frames = build_sample(decimated_channels)
    parameters = namedtuple('parameters', ['nchannels', 'sampwidth', 'framerate', 'nframes', 'comptype', 'compname'])
    params = parameters(
        nchannels=wave_obj.getnchannels(),
        sampwidth=wave_obj.getsampwidth(),
        framerate=wave_obj.getframerate()/factor,
        nframes=len(decimated_channels[0]),
        comptype=wave_obj.getcomptype(),
        compname=wave_obj.getcompname()
    )
    wave_obj.close()

    output_wave = wave.open('decimated.wav', 'wb')
    output_wave.setparams(params)
    output_wave.writeframes(frames)
    output_wave.close()

def interpolate(wave_obj, factor):
    channels = get_channels(wave_obj)

if __name__ == '__main__':
    main()
