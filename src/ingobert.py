# -*- coding: UTF-8 -*-
from google.appengine.ext import db
from google.appengine.ext import webapp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app
import difflib
import os
import re
import string

dict = {'Aa': 'Admont, Stiftsbibliothek 23 and 43',
        'Bc': 'Barcelona, Arxiu de la Corona d\'Aragó, Santa Maria de Ripoll 78',
        '5': 'Beinecke 413, 98r-102r',
        '5bis': 'Beinecke 413, 102v-104v',
        'Sirmond': '1623 Sirmond Edition',
        'Boretius': '1883 Boretius Edition'}

def compare(left, right):
    a = re.split("[\s\.]+", left.lower())
    b = re.split("[\s\.]+", right.lower())
    column = []
    diffs = difflib.ndiff(a, b)
    for diff in diffs:
        if re.match('  $', diff):
            continue
        elif re.match('\? ', diff):
            continue
        elif re.match('- ', diff):
            column.append('<span class=highlight>' + string.replace(diff, '- ', '') + '</span>')
        elif re.match('\+ ', diff):
            pass
        else:
            column.append(string.replace(diff, '  ', ''))
    return ' '.join(column)

class Capitulary(db.Model):
    number = db.IntegerProperty()
    chapter = db.IntegerProperty()
    source = db.StringProperty()
    text = db.TextProperty()

class Decretum(db.Model):
    distinction = db.BooleanProperty()
    case = db.BooleanProperty()
    number = db.IntegerProperty()
    dac = db.BooleanProperty()
    dpc = db.BooleanProperty()
    chapter = db.IntegerProperty()
    source = db.StringProperty()
    text = db.TextProperty()

class MainPage(webapp.RequestHandler):
    def get(self):
        chapters = db.GqlQuery('SELECT * FROM Decretum WHERE distinction = :1 AND number = :2', True, 63)
        for chapter in chapters:
            if (chapter.source == 'Aa'):
                Aa = chapter
            elif (chapter.source == 'Bc'):
                Bc = chapter
        template_values = {
            'page_head': 'Gratian, <cite>Decretum</cite>, D. 63, d.p.c. 34',
            'column_1_head': dict[Aa.source],
            'column_2_head': dict[Bc.source],
            'column_1_body': compare(Aa.text, Bc.text),
            'column_2_body': compare(Bc.text, Aa.text),
        }
        path = os.path.join(os.path.dirname(__file__), '2column.html')
        self.response.out.write(template.render(path, template_values))

class TwoColumn(webapp.RequestHandler):
    def get(self):
        chapters = db.GqlQuery('SELECT * FROM Capitulary WHERE chapter = :1', int(self.request.get('chapter')))
        for chapter in chapters:
            if (chapter.source == self.request.get('column_1')):
                column_1 = chapter
            if (chapter.source == self.request.get('column_2')):
                column_2 = chapter
        template_values = {
            'page_head': 'Capitulare Carisiacense, cap. ' + self.request.get('chapter'),
            'column_1_head': dict[self.request.get('column_1')],
            'column_2_head': dict[self.request.get('column_2')],
            'column_1_body': compare(column_1.text, column_2.text),
            'column_2_body': compare(column_2.text, column_1.text),
        }
        path = os.path.join(os.path.dirname(__file__), '2column.html')
        self.response.out.write(template.render(path, template_values))

class FourColumn(webapp.RequestHandler):
    def get(self):
        chapters = db.GqlQuery('SELECT * FROM Capitulary WHERE chapter = :1', int(self.request.get('chapter')))
        tmps = [None, None, None, None]
        list = ['5', '5bis', 'Sirmond', 'Boretius']
        list.remove(self.request.get('comparison'))
        for chapter in chapters:
            if (chapter.source == self.request.get('comparison')):
                tmps[0] = chapter
            if (chapter.source == list[0]):
                tmps[1] = chapter
            if (chapter.source == list[1]):
                tmps[2] = chapter
            if (chapter.source == list[2]):
                tmps[3] = chapter
        columns = []
        for tmp in tmps:
            column = {}
            if (tmp != None):
                if (tmp == tmps[0]):
                    column['highlight'] = True
                column['source'] = dict[tmp.source]
                column['text'] = compare(tmp.text, tmps[0].text)
            columns.append(column)
        template_values = {
            'title': 'Capitulare Carisiacense, cap. ' + self.request.get('chapter'),
            'columns': columns,
        }
        path = os.path.join(os.path.dirname(__file__), '4column.html')
        self.response.out.write(template.render(path, template_values))

application = webapp.WSGIApplication([('/decretum/', MainPage),
                                      ('/capitulary/2column', TwoColumn),
                                      ('/capitulary/4column', FourColumn),], debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
