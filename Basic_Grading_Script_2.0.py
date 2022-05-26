import rhinoscriptsyntax as rs
import Rhino
import Rhino.Geometry as rg
import scriptcontext as sc
#****************************************************
# Purpose: To create a graded bottom pattern series
# Inputs:  Bottom Pattern Curve, Sizes
#               
# Returns: The graded patterns, names, stick length
#****************************************************
# BASIC GRADING - VERSION 2.0
#****************************************************

# to do annotate patterns, compound transform, add offset as variable

def Transform( negative, offset_dist, softedit_dist ):
    
    
    return

def offset_bottom (curve, negative_direction):
    bbox = curve.GetBoundingBox(False) # False for bbox 'estimated'
    distance, tolerance, plane, corner_style  = 0.25, 0.01, rg.Plane(rg.Point3d(0,0,0), rg.Vector3d(0,0,1)), rg.CurveOffsetCornerStyle(1)
    
    direction_point, normal = bbox.Corner(True, True, False), rg.Vector3d(0,0,1) #get corner for outward offset
    
    if negative_direction == False:
        offset = curve.Offset(direction_point, normal, distance, tolerance, corner_style) [0] #positive move
    else: offset = curve.Offset(direction_point, normal, -distance, tolerance, corner_style) [0] #negative move
    # dir = Rhino.Geometry.Vector3d(0,increment,0)
    # crv_t = offset.ExtremeParameters(dir)
    return offset

def soft_edit_bottom( crv, negative_direction, increment ):
    #takes one curve rhino object ref (not guid)
    
    dir = Rhino.Geometry.Vector3d(0,increment,0)
    crv_t = crv.ExtremeParameters(dir) #two values
    if negative_direction == False:
        softedit_toe = rg.Curve.CreateSoftEditCurve(crv, crv_t [0], dir, 50, False)
        softedit_heel = rg.Curve.CreateSoftEditCurve(softedit_toe, crv_t [1], -dir, 50, False)
    else: 
        softedit_toe = rg.Curve.CreateSoftEditCurve(crv, crv_t [0], -dir, 50, False)
        softedit_heel = rg.Curve.CreateSoftEditCurve(softedit_toe, crv_t [1], dir, 50, False)
     
    return softedit_heel

class Grading ():
    def __init__(self):
        self.info = dict()
    
    def CreateSizeRange(self):
        size_range_start = rs.GetReal ( "Grading Size Range Lower End", 3, 3, 11.5 ) 
        size_range_end = rs.GetReal ( "Grading Size Range Upper End", 9, (size_range_start+0.5), 12 ) 
        size_range_start *= 10
        size_range_end *= 10 #multiply by 10 to get values that can be used in a range
        size_range_multiplied = range(int(size_range_start), ( int(size_range_end) + 5 ), 5) #30 - 90 in 5s
        self.size_range = [ (size / 10) for size in size_range_multiplied ]
    
    def SelectBaseSize(self):
        options = [ str ( i ) for i in self.size_range ] #needs to be stringified
        self.base_size = float ( rs.ListBox(options, "Select Base Curve Size", "Grading Size Range") )
        index = self.size_range.index( self.base_size ) # index for grading midpoint
        self.sizes_below = self.size_range [ 0 : index ]
        self.sizes_below.reverse()
        self.sizes_above = self.size_range [ index + 1 : len(self.size_range) ]
        # could begin the tupling of sizes here also

class BottomPattern():
    def __init__(self):
        self.base_curve = rs.GetCurveObject("Select Base Pattern for Grading") [0]
        self.latest_curve = self.base_curve
        
    def GradeBottomPattern(self, boolean):
        curve = self.latest_curve
        objref = rs.coercecurve(curve)
        increment = 1
        offset = offset_bottom ( objref, boolean)
        graded = soft_edit_bottom ( offset, boolean, increment )
        sc.doc.Objects.AddCurve( graded )
        return graded #guid, get the graded objref ?
    
    def GradeBottomPatternSet(self, boolean, list):
        for size in list:
            self.latest_curve = bp.GradeBottomPattern(boolean)
            # copy the graded curve into empty tule with current value of size, and stick also ?
        self.latest_curve = self.base_curve #reset the last curve
        rs.Redraw()

bp = BottomPattern()
sizes = Grading()
sizes.CreateSizeRange()
sizes.SelectBaseSize()

bp.GradeBottomPatternSet(False, sizes.sizes_above)
bp.GradeBottomPatternSet(True, sizes.sizes_below)