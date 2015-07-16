from collections import namedtuple, deque
import matplotlib.pyplot as plt
import sys
import wave
import numpy as np

__author__ = 'Nestor Velazquez'

def main():
    wave_obj = wave.open(sys.argv[1], mode='rb')
    try:
        factor = sys.argv[3]
    except IndexError:
        factor = None

    {
        'invert': invert,
        'decimate': decimate,
        'shift': shift,
        'modulate': modulate,
        'interpolate': interpolate,
        'alter': alter,
    }.get(sys.argv[2])(wave_obj, factor=factor)

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

def invert(wave_obj, **kwargs):
    channels = get_channels(wave_obj)
    plot_channels = channels
    for channel in channels:
        channel.reverse()

    frames = build_sample(channels)
    params = wave_obj.getparams()
    wave_obj.close()

    if '-n' not in sys.argv:
        plot(plot_channels, channels)

    output_wave = wave.open('inverted.wav', 'wb')
    output_wave.setparams(params)
    output_wave.writeframes(frames)
    output_wave.close()

def decimate(wave_obj, **kwargs):
    channels = get_channels(wave_obj)
    factor = int(kwargs.get('factor'))

    decimated_channels = list()
    j = 0
    for channel in channels:
        decimated_channels.append([])
        for i in range(0, len(channel) - 1, factor):
            decimated_channels[j].append(channel[i])
        j += 1

    if '-n' not in sys.argv:
        plot(channels, decimated_channels)
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

def shift(wave_obj, **kwargs):
    factor = int(kwargs.get('factor'))
    channels = get_channels(wave_obj)
    plot_channels = channels
    channel_deques = list()

    for channel in channels:
        channel_deques.append(deque(channel))
    for dequ in channel_deques:
        dequ.rotate(factor)
    for i in range(len(channels)):
        channels[i] = list(channel_deques[i])

    if '-n' not in sys.argv:
        plot(plot_channels, channels)

    frames = build_sample(channels)
    params = wave_obj.getparams()
    wave_obj.close()
    output_wave = wave.open('shifted.wav', 'wb')
    output_wave.setparams(params)
    output_wave.writeframes(frames)
    output_wave.close()

def modulate(wave_obj, **kwargs):
    factor = float(kwargs.get('factor'))
    channels = get_channels(wave_obj)
    out_channels = list()

    for channel in channels:
        out_channels.append(list())
        for i in range(len(channel)):
            out_channels[-1].append(int(channel[i]*factor) % 256)

    if '-n' not in sys.argv:
        plot(channels, out_channels)

    frames = build_sample(out_channels)
    params = wave_obj.getparams()
    wave_obj.close()
    output_wave = wave.open('modulated.wav', 'wb')
    output_wave.setparams(params)
    output_wave.writeframes(frames)
    output_wave.close()

def interpolate(wave_obj, **kwargs):
    factor = int(kwargs.get('factor'))
    channels = get_channels(wave_obj)

    out_channels = list()
    for channel in channels:
        out_channels.append([])
        for i in range(len(channel) - 1):
            chunk = list(' '*factor)
            chunk_size = int(abs(channel[i] - channel[i+1])/factor)
            for j in range(factor):
                if channel[i] < channel[i+1]:
                    chunk[j] = channel[i] + (chunk_size * (j + 1))
                else:
                    chunk[j] = channel[i] - (chunk_size * (j + 1))
            out_channels[-1] += chunk

    if '-n' not in sys.argv:
        plot(channels, out_channels)
    frames = build_sample(out_channels)
    parameters = namedtuple('parameters', ['nchannels', 'sampwidth', 'framerate', 'nframes', 'comptype', 'compname'])
    params = parameters(
        nchannels=wave_obj.getnchannels(),
        sampwidth=wave_obj.getsampwidth(),
        framerate=wave_obj.getframerate()*factor,
        nframes=len(out_channels[0]),
        comptype=wave_obj.getcomptype(),
        compname=wave_obj.getcompname()
    )
    wave_obj.close()

    output_wave = wave.open('interpolated.wav', 'wb')
    output_wave.setparams(params)
    output_wave.writeframes(frames)
    output_wave.close()

def alter(wave_obj, **kwargs):
    factor = float(kwargs.get('factor'))

    frames = wave_obj.readframes(wave_obj.getnframes())
    parameters = namedtuple('parameters', ['nchannels', 'sampwidth', 'framerate', 'nframes', 'comptype', 'compname'])
    params = parameters(
        nchannels=wave_obj.getnchannels(),
        sampwidth=wave_obj.getsampwidth(),
        framerate=int(wave_obj.getframerate()*factor),
        nframes=wave_obj.getnframes(),
        comptype=wave_obj.getcomptype(),
        compname=wave_obj.getcompname()
    )
    wave_obj.close()

    output_wave = wave.open('altered.wav', 'wb')
    output_wave.setparams(params)
    output_wave.writeframes(frames)
    output_wave.close()

def plot(in_channels, out_channels):
    colors = ['r', 'g', 'y', 'b', 'c', 'm']
    i = 0
    subplot = 221
    plt.figure(1)

    for channel in in_channels:
        plt.subplot(subplot)
        plt.plot(channel, colors[i])
        i += 1
        subplot += 1
    for channel in out_channels:
        plt.subplot(subplot)
        plt.plot(channel, colors[i])
        i += 1
        subplot += 1

    plt.show()

if __name__ == '__main__':
    main()
