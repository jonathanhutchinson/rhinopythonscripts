# Fair Edge SubD Interpolation
import Rhino
import Rhino.Geometry as rg
import rhinoscriptsyntax as rs
import scriptcontext as sc
import System

# get all the subd verts; id, control net and surface point
# get the subd smooth edge loop curve, return the ids affected
# fair the smooth curve to create the faired, smooth curve
# pull control net points 3d points to faired curve
# all other control net points become equivalent to theri surface points
# then interpolate  

# could fake the interpolation, and smooth adjacent edges too

def GetSubD():
    #select a subd, return the subd
    go = Rhino.Input.Custom.GetObject()
    go.GeometryFilter = Rhino.DocObjects.ObjectType.SubD
    go.SetCommandPrompt('Select subd for srf pt array')
    go.Get()
    objref = go.Objects() [0]
    print objref.ObjectId
    subd = objref.SubD()
    print type( subd)
    return subd

def GetSubDEdge():
    #select a subd edge, return edge ids of selection
    go = Rhino.Input.Custom.GetObject()
    go.GeometryFilter = Rhino.DocObjects.ObjectType.MeshEdge
    go.SetCommandPrompt('Select subd edge for testing of open/closedness')
    go.GetMultiple(1,0) # could be optional depending on inputs, add cmd line op?
    
    objrefs = go.Objects()
    edge_ids = [ objref.GeometryComponentIndex.Index for objref in objrefs ]
    
    curves = []
    for objref in objrefs:
        curves.append( objref.Curve( ) ) # just need the curve
    
    return edge_ids

def SubDPtsArray( subd ):
    # input a subd, return all info of subds points
    verts = subd.Vertices
    
    firstpt = verts.First
    control_net_pts, srf_pts = [ verts.First.ControlNetPoint ], [ verts.First.SurfacePoint() ]
    subd_vert_objects = [verts.First]
    subd_vert_ids = [verts.First.Id]
    
    for vert in range( subd.Vertices.Count  - 1 ):
        current = subd_vert_objects[-1].Next
        subd_vert_objects.append( current )
        subd_vert_ids.append( current.Id) 
        control_net_pts.append( current.ControlNetPoint )
        srf_pts.append(current.SurfacePoint( ) )
        value = [ current.ControlNetPoint, current.SurfacePoint( ) ]
    
    return subd_vert_ids, subd_vert_objects, control_net_pts, srf_pts

def GetSelectedSubDEdgePoints( edges, selected_ids ):
    
    selected_edge_points = [ ]
    net_pt = [ ]
    for edge in edges:
        if edge.Id in selected_ids:
            net_pt.append(edge.VertexFrom.ControlNetPoint)
            net_pt.append(edge.VertexTo.ControlNetPoint)
            
            selected_edge_points.append(edge.VertexFrom.Id)
            selected_edge_points.append(edge.VertexTo.Id)
    
    selected_vert_ids_set = set ( selected_edge_points )
    srf_pt = [ ]
    for id in selected_vert_ids_set:
        selectedvertex = verts.Find( id )
        srf_pt.append( selectedvertex.SurfacePoint() )
    
    ids = [ vert for vert in selected_vert_ids_set ]
    
    return ids, net_pt, srf_pt #a few things

#global vars
subd = GetSubD()
edges, verts = subd.Edges, subd.Vertices
selected_edge_ids = GetSubDEdge() #returns selected edge ids

all_pt_ids, subd_vert_objects, control_net_pt3d, srf_pt3d = SubDPtsArray( subd )

sel_ids, sel_controlnet_pt, sel_srf_pt = GetSelectedSubDEdgePoints( edges, selected_edge_ids )

# Create the edge loop points in an order to draw curve through
sorted_pts_3d = rg.Point3d.SortAndCullPointList ( sel_srf_pt, 0.1 ) #array type
sorted_pts_3d_list = [ pt for pt in sorted_pts_3d ] 
sorted_pts_3d_list.append(sorted_pts_3d_list [0] )

# Create the interpolated curve, set greville points array to the srf pts
interpolated = Rhino.Geometry.Curve.CreateInterpolatedCurve( sorted_pts_3d_list, 3, rg.CurveKnotStyle.Uniform )
periodic = rg.Curve.CreatePeriodicCurve( interpolated )
periodic.SetGrevillePoints( sorted_pts_3d_list )
sc.doc.ActiveDoc.Objects.AddCurve( periodic )

def FairCurve( curve ):
    iter = 5
    faired = curve.Fair( 2 , 1, 1, 1, iter )
    
    return faired

faircurve = FairCurve( periodic )
sc.doc.ActiveDoc.Objects.AddCurve(faircurve)

def AdaptControlNetPointsToCurve( subd, selected_vert_ids_list, curve ):
    
    newlocslist = [ ]
    
    for id in selected_vert_ids_list:
        current_loc = subd.Vertices.Find( id ).ControlNetPoint
        bool, t = curve.ClosestPoint( current_loc )
        newloc = curve.PointAt( t )
        newlocslist.append( newloc )
        subd.Vertices.Find( id ).ControlNetPoint = newloc
    
    newdict = dict ( zip ( selected_vert_ids_list, newlocslist ) )
    
    return newdict

surface_points_to_edit = AdaptControlNetPointsToCurve( subd, sel_ids, faircurve )

srfpts_dict = dict (zip( all_pt_ids, srf_pt3d ) )

controlnetpoints_tuple = zip( all_pt_ids, control_net_pt3d ) #index i is the id
new_controlnet_points = list(map(list, controlnetpoints_tuple) )

for item in new_controlnet_points:
    #item [0] is the vert index, item [1] is the location
    if item [0] in surface_points_to_edit.keys():
        #if its an id of a point to 'fair', find it, lookup its location in the dict
        item [1] = surface_points_to_edit.get( item [0] ) #srf pts to edit is a dict of index: cnet point
        
        
    elif item [0] in all_pt_ids:
        # if its not selected, convert the net position to the srf point
        item [1] = srfpts_dict.get( item [0] )
        
        
# do we sort out the list to match the original order?
# in that case, we need to amend the ORIGINAL control net points list

new_net_positions_only = [ i [1] for i in new_controlnet_points ]

def InterpolateSubDSurfacePoints( my_subd, my_new_controlnet_points ):
    array = System.Array[Rhino.Geometry.Point3d](my_new_controlnet_points)
    my_subd.InterpolateSurfacePoints( array )
    
    interpolated_subd = my_subd
    return interpolated_subd

newsubd = InterpolateSubDSurfacePoints(subd, new_net_positions_only)
sc.doc.ActiveDoc.Objects.AddSubD( newsubd )