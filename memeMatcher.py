#!/usr/bin/env python
# encoding: utf-8
"""
memeMatcher.py

Created by Benjamin Fields on 2013-12-07.
Copyright (c) 2013 . All rights reserved.
"""

import sys
import os
import unittest
import requests
import pyechonest.track

from bs4 import BeautifulSoup


def rep_genius_parser(artist='', title=''):
  rg_base = "http://rapgenius.com"
  rg_search = rg_base+"/search?hide_unexplained_songs=false&q={terms}"
  #EN or something has produced artist and track name
  print rg_search.format(terms=artist+u'+'+title)
  r = requests.get(rg_search.format(terms=artist+u'+'+title))
  soup = BeautifulSoup(r.content)
  track_link = soup.select(".song_list li a")[0].get('href')
  r = requests.get(rg_base+track_link)
  soup = BeautifulSoup(r.content)
  raw_lyrics = soup.select("div.lyrics p")[0].get_text()
  lyrics = []
  phrase = []
  for line in raw_lyrics.split('\n'):
    if line==u'' and len(phrase)>0:
      lyrics.append(phrase)
      phrase = []
      continue
    if line[0]!= '[':
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
    self.artist = self.track.artist
    self.title = self.track.title

  def _fetch_lyrics(self):
    #mild cleaning
    artist = self.artist
    title = self.title.split('/')[0]
    self.lyrics = rep_genius_parser(artist, title)

  def _fetch_cover_art(self):
    pass

  def select_and_align_memes(self):
    pass


class memeMatcherTests(unittest.TestCase):
	def setUp(self):
		self.tester = memeMatcher('')


if __name__ == '__main__':
	unittest.main()
