# -*- coding: utf-8 -*-
# Author: Dylan Jones
# Date:   2023-02-01

import os
import pytest
from pytest import mark
import tempfile
from sqlalchemy.orm.query import Query
from pyrekordbox import Rekordbox6Database, open_rekordbox_database
from pyrekordbox.db6 import tables

TEST_ROOT = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".testdata")
UNLOCKED = os.path.join(TEST_ROOT, "rekordbox 6", "master_unlocked.db")

DB = Rekordbox6Database(UNLOCKED, unlock=False)


def test_open_rekordbox_database():
    con = open_rekordbox_database(UNLOCKED, unlock=False)
    con.execute("SELECT name FROM sqlite_master WHERE type='table';")


def test_close_open():
    db = Rekordbox6Database(UNLOCKED, unlock=False)
    db.close()
    db.open()
    _ = db.get_content()[0]  # Try to query the database


@mark.parametrize(
    "name,cls",
    [
        ("get_active_censor", tables.DjmdActiveCensor),
        ("get_album", tables.DjmdAlbum),
        ("get_artist", tables.DjmdArtist),
        ("get_category", tables.DjmdCategory),
        ("get_color", tables.DjmdColor),
        ("get_content", tables.DjmdContent),
        ("get_cue", tables.DjmdCue),
        ("get_device", tables.DjmdDevice),
        ("get_genre", tables.DjmdGenre),
        ("get_history", tables.DjmdHistory),
        ("get_hot_cue_banklist", tables.DjmdHotCueBanklist),
        ("get_key", tables.DjmdKey),
        ("get_label", tables.DjmdLabel),
        ("get_menu_items", tables.DjmdMenuItems),
        ("get_mixer_param", tables.DjmdMixerParam),
        ("get_my_tag", tables.DjmdMyTag),
        ("get_playlist", tables.DjmdPlaylist),
        ("get_property", tables.DjmdProperty),
        ("get_related_tracks", tables.DjmdRelatedTracks),
        ("get_sampler", tables.DjmdSampler),
        ("get_sort", tables.DjmdSort),
        ("get_agent_registry", tables.AgentRegistry),
        ("get_cloud_agent_registry", tables.CloudAgentRegistry),
        ("get_content_active_censor", tables.ContentActiveCensor),
        ("get_content_cue", tables.ContentCue),
        ("get_content_file", tables.ContentFile),
        ("get_hot_cue_banklist_cue", tables.HotCueBanklistCue),
        ("get_image_file", tables.ImageFile),
        ("get_setting_file", tables.SettingFile),
        ("get_uuid_map", tables.UuidIDMap),
    ],
)
def test_getter(name, cls):
    getter = getattr(DB, name)
    # Test return is query
    query = getter()
    assert isinstance(query, Query)
    assert query.column_descriptions[0]["type"] == cls

    # Test type of query result is the right table class
    res = query.first()
    assert res is None or isinstance(res, cls)


@mark.parametrize(
    "name,cls",
    [
        ("get_active_censor", tables.DjmdActiveCensor),
        ("get_album", tables.DjmdAlbum),
        ("get_artist", tables.DjmdArtist),
        ("get_category", tables.DjmdCategory),
        ("get_color", tables.DjmdColor),
        ("get_content", tables.DjmdContent),
        ("get_cue", tables.DjmdCue),
        ("get_device", tables.DjmdDevice),
        ("get_genre", tables.DjmdGenre),
        ("get_history", tables.DjmdHistory),
        ("get_hot_cue_banklist", tables.DjmdHotCueBanklist),
        ("get_key", tables.DjmdKey),
        ("get_label", tables.DjmdLabel),
        ("get_menu_items", tables.DjmdMenuItems),
        ("get_mixer_param", tables.DjmdMixerParam),
        ("get_my_tag", tables.DjmdMyTag),
        ("get_playlist", tables.DjmdPlaylist),
        # ("get_property", tables.DjmdProperty),
        ("get_related_tracks", tables.DjmdRelatedTracks),
        ("get_sampler", tables.DjmdSampler),
        ("get_sort", tables.DjmdSort),
        # ("get_agent_registry", tables.AgentRegistry),
        ("get_cloud_agent_registry", tables.CloudAgentRegistry),
        ("get_content_active_censor", tables.ContentActiveCensor),
        ("get_content_cue", tables.ContentCue),
        ("get_content_file", tables.ContentFile),
        ("get_hot_cue_banklist_cue", tables.HotCueBanklistCue),
        ("get_image_file", tables.ImageFile),
        ("get_setting_file", tables.SettingFile),
        ("get_uuid_map", tables.UuidIDMap),
    ],
)
def test_getter_by_id(name, cls):
    # Get method from class
    getter = getattr(DB, name)

    # Try to get a valid ID
    item = getter().first()
    if item is None:
        return
    id_ = item.ID

    # Test type of result is a table class, not the query
    res = getter(ID=id_)
    assert res is None or isinstance(res, cls)


@mark.parametrize(
    "parent_name,cls",
    [
        ("get_playlist", tables.DjmdSongHistory),
        ("get_hot_cue_banklist", tables.DjmdSongHotCueBanklist),
        ("get_my_tag", tables.DjmdSongMyTag),
        ("get_playlist", tables.DjmdSongPlaylist),
        ("get_related_tracks", tables.DjmdSongPlaylist),
        ("get_sampler", tables.DjmdSongPlaylist),
    ],
)
def test_songs_getters(parent_name, cls):
    # Get list (containing songs) getter
    getter = getattr(DB, parent_name)
    # Try to get a valid list ID
    query = getter()
    if not query.count():
        return  # No data to check...

    item = query.first()
    id_ = item.ID

    # Get list songs getter
    getter = getattr(DB, f"{parent_name}_songs")
    # Get song items
    query = getter(id_)
    if not query.count():
        return  # No data to check...

    assert isinstance(query.first(), cls)


@mark.parametrize(
    "search,ids",
    [
        ("Demo Track 1", [178162577]),  # Title
        ("Demo Track 2", [66382436]),  # Title
        ("Loopmasters", [178162577, 66382436]),  # Label/Artist Name
        ("Noise", [24401986]),  # lowercase
        ("NOIS", [24401986]),  # incomplete
    ],
)
def test_search_content(search, ids):
    results = DB.search_content(search)
    for id_, res in zip(ids, results):
        assert int(res.ID) == id_


def test_increment_local_usn():
    db = Rekordbox6Database(UNLOCKED, unlock=False)

    old = db.get_local_usn()
    db.increment_local_usn()
    assert db.get_local_usn() == old + 1

    db.increment_local_usn(1)
    assert db.get_local_usn() == old + 2

    db.increment_local_usn(2)
    assert db.get_local_usn() == old + 4

    with pytest.raises(ValueError):
        db.increment_local_usn(0)

    with pytest.raises(ValueError):
        db.increment_local_usn(-1)


def test_autoincrement_local_usn():
    tid1 = 178162577
    tid2 = 66382436
    tid3 = 181094952
    pid = 2602250856
    db = Rekordbox6Database(UNLOCKED, unlock=False)
    old_usn = db.get_local_usn()  # store USN before changes
    track1 = db.get_content(ID=tid1)
    track2 = db.get_content(ID=tid2)
    track3 = db.get_content(ID=tid3)
    playlist = db.get_playlist(ID=pid)
    with db.session.no_autoflush:
        # Change one field in first track (+1)
        track1.Title = "New title 1"
        # Change two fields in second track (+2)
        track2.Title = "New title 2"
        track2.BPM = 12900
        # Delete row from table )+1)
        db.delete(track3)
        # Change name of playlist (+1)
        playlist.Name = "New name"

        # Auto-increment USN
        new_usn = db.autoincrement_usn()

    # Check local Rekordbox USN and instance USN's
    assert new_usn == old_usn + 5
    assert track1.rb_local_usn == old_usn + 1
    assert track2.rb_local_usn == old_usn + 3
    # USN of deleted rows obviously don't get updated
    assert playlist.rb_local_usn == new_usn


def test_get_anlz_paths():
    db = Rekordbox6Database(UNLOCKED, unlock=False)
    content = db.get_content().first()

    anlz_dir = str(db.get_anlz_dir(content)).replace("\\", "/")
    expected = r"share/PIONEER/USBANLZ/735/e8b81-e69b-41ad-80f8-9c0d7613b96d"
    assert anlz_dir.endswith(expected)


def test_to_json():
    # Check if saving to json works

    tmp = tempfile.NamedTemporaryFile(delete=False)
    try:
        DB.to_json(tmp.name)
    finally:
        tmp.close()
        os.remove(tmp.name)
