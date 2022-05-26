import Rhino
import rhinoscriptsyntax as rs
import scriptcontext as sc

#FILLET SRF MULTIPLE 1.02

def getSurface():
    go = Rhino.Input.Custom.GetObject()
    go.SetCommandPrompt("Select surfaces to fillet from")
    go.GeometryFilter = Rhino.DocObjects.ObjectType.Surface
    go.SubObjectSelect = True
    go.GetMultiple(1,0)
    if go.CommandResult()!= Rhino.Commands.Result.Success:
        return
    
    surfaceSelection = []
    for i in go.Objects():
        surfaceSelection.append(i.Surface().ToNurbsSurface())
        #returns surfaces
    return surfaceSelection

def FilletSrfMultiple(surfaces):
    
    pickedSurfaces = [ rs.coercegeometry(guid) for guid in surfaces ]
    referenceGUID = rs.GetObject("Pick surface to fillet to", filter=8)
    reference = ( rs.coercegeometry( referenceGUID ) ).Surfaces [ 0 ]
    
    radius = rs.GetReal("Enter radius value")
    
    filletSrfArrays = []
    for srf in pickedSurfaces:
        #expected Surface, got Brep
        createFilletSrf = Rhino.Geometry.Surface.CreateRollingBallFillet(srf, reference, radius, 0.01)
        filletSrfArrays.append(createFilletSrf)
    
    for array in filletSrfArrays:
        for srf in array:
            sc.doc.Objects.AddSurface(srf)

surfaces = getSurface()
FilletSrfMultiple(surfaces)

#this tool should have a preview option, enabling a flip to be done there.
# Surface.CreateRollingBallFillet(Surface, Point2d, Surface, Point2d, Double, Double)

#use a pick, bounce the point off the surface pick direction, then pull to the 'reference'

# surfaces_to_fillet( surface, point )
# for srf in surfaces_to_fillet:
#    Rhino.Geometry.Surface.CreateRollingBallFillet(refSurface, refPoint2d, surface, point, Double, Double)