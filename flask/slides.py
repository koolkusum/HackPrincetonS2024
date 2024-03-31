import google.auth
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import uuid
from google.oauth2.credentials import Credentials


gen_uuid = lambda:str(uuid.uuid4())
SCOPES = ['https://www.googleapis.com/auth/presentations']

def create_slide(presentation_id, page_id):
  # pylint: disable=maybe-no-member
  try:
    # Add a slide at index 1 using the predefined
    # 'TITLE_AND_TWO_COLUMNS' layout and the ID page_id.
    requests = [
        {
            "createSlide": {
                "objectId": page_id,
                "insertionIndex": "1",
                "slideLayoutReference": {
                    "predefinedLayout": "TITLE_AND_TWO_COLUMNS"
                },
            }
        }
    ]

    # If you wish to populate the slide with elements,
    # add element create requests here, using the page_id.

    # Execute the request.
    body = {"requests": requests}
    response = (
        service.presentations()
        .batchUpdate(presentationId=presentation_id, body=body)
        .execute()
    )
    create_slide_response = response.get("replies")[0].get("createSlide")
    print(f"Created slide with ID:{(create_slide_response.get('objectId'))}")
  except HttpError as error:
    print(f"An error occurred: {error}")
    print("Slides not created")
    return error

  return response


def create_textbox_with_text(presentation_id, page_id):

  # pylint: disable=maybe-no-member
  try:
    # Create a new square textbox, using the supplied element ID.
    element_id = "MyTextBox_10"
    pt350 = {"magnitude": 350, "unit": "PT"}
    requests = [
        {
            "createShape": {
                "objectId": element_id,
                "shapeType": "TEXT_BOX",
                "elementProperties": {
                    "pageObjectId": page_id,
                    "size": {"height": pt350, "width": pt350},
                    "transform": {
                        "scaleX": 1,
                        "scaleY": 1,
                        "translateX": 350,
                        "translateY": 100,
                        "unit": "PT",
                    },
                },
            }
        },
        # Insert text into the box, using the supplied element ID.
        {
            "insertText": {
                "objectId": element_id,
                "insertionIndex": 0,
                "text": "New Box Text Inserted!",
            }
        },
    ]

    # Execute the request.
    body = {"requests": requests}
    response = (
        service.presentations()
        .batchUpdate(presentationId=presentation_id, body=body)
        .execute()
    )
    create_shape_response = response.get("replies")[0].get("createShape")
    print(f"Created textbox with ID:{(create_shape_response.get('objectId'))}")
  except HttpError as error:
    print(f"An error occurred: {error}")

    return error

  return response


if __name__ == "__main__":
    # Put the presentation_id, Page_id of slides whose list needs
    # to be submitted.
    creds = Credentials.from_authorized_user_file("token.json", SCOPES)

    service = build("slides", "v1", credentials=creds)

    presentation = service.presentations().create(
        body={'title': 'My Presentation'}).execute()
    presentation_id = presentation.get('presentationId')

    # Get the pageObjectId of the first slide
    presentation = service.presentations().get(presentationId=presentation_id).execute()
    slides = presentation.get('slides', [])
    if slides:
        first_slide_id = slides[0]['objectId']
        #create_textbox_with_text(presentation_id, first_slide_id)
        create_slide(presentation_id, first_slide_id)
