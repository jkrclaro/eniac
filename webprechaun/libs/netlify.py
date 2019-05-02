import logging
import copy
from urllib.parse import urljoin
from dataclasses import dataclass, field

import requests


class Netlify:

    def __init__(
        self, 
        access_token: str, 
        scheme: str='https', 
        host: str='api.netlify.com', 
        version: str='/api/v1/'
    ):
        """The primary Netlify class.

            :param access_token: Personal access token generated by Netlify.
            :param scheme: Scheme of Netlify's API url.
            :param host: Host of Netlify's API url.
            :param version: Version of Netlify's API url.
        """
        self.access_token = access_token
        self.scheme = scheme
        self.host = host
        self.version = version
        self.url = f'{scheme}://{host}{version}'
        self.headers = {'Authorization': f'Bearer {access_token}'}
        self.URL_SITES = urljoin(self.url, 'sites')

    def create_site(self, name: str) -> dict:
        """Create site in Netlify.

            :param name: Name of site.
        """
        data = {'name': name}
        site = requests.post(
            self.URL_SITES, 
            data=data, 
            headers=self.headers
        ).json()

        return site

    def get_sites(self) -> list:
        """Get list of sites in Netlify."""
        sites = requests.get(self.URL_SITES, headers=self.headers).json()

        return sites

    def get_site_id(self, name: str) -> str:
        """Get site id of site by name.

            :param name: Name of site.
        """
        site_id = None
        sites = self.get_sites()
        for site in sites:
            if site['name'] == name:
                site_id = site['id']
                break

        if not site_id:
            logging.warning(f"Site '{site_id}' not found.")

        return site_id

    def deploy_site(self, site_id: str) -> dict:
        """Deploy new or updated version of website.

        Netlify supports two ways of doing deploys:

        1. Sending a digest of all files in your deploy and then uploading any
        files Netlify doesn't already have on its storage servers.

        2. Sending a zipped website and letting Netlify unzip and deploy.

        This function uses the latter.

            :param site_id: Site ID of a site.
        """
        headers = copy.deepcopy(self.headers)
        headers['Content-Type'] = 'application/zip'

        # Zip a file and name it based on its site_id

        try:
            with open(f'{site_id}.zip', 'rb') as zip_file:
                url = f'{self.URL_SITES}/{site_id}/deploys'
                status = requests.post(
                    url,
                    headers=headers,
                    data=zip_file
                ).json()
        except FileNotFoundError as file_not_found:
            logging.error(file_not_found)
            # TODO: What would be a good fallback if app zip file is missing?
            status = {'status': 'error', 'reason': file_not_found}

        return status
