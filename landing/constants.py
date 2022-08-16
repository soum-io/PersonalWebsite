import os

EMAIL = 'soumiodevelopment@gmail.com'
YOUTUBE_CHANNEL_ID = 'UC6qsb94FpS0rd5HzWjJPozg'
GITHUB_LOGO = 'https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png'
URL_REGEX = r"((https?):((//)|(\\\\))+[\w\d:#@%/;$()~_?\+-=\\\.&]*)"

# search for "octolytics-dimension-repository_id" in page source to get id of any github repo
OPEN_SOURCE_REPO_IDS = [125595640,  # tensorflow lite
                        ]
PROJECT_REPO_IDS = [167403589,  # tensorflow lite
                    181963854,  # usb
                    ]

# secrets
YOUTUBE_API_KEY = os.environ.get('YOUTUBE_API_KEY')
GITHUB_API_TOKEN = os.environ.get('GITHUB_API_TOKEN')

