
from fmp import wrappers_pb2 as fmp_wrappers
import google.protobuf.wrappers_pb2 as pb
from arista.studio.v1 import models, services
from arista.workspace.v1 import models as wsmodels, services as wsservices
from google.protobuf.json_format import MessageToDict


wsID = 'ws-autofill'
studioID = 'autofill-studio'
autofillInputID = "autofill-binding-input"
autofillActionID = "SomeActionID"
autofillActionDesc = "Does some autofill action"


def setWS(workspaceId: str):
    wid = pb.StringValue(value=workspaceId)
    key = wsmodels.WorkspaceKey(workspace_id=wid)

    workspace = wsmodels.WorkspaceConfig(
        key=key,
        display_name=pb.StringValue(value="Autofill testing ws"),
    )

    req = wsservices.WorkspaceConfigSetRequest(
        value=workspace
    )
    reqDict = MessageToDict(req)
    print(f"workspace req dict: \n{reqDict}\n")


def setStudio(studioId: str, workspaceId: str):
    wid = pb.StringValue(value=workspaceId)
    sid = pb.StringValue(value=studioId)
    key = models.StudioKey(studio_id=sid,
                           workspace_id=wid)

    rootInputID = "root"

    autofillInput = models.InputField(
        id=pb.StringValue(value=autofillInputID),
        name=pb.StringValue(value=autofillInputID),
        label=pb.StringValue(value=autofillInputID),
        type=models.INPUT_FIELD_TYPE_STRING,
        string_props=models.StringInputFieldProps()
    )

    groupProps = models.GroupInputFieldProps(
        members=fmp_wrappers.RepeatedString(
            values=[autofillInputID]
        )
    )
    rootInput = models.InputField(
        id=pb.StringValue(value=rootInputID),
        type=models.INPUT_FIELD_TYPE_GROUP,
        group_props=groupProps,
    )

    fields = models.InputFields(values={
        autofillInputID: autofillInput,
        rootInputID: rootInput,
    })
    inputSchema = models.InputSchema(fields=fields)

    updatedStudio = models.StudioConfig(
        key=key,
        display_name=pb.StringValue(value="Autofill testing studio"),
        template=models.Template(
            type=models.TEMPLATE_TYPE_MAKO,
            body=pb.StringValue(value=""),
        ),
        input_schema=inputSchema
    )

    req = services.StudioConfigSetRequest(
        value=updatedStudio
    )
    reqDict = MessageToDict(req)
    print(f"Studio req dict: \n{reqDict}\n")


def setAutofills(studioId: str, workspaceId: str):
    binding = models.AutofillActionConfig(
        key=models.AutofillActionKey(
            studio_id=pb.StringValue(value=studioId),
            workspace_id=pb.StringValue(value=workspaceId),
            input_field_id=pb.StringValue(value=autofillInputID),
        ),
        action_id=pb.StringValue(value=autofillActionID),
        description=pb.StringValue(value=autofillActionDesc),
    )

    req = services.AutofillActionConfigSetRequest(
        value=binding
    )

    reqDict = MessageToDict(req)
    print(f"Autofill req dict: \n{reqDict}\n")


def getAutofills(studioId: str, workspaceId: str):
    binding = models.AutofillAction(
        key=models.AutofillActionKey(
            studio_id=pb.StringValue(value=studioId),
            workspace_id=pb.StringValue(value=workspaceId),
        ),
    )

    req = services.AutofillActionStreamRequest(
        partial_eq_filter=[binding]
    )

    reqDict = MessageToDict(req)
    print(f"Autofill stream dict: \n{reqDict}\n")


setWS(wsID)
setStudio(studioID, wsID)
setAutofills(studioID, wsID)
getAutofills(studioID, wsID)
