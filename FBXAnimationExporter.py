import maya.cmds as cmds
import maya.mel as mel
import string


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




# Message to make sure mayaCharm is working.
print("SUCCESSFULLY LOADED!")