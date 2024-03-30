import google.auth
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import uuid
from google.oauth2.credentials import Credentials

gen_uuid = lambda: str(uuid.uuid4())
SCOPES = ['https://www.googleapis.com/auth/presentations']
def create_slide(presentation_id, title_text):
    try:
        slide_id = gen_uuid()

        requests = [
            {
                "createSlide": {
                    "objectId": slide_id,
                    "insertionIndex": "1",
                    "slideLayoutReference": {
                        "predefinedLayout": "TITLE_AND_TWO_COLUMNS"
                    },
                }
            }
        ]

        # Add request to update the title text
        requests.append({
            "updateTextStyle": {
                "objectId": slide_id,  # Title text box object ID
                "style": {
                    "bold": False,
                    "italic": False,
                    "foregroundColor": {
                        "opaqueColor": {
                            "rgbColor": {
                                "red": 0.0,
                                "green": 0.0,
                                "blue": 0.0
                            }
                        }
                    },
                    "fontSize": {
                        "magnitude": 20,
                        "unit": "PT"
                    }
                },
                "textRange": {
                    "type": "ALL"
                },
                "fields": "bold,italic,foregroundColor,fontSize"
            }
        })

        # Add request to set the title text
        requests.append({
            "insertText": {
                "objectId": slide_id,
                "text": title_text,
                "insertionIndex": 0,
            }
        })

        body = {"requests": requests}
        response = (
            service.presentations()
            .batchUpdate(presentationId=presentation_id, body=body)
            .execute()
        )
        create_slide_response = response.get("replies")[0].get("createSlide")
        print(f"Created slide with ID: {slide_id}")
    except HttpError as error:
        print(f"An error occurred: {error}")
        print("Slide not created")
        return error

    return response

if __name__ == "__main__":
    creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    service = build("slides", "v1", credentials=creds)

    presentation = service.presentations().create(
        body={'title': 'My Presentation'}
    ).execute()
    presentation_id = presentation.get('presentationId')

    create_slide_response = create_slide(presentation_id, "New Title")