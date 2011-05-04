import c4d

class MojitoExporter(c4d.plugins.SceneSaverData):
	def Save(self, node, name, doc, filterflags):
		polyDoc = doc.Polygonize(True)
		file = open(name, "w")
		
		file.write("<?xml version=\"1.0\"?>\n")
		file.write("<mojito version=\"0.1\">\n")
		if len(polyDoc.GetObjects()) > 0:
			file.write("\t<nodes>\n")
			for obj in polyDoc.GetObjects():
				printNode(obj, 2, file)
			file.write("\t</nodes>\n")
		file.write("</mojito>\n")
		
		file.close()
		return 0

def printNode(node, indent, file):
	
	firstLevelNode = False
	if indent == 2:
		firstLevelNode = True
	
	tabs = ""
	for i in range(indent):
		tabs += "\t"
	
	# write polygon object
	if node.GetTypeName() == "Polygon" and node.GetPointCount():
		file.write("%s<polygon>\n" % (tabs))
		
		# write vertices
		file.write("%s\t<vertices>" % (tabs))
		firstVertex = True
		for vertex in node.GetAllPoints():
			if firstVertex != True:
				file.write(" ")
			file.write("%s %s %s" % (vertex.x, vertex.y, vertex.z))
			firstVertex = False
		file.write("</vertices>\n")
		
		# write uvset
		allUVs = []
		uvList = []
		firstUV = True
		hasUVCoordinates = False
		
		for tag in node.GetTags():
			if tag.GetTypeName() == "UVW":
				hasUVCoordinates = True
				file.write("%s\t<uvset>" % (tabs))
				for i in range(tag.GetDataCount()):
					uv = tag.GetSlow(i)
					allUVs.append(uv["a"])
					allUVs.append(uv["b"])
					allUVs.append(uv["c"])
					allUVs.append(uv["d"])
				
				for uv in allUVs:
					if not uv in uvList:
						uvList.append(uv)
						if firstUV != True:
							file.write(" ")
						file.write("%s %s" % (uv.x, -uv.y))
						firstUV = False
				file.write("</uvset>\n")
				break
				
		if not hasUVCoordinates:
			file.write("%s\t<uvset>" % (tabs))
			file.write("%s %s" % (0.0, 0.0))
			file.write("</uvset>\n")
		
		# write normals
		file.write("%s\t<normals>" % (tabs))
		allNormals = node.CreatePhongNormals()
		normalList = []
		firstNormal = True
		for normal in allNormals:
			if not normal in normalList:
				normalList.append(normal)
				if firstNormal != True:
					file.write(" ")
				file.write("%s %s %s" % (normal.x, normal.y, normal.z))
				firstNormal = False
		file.write("</normals>\n")
		
		# write faces
		file.write("%s\t<faces>" % (tabs))
		firstFace = True
		for i in range(node.GetPolygonCount()):
			face = node.GetAllPolygons()[i]
			normalAIndex = normalList.index(allNormals[i*4])
			normalBIndex = normalList.index(allNormals[i*4+1])
			normalCIndex = normalList.index(allNormals[i*4+2])
			normalDIndex = normalList.index(allNormals[i*4+3])
			
			if hasUVCoordinates:
				uvAIndex = uvList.index(allUVs[i*4])
				uvBIndex = uvList.index(allUVs[i*4+1])
				uvCIndex = uvList.index(allUVs[i*4+2])
				uvDIndex = uvList.index(allUVs[i*4+3])
			else:
				uvAIndex = 0
				uvBIndex = 0
				uvCIndex = 0
				uvDIndex = 0
				
			
			if firstFace != True:
				file.write(" ")
						
			# 1st triangle
			file.write("%s %s %s" % (face.a, face.b, face.c))
			file.write(" %s %s %s" % (normalAIndex, normalBIndex, normalCIndex))
			file.write(" %s %s %s" % (uvAIndex, uvBIndex, uvCIndex))
			if face.c != face.d:
				# 2nd triangle
				file.write(" %s %s %s" % (face.a, face.c, face.d))
				file.write(" %s %s %s" % (normalAIndex, normalCIndex, normalDIndex))
				file.write(" %s %s %s" % (uvAIndex, uvCIndex, uvDIndex))
			firstFace = False
			
		file.write("</faces>\n")
		
		# write material name
		for tag in node.GetTags():
			if tag.GetTypeName() == "Texture":
				file.write("%s\t<material>" % (tabs))
				file.write(tag.GetMaterial().GetName());
				file.write("</material>\n")
				break
				
		# write transformation matrix
		file.write("%s\t<transformation>" % (tabs))
		ml = node.GetRelMl()
		if firstLevelNode == True:
			# make proper XYZ coordinate system
			file.write("%s %s %s %s " % (-ml.v1.x, ml.v2.x, ml.v3.x, -ml.off.x))
			file.write("%s %s %s %s " % (ml.v1.y, ml.v2.y, ml.v3.y, ml.off.y))
			file.write("%s %s %s %s " % (ml.v1.z, ml.v2.z, ml.v3.z, ml.off.z))
			file.write("%s %s %s %s" % (0.0, 0.0, 0.0, 1.0))
		else:
			file.write("%s %s %s %s " % (ml.v1.x, ml.v2.x, ml.v3.x, ml.off.x))
			file.write("%s %s %s %s " % (ml.v1.y, ml.v2.y, ml.v3.y, ml.off.y))
			file.write("%s %s %s %s " % (ml.v1.z, ml.v2.z, ml.v3.z, ml.off.z))
			file.write("%s %s %s %s" % (0.0, 0.0, 0.0, 1.0))
		file.write("</transformation>\n")
		
		# write children
		children = node.GetChildren()
		if len(children) > 0:
			file.write("%s\t<children>\n" % (tabs))
			for obj in children:
				printNode(obj, indent+2, file)
			
			file.write("%s\t</children>\n" % (tabs))
		file.write("%s</polygon>\n" % (tabs))
		
	# write null object
	else:
		file.write("%s<null>\n" % (tabs))
		children = node.GetChildren()
		
		# write material name
		for tag in node.GetTags():
			if tag.GetTypeName() == "Texture":
				file.write("%s\t<material>" % (tabs))
				file.write(tag.GetMaterial().GetName());
				file.write("</material>\n")
				break
				
		# write transformation matrix
		file.write("%s\t<transformation>" % (tabs))
		ml = node.GetRelMl()
		if firstLevelNode == True:
			# make proper XYZ coordinate system
			file.write("%s %s %s %s " % (-ml.v1.x, ml.v2.x, ml.v3.x, -ml.off.x))
			file.write("%s %s %s %s " % (ml.v1.y, ml.v2.y, ml.v3.y, ml.off.y))
			file.write("%s %s %s %s " % (ml.v1.z, ml.v2.z, ml.v3.z, ml.off.z))
			file.write("%s %s %s %s" % (0.0, 0.0, 0.0, 1.0))
		else:
			file.write("%s %s %s %s " % (ml.v1.x, ml.v2.x, ml.v3.x, ml.off.x))
			file.write("%s %s %s %s " % (ml.v1.y, ml.v2.y, ml.v3.y, ml.off.y))
			file.write("%s %s %s %s " % (ml.v1.z, ml.v2.z, ml.v3.z, ml.off.z))
			file.write("%s %s %s %s" % (0.0, 0.0, 0.0, 1.0))
		file.write("</transformation>\n")
		
		# write children
		if len(children) > 0:
			file.write("%s\t<children>\n" % (tabs))
			for obj in children:
				printNode(obj, indent+2, file)
			
			file.write("%s\t</children>\n" % (tabs))
		file.write("%s</null>\n" % (tabs))
