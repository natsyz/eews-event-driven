from google.cloud import aiplatform
from google.oauth2 import service_account

# creds = service_account.Credentials.from_service_account_file('creds/gcloud_creds.json')

# aiplatform.init(
#     # your Google Cloud Project ID or number
#     # environment default used is not set
#     project='eews-ta',

#     # the Vertex AI region you will use
#     # defaults to us-central1
#     location='us-central1',

#     # Google Cloud Storage bucket in same region as location
#     # used to stage artifacts
#     staging_bucket='gs://model-vertex-ai',

#     # custom google.auth.credentials.Credentials
#     # environment default creds used if not set
#     credentials=creds
# )

# endpoint = aiplatform.Endpoint(
#     endpoint_name="projects/639177621331/locations/us-central1/endpoints/5242159179933679616")
