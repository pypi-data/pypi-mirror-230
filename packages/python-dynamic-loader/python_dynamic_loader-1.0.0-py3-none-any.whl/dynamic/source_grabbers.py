# Copyright 2023 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from __future__ import annotations

import logging
import os
from typing import Any, Mapping

from google.cloud import secretmanager, secretmanager_v1, storage


class SourceGrabber(object):
  """SourceGrabber

  This is the interface for any datastore containing source code to be loaded
  dynamically.
  """
  def __init__(self, **unused) -> SourceGrabber:
    pass

  def fetch_source(self, source: str, **kwargs: Mapping[str, Any]) -> str:
    """Fetches the source from the datastore.

    All source should be returned as a string. It is required that the grabber
    perform this conversion as the remainder of the dynamic process will expect
    source in the form of a string, not bytes.

    Returns:
        str: the source as a string.
    """
    pass


class CloudStorage(SourceGrabber):
  """Cloud Storage SourceGrabber"""
  @property
  def project(self) -> str:
    """The Cloud Project in which the App is running, taken from the
       environment.

    Returns:
        str: GCP name
    """
    return os.environ.get('GOOGLE_CLOUD_PROJECT') or os.environ.get('GCP_PROJECT')

  @property
  def bucket(self) -> str:
    return self._bucket

  @bucket.setter
  def bucket(self, bucket: str = None) -> None:
    self._bucket = bucket

  def __init__(self, bucket: str = None, **unused) -> CloudStorage:
    self.bucket = f'{bucket or "dynamic-commands"}'

  def fetch_source(self, source: str, **unused: Any) -> str:
    """Fetches the source from the Google Cloud Storage.

    The cloud function's implicit credentials are used for this operation.
    Any args other than the one listed will be ignored.

    Args:
        source (str): the file to load

    Returns:
        str: the source
    """
    client = storage.Client()

    try:
      content = client.get_bucket(self.bucket).blob(f'{source}.py').download_as_text()
    except Exception as ex:
      content = None
      logging.error('Error fetching file %s\n%s', source, ex)

    return content


class SecretManager(SourceGrabber):
  """Secret Manager SourceGrabber"""
  @property
  def project(self) -> str:
    """The Cloud Project in which the App is running, taken from the
       environment.

    Returns:
        str: GCP name
    """
    return os.environ.get('GOOGLE_CLOUD_PROJECT') or os.environ.get('GCP_PROJECT')

  def fetch_source(self, source: str, **unused: Any) -> str:
    """Fetches the source from the Google Cloud Storage.

    The cloud function's implicit credentials are used for this operation.
    Any args other than the one listed will be ignored.

    Args:
        source (str): the name of the secret to fetch

    Returns:
        str: the source
    """
    client = secretmanager.SecretManagerServiceClient()

    try:
      secret_name = client.secret_version_path(project=self.project,
                                               secret=source,
                                               secret_version='latest')
      request = secretmanager_v1.AccessSecretVersionRequest(name=secret_name)
      response = client.access_secret_version(request=request)
      content = response.payload.data.decode(encoding='utf-8')
    except Exception as e:
      content = None
      logging.error('Error fetching secret %s\n%s', source, e)

    return content


class LocalStorage(SourceGrabber):
  """Local file SourceGrabber"""

  @property
  def folder(self) -> str:
    return self._folder

  @folder.setter
  def folder(self, folder: str = None) -> None:
    self._folder = folder

  def __init__(self, folder: str = None, **unused) -> LocalStorage:
    self.folder = folder or ''

  def fetch_source(self, source: str, **kwargs: Mapping[str, Any]) -> str:
    with open(f'{self.folder}/{source}.py', 'r') as _source:
      code = _source.read()

    return ''.join(code)
