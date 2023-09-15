import requests as req
import json
import pandas as pd
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import base64
import datetime


class DevOps:
    def __init__(self, token=None, api_version=None):
        if token is None:
            raise Exception('Token is required to connect to DevOps')

        self.headers = {"Content-Type": "application/json",
                        "Authorization": f"Basic {base64.b64encode(str(f':{token}').encode('utf-8')).decode('utf-8')}"}

        self.session = req.Session()
        retry = Retry(total=3, status_forcelist=[429, 500, 502, 504], backoff_factor=30)
        retry.BACKOFF_MAX = 190

        adapter = HTTPAdapter(max_retries=retry)
        self.session.mount('http://', adapter)
        self.session.mount('https://', adapter)

        self.base_url = 'https://dev.azure.com/BerryworldGroup'

        if api_version is None:
            self.api_version = 'api-version=7.0'
        else:
            self.api_version = f'api-version={api_version}'

    def session_request(self, method, url, headers=None, data=None, content=False):
        if headers is None:
            headers = self.headers

        if data is None:
            response = self.session.request(method, url, headers=headers)
        else:
            response = self.session.request(method, url, headers=headers, data=data)

        if response.status_code == 204:
            return pd.DataFrame()
        elif str(response.status_code).startswith('2'):
            if content:
                return response

            response = (json.loads(response.text))
            if 'value' in response:
                response_df = pd.DataFrame(response['value'])
            else:
                response_df = pd.DataFrame([response])

        else:
            raise Exception(f'Status: {response.status_code} - {response.text}')

        return response_df

    def list_projects(self):
        projects_url = f'{self.base_url}/_apis/projects'
        projects_df = self.session_request('GET', projects_url)

        return projects_df

    def list_repositories(self, project_name):
        repo_url = f"{self.base_url}/{project_name}/_apis/git/repositories"
        repo_df = self.session_request('GET', repo_url)

        return repo_df

    def list_repository_items(self, project_name, repo_id, path=None, branch=None):
        repo_items_url = f"{self.base_url}/{project_name}/_apis/git/repositories/{repo_id}/itemsbatch?" \
                         f"{self.api_version}"

        if path is None:
            path = "/"

        if branch is None:
            branch = "master"

        body = json.dumps({
            "itemDescriptors": [
                {
                    "path": path,
                    "version": branch,
                    "versionType": "branch",
                    "versionOptions": "none",
                    "recursionLevel": "full"
                }
            ],
            "includeContentMetadata": "true"
        })

        repo_items_df = self.session_request('POST', repo_items_url, data=body)

        return repo_items_df

    def list_pipeline_releases(self, project_name):
        release_definitions_url = f"https://vsrm.dev.azure.com/BerryworldGroup/{project_name}/_apis/release/definitions"
        release_definitions_df = self.session_request('GET', release_definitions_url)

        return release_definitions_df

    def list_release_revision(self, project_name, release_id, revision_name=None):
        release_revision_url = f"https://vsrm.dev.azure.com/BerryworldGroup/{project_name}/_apis/release/" \
                               f"definitions/{release_id}/revisions"

        if revision_name is not None:
            release_revision_url = f"{release_revision_url}/{revision_name}"

        release_revision_df = self.session_request('GET', release_revision_url)

        return release_revision_df

    def list_pipeline_builds(self, project_name):
        build_definitions_url = f"{self.base_url}/{project_name}/_apis/build/definitions"
        build_definitions_df = self.session_request('GET', build_definitions_url)

        return build_definitions_df

    def list_build_revision(self, project_name, build_id):
        build_revision_url = f"{self.base_url}/{project_name}/_apis/build/definitions/{build_id}/revisions"
        build_revision_df = self.session_request('GET', build_revision_url)

        return build_revision_df

    def list_artifact_feeds(self):
        artifact_feeds_url = f"https://feeds.dev.azure.com/BerryworldGroup/_apis/packaging/feeds"
        artifact_feeds_df = self.session_request('GET', artifact_feeds_url)

        return artifact_feeds_df

    def list_feed_packages(self, feed_id):
        feed_packages_url = f"https://feeds.dev.azure.com/BerryworldGroup/_apis/packaging/feeds/{feed_id}/packages"
        feed_packages_df = self.session_request('GET', feed_packages_url)

        return feed_packages_df

    def list_package_versions(self, feed_id, package_name):
        package_versions_url = f"https://feeds.dev.azure.com/BerryworldGroup/_apis/packaging/feeds/{feed_id}/" \
                               f"packages/{package_name}/versions"
        package_versions_df = self.session_request('GET', package_versions_url)

        return package_versions_df

    def get_package_version_content(self, feed_id, package_id, version_id):
        package_content_url = f"https://feeds.dev.azure.com/BerryworldGroup/_apis/packaging/feeds/{feed_id}/" \
                              f"packages/{package_id}/versions/{version_id}"
        package_content_df = self.session_request('GET', package_content_url)

        return package_content_df

    def create_repo_files(self, project_name, repo_id, environment_name, payload, branch=None):
        commits_url = f"{self.base_url}/{project_name}/_apis/git/repositories/{repo_id}/" \
                      f"commits?{self.api_version}"
        commits_df = self.session_request("GET", commits_url)
        if commits_df.shape[0] > 0:
            last_commit_id = commits_df['commitId'][0]
        else:
            last_commit_id = '0000000000000000000000000000000000000000'

        if branch is None:
            branch = "refs/heads/master"

        run_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        repo_payload = json.dumps({
            "refUpdates": [
                {
                    "name": branch,
                    "oldObjectId": last_commit_id
                }
            ],
            "commits": [{
                "comment": f"Adding {environment_name} PowerAutomate properties via API - {run_time}.",
                "changes": payload
            }]
        })

        repo_pushes_url = f"{self.base_url}/{project_name}/_apis/git/repositories/{repo_id}/pushes?{self.api_version}"

        create_repo_files = self.session_request("POST", repo_pushes_url, data=repo_payload)

        return create_repo_files

    def get_file_content(self, project_name, repo_id, file_path):
        file_content_url = f"{self.base_url}/{project_name}/_apis/git/repositories/{repo_id}/items?" \
                           f"scopePath={file_path}&includeContent=True"

        file_content = self.session_request("GET", file_content_url, content=True)

        return file_content
