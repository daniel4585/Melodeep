# 
# Copyright 2016 Google Inc.
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
# http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import base64
import codecs
import tempfile
import uuid

import magenta.music as mm
import magenta
import parser
from IPython.utils.tests.test_wildcard import q
from magenta.protobuf import music_pb2

import os
from flask import send_file, request, flash, jsonify
import pretty_midi
import sys

import models

if sys.version_info.major <= 2:
    from cStringIO import StringIO
else:
    from io import StringIO
import time
import json

from flask import Flask

app = Flask(__name__, static_url_path='', static_folder=os.path.abspath('../melodeep/dist/'))

ALLOWED_EXTENSIONS = set(['mid', 'midi'])
UPLOAD_FOLDER = 'uploaded'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

twinkle_twinkle = music_pb2.NoteSequence()

# Add the notes to the sequence.
twinkle_twinkle.notes.add(pitch=60, start_time=0.0, end_time=0.5, velocity=80)
twinkle_twinkle.notes.add(pitch=60, start_time=0.5, end_time=1.0, velocity=80)
twinkle_twinkle.notes.add(pitch=67, start_time=1.0, end_time=1.5, velocity=80)
twinkle_twinkle.notes.add(pitch=67, start_time=1.5, end_time=2.0, velocity=80)
twinkle_twinkle.notes.add(pitch=69, start_time=2.0, end_time=2.5, velocity=80)
twinkle_twinkle.notes.add(pitch=69, start_time=2.5, end_time=3.0, velocity=80)
twinkle_twinkle.notes.add(pitch=67, start_time=3.0, end_time=4.0, velocity=80)
twinkle_twinkle.notes.add(pitch=65, start_time=4.0, end_time=4.5, velocity=80)
twinkle_twinkle.notes.add(pitch=65, start_time=4.5, end_time=5.0, velocity=80)
twinkle_twinkle.notes.add(pitch=64, start_time=5.0, end_time=5.5, velocity=80)
twinkle_twinkle.notes.add(pitch=64, start_time=5.5, end_time=6.0, velocity=80)
twinkle_twinkle.notes.add(pitch=62, start_time=6.0, end_time=6.5, velocity=80)
twinkle_twinkle.notes.add(pitch=62, start_time=6.5, end_time=7.0, velocity=80)
twinkle_twinkle.notes.add(pitch=60, start_time=7.0, end_time=8.0, velocity=80)
twinkle_twinkle.total_time = 8

twinkle_twinkle.tempos.add(qpm=60);

#
# @app.route('/predict', methods=['POST'])
# def predict():
#     now = time.time()
#     values = json.loads(request.data)
#     midi_data = pretty_midi.PrettyMIDI(StringIO(''.join(chr(v) for v in values)))
#     duration = float(request.args.get('duration'))
#     ret_midi = generate_midi(midi_data, duration)
#     return send_file(ret_midi, attachment_filename='return.mid',
#         mimetype='audio/midi', as_attachment=True)


@app.route('/generate-melody', methods=['POST'])
def generate():
    now = time.time()

    midifile = request.files['file']
    if not (midifile.filename.endswith(".mid") or midifile.filename.endswith(".midi")):
        response = jsonify({"message": "Bad file format, please upload mid / midi"})
        response.status_code = 500
        return response

    filename = "uploaded/" + str(uuid.uuid4()) + ".mid"
    midifile.save(filename)

    midi_data = pretty_midi.PrettyMIDI(filename)
    primer_sequence = magenta.music.midi_io.midi_to_sequence_proto(midi_data)
    num_steps = 20  # change this for shorter or longer sequences
    temperature = 1.0  # the higher the temperature the more random the sequence.
    submodel = "basic_rnn"

    generated_sequence = models.generate(midi_data, primer_sequence, num_steps, temperature, submodel)
    print(generated_sequence)

    output = tempfile.NamedTemporaryFile()
    magenta.music.midi_io.sequence_proto_to_midi_file(generated_sequence, output.name)
    output.seek(0)
    return send_file(output, attachment_filename='generated.mid', mimetype='audio/midi', as_attachment=True)


@app.route('/', methods=['GET', 'POST'])
def index():
    return send_file('melodeep/index.html')


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080)
