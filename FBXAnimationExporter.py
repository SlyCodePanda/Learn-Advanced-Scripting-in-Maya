import maya.cmds as cmds
import maya.mel as mel
import string

# Need to store this mel file in a place that Maya can understand, like it's scripts folder.
mel.eval("source FBXAnimationExporter_FBXOptions.mel")


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
def SIP_ConnectFBXExportNodeToMeshes(exportNode, meshes):

    if cmds.objExists(exportNode):
        if not cmds.objExists(exportNode + ".exportMeshes"):
            SIP_AddFBXNodeAttrs(exportNode)

        for curMesh in meshes:
            if cmds.objExists(curMesh):
                if not cmds.objExists(curMesh + ".exportMeshes"):
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



def SIP_ExportFBXAnimation(characterName, exportNode):
    SIP_ClearGarbage()
    characters = []

    if characterName:
        characters.append(characterName)
    else:
        reference = cmds.file(reference=1, query=True)

        for curRef in reference:
            characters.append(cmds.file(curRef, namespace=1, query=True))

    for curCharacter in characters:
        # Get the meshes with blendshapes
        meshes = SIP_FindMeshWithBlendshapes(curCharacter)
        # Get origin.
        origin = SIP_ReturnOrigin(curCharacter)

        exportNodes = []

        if exportNode:
            exportNodes.append(exportNode)
        else:
            exportNodes = SIP_ReturnFBXExportNodes(origin)

        for curExportNode in exportNodes:
            if cmds.getAttr(curExportNode + ".export") and origin != "Error":
                exportRig = SIP_CopyAndConnectSkeleton(origin)

                startFrame = cmds.playbackOptions(query=True, minTime=1)
                endFrame = cmds.playbackOptions(query=True, minTime=1)

                subAnimCheck = cmds.getAttr(curExportNode + ".useSubRange")

                if subAnimCheck:
                    startFrame = cmds.getAttr(curExportNode + ".startFrame")
                    endFrame = cmds.getAttr(curExportNode + ".endFrame")

                if cmds.getAttr(curExportNode + ".moveToOrigin"):
                    newOrigin = cmds.listConnections(origin + ".translateX", source=False, d=True)
                    zeroOriginFlag = cmds.getAttr(curExportNode + ".zeroOrigin")
                    SIP_TransformToOrigin(newOrigin[0], startFrame, endFrame, zeroOriginFlag)

                cmds.select(clear=True)
                cmds.select(exportRig, add=True)
                cmds.select(meshes, add=True)

                SIP_SetAnimLayersFromSettings(curExportNode)

                mel.eval("SIP_SetFBXExportOptions_animation(" + str(startFrame) + "," + str(endFrame) + ")")

                SIP_ExportFBX(curExportNode)

            SIP_ClearGarbage()


def SIP_ExportFBXCharacter(exportNode):
    origin = SIP_ReturnOrigin("")
    exportNodes = []

    if exportNode:
        exportNodes.append(exportNode)
    else:
        exportNodes = SIP_ReturnFBXExportNodes(origin)

    parentNode = cmds.listRelatives(origin, parent=True, fullPath=True)

    if parentNode:
        cmds.parent(origin, world=True)

    for curExportNode in exportNodes:
        if cmds.getAttr(curExportNode + ".export"):
            mel.eval("SIP_SetFBXExportOptions_model()")

            cmds.select(clear=True)

            meshes = SIP_ReturnConnectedMeshes(curExportNode)
            cmds.select(origin, add=True)
            cmds.select(meshes, add=True)

            SIP_ExportFBX(curExportNode)

            if parentNode:
                cmds.parent(origin, parentNode[0])


######################################
#
#    UI Code
#
######################################

######################################
#
# Model UI Procs
#
######################################

# PURPOSE:           Populate the root joints panel in the model tab.
# PROCEDURE:         It will search for the origin. If none found, list all joints in the scene.
# PRESUMPTIONS:      Origin is going to be a joint. Rigs are not referenced in.
def SIP_FBXExporterUI_PopulateModelRootJointsPanel():
    cmds.textScrollList("sip_FBXExporter_window_modelsOriginTextScrollList", edit=True, removeAll=True)
    origin = SIP_ReturnOrigin("")

    if origin != "Error":
        cmds.textScrollList("sip_FBXExporter_window_modelsOriginTextScrollList", edit=True, ebg=False, append=origin)
    else:
        joints = cmds.ls(type="joint")
        for curJoint in joints:
            cmds.textScrollList("sip_FBXExporter_window_modelsOriginTextScrollList", edit=True, bgc=[1, 0.1, 0.1],
                                append=curJoint)

######################################
#
# Animation UI Procs
#
######################################

# PURPOSE:          To populate the actor panel in the UI.
# PROCEDURE:        Get list of all references in the scene. For each reference, get the namespace .
#                   Call SIP_ReturnOrigin for each namespace. If not "Error", add namespace to textScrollList.
# PRESUMPTIONS:     Single-layered referencing. References have namespace.
def SIP_FBXExporterUI_PopulateAnimationActorPanel():
    cmds.textScrollList("sip_FBXExporter_window_animationActorsTextScrollList", edit=True, removeAll=True)
    references = cmds.file(query=True, reference=True)

    for curRef in references:
        if not cmds.file(curRef, query=True, deferReference=True):
            ns = cmds.file(curRef, query=True, namespace=True)
            origin = SIP_ReturnOrigin(ns)

            if origin != "Error":
                cmds.textScrollList("sip_FBXExporter_window_animationActorsTextScrollList", edit=True, append=ns)


# Make UI
def SIP_FBXExporter_UI():
    if cmds.window("sip_FBXExporter_window", exists=True):
        cmds.deleteUI("sip_FBXExporter_window")

    cmds.window("sip_FBXExporter_window", s=True, width=700, height=500, menuBar=True, title="FBX Exporter")

    # Create menu bar commands
    cmds.menu("sip_FBXExporter_window_editMenu", label="Edit")
    cmds.menuItem(label="Save Settings", parent="sip_FBXExporter_window_editMenu")
    cmds.menuItem(label="Reset Settings", parent="sip_FBXExporter_window_editMenu")

    cmds.menu("sip_FBXExporter_window_helpMenu", label="Edit")
    cmds.menuItem(label="Help on Animation Export", parent="sip_FBXExporter_window_helpMenu")
    cmds.menuItem(label="Help on Model Export", parent="sip_FBXExporter_window_helpMenu")

    # Create main tab layout.
    cmds.formLayout("sip_FBXExporter_window_mainForm")
    cmds.tabLayout("sip_FBXExporter_window_tabLayout", innerMarginWidth=5, innerMarginHeight=5)
    cmds.formLayout("sip_FBXExporter_window_mainForm", edit=True,
                    attachForm=(
                        ("sip_FBXExporter_window_tabLayout", 'top', 0),
                        ("sip_FBXExporter_window_tabLayout", 'left', 0),
                        ("sip_FBXExporter_window_tabLayout", 'bottom', 0),
                        ("sip_FBXExporter_window_tabLayout", 'right', 0)))

    # Create animation UI elements.
    cmds.frameLayout("sip_FBXExporter_window_animationFrameLayout", collapse=False, label="", borderVisible=False,
                     parent="sip_FBXExporter_window_tabLayout")
    cmds.formLayout("sip_FBXExporter_window_animationFormLayout", numberOfDivisions=100,
                    parent="sip_FBXExporter_window_animationFrameLayout")
    cmds.textScrollList("sip_FBXExporter_window_animationActorsTextScrollList", width=250, height=325,
                        numberOfRows=18, allowMultiSelection=False,
                        parent="sip_FBXExporter_window_animationFormLayout")
    cmds.textScrollList("sip_FBXExporter_window_animationExportNodesTextScrollList", width=250, height=325,
                        numberOfRows=18, allowMultiSelection=False,
                        parent="sip_FBXExporter_window_animationFormLayout")
    cmds.button("sip_FBXExporter_window_animationNewExportNodeButton", width=250, height=50, label="New Export Node",
                parent="sip_FBXExporter_window_animationFormLayout")
    cmds.checkBoxGrp("sip_FBXExporter_window_animationExportCheckBoxGrp", numberOfCheckBoxes=1, label="Export",
                     columnWidth2=[85, 70], enable=False, parent="sip_FBXExporter_window_animationFormLayout")
    cmds.checkBoxGrp("sip_FBXExporter_window_animationZeroOriginCheckBoxGrp", numberOfCheckBoxes=1,
                     label="Move to Origin", columnWidth2=[85, 70], enable=False,
                     parent="sip_FBXExporter_window_animationFormLayout")
    cmds.checkBoxGrp("sip_FBXExporter_window_animationZeroOriginMotionCheckBoxGrp", numberOfCheckBoxes=1,
                     label="Zero Motion on Origin", columnWidth2=[120, 70], enable=False,
                     parent="sip_FBXExporter_window_animationFormLayout")
    cmds.checkBoxGrp("sip_FBXExporter_window_animationSubRangeCheckBoxGrp", numberOfCheckBoxes=1,
                     label="Use Sub Range", columnWidth2=[85, 70], enable=False,
                     parent="sip_FBXExporter_window_animationFormLayout")
    cmds.floatFieldGrp("sip_FBXExporter_window_animationStartFrameFloatFieldGrp", numberOfFields=1, label="Start Frame",
                       columnWidth2=[75, 70], enable=False, value1=0.0,
                       parent="sip_FBXExporter_window_animationFormLayout")
    cmds.floatFieldGrp("sip_FBXExporter_window_animationEndFrameFloatFieldGrp", numberOfFields=1, label="End Frame",
                       columnWidth2=[75, 70], enable=False, value1=1.0,
                       parent="sip_FBXExporter_window_animationFormLayout")
    cmds.textFieldButtonGrp("sip_FBXExporter_window_animationExportFileNameTextFieldButtonGrp",
                            label="Export File Name", columnWidth3=[100, 300, 30], enable=False, text='',
                            buttonLabel="Browse", parent="sip_FBXExporter_window_animationFormLayout")
    cmds.button("sip_FBXExporter_window_animationRecordAnimLayersButton", enable=False, width=150, height=50,
                label="Record Anim Layers", backgroundColor=[1, .25, .25],
                parent="sip_FBXExporter_window_animationFormLayout")
    cmds.button("sip_FBXExporter_window_animationPreviewAnimLayersButton", enable=False, width=250, height=50,
                label="Preview Anim Layers", parent="sip_FBXExporter_window_animationFormLayout")
    cmds.button("sip_FBXExporter_window_animationClearAnimLayersButton", enable=False, width=250, height=50,
                label="Clear Anim Layers", parent="sip_FBXExporter_window_animationFormLayout")
    cmds.text("sip_FBXExporter_window_animationActorText", label="Actors",
              parent="sip_FBXExporter_window_animationFormLayout")
    cmds.text("sip_FBXExporter_window_animationExportNodesText", label="Export Nodes",
              parent="sip_FBXExporter_window_animationFormLayout")
    cmds.button("sip_FBXExporter_window_animationExportSelectedAnimationButton", width=300, height=50,
                label="Export Selected Animation", parent="sip_FBXExporter_window_animationFormLayout")
    cmds.button("sip_FBXExporter_window_animationExportAllAnimationsForSelectedCharacterButton", width=300, height=50,
                label="Export All Animation for Selected Character",
                parent="sip_FBXExporter_window_animationFormLayout")
    cmds.button("sip_FBXExporter_window_animationExportAllAnimationsButton", width=300, height=50,
                label="Export All Animations", parent="sip_FBXExporter_window_animationFormLayout")

    cmds.popupMenu("sip_FBXExporter_window_animationExportNodesPopupMenu", button=3,
                   parent="sip_FBXExporter_window_animationExportNodesTextScrollList")
    cmds.menuItem("sip_FBXExporter_window_animationSelectNodeMenuItem", label="Select",
                  parent="sip_FBXExporter_window_animationExportNodesPopupMenu")
    cmds.menuItem("sip_FBXExporter_window_animationRenameNodeMenuItem", label="Rename",
                  parent="sip_FBXExporter_window_animationExportNodesPopupMenu")
    cmds.menuItem("sip_FBXExporter_window_animationDeleteNodeMenuItem", label="Delete",
                  parent="sip_FBXExporter_window_animationExportNodesPopupMenu")

    # Create model UI elements.
    cmds.frameLayout("sip_FBXExporter_window_modelFormLayout", collapse=False, label="", borderVisible=False,
                     parent="sip_FBXExporter_window_tabLayout")
    cmds.formLayout("sip_FBXExporter_window_modelFormLayout", numberOfDivisions=100,
                    parent="sip_FBXExporter_window_modelFormLayout")
    cmds.textScrollList("sip_FBXExporter_window_modelsOriginTextScrollList", width=175, height=220, numberOfRows=18,
                        allowMultiSelection=False, parent="sip_FBXExporter_window_modelFormLayout")
    cmds.textScrollList("sip_FBXExporter_window_modelsExportNodesTextScrollList", width=175, height=220,
                        numberOfRows=18, allowMultiSelection=False, parent="sip_FBXExporter_window_modelFormLayout")
    cmds.textScrollList("sip_FBXExporter_window_modelsGeomTextScrollList", width=175, height=220, numberOfRows=18,
                        allowMultiSelection=True, parent="sip_FBXExporter_window_modelFormLayout")
    cmds.button("sip_FBXExporter_window_modelTagAsOriginButton", width=175, height=50, label="Tag as Origin",
                parent="sip_FBXExporter_window_modelFormLayout")
    cmds.button("sip_FBXExporter_window_modelNewExportNodeButton", width=175, height=50, label="New Export Node",
                parent="sip_FBXExporter_window_modelFormLayout")
    cmds.button("sip_FBXExporter_window_modelAddRemoveMeshesButton", width=175, height=50, label="Add/Remove Meshes",
                parent="sip_FBXExporter_window_modelFormLayout")
    cmds.checkBoxGrp("sip_FBXExporter_window_modelExportCheckBoxGrp", numberOfCheckBoxes=1, label="Export",
                     columnWidth2=[85, 70], enable=False, parent="sip_FBXExporter_window_modelFormLayout")
    cmds.text("sip_FBXExporter_window_modelOriginText", label="Root Joints",
              parent="sip_FBXExporter_window_modelFormLayout")
    cmds.text("sip_FBXExporter_window_modelExportNodesText", label="Export Nodes",
              parent="sip_FBXExporter_window_modelFormLayout")
    cmds.text("sip_FBXExporter_window_modelsMeshesText", label="Meshes",
              parent="sip_FBXExporter_window_modelFormLayout")
    cmds.textFieldButtonGrp("sip_FBXExporter_window_modelExportFileNameTextFieldButtonGrp",
                            label="Export File Name", columnWidth3=[100, 300, 30], enable=False, text='',
                            buttonLabel="Browse", parent="sip_FBXExporter_window_modelFormLayout")
    cmds.button("sip_FBXExporter_window_modelExportMeshButton", width=175, height=50, label="Export Selected Character",
                parent="sip_FBXExporter_window_modelFormLayout")
    cmds.button("sip_FBXExporter_window_modelExportAllMeshesButton", width=250, height=50,
                label="Export All Characters", parent="sip_FBXExporter_window_modelFormLayout")

    cmds.popupMenu("sip_FBXExporter_window_modelExportNodesPopupMenu", button=3,
                   parent="sip_FBXExporter_window_modelsExportNodesTextScrollList")
    cmds.menuItem("sip_FBXExporter_window_modelSelectNodeMenuItem", label="Select",
                  parent="sip_FBXExporter_window_modelExportNodesPopupMenu")
    cmds.menuItem("sip_FBXExporter_window_modelRenameNodeMenuItem", label="Rename",
                  parent="sip_FBXExporter_window_modelExportNodesPopupMenu")
    cmds.menuItem("sip_FBXExporter_window_modelDeleteNodeMenuItem", label="Delete",
                  parent="sip_FBXExporter_window_modelExportNodesPopupMenu")

    # Set up tabs
    cmds.tabLayout("sip_FBXExporter_window_tabLayout", edit = True,
                   tabLabel=(("sip_FBXExporter_window_animationFrameLayout", "Animation"),
                             ("sip_FBXExporter_window_modelFormLayout", "Model")))

    # Set up animation form layout.
    cmds.formLayout("sip_FBXExporter_window_animationFormLayout", edit=True,
                    attachForm=
                    [("sip_FBXExporter_window_animationActorText", 'top', 5),
                    ("sip_FBXExporter_window_animationActorText", 'left', 5),
                    ("sip_FBXExporter_window_animationActorsTextScrollList", 'left', 5),
                    ("sip_FBXExporter_window_animationExportNodesText", 'top', 5),
                    ("sip_FBXExporter_window_animationExportCheckBoxGrp", 'top', 25),
                    ("sip_FBXExporter_window_animationZeroOriginCheckBoxGrp", 'top', 25),
                    ("sip_FBXExporter_window_animationZeroOriginMotionCheckBoxGrp", 'top', 25),
                    ("sip_FBXExporter_window_animationExportFileNameTextFieldButtonGrp", 'right', 5)])
    cmds.formLayout("sip_FBXExporter_window_animationFormLayout", edit=True,
                    attachControl=
                    [("sip_FBXExporter_window_animationExportNodesTextScrollList",'left', 5,
                    "sip_FBXExporter_window_animationActorsTextScrollList"),
                    ("sip_FBXExporter_window_animationExportCheckBoxGrp",'left', 20,
                    "sip_FBXExporter_window_animationExportNodesTextScrollList"),
                    ("sip_FBXExporter_window_animationZeroOriginCheckBoxGrp",'left', 5,
                    "sip_FBXExporter_window_animationExportCheckBoxGrp"),
                    ("sip_FBXExporter_window_animationZeroOriginMotionCheckBoxGrp",'left', 5,
                    "sip_FBXExporter_window_animationZeroOriginCheckBoxGrp")])

    cmds.formLayout("sip_FBXExporter_window_animationFormLayout", edit=True,
                    attachControl=
                    [("sip_FBXExporter_window_animationSubRangeCheckBoxGrp", 'left', 20,
                      "sip_FBXExporter_window_animationExportNodesTextScrollList"),
                     ("sip_FBXExporter_window_animationSubRangeCheckBoxGrp", 'top', 5,
                      "sip_FBXExporter_window_animationZeroOriginCheckBoxGrp")])
    cmds.formLayout("sip_FBXExporter_window_animationFormLayout", edit=True,
                    attachControl=[("sip_FBXExporter_window_animationStartFrameFloatFieldGrp", 'left', 30,
                                    "sip_FBXExporter_window_animationExportNodesTextScrollList"),
                                   ("sip_FBXExporter_window_animationStartFrameFloatFieldGrp", 'top', 5,
                                    "sip_FBXExporter_window_animationSubRangeCheckBoxGrp")])
    cmds.formLayout("sip_FBXExporter_window_animationFormLayout", edit=True,
                    attachControl=
                    [("sip_FBXExporter_window_animationEndFrameFloatFieldGrp", 'left', 1,
                      "sip_FBXExporter_window_animationStartFrameFloatFieldGrp"),
                     ("sip_FBXExporter_window_animationEndFrameFloatFieldGrp", 'top', 5,
                      "sip_FBXExporter_window_animationSubRangeCheckBoxGrp")])
    cmds.formLayout("sip_FBXExporter_window_animationFormLayout", edit=True,
                    attachControl=
                    [("sip_FBXExporter_window_animationExportFileNameTextFieldButtonGrp", 'left', 5,
                      "sip_FBXExporter_window_animationExportNodesTextScrollList"),
                     ("sip_FBXExporter_window_animationExportFileNameTextFieldButtonGrp", 'top', 5,
                      "sip_FBXExporter_window_animationStartFrameFloatFieldGrp")])
    cmds.formLayout("sip_FBXExporter_window_animationFormLayout", edit=True,
                    attachControl=[("sip_FBXExporter_window_animationNewExportNodeButton", 'left', 5,
                                    "sip_FBXExporter_window_animationActorsTextScrollList"),
                                   ("sip_FBXExporter_window_animationNewExportNodeButton", 'top', 5,
                                    "sip_FBXExporter_window_animationExportNodesTextScrollList")])
    cmds.formLayout("sip_FBXExporter_window_animationFormLayout", edit=True,
                    attachControl=
                    [("sip_FBXExporter_window_animationActorsTextScrollList", 'top', 5,
                      "sip_FBXExporter_window_animationActorText"),
                     ("sip_FBXExporter_window_animationExportNodesTextScrollList", 'top', 5,
                      "sip_FBXExporter_window_animationExportNodesText"),
                     ("sip_FBXExporter_window_animationExportNodesText", 'left', 225,
                      "sip_FBXExporter_window_animationActorText")])
    cmds.formLayout("sip_FBXExporter_window_animationFormLayout", edit=True,
                    attachControl=
                    [("sip_FBXExporter_window_animationRecordAnimLayersButton", 'top', 10,
                      "sip_FBXExporter_window_animationExportFileNameTextFieldButtonGrp"),
                     ("sip_FBXExporter_window_animationPreviewAnimLayersButton", 'top', 10,
                      "sip_FBXExporter_window_animationExportFileNameTextFieldButtonGrp"),
                     ("sip_FBXExporter_window_animationClearAnimLayersButton", 'top', 10,
                      "sip_FBXExporter_window_animationExportFileNameTextFieldButtonGrp")])
    cmds.formLayout("sip_FBXExporter_window_animationFormLayout", edit=True,
                    attachControl=
                    [("sip_FBXExporter_window_animationRecordAnimLayersButton", 'left', 10,
                      "sip_FBXExporter_window_animationExportNodesTextScrollList"),
                     ("sip_FBXExporter_window_animationPreviewAnimLayersButton", 'left', 10,
                      "sip_FBXExporter_window_animationRecordAnimLayersButton"),
                     ("sip_FBXExporter_window_animationClearAnimLayersButton", 'left', 10,
                      "sip_FBXExporter_window_animationPreviewAnimLayersButton")])
    cmds.formLayout("sip_FBXExporter_window_animationFormLayout", edit=True,
                    attachControl=
                    [("sip_FBXExporter_window_animationExportSelectedAnimationButton", 'top', 10,
                      "sip_FBXExporter_window_animationRecordAnimLayersButton"),
                     ("sip_FBXExporter_window_animationExportAllAnimationsForSelectedCharacterButton", 'top', 10,
                      "sip_FBXExporter_window_animationExportSelectedAnimationButton"),
                     ("sip_FBXExporter_window_animationExportAllAnimationsButton", 'top', 10,
                      "sip_FBXExporter_window_animationExportAllAnimationsForSelectedCharacterButton")])
    cmds.formLayout("sip_FBXExporter_window_animationFormLayout", edit=True,
                    attachControl=
                    [("sip_FBXExporter_window_animationExportSelectedAnimationButton", 'left', 100,
                      "sip_FBXExporter_window_animationExportNodesTextScrollList"),
                     ("sip_FBXExporter_window_animationExportAllAnimationsForSelectedCharacterButton", 'left', 100,
                      "sip_FBXExporter_window_animationExportNodesTextScrollList"),
                     ("sip_FBXExporter_window_animationExportAllAnimationsButton", 'left', 100,
                      "sip_FBXExporter_window_animationExportNodesTextScrollList")])

    # Set up model form layout.
    cmds.formLayout("sip_FBXExporter_window_modelFormLayout", edit=True,
                    attachForm=
                    [("sip_FBXExporter_window_modelOriginText", 'top', 5),
                     ("sip_FBXExporter_window_modelOriginText", 'left', 5),
                     ("sip_FBXExporter_window_modelExportNodesText", 'top', 5),
                     ("sip_FBXExporter_window_modelsMeshesText", 'top', 5),
                     ("sip_FBXExporter_window_modelsMeshesText", 'top', 5),
                     ("sip_FBXExporter_window_modelExportCheckBoxGrp", 'top', 25),
                     ("sip_FBXExporter_window_modelTagAsOriginButton", 'left', 5),])
    cmds.formLayout("sip_FBXExporter_window_modelFormLayout", edit= True,
                    attachControl=
                    [("sip_FBXExporter_window_modelExportNodesText", 'left', 125,
                      "sip_FBXExporter_window_modelOriginText"),
                     ("sip_FBXExporter_window_modelsMeshesText", 'left', 120,
                      "sip_FBXExporter_window_modelExportNodesText")])
    cmds.formLayout("sip_FBXExporter_window_modelFormLayout", edit= True,
                    attachControl=
                    [("sip_FBXExporter_window_modelsOriginTextScrollList", 'top', 5,
                      "sip_FBXExporter_window_modelOriginText"),
                     ("sip_FBXExporter_window_modelsExportNodesTextScrollList", 'top', 5,
                      "sip_FBXExporter_window_modelExportNodesText"),
                     ("sip_FBXExporter_window_modelsGeomTextScrollList", 'top', 5,
                      "sip_FBXExporter_window_modelsMeshesText")])
    cmds.formLayout("sip_FBXExporter_window_modelFormLayout", edit= True,
                    attachControl=
                    [("sip_FBXExporter_window_modelsExportNodesTextScrollList", 'left', 5,
                      "sip_FBXExporter_window_modelsOriginTextScrollList"),
                     ("sip_FBXExporter_window_modelsGeomTextScrollList", 'left', 5,
                      "sip_FBXExporter_window_modelsExportNodesTextScrollList")])
    cmds.formLayout("sip_FBXExporter_window_modelFormLayout", edit= True,
                    attachControl=
                    [("sip_FBXExporter_window_modelNewExportNodeButton", 'left', 5,
                      "sip_FBXExporter_window_modelsOriginTextScrollList"),
                     ("sip_FBXExporter_window_modelNewExportNodeButton", 'top', 5,
                      "sip_FBXExporter_window_modelsExportNodesTextScrollList")])
    cmds.formLayout("sip_FBXExporter_window_modelFormLayout", edit= True,
                    attachControl=
                    [("sip_FBXExporter_window_modelExportFileNameTextFieldButtonGrp", 'left', 5,
                      "sip_FBXExporter_window_modelsGeomTextScrollList"),
                     ("sip_FBXExporter_window_modelTagAsOriginButton", 'top', 5,
                      "sip_FBXExporter_window_modelsOriginTextScrollList")])
    cmds.formLayout("sip_FBXExporter_window_modelFormLayout", edit= True,
                    attachControl=
                    [("sip_FBXExporter_window_modelExportMeshButton", 'top', 15,
                      "sip_FBXExporter_window_modelExportFileNameTextFieldButtonGrp"),
                     ("sip_FBXExporter_window_modelExportMeshButton", 'left', 125,
                      "sip_FBXExporter_window_modelsGeomTextScrollList")])
    cmds.formLayout("sip_FBXExporter_window_modelFormLayout", edit= True,
                    attachControl=
                    [("sip_FBXExporter_window_modelAddRemoveMeshesButton", 'top', 5,
                      "sip_FBXExporter_window_modelsGeomTextScrollList"),
                     ("sip_FBXExporter_window_modelAddRemoveMeshesButton", 'left', 5,
                      "sip_FBXExporter_window_modelNewExportNodeButton")])
    cmds.formLayout("sip_FBXExporter_window_modelFormLayout", edit= True,
                    attachControl=
                    [("sip_FBXExporter_window_modelExportAllMeshesButton", 'top', 5,
                      "sip_FBXExporter_window_modelExportMeshButton"),
                     ("sip_FBXExporter_window_modelExportAllMeshesButton", 'left', 125,
                      "sip_FBXExporter_window_modelsGeomTextScrollList")])
    cmds.formLayout("sip_FBXExporter_window_modelFormLayout", edit= True,
                    attachControl=
                    [("sip_FBXExporter_window_modelExportFileNameTextFieldButtonGrp", 'top', 5,
                      "sip_FBXExporter_window_modelExportCheckBoxGrp"),
                     ("sip_FBXExporter_window_modelExportCheckBoxGrp", 'left', 125,
                      "sip_FBXExporter_window_modelsGeomTextScrollList")])

    # Populate ui
    SIP_FBXExporterUI_PopulateModelRootJointsPanel()
    SIP_FBXExporterUI_PopulateAnimationActorPanel()

    # scriptJob to refresh ui
    cmds.scriptJob(parent="sip_FBXExporter_window",
                   e=["PostSceneRead", "import FBXAnimationExporter as FBX\n"
                                       "FBX.SIP_FBXExporterUI_PopulateModelRootJointsPanel()"])
    cmds.scriptJob(parent="sip_FBXExporter_window",
                   e=["PostSceneRead", "import FBXAnimationExporter as FBX\n"
                                       "FBX.SIP_FBXExporterUI_PopulateAnimationActorPanel()"])





    cmds.showWindow("sip_FBXExporter_window")


# Message to make sure mayaCharm is working.
print("SUCCESSFULLY SOURCED!")