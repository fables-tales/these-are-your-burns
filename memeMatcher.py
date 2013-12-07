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
import requests
import pyechonest.track
import pygn

from bs4 import BeautifulSoup

GRACENOTE_KEY = os.environ['GRACENOTE_KEY']

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
    self._run()

  def _run(self):
    self.status = 'processing file'
    self._fetch_EN_analysis()
    self.status = 'gathering lyrics'
    self._fetch_lyrics()
    self.status = 'gathering cover art'
    self._fetch_cover_art()
    self.status = 'aligning to memes'
    self.select_and_align_memes()
    self.status = 'done'

  def _fetch_EN_analysis(self):
    self.track = pyechonest.track.track_from_filename(self.filepath)
    self.track.get_analysis()
    self.artist = self.track.artist
    self.title = self.track.title

  def _fetch_lyrics(self):
    #mild cleaning
    artist = self.artist
    title = self.title.split('/')[0]
    title = " ".join(title.split(" feat")[:-1])
    self.lyrics = rep_genius_parser(artist, title)

  def _fetch_cover_art(self):
    clientID = GRACENOTE_KEY
    userID = pygn.register(clientID)
    metadata = pygn.search(clientID=clientID, userID=userID, artist=self.artist, track=self.title.split('/')[0])
    try:
      r = requests.get(metadata['album_art_url'])
      artist_pic = tempfile.mkstemp(dir=os.path.join(base_path(), 'tmp'))[1]
      with open(artist_pic, 'wb') as wh:
        wh.write(r.content)
      self.album_art = '/audio_files/'+os.path.split(artist_pic)[1]
    except KeyError:
      print 'for', self.artist, ':', self.track, "gracenote doesn't have any album art"
      self.album_art = None

  def select_and_align_memes(self):
    with open(os.path.join(base_path(),'images.json')) as rh:
      memes = json.loads(rh.read())['memes']
    if self.album_art:
      self.timings = [{"image_url":self.album_art,
                        "transition_after": int(self.track.sections[0]['duration']*1000),
                        "top_text": '',
                        "bottom_text": '',
                      }] 
      start_section = 1
    else:
      self.timings = []
      start_section = 0
    shuffled_img = random.sample(memes.keys(), len(memes.keys()))
    print shuffled_img
    shuffled_phrases = random.sample(self.lyrics, len(self.lyrics))
    for section in self.track.sections[start_section:]:
      #draw cards
      key = shuffled_img.pop()
      img = memes[key]
      print img
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


class memeMatcherTests(unittest.TestCase):
	def setUp(self):
		self.tester = memeMatcher('')


if __name__ == '__main__':
	unittest.main()
