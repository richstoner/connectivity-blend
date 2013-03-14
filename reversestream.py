import numpy as np
import struct, zipfile, os, json
from scipy import spatial, interpolate, ndimage
from pylab import *
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
    for i in xrange(nSegments):
        # Number of points in this segment
        nPoints = struct.unpack("H", fp.read(2))[0]

        # Read the segment data, 5 floats x, y, z, intensity, density, shape them properly
        pts = np.frombuffer(fp.read(4*5*nPoints), dtype=np.float32).reshape((-1,5)).T

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
        # Return just the Segments
        return segments

def dumpCSVs(segmentList):
    for n, segment in enumerate(segmentList):
        if n % 1000 == 0: print n
        savetxt("csv/%06i.csv" % n, segment, delimiter=",")

def loadAllSegments():
    segmentList = []
    # Go through the raw data
    pathList = [os.path.join("rawdata", f) for f in os.listdir("rawdata")]
    for n, path in enumerate(pathList):
        print path
        segmentList += readStream(path)
        print "\t%i segments loaded" % len(segmentList)

    return segmentList

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

        nPointsToInterp = int(segmentLength * 2)

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
    

    return c_[xd/mag, yd/mag, zd/mag].T


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



def computeDensityFeild(xyzid):
    xyz     = xyzid[0:3,:]
    density = xyzid[3,:]
    intensi = xyzid[4,:]

    print floor(xyz.min(axis=1))
    print ceil(xyz.max(axis=1))

    densitySampleShapes = tuple( ceil(xyz.max(axis=1)) )
    densityFeild = zeros(densitySampleShapes)

    print "Building KD Tree"
    kdt = spatial.cKDTree(xyz.T)
    
    for pt, value in ndenumerate(densityFeild):
        xp, yp, zp = pt
        # if xp < 75:
        #     continue
        # if xp > 75: 
        #     break

        print "Querying point:", pt

        dists, indxs = kdt.query(array(pt), k=80000, distance_upper_bound = 3)

        notInvalid = logical_not(isinf(dists))
        dists = dists[notInvalid]
        indxs = indxs[notInvalid]
        
        # print dists
        # print indxs

        if indxs.size == 0:
            densityFeild[pt] = 0
            continue
        

        nearbyInt = intensi[:,indxs]
        nearbyDen = density[:,indxs]

        nearbyXYZ = xyz[:,indxs][:,nearbyInt > 500]
        nearbyGrad = allGradientArray[:,indxs][:,nearbyInt > 500]

        densityFeild[pt] = nearbyXYZ.shape[1]

    return densityFeild


def parseOntology(jsn, structures={}, gOrder=0):
    # print jsn.keys()
    i = jsn['id']
    n = jsn["name"]
    p = jsn["parent_structure_id"]
    c = jsn['color_hex_triplet']

    struct = {"id":i, "name":n, "order":gOrder, "parent":p, "color": c}

    structures[i] = struct

    for child in jsn["children"]:
        parseOntology(child, structures, gOrder = gOrder + 1)


class AtlasDereference(object):
    def __init__(self):
        self.atlasVolume = fromfile("gridAnnotation_100micron/gridAnnotation.raw", dtype=uint16).reshape((115, 81, 133)).T # (133, 81, 115)

        self.ont = {}
        jsn = json.load(open("gridAnnotation_100micron/1.json"))
        parseOntology(jsn["msg"][0], self.ont)
        
        deepestNode = -1
        for struct in self.ont.values():
            if struct["order"] > deepestNode:
                deepestNode = struct["order"]

        # print deepestNodecolor_hex_triplet


    def idAtPoint(self, point):
        indx = around(point).astype(int)
        return self.atlasVolume[tuple(indx)]

    def nameAtPoint(self, point, level):        
        return self.infoAtPoint(point, level)["name"]

    def infoAtPoint(self, point, level):
        id = self.idAtPoint(point)
        info = self.ont[id]
        while info["order"] > level:
            info = self.ont[info["parent"]]
        return info

    def colorAtPoint(self, point, level):
        return self.infoAtPoint(point, level)["color"]


HEX = '0123456789abcdef'
HEX2 = dict((a+b, HEX.index(a)*16 + HEX.index(b)) for a in HEX for b in HEX)

def rgb(triplet):
    triplet = triplet.lower()

    return (HEX2[triplet[0:2]]/255.0, HEX2[triplet[2:4]]/255.0, HEX2[triplet[4:6]]/255.0)

if __name__ == "__main__":

    print('hello from reversestream')
    ad = AtlasDereference()
    pt = array([6.7, 4.135, 5.444]) * 10
    print pt

    for level in range(9):
        # print " "* level + "+-" + rgb(ad.colorAtPoint(pt, level) )
        print rgb(ad.colorAtPoint(pt, level) ) 

    # allSegs = loadAllSegments()
    # reSegs = reinterpolateSegments(allSegs)

    # allSegmentArray = concatenate(allSegs, axis=1)
    # newSegments = concatenate(reSegs, axis=1)

    # segmentGradientList = computeAllGradients(reSegs)
    # allGradientArray = concatenate(segmentGradientList, axis=1)
    
    # xyz = newSegments[0:3,:]
    # density = newSegments[3,:]
    # intensi = newSegments[4,:]
    # print "Building KD Tree"
    # kdt = spatial.cKDTree(xyz.T)

    # df = computeDensityFeild(newSegments)
    # 1/0

    # print "Running Query"
    # # Lets query the midpoint
    
    # queryPoint = array([7.119, 2.617, 5.13]) * 10
    # dists, indxs = kdt.query(queryPoint, k=80000)
    

    # nearbyInt = intensi[:,indxs]
    # nearbyDen = density[:,indxs]

    # nearbyXYZ = xyz[:,indxs][:,nearbyInt > 500]
    # nearbyGrad = allGradientArray[:,indxs][:,nearbyInt > 500]

    # gradRTP = xyz2rtp(nearbyGrad)
    
    
    # figure()
    # title("theta")
    # hist(gradRTP[1,:], bins=100)

    # figure()
    # title("phi")
    # hist(gradRTP[2,:], bins=100)

    # figure()
    # plot(gradRTP[2,:], gradRTP[1,:], "bo", alpha=0.4)
    

    # figure()
    # quiver(nearbyXYZ[0,:], nearbyXYZ[1,:], nearbyGrad[0,:], nearbyGrad[1,:])
    # axis("image")
    # show()

    # 1/0

    # deltaXYZ = nearbyXYZ - queryPoint[:,newaxis]
    
    
    # figure()
    # hist(theta.flat, bins=30)

    # figure()
    # hist(phi.flat, bins=30)

    # figure()
    # plot(theta, phi, "bo", alpha=0.7)
    # xlabel("Phi")
    # ylabel("Theta")

    # figure()
    # plot(subSegments[0,::10], subSegments[1,::10], "bo", alpha=0.5)

    # axis("image")
    # xlabel("x")
    # ylabel("y")

    # figure()
    # plot(newSegments[0,::10], newSegments[1,::10], "ro", alpha=0.5)

    # axis("image")
    # xlabel("x")
    # ylabel("y")

    # # figure()
    # # plot(subSegments[0,:], subSegments[2,:], "bo", alpha=0.5)
    # # plot(newSegments[0,:], newSegments[2,:], "ro", alpha=0.5)
    # # axis("image")
    # # xlabel("x")
    # # ylabel("z")

    # # figure()
    # # plot(subSegments[1,:], subSegments[2,:], "bo", alpha=0.5)
    # # plot(newSegments[1,:], newSegments[2,:], "ro", alpha=0.5)
    # # axis("image")
    # # xlabel("y")
    # # ylabel("z")

    # show()
