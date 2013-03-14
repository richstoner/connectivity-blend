import tornado.ioloop
import tornado.web
from reversestream import AtlasDereference

import numpy as np
import struct, zipfile, os, json
from scipy import spatial, interpolate, ndimage
from pylab import *
import networkx as nx

import json
import urllib2

HEX = '0123456789abcdef'
HEX2 = dict((a+b, HEX.index(a)*16 + HEX.index(b)) for a in HEX for b in HEX)

def rgb(triplet):
    triplet = triplet.lower()

    return (HEX2[triplet[0:2]]/255.0, HEX2[triplet[2:4]]/255.0, HEX2[triplet[4:6]]/255.0)


class MainHandler(tornado.web.RequestHandler):
    
    def prepare(self):
        self.ad = AtlasDereference()

    def get(self):
        pt = array([6.7, 4.135, 5.444]) * 10
        for level in range(9):
            # print " "* level + "+-" + rgb(self.ad.colorAtPoint(pt, level) )
            print rgb(self.ad.colorAtPoint(pt, level) ) 

        level = 10
        _rgb  = rgb(self.ad.colorAtPoint(pt, level))
        colorstring = '%f,%f,%f' % (_rgb[0], _rgb[1], _rgb[2]) 
        self.write(colorstring)

    def post(self):

        data = self.get_argument('loc', 'No data received')
        vals = data.split(',')
        newv = (float(vals[0]), float(vals[1]), float(vals[2]))
        level = 10

        _rgb  = rgb(self.ad.colorAtPoint(newv, level))
        colorstring = '%f,%f,%f' % (_rgb[0], _rgb[1], _rgb[2]) 
        self.write(colorstring)

class SeriesHandler(tornado.web.RequestHandler):
    
    def prepare(self):
        self.ad = AtlasDereference()

        if not hasattr(self, 'jsondata'):

            f = open('query.json','r')
            import json
            self.jsondata = json.load(f)
            # import pprint
            # pprint.pprint(self.jsondata)

            # print(self.jsondata['msg'])
            self.arrayofexps = self.jsondata['msg']

    def get(self,param):    

        # param = '126862385'

        # urlstring = '''http://api.brain-map.org/api/v2/data/query.json?criteria=model::SectionDataSet,rma::criteria,%5Bid$eq''' + param +'''%5D,rma::include,specimen(injections(structure%5Bid$eq385%5D)),equalization,sub_images,rma::options%5Border$eq'sub_images.section_number$asc'%5D'''
        # urlstring = '''http://api.brain-map.org/api/v2/data/query.json?criteria=model::SectionDataSet,rma::criteria,%5Bid$eq''' + param + '''%5D,rma::include,equalization,sub_images,rma::options%5Border$eq'sub_images.section_number$asc'%5D'''
        urlstring = '''http://api.brain-map.org/api/v2/data/query.json?criteria=model::SectionDataSet,rma::criteria,[id$eq''' + param + '''],products,rma::include,specimen(injections(primary_injection_structure,structure),structure)'''
        import json
        jsonstr = urllib2.urlopen(urlstring).read()

        print jsonstr
        freshdata = json.loads(jsonstr)

                        # u'injections': [{u'age_id': 15,
                        #          u'angle': 0,
                        #          u'coordinates_ap': u'-4.48',
                        #          u'coordinates_dv': u'0.31',
                        #          u'coordinates_ml': u'1.60',


        import pprint
        pprint.pprint(freshdata['msg'])
        # print self.arrayofexps
        # for exp in self.arrayofexps:
            # pprint.pprint(exp)

        colorhex = freshdata['msg'][0]['specimen']['injections'][0]['structure']['color_hex_triplet']

        ap = freshdata['msg'][0]['specimen']['injections'][0]['coordinates_ap']
        dv = freshdata['msg'][0]['specimen']['injections'][0]['coordinates_dv']
        ml = freshdata['msg'][0]['specimen']['injections'][0]['coordinates_ml']

        

        _rgb  = rgb(colorhex)
        colorstring = '%f,%f,%f' % (_rgb[0], _rgb[1], _rgb[2]) 
        self.write(colorstring)

        # vals = data.split(',')
        # newv = (float(vals[0]), float(vals[1]), float(vals[2]))
        # level = 10

        # _rgb  = rgb(self.ad.colorAtPoint(newv, level))
        # colorstring = '%f,%f,%f' % (_rgb[0], _rgb[1], _rgb[2]) 
        # self.write(colorstring)




application = tornado.web.Application([
    (r"/", MainHandler),
    (r"/series/(.*)", SeriesHandler)
])

if __name__ == "__main__":
    application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()