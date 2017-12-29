# Copyright 2018 Google Inc. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Models for blob-management tool.
"""

from google.appengine.ext import ndb


class NdbBlobInfo(ndb.Model):
  """Interface ndb to __BlobInfo__ entities."""
  @classmethod
  def _get_kind(cls):
    return '__BlobInfo__'

  filename = ndb.StringProperty()
  content_type = ndb.StringProperty()
  creation = ndb.DateTimeProperty()
  size = ndb.IntegerProperty()

  @property
  def creation_epoch(self):
    return self.creation.strftime('%s')
