from dataclasses import dataclass, field
from typing import Dict, Any, List, Tuple, Union
from datetime import datetime
from .enumerators import (
    CreatorType, SlotType, QuestionMode,
    IssueType, IssueStatus, ResolveActionType
)
from .utils import Dictable


@Dictable.decorator
@dataclass
class Text(Dictable):
    mutations: Dict[str, str] = field(default_factory=dict)

    def __init__(self, mutations: Union[str, Dict[str, str]]):
        if isinstance(mutations, str):
            self.mutations = {"original": mutations}
        else:
            self.mutations = mutations

    def add_mutation(self, key, mutation):
        self.mutations[key] = mutation

    def get(self, key="original") -> str:
        return self.mutations[key] if key in self.mutations else ""


@Dictable.decorator
@dataclass
class Entity(Dictable):
    name: str
    val: str
    input_type: str = "original"
    sidx: int = 0
    eidx: int = 0
    confidence: float = 0.0


@Dictable.decorator
@dataclass
class Intent(Dictable):
    chosen: str = ""
    scores: Dict[str, float] = field(default_factory=dict)
    positives: List[str] = field(default_factory=list)
    negatives: List[str] = field(default_factory=list)
    issue_intents: List[str] = field(default_factory=list)


@Dictable.decorator
@dataclass
class ResolveAction(Dictable):
    id: str
    endpoint: Union[None, str] = None
    apiResponses: Dict[str, str] = field(default_factory=dict)
    responseCodes: List[str] = field(default_factory=list)
    next_group: Union[None, str] = None
    subflow: Union[None, str] = None
    type: ResolveActionType = ResolveActionType.RESPONSE


@Dictable.decorator
@dataclass
class ResolveAttempt(Dictable):
    resolveAction: ResolveAction
    id: str = field(default_factory=Dictable.new_id)
    created: datetime = field(default_factory=datetime.now)
    accepted: Union[None, bool] = None
    creator: CreatorType = CreatorType.BOT
    signature: str = ""

    def is_equal(self, other):
        return self.resolveAction == other.resolveAction


@Dictable.decorator
@dataclass
class Question(Dictable):
    code: str
    type: SlotType = SlotType.ANY
    mode: QuestionMode = QuestionMode.SLOT
    relatedSlotName: Union[None, str] = None
    slotFillValue: Union[None, List[Tuple[str, Any]]] = None
    relatedIssueName: Union[None, str] = None
    resolveId: Union[None, str] = None


@Dictable.decorator
@dataclass
class SlotVal(Dictable):
    name: str
    takenFromEntity: Union[None, str] = None
    value: Union[None, Any] = None  # TODO what if user dont want to give info
    default: Union[None, Any] = None

    def update_value(self, msg):
        if self.takenFromEntity is not None:
            self.value = msg.get_entity_val(self.takenFromEntity)


@Dictable.decorator
@dataclass
class Issue(Dictable):
    name: str
    created: datetime = field(default_factory=datetime.now)
    id: str = field(default_factory=Dictable.new_id)
    type: IssueType = IssueType.INFO
    assignees: List[str] = field(default_factory=list)
    status: IssueStatus = IssueStatus.ACTIVE
    resolveAttempts: List[ResolveAttempt] = field(default_factory=list)
    slotValues: Dict[str, SlotVal] = field(default_factory=dict)
    expectingAnswers: List[Question] = field(default_factory=list)
    activeGroup: Union[None, str] = None


@Dictable.decorator
@dataclass
class UserSignature(Dictable):
    userId: Union[None, str] = None
    email: List[str] = field(default_factory=list)
    phone: List[str] = field(default_factory=list)


@Dictable.decorator
@dataclass
class Response(Dictable):
    code: str = ""
    appId: str = ""
    relatedSlot: Union[None, str] = None
    relatedIssueId: Union[None, str] = None


@Dictable.decorator
@dataclass
class Context(Dictable):
    userSignature: UserSignature = field(default_factory=lambda : UserSignature.from_dict({}))
    variables: Dict[str, SlotVal] = field(default_factory=dict)
    activeIssues: List[Issue] = field(default_factory=list)
    inactiveIssues: List[Issue] = field(default_factory=list)
    impendingQuestions: List[Question] = field(default_factory=list)
    impendingNotifications: List[str] = field(default_factory=list)
    lastResponseCodes: List[str] = field(default_factory=list)
    pastEntities: List[Entity] = field(default_factory=list)
    pastIntents: List[Intent] = field(default_factory=list)
    appId: str = ""
    incompleteIntents: List[str] = field(default_factory=list)
    topics: List[str] = field(default_factory=list)
    logs: List[Tuple[Text, Intent, List[Entity], Any]] = field(default_factory=list)

    def apply_last_responses(self, responses: List[Response]):
        self.lastResponseCodes = [resp.code for resp in responses]

    def get_issue(self, issueId) -> Union[None, Issue]:
        for issue in self.activeIssues + self.inactiveIssues:
            if issue.id == issueId:
                return issue
        return None

    def get_resolve(self, resolveId) -> Union[None, ResolveAttempt]:
        for issue in self.activeIssues + self.inactiveIssues:
            for resolve in issue.resolveAttempts:
                if resolve.id == resolveId:
                    return resolve
        return None


@Dictable.decorator
@dataclass
class UserMessage(Dictable):
    user_id: str = ""
    app_id: str = ""
    channel_id: str = ""
    text: Union[None, Text] = None
    intent: Union[None, Intent] = None
    entities: List[Entity] = field(default_factory=list)
    context: Union[None, Context] = None
    misc: Dict[Any, Any] = field(default_factory=dict)

    def select(self, key):
        args = key.split(":")
        if args[0] == "text":
            return self.text.get(args[1])  # type:ignore
        elif args[0] == "intent":
            return self.intent.chosen  # type:ignore
        elif args[0] == "entity":
            for e in self.entities:  # type:ignore
                if e.name == args[1]:
                    return e.val
        return ""

    def get_entity_val(self, name, default=None):
        if self.entities is not None:
            for e in self.entities:
                if e.name == name:
                    return e.val
        return default


@Dictable.decorator
@dataclass
class BotMessage(Dictable):
    user_id: str = ""
    app_id: str = ""
    channel_id: str = ""
    code: Union[None, str] = None
    text: Union[None, str] = None
    buttons: List[str] = field(default_factory=list)
    misc: Any = None


@Dictable.decorator
@dataclass
class Event(Dictable):
    name: str = ""
    responseCode: Union[None, str] = None
    issueQuestions: List[Question] = field(default_factory=list)
    responseVars: Any = None
    isFailed: bool = False
