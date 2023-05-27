
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect
from django.views import View
from google.oauth2 import credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build

# Google Calendar Init View
class GoogleCalendarInitView(View):
    def get(self, request):
        # Set up the OAuth2 flow
        flow = Flow.from_client_secrets_file(
            'client_secrets.json',  # Path to your client secrets JSON file
            scopes=['https://www.googleapis.com/auth/calendar.readonly'],
            redirect_uri=request.build_absolute_uri('/rest/v1/calendar/redirect/')
        )

        # Generate the authorization URL
        authorization_url, state = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true'
        )

        # Save the OAuth2 state in the session
        request.session['google_auth_state'] = state

        # Redirect the user to the Google OAuth2 login page
        return HttpResponseRedirect(authorization_url)


# Google Calendar Redirect View
class GoogleCalendarRedirectView(View):
    def get(self, request):
        # Verify the OAuth2 state
        if 'google_auth_state' not in request.session or request.GET.get('state') != request.session['google_auth_state']:
            return HttpResponse('Invalid state parameter', status=400)

        # Exchange the authorization code for access token
        flow = Flow.from_client_secrets_file(
            'client_secrets.json',  # Path to your client secrets JSON file
            scopes=['https://www.googleapis.com/auth/calendar.readonly'],
            redirect_uri=request.build_absolute_uri('/rest/v1/calendar/redirect/')
        )
        flow.fetch_token(
            authorization_response=request.build_absolute_uri(),
        )

        # Create a Google Calendar API service instance
        credentials = flow.credentials
        service = build('calendar', 'v3', credentials=credentials)

        # Get the list of events from the user's calendar
        events_result = service.events().list(calendarId='primary', maxResults=10).execute()
        events = events_result.get('items', [])

        # Process the events as per your requirements
        # ...

        # Return the list of events as JSON response
        return JsonResponse({'events': events})