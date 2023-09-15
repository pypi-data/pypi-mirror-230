import pandas as pd

fallback_description = """
Replaces a text pattern Ex:'P.S {first_name}
what did you think?' with data from the contact. In this example, {first_name}
would be swapped with the column value of 'first_name' in your contact data.
"""

historic_data_description = """
Doesn't perform any scrape and uses
the current contact data and any scraped data
to generate a sentence using Copyfactory.
"""

case_study_description = """
This scraper aims to gather data about a
case study that the target company has worked on.
The data points you can expect to retrive are the following:
Case Study Overview, One Sentence Case Study Summary,
The company mentioned in the case study
and the source of where the data was found.
"""

company_achievement_description = """
This scraper aims to gather data
about a recent company achievement.
The data points you can expect to
retrieve are the following: Company Achievement Overview,
One Sentence Achievement Summary,
The company mentioned in the Achievement and
the source of where the data was found.
"""

company_description_description = """
This scraper aims to gather data about the comapnies description of what they do.
The data points you can expect to retrieve are the following:
Company Description, One Sentence Description Summary,
The company mentioned in the Description and the source of where the data was found.
"""

company_announcement_description = """
This scraper aims to gather data about a recent company announcement.
The data points you can expect to retrieve are the following:
 Company Announcement, One Sentence Announcement Summary,
 The company mentioned in the Announcement and the source of where the data was found.
"""

search_google_description = """
This scraper aims to gather data about a Google Search.
The data points you can expect to retrieve are the following:
 Customer Review, SEO Ranking of website for search term,
 The company mentioned in the result, The company description,
 The Title of the page and the search term used for the search
 and the source of where the data was found.
"""
get_linked_profile_description = """
This scraper aims to gather data about a prospect from their LinkedIn profile.
The data points you can expect to retrieve are the following: FIrst Name,
 Last Name, Company Name, City, State, Country, Current Employment Name,
  Current Title, Start Date, Company Description, Previous employment
  company name, Previous employment title, Previous employment start date,
  Previous employment end date, Previous employment company description,
  Education Establishment Name, Education Degree Name, Education start date,
  Education End Date,  Languages they speak, time in current role, did they
  recently change job, did they recently get promoted, LinkedIn profile URL.
"""
company_profile_description = """
Gathers data about the company public Linkedin profile.
"""
default_scraper_options = pd.DataFrame(
    data=[
        {
            "Scraper": "FALLBACK",
            "Scraper Description": fallback_description.strip(),
            "Notes": "",
        },
        {
            "Scraper": "USE_HISTORIC_DATA",
            "Scraper Description": historic_data_description.strip(),
            "Notes": "",
        },
        {
            "Scraper": "get-case-study",
            "Scraper Description": case_study_description.strip(),
            "Notes": "",
        },
        {
            "Scraper": "get-company-achievement",
            "Scraper Description": company_achievement_description.strip(),
            "Notes": "",
        },
        {
            "Scraper": "get-company-description",
            "Scraper Description": company_description_description.strip(),
            "Notes": "",
        },
        {
            "Scraper": "get-company-announcement",
            "Scraper Description": company_announcement_description.strip(),
            "Notes": "",
        },
        {
            "Scraper": "search-google",
            "Scraper Description": search_google_description.strip(),
            "Notes": "",
        },
        {
            "Scraper": "get-person-profile",
            "Scraper Description": get_linked_profile_description.strip(),
            "Notes": "This can be expensive to use please "
            "check estimate for scraping LinkedIn",
        },
        {
            "Scraper": "get-company-profile",
            "Scraper Description": company_profile_description.strip(),
            "Notes": "",
        },
        {
            "Scraper": "get-website-metadata",
            "Scraper Description": "Get the social media handles"
            " and technologies of a website.",
            "Notes": "",
        },
        {
            "Scraper": "get-company-news",
            "Scraper Description": "Searches Google for "
            "company news in the last 6 months.",
            "Notes": "",
        },
        {
            "Scraper": "get-social-media-profile-from-website",
            "Scraper Description": "Searches a companies homepage "
            "for an Instagram handle and pulls "
            "the profile data.",
            "Notes": "",
        },
        {
            "Scraper": "instagram/profile",
            "Scraper Description": "Based on an instagram "
            "profile will pull profile and posts data.",
            "Notes": "",
        },
    ]
)
