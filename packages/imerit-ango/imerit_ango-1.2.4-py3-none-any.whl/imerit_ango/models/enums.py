from enum import Enum


class TaskStatus(Enum):
    TODO = 'TODO'
    COMPLETED = 'Completed'


class Metrics(Enum):
    LabelStageGroups = 'LabelStageGroups'
    TimePerTask = 'TimePerTask'
    AnnotationStatus = 'AnnotationStatus'
    AnswerDistribution = 'AnswerDistribution'
    ConsensusRanges = 'ConsensusRanges'
    AssetSize = 'AssetSize'
