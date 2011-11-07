# Miro - an RSS based video player application
# Copyright (C) 2005, 2006, 2007, 2008, 2009, 2010, 2011
# Participatory Culture Foundation
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301 USA
#
# In addition, as a special exception, the copyright holders give
# permission to link the code of portions of this program with the OpenSSL
# library.
#
# You must obey the GNU General Public License in all respects for all of
# the code used other than OpenSSL. If you modify file(s) with this
# exception, you may extend this exception to your version of the file(s),
# but you are not obligated to do so. If you do not wish to do so, delete
# this exception statement from your version. If you delete this exception
# statement from all source files in the program, then also delete it here.

"""``miro.metadata`` -- Handle metadata properties for *Items. Generally the
frontend cares about these and the backend doesn't.
"""

import logging
import fileutil
import os.path
import threading
from contextlib import contextmanager

from miro.util import returns_unicode, returns_filename
from miro import coverart
from miro import filetypes
from miro import app
from miro.database import DDBObject
from miro.plat.utils import thread_body

class Source(object):
    """Object with readable metadata properties."""

    def get_iteminfo_metadata(self):
        return dict(
            name = self.get_title(),
            title_tag = self.title_tag,
            description = self.get_description(),
            album = self.album,
            album_artist = self.album_artist,
            artist = self.artist,
            track = self.track,
            album_tracks = self.album_tracks,
            year = self.year,
            genre = self.genre,
            rating = self.rating,
            cover_art = self.cover_art,
            has_drm = self.has_drm,
            show = self.show,
            episode_id = self.episode_id,
            episode_number = self.episode_number,
            season_number = self.season_number,
            kind = self.kind,
        )

    def get_frontend_data(self):
        try:
            data, = ItemFrontendMetadata.info_view(self.id)
        except ValueError:
            logging.debug("no info for %s", self.id)
            return dict(
                name = u"",
                description = u"",
                album = u"",
                artist = u"",
                album_artist = u"",
                track = None,
                year = None,
                genre = u"",
                show = u"",
                episode_id = u"",
                episode_number = None,
                season_number = None,
                kind = None,
            )
        return dict(
            name = info.title,
            description = info.description,
            album = info.album,
            artist = info.artist,
            album_artist = info.album_artist,
            track = info.track,
            year = info.year,
            genre = info.genre,
            show = info.show,
            episode_id = info.episode_id,
            episode_number = info.episode_number,
            season_number = info.season_number,
            kind = info.kind,
        )

    def setup_new(self):
        self.reset_primary_metadata()
        self.calc_composite_metadata()

    def reset_primary_metadata(self):
        self.title = u""
        self.title_tag = None
        self.description = u""
        self.album = None
        self.album_artist = None
        self.artist = None
        self.track = None
        self.album_tracks = None
        self.year = None
        self.genre = None
        self.rating = None
        self.cover_art = None
        self.has_drm = None
        self.file_type = None
        self.show = None
        self.episode_id = None
        self.episode_number = None
        self.season_number = None
        self.kind = None

    def set_primary_metadata(self, data=None):
        """Apply the single-source (frontend) data from a given source"""
        self.reset_primary_metadata()
        self.title = data.title
        self.description = data.description
        self.album = data.album
        self.album_artist = data.album_artist
        self.artist = data.artist
        self.track = data.track
        self.album_tracks = data.album_tracks
        self.year = data.year
        self.genre = data.genre
        self.rating = data.rating
        self.cover_art = data.cover_art
        self.show = data.show
        self.episode_id = data.episode_id
        self.episode_number = data.episode_number
        self.season_number = data.season_number
        self.kind = data.kind
        self.signal_change()

    def calc_composite_metadata(self):
        # set duration
        # set filetype
        # set has_drm
        self.file_type = 'audio'
        self.duration = 100
        self.has_drm = False
        self.signal_change()

    @property
    def media_type_checked(self):
        """This was previously tracked as a real property; it's used by
        ItemInfo. Provided for compatibility with the previous API.
        """
        return self.file_type is not None

    @returns_filename
    def get_thumbnail(self):
        # XXX TODO: probably just make thumbnail a metadata property
        info = self.get_iteminfo_metadata()
        if 'cover_art' in info:
            path = info['cover_art']
            return resources.path(fileutil.expand_filename(path))
#        elif info['screenshot']:
#            path = info['screenshot']
#            return resources.path(fileutil.expand_filename(path))

    @returns_unicode
    def get_title(self):
        return self.title

def metadata_setter(attribute, type_=None):
    def set_metadata(self, value, _bulk=False):
        if value is not None and type_ is not None:
            # None is always an acceptable value for metadata properties
            value = type_(value)
        if not _bulk:
            self.confirm_db_thread()
        setattr(self, attribute, value)
        if not _bulk:
            self.signal_change()
            self.write_back((attribute,))
    return set_metadata

class Store(Source):
    """Object with read/write metadata properties."""

    set_title = metadata_setter('title', unicode)
    set_title_tag = metadata_setter('title_tag', unicode)
    set_description = metadata_setter('description', unicode)
    set_album = metadata_setter('album', unicode)
    set_album_artist = metadata_setter('album_artist', unicode)
    set_artist = metadata_setter('artist', unicode)
    set_track = metadata_setter('track', int)
    set_album_tracks = metadata_setter('album_tracks')
    set_year = metadata_setter('year', int)
    set_genre = metadata_setter('genre', unicode)
    set_rating = metadata_setter('rating', int)
    set_file_type = metadata_setter('file_type', unicode)
    set_has_drm = metadata_setter('has_drm', bool)
    set_show = metadata_setter('show', unicode)
    set_episode_id = metadata_setter('episode_id', unicode)
    set_episode_number = metadata_setter('episode_number', int)
    set_season_number = metadata_setter('season_number', int)
    set_kind = metadata_setter('kind', unicode)

    def set_cover_art(self, new_file, _bulk=False):
        """Set new cover art. Deletes any old cover art.

        Creates a copy of the image in our cover art directory.
        """
        if not _bulk:
            self.confirm_db_thread()
        if new_file:
            new_cover = coverart.Image.from_file(new_file, self.get_filename())
        self.delete_cover_art()
        if new_file:
            self.cover_art = new_cover
        if not _bulk:
            self.signal_change()
            self.write_back(('cover_art',))

    def delete_cover_art(self):
        """Delete the cover art file and unset cover_art."""
        try:
            fileutil.remove(self.cover_art)
        except (OSError, TypeError):
            pass
        self.cover_art = None

    def setup_new(self):
        Source.setup_new(self)
        self._deferred_update = {}

    def set_metadata_from_iteminfo(self, changes, _deferrable=True):
        self.confirm_db_thread()
        for field, value in changes.iteritems():
            Store.ITEM_INFO_TO_ITEM[field](self, value, _bulk=True)
        self.signal_change()
        self.write_back(changes.keys())

    def write_back(self, _changed):
        """Write back metadata changes to the original source, if supported. If
        this method fails because the item is playing, it should add the changed
        fields to _deferred_update.
        """
        # not implemented yet
        #logging.debug("%s can't write back changes", self.__class__.__name__)

    def set_is_playing(self, playing):
        """Hook so that we can defer updating an item's data if we can't change
        it while it's playing.
        """
        if not playing and self._deferred_update:
            self.set_metadata_from_iteminfo(self._deferred_update, _deferrable=False)
            self._deferred_update = {}
        super(Store, self).set_is_playing(playing)

    ITEM_INFO_TO_ITEM = dict(
        name = set_title,
        title_tag = set_title_tag,
        description = set_description,
        album = set_album,
        album_artist = set_album_artist,
        artist = set_artist,
        track = set_track,
        album_tracks = set_album_tracks,
        year = set_year,
        genre = set_genre,
        rating = set_rating,
        file_type = set_file_type,
        cover_art = set_cover_art,
        has_drm = set_has_drm,
        show = set_show,
        episode_id = set_episode_id,
        episode_number = set_episode_number,
        season_number = set_season_number,
        kind = set_kind,
    )

class ItemMetadataStatus(DDBObject):
    """State of metadata of one Item.

    An item will have no ItemMetadataStatus if it is not queued and has not been
    examined either (e.g. if it doesn't have an associated file (yet)). An
    ItemMetadataStatus should be created when the item becomes examinable;
    creating the Status object puts the item into the appropriate extractor
    queues.
    """
    def setup_new(self, item_id):
        self.item_id = item_id
        # cross-extractor info: ``what info would be useful at this point?''
        self.best_successful_extractor_priority = None
        self.drm_checked = False
        # per-extractor status: ``what have we already tried?''
        self.echonest_examined = False
        self.mutagen_examined = False
        self.mdp_examined = False

class Extractor(object):
    """Base of all metadata-finders"""
    NAME = NotImplemented
    PRIORITY = NotImplemented
    IDENTIFIES_DRM = NotImplemented

    @classmethod
    def queue_view(cls):
        drm_clause = " OR (NOT drm_checked)" if cls.IDENTIFIES_DRM else ""
        return ItemMetadataStatus.make_view("(NOT %s_examined) AND "
                "((NOT best_successful_extractor_priority > ?) %s)" %
                (cls.NAME, drm_clause),
                (cls.PRIORITY,))

    def process_item(self, item_):
        raise NotImplementedError

    def mark_processed(self, item_, metadata_succcess):
        status, = ItemMetadataStatus.make_view('item_id = ?', (item_.id,))
        setattr(status, '%s_examined' % (self.__class__.NAME,), True)
        if self.__class__.IDENTIFIES_DRM:
            status.drm_checked = True
        if metadata_succcess and status.best_successful_extractor_priority:
            new_best = max(status.best_successful_extractor_priority,
                    self.__class__.PRIORITY)
            status.best_successful_extractor_priority = new_best

class ItemMetadata(DDBObject):
    """Metadata describing one item, from one source

    Backend-ish stuff that tends to be combined between different
    providers
    """
    def setup_new(self, item_id, extractor_priority, extractor_name):
        # identify the block
        self.item_id = item_id
        self.extractor_priority = extractor_priority
        self.extractor_name = extractor_name
        # the data
        self.duration = None
        self.has_drm = None
        self.file_type = None

class ItemFrontendMetadata(DDBObject):
    """Metadata describing one item, from one source

    Frontend-ish stuff that is not combined with data from other sources
    """
    def setup_new(self, item_id, extractor_priority, extractor_id):
        # identify the block
        self.item_id = item_id
        self.extractor_priority = extractor_priority
        self.extractor_name = extractor_name
        # the data
        self.title = None
        self.description = None
        self.album = None
        self.artist = None
        self.album_artist = None
        self.track = None
        self.year = None
        self.genre = None
        self.show = None
        self.episode_id = None
        self.episode_number = None
        self.season_number = None
        self.kind = None

    @classmethod
    def info_view(cls, item_id):
        """Return a view that always corresponds to the highest-ranking
        available data for an item.
        """
        return cls.make_view(
                "item_id=?", values=(item_id,),
                order_by='extractor_priority', limit='1')

class MetadataManager(object):
    def __init__(self):
        self.thread = None
        self.should_shutdown = False
        self.extractors = []

    def register_provider(self, provider):
        self.extractors = sorted(self.extractors + [provider],
                lambda x: -x.PRIORITY)

    def get_provider(self, name):
        raise NotImplementedError

    def process_downloaded_item(self, item_id):
        """Queue the item for extraction by all applicable extractors."""
        if ItemMetadataStatus.make_view("item_id=?", (item_id,)):
            # item has already been in the queue before
            return
        # begin tracking the item's metadata status (this enqueues the item)
        ItemMetadataStatus(item_id)
        # wake up the processor, if it was sleeping
        self.start_processing_thread()

    def start_processing_thread(self):
        """Launch the processing thread."""
        if self.thread is not None:
            # nothing to do
            return
        self.should_shutdown = False
        self.thread = threading.Thread(name='Metadata Thread',
                                       target=thread_body,
                                       args=[self._thread_loop])
        self.thread.setDaemon(True)
        self.thread.start()

    def stop_processing_thread(self):
        """The processing thread, if running, will exit when it finishes the
        current item.
        """
        self.should_shutdown = True
        self.thread = None

    @contextmanager
    def looping(self):
        """Simple contextmanager to ensure that whatever happens in a
        thread_loop, we signal begin/end properly.
        """
        self.emit('begin-loop')
        try:
            yield
        finally:
            self.emit('end-loop')

    def _thread_loop(self):
        """Examine items with any appropriate extractors, until there are none
        left or self.should_shutdown is set.
        """
        for extractor in self.extractors:
            for item_ in extractor.__class__.queue_view():
                if self.should_shutdown:
                    self.thread = None
                    return
                with self.looping:
                    metadata_succcess = extractor.process_item(item_)
                    extractor.mark_processed(item_, metadata_succcess)

app.metadata_manager = MetadataManager()
