# FlowAlongBrepFaces
# ---
# Flows Geometry from picked base to each face of a Brep
# Also converts a SubD into Bezier patches
#
# TBD - Switch around process: pick Geo, Base generate target(s)
# ---
import Rhino.Geometry as rg
import rhinoscriptsyntax as rs
import scriptcontext as sc



def SubDToBrepFaces( ):
    subd_guid = rs.GetObject("Pick a SubD to flow along", preselect=False)
    subd_obj = rs.coercerhinoobject( subd_guid ) # Rhino.DocObjects.ObjRef 
    subd_geom = subd_obj.Geometry # Rhino.Geometry.SubD
    
    print "Picked", type(subd_geom)
    if subd_geom.HasBrepForm:
        faces = subd_geom.Faces
        print "Picked SubD (with {} Faces) can be converted to NURBS patches. Converting...".format( faces.Count ), "\n"
        # print type(faces)
        #print "Converted Brep:", type(brep_geom) # brep_srf_list = brep_geom.Surfaces ?
        
        brep_faces = subd_geom.ToBrep().Faces #Faces property of SubD to NURBS
        
        if brep_faces:
            print "Converted", type(subd_geom), "into", type( brep_faces ) 
            print "Returned {} Brep Faces".format( brep_faces.Count), "\n"
            return brep_faces #Returns: Type BrepFaceList
        else:
            print "No Faces. Something's gone wrong."
            return

def FlowAlongBrepFaces( brep_faces ):
    surfaces = [ face.ToNurbsSurface() for face in brep_faces ]
    
    object_to_flow = rs.coercerhinoobject(rs.GetObjects('Select Object to flow', filter=16, preselect=False)).Geometry
    base = rs.coercesurface(rs.GetObject('Select Base Surface', filter=8, preselect=False ))
    
    sporph_space_morphs = [ rg.Morphs.SporphSpaceMorph( base, srf ) for srf in surfaces ]
    
    morphed_breps = [] 
    for morph in sporph_space_morphs:
        dupsrf = rg.Brep.Duplicate(object_to_flow) #Create a duplicate of object_to_flow
        morph.Morph(dupsrf) # Mutate dups with .Morph method (return is bool)
        morphed_breps.append(dupsrf)
        
    return morphed_breps # List of Breps

if __name__ == "__main__" :
    # Create BrepFaceList from pickedSubD
    brep_face_list = SubDToBrepFaces()
    
    # Pick base and geometry for flow. Create sporphs.
    morphed_breps = FlowAlongBrepFaces ( brep_face_list )
    
    # Add morphed objects to document geometry
    if morphed_breps:
        print "Drawing morphed Breps..."
        for brep in morphed_breps:
            sc.doc.Objects.AddBrep( brep ) # How to join up? At FlowAlong stage
            
        sc.doc.Views.Redraw()
    else: print "No Breps available to flow"