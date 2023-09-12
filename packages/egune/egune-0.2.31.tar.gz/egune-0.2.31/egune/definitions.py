from dataclasses import dataclass, field
from .utils import Dictable
from .enumerators import SlotType, IntentType, IssueType, IssueStatus, ResponseType, QuestionMode
from .dataclasses import SlotVal, Issue, ResolveAction
from typing import Any, List, Tuple, Union, Dict
from copy import deepcopy
from datetime import datetime


@Dictable.decorator
@dataclass
class SlotDef(Dictable):
    name: str
    type: SlotType = SlotType.ANY
    entities: List[str] = field(default_factory=list)
    intent: List[Tuple[str, Any]] = field(default_factory=list)
    options: Union[None, List[Any]] = None
    defaultQuestionAnswerValues: Union[None, List[Tuple[Any, Any]]] = None
    defaultQuestionCode: str = ""
    canUsePrev: bool = False


@Dictable.decorator
@dataclass
class IntentDefinition(Dictable):
    type: IntentType
    name: str
    removeOnly: List[str] = field(default_factory=list)
    removeAll: bool = False
    revoke: str = ""
    info: Dict[str, Any] = field(default_factory=dict)


@Dictable.decorator
@dataclass
class ResolveDefinition(Dictable):
    action: ResolveAction
    group: Union[None, str] = None
    slotValues: List[SlotVal] = field(default_factory=list)
    prohibitedActions: List[str] = field(default_factory=list)


@Dictable.decorator
@dataclass
class ResponseDefinition(Dictable):
    type: ResponseType
    code: str
    appId: str
    slots: List[str] = field(default_factory=list)
    slotVariations: Dict[List[str], str] = field(default_factory=dict)
    slotType: SlotType = SlotType.ANY
    questionMode: QuestionMode = QuestionMode.INTENT_FILL
    relatedSlot: Union[None, str] = None
    slotFillValue: Union[None, Any] = None
    relatedIssues: Union[None, str] = None


def find_slot(slotDef: SlotDef, context=None, userMessage=None):
    slotName = slotDef.name
    if userMessage is not None:
        for entity_name in slotDef.entities:
            entity_val = userMessage.get_entity_val(entity_name)
            if entity_val is not None:
                return SlotVal(slotName, entity_name, entity_val, None)
        for intent, value in slotDef.intent:
            if intent in userMessage.intent.positives:
                return SlotVal(slotName, None, value, None)
    if slotDef.canUsePrev and context is not None:
        for prev_issue in (context.activeIssues + context.inactiveIssues)[::-1]:
            if slotName in prev_issue.slotValues:
                return deepcopy(prev_issue.slotValues[slotName])
        else:
            for entity_name in slotDef.entities:
                for entity in context.pastEntities[::-1]:
                    if entity.name == entity_name:
                        return SlotVal(slotName, entity_name, entity.val, None)
    return None


@Dictable.decorator
@dataclass
class GroupDefinition(Dictable):
    type: IssueType = IssueType.INFO
    name: str = ""
    slotNames: List[str] = field(default_factory=list)
    possibleResolves: List[ResolveDefinition] = field(default_factory=list)
    relatedQuestion: Union[None, str] = None

    def build_issue(self, slotDefs: List[SlotDef], id=None, context=None, userMessage=None):
        filled_slots = {}
        for slotDef in slotDefs:
            slot = find_slot(slotDef, context, userMessage)
            if slot is not None:
                filled_slots[slotDef.name] = slot

        return Issue(
            id=Issue.new_id() if id is None else id,
            type=self.type,
            name=self.name,
            created=datetime.now(),
            assignees=[],
            status=IssueStatus.ACTIVE,
            resolveAttempts=[],
            slotValues=filled_slots,
            expectingAnswers=[],
            activeGroup=None
        )


@Dictable.decorator
@dataclass
class EventDefinition(Dictable):
    name: str = ""
    issue: Union[None, str] = None
    codes: List[str] = field(default_factory=list)
    onFail: str = ""
