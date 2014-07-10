# -*- coding: UTF-8 -*-
from django.template.loaders.filesystem import Loader
from django.template.loader import render_to_string
from google.appengine.ext import ndb
import diff_match_patch
import difflib
import os
import re
import webapp2

sourceDict = {'Aa': 'Admont, Stiftsbibliothek 23 and 43',
        'Bc': 'Barcelona, Arxiu de la Corona d\'Aragó, Santa Maria de Ripoll 78',
        '5': 'Beinecke 413, 98r-102r',
        '5bis': 'Beinecke 413, 102v-104v',
        'Sirmond': '1623 Sirmond Edition',
        'Boretius': '1883 Boretius Edition'}

def compare(left, right):
    a = re.split('[\s\.]+', left.lower())
    b = re.split('[\s\.]+', right.lower())
    column = []
    dmp = diff_match_patch.diff_match_patch()
    (wordText1, wordText2, wordArray) = dmp.diff_linesToChars('\n'.join(a), '\n'.join(b))
    diffs = dmp.diff_main(wordText1, wordText2, False);
    dmp.diff_charsToLines(diffs, wordArray)
    for diff in diffs:
        text = ' '.join(re.split('\n', diff[1]))
        if diff[0] == 1:
            continue
        elif diff[0] == 0:
            column.append(text)
        elif diff[0] == -1:
            column.append('<span class=highlight>' + text.rstrip() + '</span>')
    return(' '.join(column))
    
class Capitulary(ndb.Model):
    number = ndb.IntegerProperty()
    chapter = ndb.IntegerProperty()
    source = ndb.StringProperty()
    text = ndb.TextProperty()

class Decretum(ndb.Model):
    distinction = ndb.BooleanProperty()
    case = ndb.BooleanProperty()
    number = ndb.IntegerProperty()
    dac = ndb.BooleanProperty()
    dpc = ndb.BooleanProperty()
    chapter = ndb.IntegerProperty()
    source = ndb.StringProperty()
    text = ndb.TextProperty()

class MainPage(webapp2.RequestHandler):
    def get(self):
        os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
        chapters = ndb.gql('SELECT * FROM Decretum WHERE distinction = :1 AND number = :2', True, 63)
        for chapter in chapters:
            if (chapter.source == 'Aa'):
                Aa = chapter
            elif (chapter.source == 'Bc'):
                Bc = chapter
        template_values = {
            'page_head': 'Gratian, <cite>Decretum</cite>, D. 63, d.p.c. 34',
            'column_1_head': sourceDict[Aa.source],
            'column_2_head': sourceDict[Bc.source],
            'column_1_body': compare(Aa.text, Bc.text),
            'column_2_body': compare(Bc.text, Aa.text),
        }
        self.response.out.write(render_to_string('2column.html', template_values))

class TwoColumn(webapp2.RequestHandler):
    def get(self):
        os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
        chapters = ndb.gql('SELECT * FROM Capitulary WHERE chapter = :1', int(self.request.get('chapter')))
        column_1 = column_2 = None
        column_1_body = column_2_body = ''
        for chapter in chapters:
            if (chapter.source == self.request.get('column_1')):
                column_1 = chapter
            if (chapter.source == self.request.get('column_2')):
                column_2 = chapter
        if column_1 is not None:
            if column_2 is not None:
                column_1_body = compare(column_1.text, column_2.text)
            else:
                column_1_body = compare(column_1.text, '')
        if column_2 is not None:
            if column_1 is not None:
                column_2_body = compare(column_2.text, column_1.text)
            else:
                column_2_body = compare(column_2.text, '')
        template_values = {
            'page_head': 'Capitulare Carisiacense, cap. ' + self.request.get('chapter'),
            'column_1_head': sourceDict[self.request.get('column_1')],
            'column_2_head': sourceDict[self.request.get('column_2')],
            'column_1_body': column_1_body,
            'column_2_body': column_2_body,
        }
        self.response.out.write(render_to_string('2column.html', template_values))

class FourColumn(webapp2.RequestHandler):
    def get(self):
        os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
        chapters = ndb.gql('SELECT * FROM Capitulary WHERE chapter = :1', int(self.request.get('chapter')))
        tmps = [None, None, None, None]
        sourceList = ['5', '5bis', 'Sirmond', 'Boretius']
        sourceList.remove(self.request.get('comparison'))
        for chapter in chapters:
            if (chapter.source == self.request.get('comparison')):
                tmps[0] = chapter
            if (chapter.source == sourceList[0]):
                tmps[1] = chapter
            if (chapter.source == sourceList[1]):
                tmps[2] = chapter
            if (chapter.source == sourceList[2]):
                tmps[3] = chapter
        columns = []
        for tmp in tmps:
            column = {}
            if (tmp != None):
                if (tmp == tmps[0]):
                    column['highlight'] = True
                column['source'] = sourceDict[tmp.source]
                if (tmps[0] != None):
                    column['text'] = compare(tmp.text, tmps[0].text)
                elif (tmps[0] == None):
                    column['text'] = compare(tmp.text, '')
            columns.append(column)
        template_values = {
            'title': 'Capitulare Carisiacense, cap. ' + self.request.get('chapter'),
            'columns': columns,
        }
        self.response.out.write(render_to_string('4column.html', template_values))

app = webapp2.WSGIApplication([('/decretum/', MainPage),
                               ('/capitulary/2column', TwoColumn),
                               ('/capitulary/4column', FourColumn),], debug=True)

