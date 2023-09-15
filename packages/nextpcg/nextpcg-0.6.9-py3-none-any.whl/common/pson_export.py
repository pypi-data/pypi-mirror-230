import json

types = ["Mesh", "Curve", "Volume", "Instance", "Heightfield"]


class next_output:

    def __init__(self, index, intype, label):
        self.index = index
        self.type = intype
        self.label = label

    def __eq__(self, o):
        if o.index == self.index:
            if o.type != self.type or o.label != self.label:
                return True
            else:
                return False
        else:
            return False

    def __repr__(self):
        return "index is {}; type is {}; label is {}".format(self.index, types[self.type], self.label)


# Get Input/Output Dict
def getInputOutput(node, jsondata):
    # get input tuple
    jsoninputdata = {}
    input_idx = 0
    for in_name in node.inputNames():
        json_temp_in = {}
        json_temp_in["label"] = node.inputLabels()[input_idx]
        jsoninputdata[in_name] = json_temp_in
        input_idx = input_idx + 1
    jsondata["Inputs"] = jsoninputdata
    # get output tuple
    jsonoutputdata = {}
    output_idx = 0
    for out_name in node.outputNames():
        json_temp_out = {}
        json_temp_out["label"] = node.outputLabels()[output_idx]
        jsonoutputdata[out_name] = json_temp_out
        output_idx = output_idx + 1
    jsondata["Outputs"] = jsonoutputdata


def getInputOutput_new(input, jsondata):
    if input:
        # ds = input.dependents(True)
        ds = input.allSubChildren(top_down=True, recurse_in_locked_nodes=False)
        bcontain = 0
        for d in ds:
            td = d.type().name()
            if td == 'next_output':
                bcontain = 1

    out_name_index = 1
    jsonoutputdata = {}
    index_array = []
    if bcontain == 1:
        jsondata["Outputs"] = {}
        for d in ds:
            td = d.type().name()
            if td == 'next_output':
                output_index = d.parm("output_index").evalAsInt()
                output_type = d.parm("output_type").evalAsInt()
                output_label = d.parm("output_label").evalAsString()
                output = next_output(output_index, output_type, output_label)
                if output in index_array:
                    # check the output index
                    node_path = d.path()
                    hou.ui.displayMessage(
                        'The index of the below output is conflict !!! \n {} \n {}'.format(node_path, output))
                    print(node_path)
                    jsonoutputdata = {}
                    return False
                index_array.append(output)

                json_temp_out = {}
                # types = ["Mesh", "Curve", "Volume", "Instance", "Heightfield"]
                json_temp_out["label"] = types[output_type] + ' ' + output_label
                json_temp_out["index"] = output_index
                # json_temp_out["name"] = output_label
                out_name = 'output' + str(out_name_index)
                out_name_index += 1
                jsonoutputdata[out_name] = json_temp_out
        jsondata["Outputs"] = jsonoutputdata
        return True
    else:
        # Compatible with old methods
        return True

    # get all parmTemplates


def allParmTemplates(group_or_folder):
    for parm_template in group_or_folder.parmTemplates():
        yield parm_template

    # Note that we don't want to return parm templates inside multiparm
    # blocks, so we verify that the folder parm template is actually
    # for a folder.
    # if (parm_template.type() == hou.parmTemplateType.Folder and parm_template.isActualFolder()):
    #    for sub_parm_template in allParmTemplates(parm_template):
    #        yield sub_parm_template


# Get Parm Template
def getParmTemplate(parm, jsondata):
    # export visiable parameters only
    # if parm.isVisible():
    if not parm.isHidden():
        # get parmTemplate data
        key = parm.name()
        jsontmpdata = {}

        jsontmpdata["Label"] = parm.label()
        jsontmpdata["Data Type"] = str(parm.dataType())
        jsontmpdata["Help"] = parm.help()
        jsontmpdata["Tags"] = parm.tags()

        parmtype = parm.type()
        jsontmpdata["Type"] = str(parmtype)

        if parmtype == hou.parmTemplateType.Int:
            jsontmpdata["Default Value"] = parm.defaultValue()
            jsontmpdata["Min Value"] = parm.minValue()
            jsontmpdata["Max Value"] = parm.maxValue()

        if parmtype == hou.parmTemplateType.Float:
            jsontmpdata["Default Value"] = parm.defaultValue()
            jsontmpdata["Min Value"] = parm.minValue()
            jsontmpdata["Max Value"] = parm.maxValue()

        if parmtype == hou.parmTemplateType.String:
            jsontmpdata["Default Value"] = parm.defaultValue()
            jsontmpdata["String Type"] = str(parm.stringType())
            jsontmpdata["File Type"] = str(parm.fileType())
            jsontmpdata["Menu Type"] = str(parm.menuType())
            jsontmpdata["Menu Items"] = parm.menuItems()
            jsontmpdata["Menu Labels"] = parm.menuLabels()

        if parmtype == hou.parmTemplateType.Toggle:
            jsontmpdata["Default Value"] = parm.defaultValue()

        if parmtype == hou.parmTemplateType.Menu:
            jsontmpdata["Menu Items"] = parm.menuItems()
            jsontmpdata["Menu Labels"] = parm.menuLabels()
            jsontmpdata["Default Value"] = parm.defaultValue()
            jsontmpdata["Menu Type"] = str(parm.menuType())

        if parmtype == hou.parmTemplateType.Folder:

            is_actual_folder = parm.isActualFolder()
            is_multiparam = not is_actual_folder

            if is_multiparam:
                jsontmpdata["Folder Type"] = str(parm.folderType())
                jsontmpdata["Folder Actural"] = str(is_actual_folder)

                folderjsondata = {}
                folderparams = parm.parmTemplates()
                for folderparam in folderparams:
                    getParmTemplate(folderparam, folderjsondata)
                    jsontmpdata["Folder Parm Template"] = folderjsondata

                jsontmpdata["Folder Tab Conditionals"] = str(parm.tabConditionals())
                jsontmpdata["Folder Tab Group Ends"] = str(parm.endsTabGroup())
            else: # kivlin. skip the pure folder and keep recursive to find the real parameter.
                folderparams = parm.parmTemplates()
                for folderparam in folderparams:
                    getParmTemplate(folderparam, jsondata)
                return # kivlin. return here to skip the pure folder itself to serialize.

        if parmtype == hou.parmTemplateType.FolderSet:
            jsontmpdata["Folder Names"] = parm.folderNames()
            jsontmpdata["Folder Type"] = str(parm.folderType())
            jsontmpdata["Folder Style"] = str(parm.folderStyle())

        if parmtype == hou.parmTemplateType.Label:
            jsontmpdata["Column Labels"] = parm.columnLabels()

        if parmtype == hou.parmTemplateType.Ramp:
            jsontmpdata["Default Value"] = parm.defaultValue()
            jsontmpdata["Default Basis"] = parm.defaultBasis()
            jsontmpdata["Parm Type"] = str(parm.parmType())

        # make Default Value as array
        if "Default Value" in jsontmpdata:
            if type(jsontmpdata["Default Value"]) == tuple:
                pass
            else:
                jsontmpdata["Default Value"] = (jsontmpdata["Default Value"],)

        # for each param data
        jsondata[str(key)] = jsontmpdata


# Get Parm Dict
def getParmDict(node, jsondata):
    # get parms tuple
    # parm_groups = node.parms()
    # parms = node.parmTemplateGroup().parmTemplates()

    parm_groups = node.parmTemplateGroup()

    jsonparamdata = {}
    rootkey = "Params"
    for parm in allParmTemplates(parm_groups):
        # export visiable parameters only
        # if parm.isVisible():
        getParmTemplate(parm, jsonparamdata)
    # for each .hda data
    jsondata[rootkey] = jsonparamdata


def export_pson(kwargs):
    # main
    self = kwargs['node']
    # input data
    nodes = self.inputs()

    if len(nodes) == 0:
        hou.ui.displayMessage("Export needs having an input!")
        return

    txt_path = self.parm("save_path").evalAsString()

    if txt_path == '':
        hou.ui.displayMessage("Export needs having a path!")
        return

    # collect data
    jsondata = {}

    node = nodes[0]
    # hda path
    hdaFile = node.type().definition().libraryFilePath()
    hdaname = hdaFile.split('/')[-1]

    #    if 'HoudiniProjects' in hdaFile and txt_path == '':
    #        hdapath = hdaFile.split('HoudiniProjects')[0]
    #        psonPath = hdapath + 'HoudiniClient/TestNextPCG/NextPCG/pson/' # + hdaname.split('.hda')[0] + '.pson'
    #        self.parm("save_path").set(psonPath)

    hdajsondata = {}

    getParmDict(node, hdajsondata)  # collect params

    getInputOutput(node, hdajsondata)  # collect inputs/outputs

    # kivlin, raw output count the avoid merge node.
    hda_native_output_count = len(hdajsondata['Outputs'])

    bget = getInputOutput_new(node, hdajsondata)  # new method to collect inputs/outputs

    if bget and len(hdajsondata['Outputs']) > 0:
        jsondata[hdaname] = hdajsondata
        jsondata['hda_native_output_count'] = hda_native_output_count
        jsondata['io_mode'] = 2  # default io mode as houdini_binary
        # auto path
        # txt_path = txt_path + hdaname + ".pson"
        txt_path = txt_path + hdaname.split('.hda')[0] + '.pson'
        # export file
        with open(txt_path, 'w') as json_file:
            json.dump(jsondata, json_file)
        hou.ui.displayMessage("Export: " + txt_path + " successfully!!")


