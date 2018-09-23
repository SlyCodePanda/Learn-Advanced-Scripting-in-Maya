import maya.cmds as cmds
import maya.mel as mel
import string



#######################################
#
#    Low-level procs
#
#######################################



# PURPOSE:         Tag the given node with the origin attribute and set to true.
# PROCEDURE:       If the object exists, and the attribute does not exist,
#                  add the origin bool attribute and set to true.
# PRESUMPTION:     none
def SIP_TagForOrigin(node):
    if cmds.objExists(node) and not cmds.objExists(node + ".origin"):
        cmds.addAttr(node, shortName="org", longName="origin", at="bool")
        cmds.setAttr(node + ".origin", True)


# PURPOSE:          add attributes to the mesh so exporter can find them.
# PROCEDURE         if object exists, and the attribute does not, add exportMeshes message attribute.
# PRESUMPTION       none
def SIP_TagForMeshExport(mesh):
    if cmds.objExists(mesh) and not cmds.objExists(mesh + ".exportMeshes"):
        cmds.addAttr(mesh, shortName="xms", longName="exportMeshes", at="message")


# PURPOSE:         Add attribute to the node so exporter can find export definitions
# PROCEDURE:       If the object exists, and the attribute does not exist,
#                  add the exportNode message attribute and set to true.
# PRESUMPTION:     none
def SIP_TagForExportNode(node):
    if cmds.objExists(node) and not cmds.objExists(node + ".exportNode"):
        cmds.addAttr(node, shortName="xnd", longName="exportNode", at="message")


# PURPOSE:          Return the origin of the given namespace
# PROCEDURE:        If ns is not empty string, list all joints with the matching namespace, else list all joints.
#                   For list of joints, look for the origin attribute and if it is set to true. If found, return the
#                   name of the joint, else return "Error".
# PRESUMPTION:      Origin attribute is on a joint.
#                   "Error" is not a joint name.
#                   namespace does not include colon.
def SIP_ReturnOrigin(ns):
    joints = []

    if ns:
        joints = cmds.ls((ns + ":*"), type="joint")
    else:
        joints = cmds.ls(type="joint")

    if len(joints):
        for curJoint in joints:
            if cmds.objExists(curJoint + ".origin") and cmds.getAttr(curJoint + ".origin"):
                return curJoint

    return "Error"


# PURPOSE:          Removes all nodes tagged as garbage.
# PROCEDURE:        List all transforms in scene, iterate through the list, anything with the "deleteMe" attribute
#                   will be deleted.
# PRESEUMPTIONS:    The deleteMe attribute is the correct name of the attribute signifying garbage.
def SIP_ClearGarbage():
    list = cmds.ls(tr=True)

    for cur in list:
        if cmds.objExists(cur + ".deleteMe"):
            cmds.delete(cur)


# PURPOSE:          Tag objects for being garbage.
# PROCEDURE:        If node is valid object and attribute does not exist, add deleteMe attribute.
# PRESUMPTIONS:     None.
def SIP_TagForGarbage(node):
    if cmds.objExists(node) and not cmds.objExists(node + ".deleteMe"):
        cmds.addAttr(node, shortName="del", longName="deleteMe", at="bool")
        cmds.setAttr(node + ".deleteMe", True)


# PURPOSE:          Return the meshes connected to blendshape nodes.
# PROCEDURE:        Get a list of blendshape nodes, follow those connections to the mesh shape node,
#                   Traverse up the hierarchy to find the parent transform node.
# PRESUMPTION:      Character has a valid namespace, and namespace does not have colon.
#                   Only exporting polygonal meshes.
def SIP_FindMeshWithBlendshapes(ns):
    returnArray = []

    blendshapes = cmds.ls((ns + ":*"), type="blendShape")
    for curBlendshape in blendshapes:
        downstreamNodes = cmds.listHistory(curBlendshape, future=True)
        for curNode in downstreamNodes:
            if cmds.objectType(curNode, isType="mesh"):
                parents = cmds.listRelatives(curNode, parent=True)
                returnArray.append(parents[0])

    return returnArray



#######################################
#
#    Export settings node procs
#
#######################################



# PURPOSE:          Return all export nodes connected to given origin.
# PROCEDURE:        If origin is valid and has the exportNode attribute, return list of export nodes connected to it.
# PRESUMPTION:      Only export nodes are connected to exportNode attribute.
def SIP_ReturnFBXExportNodes(origin):
    exportNodeList = []

    if cmds.objExists(origin + ".exportNode"):
        exportNodeList = cmds.listConnections(origin + ".exportNode")

    return exportNodeList


# PURPOSE:          Connect the fbx export node to the origin.
# PROCEDURE:        Check if attributes exist in nodes are valid, if they are, connect attributes.
# PRESUMPTIONS:     None.
def SIP_ConnectFBXExportNodeToOrigin(exportNode, origin):
    if cmds.objExists(origin) and cmds.objExists(exportNode):
        if not cmds.objExists(origin + ".exportNode"):
            SIP_TagForExportNode(origin)
        if not cmds.objExists(exportNode + ".exportNode"):
            SIP_AddFBXNodeAttrs(fbxExportNode)
        cmds.connectAttr(origin + ".exportNode", exportNode + ".exportNode")


# PURPOSE:          Delete given export node.
# PROCEDURE:        If object exists, delete.
# PRESUMPTION:      none.
def SIP_DeleteFBXExportNode(exportNode):
    if cmds.objExists(exportNode):
        cmds.delete(exportNode)


# PURPOSE:          To add the attributes to the export node to store our export settings.
# PROCEDURE:        For each attribute we want to add, check if it exists. If it doesn't exist, add.
# PRESUMPTION:      Assume fbxExportNode is a valid object.
def SIP_AddFBXNodeAttrs(fbxExportNode):
    if not cmds.attributeQuery("export", node=fbxExportNode, exists=True):
        cmds.addAttr(fbxExportNode, longName="export", at="bool")

    if not cmds.attributeQuery("moveToOrigin", node=fbxExportNode, exists=True):
        cmds.addAttr(fbxExportNode, longName="moveToOrigin", at="bool")

    if not cmds.attributeQuery("zeroOrigin", node=fbxExportNode, exists=True):
        cmds.addAttr(fbxExportNode, longName="zeroOrigin", at="bool")

    if not cmds.attributeQuery("exportName", node=fbxExportNode, exists=True):
        cmds.addAttr(fbxExportNode, longName="exportName", dt="string")

    if not cmds.attributeQuery("useSubRange", node=fbxExportNode, exists=True):
        cmds.addAttr(fbxExportNode, longName="useSubRange", at="bool")

    if not cmds.attributeQuery("startFrame", node=fbxExportNode, exists=True):
        cmds.addAttr(fbxExportNode, longName="startFrame", at="float")

    if not cmds.attributeQuery("endFrame", node=fbxExportNode, exists=True):
        cmds.addAttr(fbxExportNode, longName="endFrame", at="float")

    if not cmds.attributeQuery("exportMeshes", node=fbxExportNode, exists=True):
        cmds.addAttr(fbxExportNode, longName="exportMeshes", at="message")

    if not cmds.attributeQuery("exportNode", node=fbxExportNode, exists=True):
        cmds.addAttr(fbxExportNode, shortName="xnd", longName="exportNode", at="message")

    if not cmds.attributeQuery("animLayers", node=fbxExportNode, exists=True):
        cmds.addAttr(fbxExportNode, longName="animLayers", dt="string")


# PURPOSE:          Create the export node to store our export settings.
# PROCEDURE:        Create an empty transform node, send it to SIP_AddFBXNodeAttrs to add the needed attributes.
# PRESUMPTION:      None.
def SIP_CreateFBXExportNode(characterName):
    fbxExportNode = cmds.group(em=True, name=characterName + "FBXExportNode#")
    SIP_AddFBXNodeAttrs(fbxExportNode)
    cmds.setAttr(fbxExportNode+".export", 1)
    return fbxExportNode




######################################
#
#    Model export procs
#
######################################



# PURPOSE:          To connect meshes to the export node so the exporter can find them.
# PROCEDURE:        Check to make sure meshes and exportNode is valid, check for attribute "exportNode".
#                   If no attribute, add it. Then connect attributes.
# PRESUMPTION:      exportNode is an actual exportNode, and meshes is a list of transform nodes for polygon meshes.
def SIP_ConnectFBXExporterNodeToMeshes(exportNode, meshes):
    if cmds.objExists(exportNode):
        if not cmds.objExists(exportNode + ".exportMeshes"):
            SIP_AddFBXNodeAttrs(fbxExportNode)

        for curMesh in meshes:
            if cmds.objExists(curMesh):
                if not cmds.objExists(exportNode + ".exportMeshes"):
                    SIP_TagForMeshExport(curMesh)

                cmds.connectAttr(exportNode + ".exportMeshes", curMesh + ".exportMeshes", force=True)



# PURPOSE:          To disconnect the message attribute between the export node and the meshes.
# PROCEDURE:        Itterate through list of meshes and if mesh exists, disconnect.
# PRESUMPTION:      That node and mesh are connected via export exportMeshes message attr.
def SIP_DisconnectFBXExporterNodeToMeshes(exportNode, meshes):
    if cmds.objExists(exportNode):
        for curMesh in meshes:
            if cmds.objExists(curMesh):
                cmds.disconnectAttr(exportNode + ".exportMeshes", curMesh + ".exportMeshes")


# PURPOSE:          Return a list of meshes connected to the export node.
# PROCEDURE:        List connections to exportNode attribute.
# PRESUMPTION:      exportMeshes attribute is used to connect to export meshes, exportMeshes are valid.
def SIP_ReturnConnectedMeshes(exportNode):
    meshes = cmds.listConnections((exportNode + ".exportMeshes"), source=False, destination=True)
    return meshes



######################################
#
#    Animation export procs
#
######################################


# PUPROSE:
# PROCEDURE:
# PRESUMPTION:
def SIP_UnlockJointTransforms(root):
    hierarchy = cmds.listRelatives(root, ad=True, f=True)

    hierarchy.append(root)

    for cur in hierarchy:
        cmds.setAttr((cur + '.translateX'), lock=False)
        cmds.setAttr((cur + '.translateY'), lock=False)
        cmds.setAttr((cur + '.translateZ'), lock=False)
        cmds.setAttr((cur + '.rotateX'), lock=False)
        cmds.setAttr((cur + '.rotateY'), lock=False)
        cmds.setAttr((cur + '.rotateZ'), lock=False)
        cmds.setAttr((cur + '.scaleX'), lock=False)
        cmds.setAttr((cur + '.scaleY'), lock=False)
        cmds.setAttr((cur + '.scaleZ'), lock=False)



# PUPROSE:          Connect given node to another given node via specified transform.
# PROCEDURE:        Call connectAttr
# PRESUMPTION:      Assume that the 2 nodes exist and transform type is valid.
def SIP_ConnectAttrs(sourceNode, destNode, transform):
    cmds.connectAttr(sourceNode + "." + transform + "X", destNode + "." + transform + "X")
    cmds.connectAttr(sourceNode + "." + transform + "Y", destNode + "." + transform + "Y")
    cmds.connectAttr(sourceNode + "." + transform + "Z", destNode + "." + transform + "Z")



# PURPOSE:          To copy the skeleton and connect the copy to the original bind.
# PROCEDURE:        Duplicate hierarchy, delete everything that is not a joint, unlock all the joints,
#                   connect the translates, rotates, and scales. Parent copy to the world. Add deleteMe attr.
# PRESUMPTION:      No joints are children of anything but other joints.
def SIP_CopyAndConnectSkeleton(origin):
    newHierarchy = []

    if origin != "Error" and cmds.objExists(origin):
        dupHierarchy = cmds.duplicate(origin)
        tempHierarchy = cmds.listRelatives(dupHierarchy[0], allDescendents=True, f=True)

        for cur in tempHierarchy:
            if cmds.objExists(cur):
                if cmds.objectType(cur) != "joint":
                    cmds.delete(cur)

        SIP_UnlockJointTransforms(dupHierarchy[0])

        origHierarchy = cmds.listRelatives(origin, ad=True, type="joint")
        newHierarchy = cmds.listRelatives(dupHierarchy[0], ad=True, type="joint")

        origHierarchy.append(origin)
        newHierarchy.append(dupHierarchy[0])

        for index in range(len(origHierarchy)):
            SIP_ConnectAttrs(origHierarchy[index], newHierarchy[index], "translate")
            SIP_ConnectAttrs(origHierarchy[index], newHierarchy[index], "rotate")
            SIP_ConnectAttrs(origHierarchy[index], newHierarchy[index], "scale")

        cmds.parent(dupHierarchy[0], world=True)
        SIP_TagForGarbage(dupHierarchy[0])

    return newHierarchy



# PURPOSE:          Translate export skeleton to origin. May or may not kill origin animation depending on input.
# PROCEDURE:        Bake the animation onto the origin. Create an animLayer. animLayer will either be additive or
#                   override depending on parameters we pass it. Add deleteMe attr to animLayer. Move to origin.
# PRESUMPTION:      Origin is valid, end frame is greater than start frame, zeroOrigin is boolean.
def SIP_TransformToOrigin(origin, startFrame, endFrame, zeroOrigin):
    cmds.bakeResults(origin, t=(startFrame, endFrame),
                     at=["rx", "ry", "rz", "sx", "sy", "sz", "tx", "ty", "tz"], hi="none")

    cmds.select(clear=True)
    cmds.select(origin)
    newAnimLayer=""

    if zeroOrigin:
        # Kills origin animation.
        newAnimLayer = cmds.animLayer(aso=True, mute=False, solo=False, override=True, passthrough=True, lock=False)
        cmds.setAttr(newAnimLayer + ".rotationAccumulationMode", 0)
        cmds.setAttr(newAnimLayer + ".scaleAccumulationMode", 1)
    else:
        # Shifts the origin animation.
        newAnimLayer = cmds.animLayer(aso=True, mute=False, solo=False, override=False, passthrough=False, lock=False)

    SIP_TagForGarbage(newAnimLayer)

    # Turn animLayer on.
    cmds.animLayer(newAnimLayer, edit=True, weight=1)
    cmds.setKeyframe(newAnimLayer + ".weight")

    # Move origin animation to world origin.
    cmds.setAttr(origin + ".translate", 0, 0, 0)
    cmds.setAttr(origin + ".rotate", 0, 0, 0)
    cmds.setKeyframe(origin, al=newAnimLayer, t=startFrame)





######################################
#
#    AnimLayers procs
#
######################################


# PURPOSE:          Record the animLayer settings used in the animation and store in the exportNode as a string.
# PROCEDURE:        List all the animLayers, query their mute and solo attributes. List them in one single string.
#                   Uses ; as sentinel value to split separate animLayers.
#                   Uses , as sentinel value to split separate fields for animLayer.
#                   Uses = as sentinel value to split separate attrs from their values in field.
# PRESUMPTION:      None.
def SIP_SetAnimLayerSettings(exportNode):
    if not cmds.attributeQuery("animLayers", node=exportNode, exists=True):
        SIP_AddFBXNodeAttrs(exportNode)

    animLayers = cmds.ls(type="animLayers")
    animLayerCommandStr = ""

    for curLayer in animLayers:
        mute = cmds.animLayer(curLayer, query=True, mute=True)
        solo = cmds.animLayer(curLayer, query=True, solo=True)
        animLayerCommandStr += (curLayer + ",  mute = " + str(mute) + ", solo = " + str(solo) + ";")

    cmds.setAttr(exportNode + "animLayers", animLayerCommandStr, type="string")




# PURPOSE:          Set the animLayers based on the string value in the exportNode.
# PROCEDURE:        Use the predefined sentinel values to split the string for the separate animLayers.
#                   And parse out the attributes and their values, then set.
# PRESUMPTION:      Uses ; as sentinel value to split separate animLayers.
#                   Uses , as sentinel value to split separate fields for animLayer.
#                   Uses = as sentinel value to split separate attrs from their values in field.
#                   Order is Layer, mute, solo.
def SIP_SetAnimLayersFromSettings(exportNode):
    if cmds.objExists(exportNode) and not cmds.objExists(exportNode + ".animLayers"):
        animLayersRootString = cmds.getAttr(exportNode + ".animLayers", asString=True)

        if animLayersRootString:
            animLayerEntries = animLayersRootString.split(";")

            for curEntry in animLayerEntries:
                if curEntry:
                    fields = curEntry.split(",")
                    animLayerField = fields[0]
                    curMuteField = fields[1]
                    curSoloField = fields[2]

                    muteFieldStr = curMuteField.split(" = ")
                    soloFieldStr = curSoloField.split(" = ")

                    # Convert string to bool values.
                    muteFieldBool = True
                    soloFieldBool = True

                    if muteFieldStr[1] != "True":
                        muteFieldBool = False

                    if soloFieldStr[1] != "True":
                        soloFieldBool = False

                cmds.animLayer(animLayerField, edit=True, mute=muteFieldBool, solo=soloFieldBool)





def SIP_ClearAnimLayerSettings(exportNode):
    cmds.setAttr(exportNode + ".animLayers", "", type="string")




######################################
#
#    Export procs
#
######################################



def SIP_ExportFBX(exportNode):
    curWorkspace = cmds.workspace(q=True, rd=True)
    fileName = cmds.getAttr(exportNode + ".exportName")

    if fileName:
        newFBX = curWorkspace + fileName
        cmds.file(newFBX, force=True, type='FBX export', pr=True, es=True)
    else:
        cmds.warning("No Valid Export Filename for Export Node " + exportNode + "\n")



def SIP_ExportFBXAnimation(character, exportNode):
    pass



def SIP_ExportFBXXharacter(exportNode):
    pass





# Message to make sure mayaCharm is working.
print("SUCCESSFULLY LOADED!")