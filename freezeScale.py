import maya.cmds as cmds
import sys  # just for beautiful warnings output
import json, ast  # dealing with unicode characters
import re  # regex

# Paul Popov, 11/7/2022

selOld = cmds.ls(sl=1)
sizeSel = len(selOld)
if sizeSel != 1:
    sys.stdout.write('You should select one object!')
else:
    newGroupName = 'cleanGroup'
    cmds.group(em=True, name=newGroupName, w=1)
    cmds.parent(cmds.duplicate(selOld, rr=1, ic=1), newGroupName)
    cmds.makeIdentity(apply=True, t=0, r=0, s=1, n=0)
    selNew = cmds.ls(sl=1)
    cmds.rename(selNew, selOld)

    # Unicode names
    selNewS = str(selNew)
    selNewS = selNewS[3:]
    selNewS = selNewS[:-2]
    selOldS = str(selOld)
    selOldS = selOldS[3:]
    selOldS = selOldS[:-2]
    selOldS = '|'+selOldS

    def hierarchyTree(parent, tree):
        children = cmds.listRelatives(parent, c=True, type='transform', pa=1)
        if children:
            tree[parent] = (children, {})
            for child in children:
                hierarchyTree(child, tree[parent][1])


    hierarchy_tree_old = {}
    hierarchyTree(selOldS, hierarchy_tree_old)
    hierarchy_tree_old_clean = {}
    hierarchy_tree_old_clean = ast.literal_eval(json.dumps(hierarchy_tree_old))
    hierarchy_tree_new = {}
    hierarchyTree(newGroupName, hierarchy_tree_new)
    hierarchy_tree_new_clean = {}
    hierarchy_tree_new_clean = ast.literal_eval(json.dumps(hierarchy_tree_new))
    od = str(hierarchy_tree_old_clean)
    od = od.replace('"', "'")
    pattern = "(?:\[|\s)\'\|.*?(?:\'\],|\',)"
    olist = re.findall(pattern, od)
    olist.insert(0, selOldS)
    list_str = [s.strip(" ['],") for s in olist]
    list_str[:] = [re.sub(r".*?\:\s\[\[\'", "", x) for x in list_str]

    # Time range
    anim_startTime = cmds.playbackOptions(ast=True, q=True)
    anim_endTime = cmds.playbackOptions(aet=True, q=True)

    # The main task
    for x in list_str:
        pc = cmds.parentConstraint(x, "|" + newGroupName + x, mo=0)
        cmds.bakeResults(("|" + newGroupName + x), simulation=True, t=(anim_startTime, anim_endTime), at=["tx", "ty", "tz", "rx", "ry", "rz", "visibility"], hi="none")
        cmds.delete(pc)

    sys.stdout.write('Done')