import os
import json
import time
import nijtaio
import fire

def voice_harbor_api(token: str,  
                     input_data: list,  
                     language: str,  
                     gender:str ,  
                     voice: bool,  
                     content: bool,  
                     output_folder:str,
                     api_url = 'https://api.nijta.com/'):
    """Run voiceharbor CLI
    
    Args:
        token (str): Your Voice Harbor API token.
        input_data (str or list): A path to a folder with audio files or a list of audio file paths.
        language (str): The language of the audio files. Options: 'french_8', 'english_16'
        gender (str): The gender of the target speaker. Options: 'f', 'm'
        voice (bool): Whether to anonymize voice or not. Options: True, False
        content (bool): Whether to anonymize content or not. Options: True, False
        output_folder (str): The output folder for the anonymized audio files.
        api_url (str, optional): The URL of the Voice Harbor API. Defaults to 'https://api.nijta.com
    
    """
    if language not in ('english_16', 'french_8'):
        print('Language should be either "english_16" or "french_8".')
        return
    if gender not in ('f','m'):
        print('Gender should be either "f" or "m".')
        return
    if not isinstance(voice, bool):
        print('Voice should be either True or False')
        return
    if not isinstance(content, bool):
        print('Content should be either True or False')
        return
    
    headers = {
      "Content-Type": "application/json; charset=utf-8",
      "TOKEN": token
    }

    params = {
        'language': language,
        'gender': gender,
        'voice': voice,
        'content': content
    }

    # Start a new session with the provided token
    session_id = nijtaio.session(token)

    # Send a batch of audio files for processing and get the task id
    response = nijtaio.send_request(
        input_data,
        params,
        headers=headers,
        session_id=session_id,
        api_url=api_url
    )
    task_id = json.loads(response.content)['data']['task_id']
    print(task_id)

    # Monitor the processing status of the batch
    print('Waiting for the batch to be processed.')
    while True:
        time.sleep(1)
        status, anonymized_batch = nijtaio.read_response(task_id, api_url=api_url)
        if status == 'finished':
            break

    # Process and save the anonymized results
    print(f'Writing results in {output_folder}.')
    os.makedirs(output_folder, exist_ok=True)
    for original_filepath in anonymized_batch:
        filename = os.path.basename(original_filepath)
        if voice:
            # Save anonymized audio if voice parameter is True
            with open(os.path.join(output_folder, filename), mode='wb') as f:
                f.write(anonymized_batch[original_filepath]['audio'])
        if content:
            # Print transcription if content parameter is True
            print(filename, anonymized_batch[original_filepath]['transcription'])

    print(f'Done. Check the results in the {output_folder} directory.')


def main():
    fire.Fire(voice_harbor_api)
