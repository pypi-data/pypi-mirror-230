# NijtaIO

The `nijtaio` library provides helper functions to streamline access to Nijta's API for Python application. It includes helper functions to prepare and retrieve the audio data.

You can find usage examples in our API reference and the Nijta samples repository.

## Installation

You can install the module using `pip`:

```bash
pip install nijtaio
```

## Basic Usage

```python
import os
import json
import time
import nijtaio

TOKEN = '<token>'
API_URL = 'https://api.nijta.com'
headers = {"Content-Type": "application/json; charset=utf-8", "TOKEN":TOKEN}
params = {
    'language':'french_8',
    'gender':'f',
    'voice':True,
    'content':True
}
output_folder = 'output'

session_id = nijtaio.session(TOKEN, api_url=API_URL)
response = nijtaio.send_request(["path/to/audio_1.wav",
                                 "path/to/audio_2.wav"],
                                params,session_id,
                                headers=headers,
                                api_url=API_URL)
task_id = json.loads(response.content)['data']['task_id']

print('Waiting for the batch to be processed.')
while True:
    time.sleep(1)
    status, anonymized_batch = nijtaio.read_response(task_id, api_url=API_URL)
    if status == 'finished':
        break

print(f'Writing results in {output_folder}.')

for original_filepath in anonymized_batch:
    filename = os.path.basename(original_filepath)
    with open(os.path.join(output_folder, filename), mode='wb') as f:
        f.write(anonymized_batch[original_filepath]['audio'])
    if params['content']:
        print(filename, anonymized_batch[original_filepath]['transcription'])
        
print(f'Done. Check the results in the {output_folder} directory.')
```