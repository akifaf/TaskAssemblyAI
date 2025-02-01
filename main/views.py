import requests
import time
import logging
from django.conf import settings
from .models import CallRecord
import json
from datetime import datetime
from django.http import JsonResponse

def index(request):
    try:
        # Call the function
        fetch_and_process_calls()
        return JsonResponse({'status': 'success', 'message': 'Call fetched and processed'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})


logging.basicConfig(
    filename="main/log/call_fetch.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


ASSEMBLY_AI_API_KEY = settings.ASSEMBLY_AI_API_KEY
location_id = settings.LOCATION_ID
ghl_private_key = settings.GHL_PRIVATE_KEY


def transcribe_call(recording_url):

    url = "https://api.assemblyai.com/v2/transcript"
    headers = {
        "Authorization": ASSEMBLY_AI_API_KEY,
        "Content-type": "application/json"
    }
    data = {
        "audio_url": recording_url,
        "speech_model": "nano",
        "summarization": True,
        "summary_model": "conversational",
        "summary_type": "bullets",
        "dual_channel": True
    }

    # Step 1: Initiate transcription
    response = requests.post(url, json=data, headers=headers)
    if response.status_code != 200:
        return None, None, None    
        

    transcript_id = response.json()["id"]
    
    # Step 2: Poll for completion
    while True:
        transcript_response = requests.get(f"{url}/{transcript_id}", headers=headers)
        result = transcript_response.json()
        print()
        print(result, 'transcript', result['status'])
        print()
        
        if result["status"] == "completed":
            return transcript_id, result.get("text", ""), result.get("summary", "")
        elif result["status"] == "failed":
            return None, None, None

        time.sleep(5)  # Wait before retrying




def create_note(call_sid):
    print('create note called')
    call_details = CallRecord.objects.get(call_sid=call_sid)
    contact_id = call_details.ghl_contact_id
    url = f"https://services.leadconnectorhq.com/contacts/{contact_id}/notes"

    # Note details
    data = f"""
        Call Recording URL: {call_details.call_sid}
        Call Date Time: {call_details.call_started_at}
        Call Duration: {call_details.call_duration}
        Call Transcription: {call_details.transcription}
        Call Summary: {call_details.summary}
        Call From Number: {call_details.call_from}
        Call To Number: {call_details.call_to}
        Call Direction: {call_details.call_direction}
        """

    payload = {
    "userId": contact_id,
    "body": data
    }

    headers = {
        "Authorization": f"Bearer {ghl_private_key}",
        "Version": "2021-07-28",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    response = requests.post(url, json=payload, headers=headers)

    print(response.json(), 'from here')


def update_fields(call_sid):
    print("\nupdate_fields called\n")

    call_details = CallRecord.objects.get(call_sid=call_sid)
    contact_id = call_details.ghl_contact_id
    print(call_details, 'call_details', call_details.call_recording_url)


    url = f"https://services.leadconnectorhq.com/contacts/{contact_id}"

    payload = {
        "customFields": [
            {
                "id": "efzLl5zgfZwr9jcQP3Zm",
                "field_value": call_details.call_recording_url
            },
            {
                "id": "ESo3LfPuqmuPZzWEYisV",
                "field_value": call_details.call_started_at.strftime('%Y-%m-%d %H:%M:%S') if call_details.call_started_at else None
            },
            {
                "id": "Dc2naOOqbhtdEXkIOFXz",
                "field_value": call_details.call_duration
            },
            {
                "id": "GKPezsc0NSOZIe6Tee9s",
                "field_value": call_details.transcription
            },
            {
                "id": "K0B19JjVSf1xMwaRTCIR",
                "field_value": call_details.summary
            },
            {
                "id": "Wwj71is2KQ5A4zPGZ2RD",
                "field_value": call_details.call_from
            }, 
            {
                "id": "7vEpxn1Zo9cKEop7vCXd",
                "field_value": call_details.call_to
            }, 
            {
                "id": "VQtsy6VHExK8WX6U9TaH",
                "field_value": call_details.call_duration
            }
        ],
    }
    headers = {
        "Authorization": f"Bearer {ghl_private_key}",
        "Version": "2021-07-28",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    response = requests.put(url, json=payload, headers=headers)

    print(response.json())
    return response.json()
    
def fetch_and_process_calls():

    skipvalue = 0
    now = datetime.now()
    dt_string = now.strftime("%Y-%m-%dT%H:%M:%SZ")

    while True:
        # Get token to fetch all calls
        url = "https://securetoken.googleapis.com/v1/token?key=AIzaSyB_w3vXmsI7WeQtrIOkjR6xTRVN5uOieiE"
        
        payload = 'grant_type=refresh_token&refresh_token=AMf-vBzsy360piu9afzB8FfHT9hzDOvvEF03pjN4qkNKNtu0bt7aWeDCEgTMVyZ6JHWE3Z4_GkPVhxi0Jz9yXC0WndJ6GfFd7me_of2yjOjShvrl80gmW32_199d2h7AZpIciV0NgIIrrugv4FjgFtKvWlkoBByhN3tSOigbQDAiXdG4uOjwREt5GY_UyQ-G7-AMVb42SqLCednBphVVvimVaVjZGC9NEnwPrXI0MhCxE8j4PcOqUS8O8x-VO4SzEcR2yyMUHcIoaOh4tXshVQwxT4uLAN0KmEvdb3qLi1R2KQgDH6iHyTRqV2dk4G-4fTKuq77O0KD9lmQybjr6WHbPiY5QqCNrQr5uG2v2MQ7HO1OzrLzUGHiA4eZymjS1ScUD5MzEWZeT8w_go7iDdHaqaWnLmGEHr5okV0s07XlaJmCo2Y-Q8Pq1hjlhXALn_YZlhvgBRoQ9B5yqkj80h4vXpEwfeGq_yg'
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        response = requests.post(url, headers=headers, data=payload)
        response_json = json.loads(response.text)
        id_token = response_json['id_token']

        url = "https://backend.leadconnectorhq.com/reporting/calls/get-all-phone-calls-new"
        payload = json.dumps({
            "locationId": "0rrNZinFkHbXD50u5nyq",
            "source": [],
            "sourceType": [],
            "keyword": [],
            "landingPage": [],
            "referrer": [],
            "campaign": [],
            "callStatus": [],
            "deviceType": [],
            "qualifiedLead": False,
            "firstTime": False,
            "duration": None,
            "selectedPool": "all",
            "direction": None,
            "startDate": "2010-01-01T00:00:00.000Z",
            "endDate": dt_string,
            "userId": "",
            "limit": 1000,
            "skip": skipvalue
        })
        
        headers = {
          'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:126.0) Gecko/20100101 Firefox/126.0',
          'Accept': 'application/json, text/plain, */*',
          'Accept-Language': 'en-US,en;q=0.5',
          'Accept-Encoding': 'gzip, deflate, br, zstd',
          'Content-Type': 'application/json',
          'Channel': 'APP',
          'Source': 'WEB_USER',
          'Version': '2021-04-15',
          'token-id': id_token,
          'sentry-trace': 'd57dfd1f3bbf4bd3a276eefdf55959d9-b3c213836e5201ab',
          'baggage': 'sentry-environment=production,sentry-release=dd23d24331896938a57ace8d425d247eee3e57f2,sentry-public_key=c67431ff70d6440fb529c2705792425f,sentry-trace_id=d57dfd1f3bbf4bd3a276eefdf55959d9',
          'Origin': 'https://loop.kerrijames.co',
          'Connection': 'keep-alive',
          'Referer': 'https://loop.kerrijames.co/',
          'Sec-Fetch-Dest': 'empty',
          'Sec-Fetch-Mode': 'cors',
          'Sec-Fetch-Site': 'cross-site',
          'TE': 'trailers'
        }

        response = requests.request("POST", url, headers=headers, data=payload)
        response_json = json.loads(response.text)

        if not response_json.get('rows', []):
            logging.info("Calls Data is empty: " + response.text)
            break
        else:
            skipvalue += 1000

        logging.info(response.text)
        print()
        print(len(response_json), 'jfoiaejoij')
        print()

        for each_row in json.loads(response.text)['rows']:
        #for each_row in response['rows']:
            # print(each_row, 'each_row')
            if 'callSid' in each_row:
                call_sid = each_row['callSid']
                if CallRecord.objects.filter(call_sid=call_sid).exists():
                    print('processed')
                    continue
            else:
                continue

            if 'callStatus' in each_row:
                call_status = each_row['callStatus']
            else:
                call_status = None

            if 'contactId' in each_row:
                contact_id = each_row['contactId']
            else:
                contact_id = None
                contact_fullname = None

            if 'locationId' in each_row:
                location_id = each_row['locationId']
            else:
                location_id = None

            if 'from' in each_row:
                from_number = each_row['from']
            else:
                from_number = None

            if 'to' in each_row:
                to_number = each_row['to']
            else:
                to_number = None

            if 'dateAdded' in each_row:
                call_date = each_row['dateAdded']
            else:
                call_date = None

            if 'createdAt' in each_row and each_row['createdAt'] != None and call_date == None:
                call_date = each_row['createdAt']

            if 'direction' in each_row:
                call_direction = each_row['direction']
            else:
                call_direction = None

            if 'duration' in each_row and each_row['duration'] != None and int(each_row['duration']) > 30:
                print(each_row['duration'], 'duration')
                call_duration = each_row['duration']
            else:
                continue

            if 'recordingUrl' in each_row:
                recording_url = each_row['recordingUrl']
            else:
                recording_url = None

            if 'firstTime' in each_row:
                first_time = str(each_row['firstTime'])
            else:
                first_time = None

            if 'source' in each_row:
                source = each_row['source']
            else:
                source = None

            if 'sourceType' in each_row:
                source_type = each_row['sourceType']
            else:
                source_type = None

            if 'landingPage' in each_row:
                landing_page = each_row['landingPage']
            else:
                landing_page = None

            if 'referrer' in each_row:
                referrer = each_row['referrer']
            else:
                referrer = None

            if 'campaign' in each_row:
                campaign = each_row['campaign']
            else:
                campaign = None

            #Fetch full name of contact
            if contact_id != None:

                url = "https://services.leadconnectorhq.com/contacts/"+str(contact_id)

                headers = {
                    "Authorization": "Bearer "+ ghl_private_key,
                    "Version": "2021-07-28",
                    "Accept": "application/json"
                }

                response = requests.get(url, headers=headers)

                if response.status_code == 200:
                    # print(response.text)
                    if 'fullNameLowerCase' in json.loads(response.text)['contact']:
                        contact_fullname = json.loads(response.text)['contact']['fullNameLowerCase']
                    else:
                        contact_fullname = None
                else:
                    contact_fullname = None

            # Transcribe & summarize
            transcript_id, transcription, summary = transcribe_call(recording_url)
            if not transcription:
                continue


            try:
                CallRecord.objects.create(
                    call_sid=call_sid,
                    call_status=call_status,
                    ghl_contact_id=contact_id,
                    ghl_contact_fullname=contact_fullname,
                    ghl_location_id=location_id,
                    call_from=from_number,
                    call_to=to_number,
                    call_started_at=call_date,
                    call_direction=call_direction,
                    call_duration=call_duration,
                    call_recording_url=recording_url,
                    first_time=first_time,
                    ghl_location_name=None, 
                    source=source,
                    source_type=source_type,
                    landing_page=landing_page,
                    referrer=referrer,
                    campaign=campaign,

                    transcript_id=transcript_id,
                    transcription=transcription,
                    summary=summary
                )
                logging.info(f"Inserted call_sid: {call_sid}")

                # Call create_note immediately after creating the CallRecord
                create_note(call_sid)
                update_fields(call_sid)

            except Exception as e:
                print(e, 'errro``')
                logging.error(f"Error inserting call_sid {call_sid}: {str(e)}")
                continue
