import c4d
import os
from c4d import gui, plugins, bitmaps, utils

PLUGIN_ID = 1040844

def GenerateSingleMesh(obj, doc):
	if not obj or not isinstance(obj, c4d.BaseObject): return None
	
	statelist = utils.SendModelingCommand(command=c4d.MCOMMAND_CURRENTSTATETOOBJECT, list=[obj], mode=c4d.MODELINGCOMMANDMODE_ALL, doc=doc)
	mx = obj.GetMg()
	container = c4d.BaseObject(c4d.Onull)
	for o in statelist:
		if isinstance(o, c4d.BaseObject):
			mg = o.GetMg()
			o.Remove()
			o.InsertUnder(container)
			o.SetMl(mg)
	joinlist = c4d.utils.SendModelingCommand(c4d.MCOMMAND_JOIN, container.GetChildren())
	meshobj = joinlist[0]
	
	if not meshobj.CheckType(c4d.Opolygon): return None
	return meshobj


def GenerateSplines(meshobj):
	if not meshobj or not meshobj.CheckType(c4d.Opolygon): return None
 
	nbr = utils.Neighbor()
	nbr.Init(meshobj)
	edges = c4d.BaseSelect()
	edges.SelectAll(nbr.GetEdgeCount()-1)
	meshobj.SetSelectedEdges(nbr, edges, c4d.EDGESELECTIONTYPE_SELECTION)
	if meshobj.GetEdgeS().GetCount() == 0: return None
 
	if c4d.utils.SendModelingCommand(c4d.MCOMMAND_EDGE_TO_SPLINE, [meshobj]):
		return meshobj.GetDown().GetClone()

		
class EdgeToSpline(plugins.ObjectData):
	def GetVirtualObjects(self, op, hierarchyhelp):
		objInput = op.GetDown()
		if objInput is None: return None
		
		doc = op.GetDocument()
		if doc is None: return None
		
		hierarchyClone = op.GetAndCheckHierarchyClone(hierarchyhelp, objInput, c4d.HIERARCHYCLONEFLAGS_ASIS, True)
		if hierarchyClone["dirty"] is False:
			return hierarchyClone["clone"]
		clone = hierarchyClone["clone"]
		if clone is None:
			return spline
		
		meshobj = GenerateSingleMesh(clone, doc)
		spline = GenerateSplines(meshobj)
		if spline is None: return c4d.BaseObject(c4d.Ospline)
		return spline			


if __name__ == "__main__":
	dir, file = os.path.split(__file__)
	bmp = bitmaps.BaseBitmap()
	bmp.InitWith(os.path.join(dir, "res", "icon.tif"))
	okyn = plugins.RegisterObjectPlugin(id=PLUGIN_ID, str="Edge to Spline", g=EdgeToSpline, description="generateedgesplines", icon=bmp, info=c4d.OBJECT_GENERATOR|c4d.OBJECT_ISSPLINE)
	if (okyn): print "Edge to Spline v0.1-beta initialized"