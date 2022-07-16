import os
from base64 import urlsafe_b64decode

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build, Resource


def authenticate() -> Resource:
    """ follow https://developers.google.com/gmail/api/quickstart/python ,
        and make sure to add test-user with self-email-address to oauth consent """
    # If modifying these scopes, delete the file token.json.
    scopes = ['https://www.googleapis.com/auth/gmail.readonly']
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    temp_token_file_p = 'token.json'
    credentials_file_p = 'client_secret_304235664670-s33nhsh0p5r8li3c475gr26i74eb0pdp.apps.googleusercontent.com.json'
    if os.path.exists(temp_token_file_p):
        creds = Credentials.from_authorized_user_file(temp_token_file_p, scopes)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                credentials_file_p, scopes)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    service = build('gmail', 'v1', credentials=creds)
    return service


class EmailAttachmentsDownloader:
    """
        based on https://github.com/x4nth055/pythoncode-tutorials/blob/master/general/gmail-api/read_emails.py
        with a bug-fix to handle >100 attachments of emails with the same subjects,
        and reduced only to download attachments.
    """

    @staticmethod
    def read_message(service, message):
        """
        This function takes Gmail API `service` and the given `message_id` and does the following:
            - Downloads the content of the email
            - Creates a folder for each email based on the subject
            - Downloads any file that is attached to the email and saves it in the folder created
        """
        msg = service.users().messages().get(userId='me', id=message['id'], format='full').execute()
        # parts can be the message body, or attachments
        payload = msg['payload']
        headers = payload.get("headers")
        parts = payload.get("parts")
        folder_name = "email"
        has_subject = False
        if headers:
            # this section prints email basic info & creates a folder for the email
            for header in headers:
                name = header.get("name")
                value = header.get("value")
                if name.lower() == 'from':
                    print("From:", value)
                if name.lower() == "to":
                    print("To:", value)
                if name.lower() == "subject":
                    has_subject = True
                    folder_name = EmailAttachmentsDownloader._clean(value)
                    folder_counter = 0
                    while os.path.isdir(folder_name):
                        folder_counter += 1
                        # we have the same folder name, add a number next to it
                        if folder_name[-1].isdigit() and folder_name[-2] == "_":
                            folder_name = f"{folder_name[:-2]}_{folder_counter}"
                        elif folder_name[-2:].isdigit() and folder_name[-3] == "_":
                            folder_name = f"{folder_name[:-3]}_{folder_counter}"
                        elif folder_name[-3:].isdigit() and folder_name[-4] == "_":
                            folder_name = f"{folder_name[:-4]}_{folder_counter}"
                        else:
                            folder_name = f"{folder_name}_{folder_counter}"
                    os.mkdir(folder_name)
                    print("Subject:", value)
                if name.lower() == "date":
                    print("Date:", value)
        if not has_subject:
            # if the email does not have a subject, then make a folder with "email" name
            # since folders are created based on subjects
            if not os.path.isdir(folder_name):
                os.mkdir(folder_name)
        EmailAttachmentsDownloader._parse_parts(service, parts, folder_name, message)
        print("=" * 50)

    @staticmethod
    def _get_size_format(b, factor=1024, suffix="B"):
        """
        Scale bytes to its proper byte format
        e.g:
            1253656 => '1.20MB'
            1253656678 => '1.17GB'
        """
        for unit in ["", "K", "M", "G", "T", "P", "E", "Z"]:
            if b < factor:
                return f"{b:.2f}{unit}{suffix}"
            b /= factor
        return f"{b:.2f}Y{suffix}"

    @staticmethod
    def _clean(text):
        # clean text for creating a folder
        return "".join(c if c.isalnum() else "_" for c in text)

    @staticmethod
    def _parse_parts(service, parts, folder_name, message):
        """
        Utility function that parses the content of an email partition
        """
        if parts:
            for part in parts:
                filename = part.get("filename")
                mime_type = part.get("mimeType")
                body = part.get("body")
                file_size = body.get("size")
                part_headers = part.get("headers")
                if part.get("parts"):
                    # recursively call this function when we see that a part
                    # has parts inside
                    EmailAttachmentsDownloader._parse_parts(service, part.get("parts"), folder_name, message)
                if mime_type != "text/plain" and mime_type != "text/html":
                    # attachment other than a plain text or HTML
                    for part_header in part_headers:
                        part_header_name = part_header.get("name")
                        part_header_value = part_header.get("value")
                        if part_header_name == "Content-Disposition":
                            if "attachment" in part_header_value:
                                # we get the attachment ID
                                # and make another request to get the attachment itself
                                print("Saving the file:", filename, "size:",
                                      EmailAttachmentsDownloader._get_size_format(file_size))
                                attachment_id = body.get("attachmentId")
                                attachment = service.users().messages() \
                                    .attachments().get(id=attachment_id, userId='me',
                                                       messageId=message['id']).execute()
                                data = attachment.get("data")
                                filepath = os.path.join(folder_name, filename)
                                if data:
                                    with open(filepath, "wb") as f:
                                        f.write(urlsafe_b64decode(data))


def main() -> None:
    service = authenticate()

    messages = []
    from_query = "from:noreply@email.iforms.co.il"
    result = service.users().messages().list(userId='me', q=from_query, includeSpamTrash=False).execute()
    if 'messages' in result:
        messages.extend(result['messages'])
    while 'nextPageToken' in result:
        page_token = result['nextPageToken']
        result = service.users().messages().list(userId='me', q=from_query, pageToken=page_token).execute()
        if 'messages' in result:
            messages.extend(result['messages'])

    extractor = EmailAttachmentsDownloader()
    for msg in messages:
        extractor.read_message(service, msg)


if __name__ == '__main__':
    # remove unneeded attachments: `find . -name 'תיעוד פרטי המסמך.pdf' -delete`
    main()
