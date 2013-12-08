#!/usr/bin/env python
# encoding: utf-8
"""
memeMatcher.py

Created by Benjamin Fields on 2013-12-07.
Copyright (c) 2013 . All rights reserved.
"""

import sys
import os, os.path
import unittest
import tempfile
import json
import random
import md5

import sqlite3
import requests
import pyechonest.track

import pygn

from itertools import izip_longest
from bs4 import BeautifulSoup

GRACENOTE_KEY = os.environ['GRACENOTE_KEY']


def database_connection():
    if not os.path.isfile(base_path() + '/db/app.db'):
        raise "YOUR DATABASE DOESNT EXIST FOOL, RUN db/migrate.sh"

    return sqlite3.connect(base_path() + '/db/app.db')

def grouper(n, iterable, fillvalue=None):
    "grouper(3, 'ABCDEFG', 'x') --> ABC DEF Gxx"
    args = [iter(iterable)] * n
    return izip_longest(fillvalue=fillvalue, *args)

def base_path():
    return os.path.dirname(os.path.realpath(__file__))

def rep_genius_parser(artist='', title=''):
  rg_base = "http://rapgenius.com"
  rg_search = rg_base+"/search?hide_unexplained_songs=false&q={terms}"
  #EN or something has produced artist and track name
  print rg_search.format(terms=artist+u'+'+title)
  r = requests.get(rg_search.format(terms=artist+u'+'+title))
  print r
  soup = BeautifulSoup(r.content)
  track_link = soup.select(".song_list li a")[0].get('href')
  r = requests.get(rg_base+track_link)
  print r
  soup = BeautifulSoup(r.content)
  raw_lyrics = soup.select("div.lyrics p")[0].get_text()
  lyrics = []
  phrase = []
  for line in raw_lyrics.split('\n'):
    if len(line) == 0 and len(phrase) > 0:
      lyrics.append(phrase)
      phrase = []
      continue
    if len(line) > 0 and line[0] != '[':
      #don't add functional phrase labels
      phrase.append(line)
  return lyrics

class memeMatcher:
  def __init__(self, filepath):
    self.filepath = filepath
    self.filename = os.path.split(filepath)[-1]
    self._run()

  def _run(self):
    sync_method = 'linear_seq'
    self.status = 'processing file'
    self._fetch_EN_analysis()
    try:
      #cache grab
      self.deserialize_timing(sync_method)
    except TypeError:
      #otherwise make a new one
      self.status = 'gathering lyrics'
      self._fetch_lyrics()
      self.status = 'gathering cover art'
      self._fetch_cover_art()
      self.status = 'aligning to memes'
      self.select_and_align_memes()
      self.status = 'done'
      self.serialize_timing(sync_method, self.timings)

  def _fetch_EN_analysis(self):
    self.track = pyechonest.track.track_from_filename(self.filepath)
    self.track.get_analysis()
    self.artist = self.track.artist
    self.title = self.track.title

  def _fetch_lyrics(self):
    #mild cleaning
    artist = self.artist
    title = self.title.split('/')[0]
    if " feat" in title:
      title = " ".join(title.split(" feat"))
    self.lyrics = rep_genius_parser(artist, title)

  def _fetch_cover_art(self):
    clientID = GRACENOTE_KEY
    userID = pygn.register(clientID)
    metadata = pygn.search(clientID=clientID, userID=userID, artist=self.artist, track=self.title.split('/')[0])
    try:
      artist_pic = os.path.join(base_path(), 'tmp', md5.md5(metadata['album_art_url']).hexdigest())
      if not os.path.exists(artist_pic):
        r = requests.get(metadata['album_art_url'])
        with open(artist_pic, 'wb') as wh:
          wh.write(r.content) 
      self.album_art = '/audio_files/'+os.path.split(artist_pic)[1]
    except KeyError:
      print 'for', self.artist, ':', self.track, "gracenote doesn't have any album art"
      self.album_art = None
  
  def deserialize_timing(self, sync_method):
      conn = database_connection()
      cur = conn.cursor()
      try:
        self.song_id
      except AttributeError:
        cur.execute("SELECT id from upload WHERE file_name=?", (self.filename, ))
        self.song_id = cur.fetchone()[0]
      cur.execute("SELECT json from timings WHERE id=? AND sync_method=?", (self.song_id, sync_method,))
      return json.loads(cur.fetchone()[0])

  def serialize_timing(self, sync_method, timing):
      conn = database_connection()
      cur = conn.cursor()
      try:
        self.song_id
      except AttributeError:
        cur.execute("SELECT id from upload WHERE file_name=?", (self.filename, ))
        self.song_id = cur.fetchone()[0]
      cur.execute("INSERT INTO timings (id, sync_method, json) VALUES (?, ?, ?)", (self.song_id, sync_method, json.dumps(timing)))
      conn.commit()
  
  def select_and_align_memes(self, method='linear_seq', intro_num_sections = 1, **kwargs):
    with open(os.path.join(base_path(),'images.json')) as rh:
      memes = json.loads(rh.read())['memes']
      if self.album_art:
        self.timings = [{"image_url":self.album_art,
                          "transition_after": int(sum([sect[u'duration'] for sect in self.track.sections[:intro_num_sections]])*1000),
                          "top_text": '',
                          "bottom_text": '',
                        }] 
        start_section = intro_num_sections
      else:
        self.timings = []
        start_section = 0
      if method == 'random_shuffle':
        self.random_shuffle_memes(memes, start_section)
      elif method == 'maximum_spread':
        self.maximum_spread(memes, start_section)
      elif method == 'linear_seq':
        self.linear_sequence_memes(memes, start_section, **kwargs)
      else:
        raise ValueError('unknown alignment method')
      print self.timings
  
  def linear_sequence_memes(self, memes, start_section, first_block=4, second_block=4):
    shuffled_img = random.sample(memes.keys(), len(memes.keys()))
    flat_lyrics = []
    for lyric_block in self.lyrics:
      if len(lyric_block) % 2 == 1:
        if len(lyric_block) > 4:
          lyric_block.pop(-3)
        else:
          lyric_block.pop(-1)
      flat_lyrics += lyric_block
    bars_left = [bar for bar in self.track.bars if (bar[u'start']>=self.track.sections[start_section][u'start'])]
    for some_bars in grouper(first_block+second_block, bars_left):
      for block_length in (first_block, second_block):
        key = shuffled_img.pop()
        img = memes[key]
        img_path = img["source_image"]
        if len(shuffled_img)==0:
          shuffled_img = random.sample(memes.keys(), len(memes.keys()))
        if len(flat_lyrics) < 2:
          flat_lyrics = reduce(lambda x,y:x+y, self.lyrics)
        top_line = flat_lyrics.pop(0)
        bottom_line = flat_lyrics.pop(0)
        print "first:", first_block, "second:", second_block, 'current:', block_length, "left:", len(some_bars)
        duration = int(sum([bar[u'duration'] for bar in some_bars[:block_length] if bar != None])*1000)
        some_bars = some_bars[block_length:] #trim the bars that were used
        self.timings.append({"image_url":img_path,
                             "transition_after": duration,
                             "top_text": top_line,
                             "bottom_text": bottom_line,
                            })
  
  def random_shuffle_memes(self, memes, start_section):
    shuffled_img = random.sample(memes.keys(), len(memes.keys()))
    # print shuffled_img
    shuffled_phrases = random.sample(self.lyrics, len(self.lyrics))
    for section in self.track.sections[start_section:]:
      #draw cards
      key = shuffled_img.pop()
      img = memes[key]
      # print img
      img_path = img["source_image"]
      this_phrase = shuffled_phrases.pop()
      while len(this_phrase) < 2:
        if len(shuffled_phrases)==0:
          this_phrase=['','']
        else:
          this_phrase = shuffled_phrases.pop()
      #reshuffle the decks, if needed
      if len(shuffled_img)==0:
        shuffled_img = random.sample(memes.keys(), len(memes.keys()))
      if len(shuffled_phrases)==0:
        shuffled_phrases = random.sample(self.lyrics, len(self.lyrics))
      lyric_idx = random.sample(range(len(this_phrase)/2),1)[0]*2
      print img_path
      self.timings.append({"image_url":img_path,
                           "transition_after": int(section['duration']*1000),
                           "top_text": this_phrase[lyric_idx],
                           "bottom_text": this_phrase[lyric_idx+1],
                          })
  
  def maximum_spread(self, memes, start_section):
    shuffled_img = random.sample(memes.keys(), len(memes.keys()))
    sections_per_phrase = len(self.track.sections[start_section:-1])/len(self.lyrics)
    current_section=start_section
    for lyric_block in self.lyrics:
      bars = []
      for section in self.track.sections[current_section:current_section+sections_per_phrase]:
        bars += [bar for bar in self.track.bars \
                  if (bar[u'start']>=section[u'start']) and (bar[u'start']+bar[u'duration'])<=(section[u'start']+section[u'duration'])]
      bars_per_linepair = len(bars)/(len(lyric_block)/2)
      if bars_per_linepair <= 4:
        bars_per_linepair = 4
      else:
        bars_per_linepair = 8
      # bars_per_linepair = 4
      for some_bars in grouper(bars_per_linepair,bars):
        if some_bars.count(None)>0 or len(lyric_block)<2:
          #combine with the last one and force last linepair of the phrase
          self.timings[-1]["transition_after"] += int(sum([bar[u'duration'] for bar in bars if bar != None])*1000)
          if len(lyric_block) > 1:
            self.timings[-1]['bottom_text'] = lyric_block.pop(-1)
            self.timings[-1]['top_text'] = lyric_block.pop(-1)
        else:
          key = shuffled_img.pop()
          img = memes[key]
          img_path = img["source_image"]
          if len(shuffled_img)==0:
            shuffled_img = random.sample(memes.keys(), len(memes.keys()))
          top = lyric_block.pop(0)
          bottom = lyric_block.pop(0)
          self.timings.append({"image_url":img_path,
                               "transition_after": int(sum([bar[u'duration'] for bar in some_bars])*1000),
                               "top_text": top,
                               "bottom_text": bottom,
                              })
    current_section += sections_per_phrase
    #last section gets the album art again
    self.timings.append({"image_url":self.album_art,
                        "transition_after": int(self.track.sections[-1]['duration']*1000),
                        "top_text": '',
                        "bottom_text": '',
                        })
    
class memeMatcherTests(unittest.TestCase):
  def setUp(self):
    self.tester = memeMatcher('')


if __name__ == '__main__':
  unittest.main()
