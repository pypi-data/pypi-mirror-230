# 🧙 ContactMagic

## What is ContactMagic?

**ContactMagic** is a wrapper around [Copyfactory](https://copyfactory.io/) and
[SalesScrapers](https://salesscrapers.dev/) to build programmatic workflows that enrich contact data
and create personalized and engaging messaging.

With ContactMagic, you can programmatically:

- Enrich people and companies with hard to find datapoints such as case studies, news announcements and more.
- Build your own custom scrapers in a few lines of code *(Soon)*
- Bulk personalize and enrich data with as many datapoints as you need.
- Create custom personalization templates.
- Manage and run personalization workflows for clients at scale (contact [eric@copyfactory.io](eric@copyfactory.io) to learn more)

## Before you install

ContactMagic was designed with concurrency in mind. All operations make use of Asyncio to accelerate the process. You
can set the number of concurrent workers in the settings.

Before installing, you should also ensure that you have a registered account with [Copyfactory](https://copyfactory.io/)
and [SalesScrapers](https://salesscrapers.dev/) as API keys for both services is required.

## Rate limit and error handling

There is no need for you to handle rate limits (`429` HTTP status error). The library handles rate limits automatically.

## Configuration

A 'SETTINGS' variable is exposed from the `settings.py` file which reads from your environment to set API key values.

Here are the current settings you should have in your .env file or environment.

```python
COPYFACTORY_API_KEY=''
SALES_SCRAPERS_API_KEY=''
MASTERSHEET_URL=''
GOOGLE_PROJECT_ID=''
GOOGLE_PRIVATE_KEY_ID=''
GOOGLE_PRIVATE_KEY=''
GOOGLE_CLIENT_ID=''
GOOGLE_CLIENT_EMAIL=''
TIMEZONE="America/New_York"
# list and dict are parsed as JSON.
ALLOWED_SCRAPER_NAMES='["get-case-study", "get-company-achievement", "get-company-description", "get-company-announcement", "FALLBACK", "search-google"]'
MAX_WORKERS='5'  # Number of concurrent workers to process. 5-10 is likely enough.
```

If you are not using the agency workflows and just want to use the underlying PersonalizationSetttings objects you only
need to set the following environment variables.

```python
COPYFACTORY_API_KEY=''
SALES_SCRAPERS_API_KEY=''
# Optional since has default value
ALLOWED_SCRAPER_NAMES='["get-case-study", "get-company-achievement", "get-company-description", "get-company-announcement", "FALLBACK", "search-google"]'
# Optional since has default value
MAX_WORKERS='5'
```

## Usage & Examples

The core underlying model you will be using is 'PersonalizationSettings' which is responsible for understanding what
you want to scrape and how you want to personalize.

```python
from contact_magic import PersonalizationSettings
import pandas as pd

data = [
    {
        # name this column anything you want
        "col_name": "personalized_field1",
        # If the first scraper returns nothing, will iterate through list until a successful scrape is complete.
        "allowed_scrapers": [
            {
                "scraper_name": "get-case-study",  # endpoint for SalesScrapers
                "premise_url": "https://app.copyfactory.io/profiles/1065/premises/7478/"  # Copyfactory premise url
            },
            {
                "scraper_name": "another-scraper",
                "premise_url": "https://app.copyfactory.io/profiles/1065/premises/7478/"
            }
        ],
    }, ...
]

# Set the datapoints. Notice how it's a list? This means you can generate as many personalized sentences as you want.
settings = PersonalizationSettings(datapoints=data)
dataframe = pd.read_csv("my_csv_file.csv")
# Run the settings against the DataFrame
personalized_dataframe = settings.process_from_dataframe(dataframe)
```

What happens when we run `process_from_dataframe`?

1. The dataframe is extended with new columns. For each 'col_name' in the list of datapoints you provided a new
   column with the name you set for 'col_name' and another one for the source which is 'source__{col_name_value}' is added.
    - In our example above, the columns created would be 'personalized_field1' and 'source__personalized_field1'.
2. For each datapoint, the list of 'allowed_scrapers' is iterated on and SalesScraper tries to find the data, if it does
   it sends the scraped data to Copyfactory to generate a personalized sentence.
3. The source from SalesScrapers is set for that datapoints source column, and the personalized sentence is set on the
   datapoints column name.
