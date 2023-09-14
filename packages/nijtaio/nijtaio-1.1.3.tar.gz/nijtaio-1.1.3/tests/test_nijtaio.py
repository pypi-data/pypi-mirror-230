import json
import nijtaio
import datasets

def test_serializer():
    audio_dataset = datasets.load_dataset('audiofolder', data_files=['../samples/e0003.wav'])
    s = nijtaio._nijta_serializer(audio_dataset)
    assert type(s) == dict

    print(s.keys())

    s2 = json.dumps(audio_dataset.cast_column("audio", datasets.Audio(decode=True)),
                                                       default=nijtaio._nijta_serializer)
