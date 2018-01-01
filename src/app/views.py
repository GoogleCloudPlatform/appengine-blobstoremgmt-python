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
Views for blob-management tool.
"""
import datetime
import logging
import os
import json

import jinja2
from google.appengine.ext import blobstore
from google.appengine.ext import ndb
from google.appengine.ext.webapp import blobstore_handlers
import webapp2

from app import models


PAGE_SIZE = 20
VALID_SORT_COLUMNS = set(['filename', 'content_type', 'size', 'creation'])
VALID_FILTERS = VALID_SORT_COLUMNS
VALID_SORT_DIRECTIONS = set(['asc', 'desc'])
VALID_SIZE_OP = set(['le', 'ge'])
SIZE_OP_MAP = {
  'le': ('<=', 'asc'),
  'ge': ('>=', 'desc'),
}
VALID_SIZE_UNIT = set(['B', 'KB', 'MB', 'GB'])
SIZE_UNIT_MULTIPLIER = {
  'B': 1,
  'KB': 1024,
  'MB': 1024*1024,
  'GB': 1024*1024*1024,
}
VALID_CREATION_OP = set(['day', 'week', 'month', 'range'])
CREATION_OP_DAYS = {
  'day': 1,
  'week': 7,
  'month': 31,
}


JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(
      os.path.join(os.path.dirname(__file__), '..', 'templates')
    ),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True,
)


class UserView(webapp2.RequestHandler):
  """A user-facing view."""
  def render_response(self, template_name, **context):
    self.response.headers['Content-Type'] = 'text/html'
    template = JINJA_ENVIRONMENT.get_template(template_name)
    self.response.write(template.render(**context))


class JsonHandler(webapp2.RequestHandler):
  """A JSON-emitting handler."""
  def emit_json(self, data):
    self.response.headers['Content-Type'] = 'application/json'
    self.response.write(json.dumps(data))


class Browse(UserView):
  """The main page containing the JS driver."""

  def get(self):

    args = BrowseArgs(self.request.GET)
    try:
      args.validate()
    except ValueError as e:
      self.response.status = 400
      logging.info(e.message)
      self.response.write(e.message)
      return

    query = args.build_gql_query()
    blobs, cursor, more = ndb.gql(query).fetch_page(
        page_size=PAGE_SIZE,
        start_cursor=ndb.Cursor(urlsafe=self.request.get('start')))
    if cursor:
      cursor = cursor.urlsafe()
    context = {
      'blobs': blobs,
      'cursor': cursor,
      'more': more,
    }
    if args.has_filter:
      context['filter'] = args.filter
      if args.has_filename_prefix:
        context['filename_prefix'] = args.filename_prefix
      if args.has_content_type:
        context['content_type'] = args.content_type
      if args.has_size_op:
        context['size_op'] = args.size_op
      if args.has_size_unit:
        context['size_unit'] = args.size_unit
      if args.has_size:
        context['size'] = args.size
      if args.has_creation_op:
        context['creation_op'] = args.creation_op
      if args.has_creation_start:
        context['creation_start'] = args.creation_start
      if args.has_creation_end:
        context['creation_end'] = args.creation_end
    else:
      opp_sort_dir = args.sort_dir == 'asc' and 'desc' or 'asc'
      context['sort_col'] = args.sort_col
      context['sort_dir'] = args.sort_dir
      context['opp_sort_dir'] = opp_sort_dir
    self.render_response('index.html', **context)


class Upload(UserView, blobstore_handlers.BlobstoreUploadHandler):
  """Form to upload a blob, e.g., for testing."""
  def get(self):
    MESSAGES = {
      'SUCCESS': ('success', 'Blob uploaded successfully'),
      'FILE_REQUIRED': ('danger', 'You must specify a file.'),
    }
    message_style, message = MESSAGES.get(self.request.GET.get('message'),
                                          (None, None))
    upload_url = blobstore.create_upload_url('/upload')
    context = {
        'upload_url': upload_url,
        'message': message,
        'message_style': message_style,
    }
    self.render_response('upload.html', **context)

  def post(self):
    uploads = self.get_uploads()
    message = 'SUCCESS'
    if len(uploads) == 0:
      message = 'FILE_REQUIRED'
    self.redirect('/upload?message=%s' % message)


class Serve(blobstore_handlers.BlobstoreDownloadHandler):
  """Serves a blob."""
  def get(self):
    key = self.request.GET['key']
    blobkey = blobstore.BlobKey(ndb.Key(urlsafe=key).id())
    self.send_blob(blobkey)


class Delete(JsonHandler):
  """Deletes a set of blobs."""
  def post(self):
    keys = self.request.POST['keys']
    if not keys:
      return
    keys = [k.strip() for k in keys.split(',')]
    blobstore.delete(keys)
    self.emit_json({})


class BrowseArgs(object):
  """Parses and validates arguments for the browse page."""
  def __init__(self, args):
    self.args = args or {}

  @property
  def filter(self):
    if not self.has_filter:
      raise AttributeError('filter')
    return self.args['filter'].strip()

  @property
  def has_filter(self):
    return 'filter' in self.args

  @property
  def sort_col(self):
    return self.args.get('sort_col', 'filename').strip()

  @property
  def sort_dir(self):
    return self.args.get('sort_dir', 'asc').strip()

  @property
  def size_op(self):
    if not self.has_size_op:
      raise AttributeError('size_op')
    return self.args['size_op'].strip()

  @property
  def has_size_op(self):
    return 'size_op' in self.args

  @property
  def size_unit(self):
    if not self.has_size_unit:
      raise AttributeError('size_unit')
    return self.args['size_unit'].strip()

  @property
  def has_size_unit(self):
    return 'size_unit' in self.args

  @property
  def size(self):
    if not self.has_size:
      raise AttributeError('size')
    return float(self.args['size'].strip())

  @property
  def has_size(self):
    return 'size' in self.args

  @property
  def creation_op(self):
    if not self.has_creation_op:
      raise AttributeError('creation_op')
    return self.args['creation_op'].strip()

  @property
  def has_creation_op(self):
    return 'creation_op' in self.args

  @property
  def creation_start(self):
    if not self.has_creation_start:
      raise AttributeError('creation_start')
    return int(self.args['creation_start'].strip())

  @property
  def has_creation_start(self):
    return 'creation_start' in self.args

  @property
  def creation_end(self):
    if not self.has_creation_end:
      raise AttributeError('creation_end')
    return int(self.args['creation_end'].strip())

  @property
  def has_creation_end(self):
    return 'creation_end' in self.args

  @property
  def filename_prefix(self):
    if not self.has_filename_prefix:
      raise AttributeError('filename_prefix')
    return self.args['filename_prefix'].strip()

  @property
  def has_filename_prefix(self):
    return 'filename_prefix' in self.args

  @property
  def content_type(self):
    if not self.has_content_type:
      raise AttributeError('content_type')
    return self.args['content_type'].strip()

  @property
  def has_content_type(self):
    return 'content_type' in self.args

  def validate(self):
    if self.sort_col not in VALID_SORT_COLUMNS:
      raise ValueError('sort_col must be in %s.' % VALID_SORT_COLUMNS)

    if self.sort_dir not in VALID_SORT_DIRECTIONS:
      raise ValueError('sort_dir must be in %s.' % VALID_SORT_DIRECTIONS)

    if self.has_size_op and self.size_op not in VALID_SIZE_OP:
      raise ValueError('size_op must be in %s.' % VALID_SIZE_OP)

    if self.has_size_unit and self.size_unit not in VALID_SIZE_UNIT:
      raise ValueError('size_unit must be in %s.' % VALID_SIZE_UNIT)

    if self.has_size:
      try:
        size = self.size
      except ValueError:
        raise ValueError('size must be a float.')
      if size < 0:
        raise ValueError('size must be non-negative.')

    if self.has_creation_op and self.creation_op not in VALID_CREATION_OP:
      raise ValueError('creation_op must be in %s.' % VALID_CREATION_OP)

    if self.has_creation_start:
      try:
        creation_start = self.creation_start
      except ValueError:
        raise ValueError('creation_start must be an integer.')
      if creation_start < 0:
        raise ValueError('creation_start must be non-negative.')

    if self.has_creation_end:
      try:
        creation_end = self.creation_end
      except ValueError:
        raise ValueError('creation_end must be an integer.')
      if creation_end < 0:
        raise ValueError('creation_end must be non-negative.')

    if self.has_filter:

      if self.filter not in VALID_FILTERS:
        raise ValueError('filter must be in %s.' % VALID_FILTERS)

      if self.filter == 'filename':
        if not self.has_filename_prefix:
          raise ValueError('filename_prefix is required.')

      elif self.filter == 'content_type':
        if not self.has_content_type:
          raise ValueError('content_type is required.')

      elif self.filter == 'size':
        if not self.has_size or not self.has_size_op or not self.has_size_unit:
          raise ValueError('size, size_op, size_unit are required.')

      elif self.filter == 'creation':
        if not self.has_creation_op:
          raise ValueError('creation_op is required')
        if self.creation_op == 'range':
          if not self.has_creation_start and not self.has_creation_end:
            raise ValueError('At least one of creation_start or creation_end '
                             'are required.')

  def _make_gql_dt(self, dt):
    return 'DATETIME(%d, %d, %d, %d, %d, %d)' % (
        dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second)

  def _make_gql_str(self, st, tilde=False):
    return "'%s%s'" % (st.replace("'", "''"), tilde and '~' or '')

  def build_gql_query(self):
    """Builds a GQL (NDB) query string for the args."""
    qstr = 'SELECT * FROM __BlobInfo__ '

    if not self.has_filter:
      qstr += 'ORDER BY %s %s' % (self.sort_col, self.sort_dir)
      return qstr

    if self.filter == 'filename':
      qstr += 'WHERE filename >= %s AND filename < %s ORDER BY filename' % (
          self._make_gql_str(self.filename_prefix),
          self._make_gql_str(self.filename_prefix, tilde=True))
      return qstr

    if self.filter == 'content_type':
      qstr += 'WHERE content_type = %s ORDER BY content_type' % (
          self._make_gql_str(self.content_type))
      return qstr

    if self.filter == 'size':
      op, direction = SIZE_OP_MAP[self.size_op]
      size = self.size * SIZE_UNIT_MULTIPLIER[self.size_unit]
      qstr += 'WHERE size %s %d ORDER BY size %s' % (op, size, direction)
      return qstr

    if self.filter == 'creation':

      if self.creation_op in ['day', 'week', 'month']:
        days = CREATION_OP_DAYS[self.creation_op]
        start = datetime.datetime.utcnow() -  datetime.timedelta(days=days)
        qstr += 'WHERE creation >= %s ORDER BY creation' % (
            self._make_gql_dt(start))
        return qstr

      if self.creation_op == 'range':
        qstr += 'WHERE '
        if self.has_creation_start and self.creation_start:
          start = datetime.datetime.fromtimestamp(self.creation_start)
          qstr += 'creation >= %s ' % self._make_gql_dt(start)
          if self.has_creation_end and self.creation_end:
            qstr += 'AND '
        if self.has_creation_end and self.creation_end:
          end = datetime.datetime.fromtimestamp(self.creation_end)
          qstr += 'creation <= %s ' % self._make_gql_dt(end)
        qstr += 'ORDER BY creation'
        return qstr

      raise ValueError('Unknown creation_op "%s".' % self.creation_op)

    raise ValueError('Unknown filter "%s".' % self.filter)
