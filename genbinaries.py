# -*- coding: utf-8 -*-
"""
Created on Thu Mar 14 00:59:39 2013

@author: Administrator
"""

#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np
import struct, zipfile, os
from scipy import spatial, interpolate
from pylab import *
import struct
import networkx as nx


def readStream(zf, returnSegmentGraph=False):
    # Open the zipfile
    zf = zipfile.ZipFile(zf)

    # Extract (in ram) the streamlines file
    fp = zf.open("streamlines.sl")

    # Ignore the first six bytes. . .  No idea what they are
    unknown = struct.unpack("HHH", fp.read(6)) 

    # This is the number of segments that are listes
    nSegments = struct.unpack("I", fp.read(4))[0]
    
    segmentGraph = nx.DiGraph()

    segments = []
    # For each segment

    # print('number of segments %d' % nSegments)

    for i in xrange(nSegments):
        # Number of points in this segment
        nPoints = struct.unpack("H", fp.read(2))[0]

        # print nPoints

        # Read the segment data, 5 floats x, y, z, intensity, density, shape them properly
        pts = np.frombuffer(fp.read(4*5*nPoints), dtype=np.float32).reshape((-1,5)).T

        # print pts.shape

        # Store the segment for later return
        segments.append(pts)

        # Compute the graph start and end nodes
        segmentStartTuple = tuple(pts[0:3,0])
        segmentEndingTuple = tuple(pts[0:3,-1])

        # Populate the graph
        segmentGraph.add_edge(segmentStartTuple, segmentEndingTuple)

    if returnSegmentGraph:
        # Return the segments plus the graph
        return segments, segmentGraph
    else:

        print len(segments)

        # Return just the Segments
        return segments

def dumpCSVs(segmentList):
    for n, segment in enumerate(segmentList):
        if n % 1000 == 0: print n
        save("csv/%06i.bin" % n, segment, delimiter=",")



def loadAllSegments():
    
    # Go through the raw data
    segmentList = []
    path_to_return = []
    pathList = [os.path.join("rawdata", f) for f in os.listdir("rawdata")]
    for n, path in enumerate(pathList):
        print path
        if '.DS' not in path:
            path_to_return.append(path)
            segmentList.append(readStream(path))
            print "\t%i segments loaded" % len(segmentList)

    print len(segmentList)

    return [path_to_return, segmentList]

# def loadSegment():
#     count = 1
#     segmentList = []
#     # Go through the raw data
#     path_to_return = ''
#     pathList = [os.path.join("rawdata", f) for f in os.listdir("rawdata")]
    
#     for n, path in enumerate(pathList):

#         segmentList = []

#         if '.DS' not in path:
#             if count > 0:
#                 print path
#                 path_to_return = path
#                 segmentList.append(readStream(path))
#                 print "\t%i segments loaded" % len(segmentList)
#                 count -= 1

#     return [path_to_return , segmentList]

def reinterpolateSegments(segmentList):
    newSegmentList = []
    
    # Go through all the segments
    for n, segment in enumerate(segmentList):
        # Barf status info occasionally
        if n % 100 == 0: print n, "of", len(segmentList)

        # Find the lenght of this segment in the aba coordiante system
        segmentLength = computeSegmentLength(segment)
        
        if segmentLength == 0:
            continue

        nPointsToInterp = floor(int(segmentLength * 2) / 4)

        newSegment = zeros((segment.shape[0], nPointsToInterp), dtype=float32)

        nd = linspace(0.0, segmentLength, segment.shape[1])
        for indx in xrange(segment.shape[0]):
            iInterp = interpolate.interp1d(nd, segment[indx,:], copy=False)
            newSegment[indx,:] = iInterp( linspace(0, segmentLength, nPointsToInterp ) )
            
        newSegmentList.append(newSegment)

    return newSegmentList


def testStream():
    for n, f in enumerate(os.listdir("rawdata")):
        print f
        path = os.path.join("rawdata", f)
        failureIDs = []

        streamSegments = readStream(path)

        for stream in streamSegments:
            xs, ys, zs, i1, i2 = stream

            figure(1)
            plot(xs, ys, "b", alpha=0.3)

            figure(2)
            plot(ys, zs, "b", alpha=0.3)

            figure(3)
            plot(xs, zs, "b", alpha=0.3)

        if n > 4:
            break

    print failureIDs


def computeSegmentLength(segmentArray):
    xs, ys, zs, ii, ij = segmentArray
    
    xd = diff(xs)
    yd = diff(ys)
    zd = diff(zs)

    dist = sqrt( xd**2 + yd**2 + zd**2 )
    
    return sum(dist)

def computeSegmentGradients(segmentArray):
    xs, ys, zs, ii, ij = segmentArray
    
    xd = ndimage.gaussian_filter1d(xs, 1.0, order=1)
    yd = ndimage.gaussian_filter1d(ys, 1.0, order=1)
    zd = ndimage.gaussian_filter1d(zs, 1.0, order=1)
    
    mag = sqrt( xd**2 + yd**2 + zd**2 )
    mag[mag==0] = 1
    

    return c_[xd/mag, yd/mag, zd/mag]


def xyz2rtp(xyz):
    r = sqrt(xyz[0,:]**2 + xyz[1,:]**2 + xyz[2,:]**2)
    theta = arccos(xyz[2,:]/r)
    phi   = arctan2(xyz[1,:], xyz[0,:])

    # No gradient makes a poorly defined theta and phi
    theta[r==0] = 0
    phi[r==0] = 0

    print xyz[:,isnan(theta)]

    if any(isnan(theta)):
        raise ValueError("wtf! ^^")

    return c_[r, theta, phi].T


def computeAllGradients(segmentList):
    print "Computing gradients"
    segmentGradients = []
    for n, s in enumerate( segmentList ):
        if n % 10000 == 0: print n, "of", len(segmentList)
        segmentGradients.append( computeSegmentGradients(s) )
    return segmentGradients


def computeAllDistances(segmentList):
    distances = []
    for segment in segmentList:
        distances.append(computeSegmentLength(segment))

    d = concatenate(distances)
    print d.shape
    hist(d, bins=200)
    print d.min(), d.max()
    show()

def dumpToBin(segmentList, outfilename):

    print outfilename

    import struct
    import ctypes

    x,y,z,d,e = segmentList

    vertex_count = len(x)
    buffer_size = vertex_count * 4 * 3

    bytes = ctypes.create_string_buffer(buffer_size)

    for i in range(0,vertex_count):
        # print '%d %d %d %d' % (i, 4*i, 12*i+4, 12*i+8)

        struct.pack_into('f', bytes, 12*i, x[i])
        struct.pack_into('f', bytes, 12*i+4, y[i])
        struct.pack_into('f', bytes, 12*i+8, z[i])    
    
    # struct.pack_into('f', bytes, 4, 0.5)

    f = open(outfilename, 'wb')
    f.write(bytes)
    f.close()

if __name__ == "__main__":
    allSegs = loadAllSegments()
    # singleSeg = loadSegment()
    # segName = singleSeg[0]

    # print allSegs[0]
    # print 'segs: %d' % len(allSegs[1])

    for i in range(0,len(allSegs[0])):
        segName = allSegs[0][i]

        for j in range(0,len(allSegs[1][i])):
            jname = '-%04d' % j
            outName = segName.replace('rawdata', 'bindata').split('.')[0] + jname  + '.isl' 
            print outName

            dumpToBin(allSegs[1][i][j], outName)

        
    #     singleSeg = allSegs[1][i]


    #     # print singleSeg.shape

    #     # print singleSeg

            
    #     # print outName
        

    # dumpCSVs(allSegs)



































