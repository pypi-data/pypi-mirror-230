import numpy as np
import pandas as pd
import sys
from numba import njit
from abc import ABC, abstractmethod
from hcai_datasets.hcai_nova_dynamic.utils.nova_string_utils import merge_role_key
from nova_utils.db_utils import nova_types as nt

# TODO: Currently we do not take the rest class into account when calculating the label for the frame. Maybe we should do this
@njit
def _get_overlap(a, start, end):
    """
    Calculating all overlapping intervals between the given array of time intervals and the interval [start, end]
    Args:
        a (): numpy array of shape (1,2), where each entry contains an interval [from, to]
        start (): start of the interval to check
        end (): end of the interval to check

    Returns:
    Numpy array with boolean values. The array is true where the interval specified in a overlaps [start, end]
    """
    annos_for_sample = (
        # annotation is bigger than frame
        ((a[:, 0] <= start) & (a[:, 1] >= end))
        # end of annotation is in frame
        | ((a[:, 1] >= start) & (a[:, 1] <= end))
        # start of annotation is in frame
        | ((a[:, 0] >= start) & (a[:, 0] <= end))
    )
    return annos_for_sample


def _get_anno_majority(a, overlap_idxs, start, end):
    """
    Returns the index of the annotation with the largest overlap with the current frame
    Args:
        a (): numpy array of shape (1,2), where each entry contains an interval [from, to]
        overlap_idxs (): aray of boolean values where a is overlapping the intervall [start, end] (as returned by get _get_overlap())
        start (): start of the interval to check
        end (): end of the interval to check

    Returns:

    """
    # TODO: rewrite for numba jit
    majority_index = -1
    overlap = 0
    for i in np.where(overlap_idxs)[0]:
        if (
            cur_overlap := np.minimum(end, a[i][1]) - np.maximum(start, a[i][0])
        ) > overlap:
            overlap = cur_overlap
            majority_index = i
    return majority_index


def _is_garbage(local_label_id, nova_garbage_label_id):
    # check for nan or compare with garbage label id
    if local_label_id != local_label_id or local_label_id == nova_garbage_label_id:
        return True
    return False


class Annotation(ABC):

    # Uniform label for garbage class handling in python
    GARBAGE_LABEL_ID = np.NAN

    def __init__(self, role: str = "", scheme: str = "", is_valid: bool = True):
        self.role = role
        self.scheme = scheme
        self.is_valid = is_valid

        # Gets set when set_annotation_from_mongo_doc is called
        self.data = None

    @abstractmethod
    def get_info(self):
        """
        Returns the labels for this annotation to create the DatasetInfo for tensorflow
        """
        raise NotImplementedError

    @abstractmethod
    def set_annotation_from_mongo_doc(self, session, time_to_ms=False):
        """
        Returns the labels for this annotation to create the DatasetInfo for tensorflow
        """
        raise NotImplementedError

    @abstractmethod
    def get_label_for_frame(self, start: int, end: int) -> object:
        """
        Returns the label for this frame

        Args:
            start (int): Start time of the frame in milliseconds
            end (int): End time of the frame in milliseconds
        """
        raise NotImplementedError

    @abstractmethod
    def postprocess(self):
        """
        Default post-processing for the respective annotation type
        """
        raise NotImplementedError


class DiscreteAnnotation(Annotation):

    # Class ids and string names as provided from NOVA-DB and required by SSI
    NOVA_REST_CLASS_NAME = "REST"
    NOVA_GARBAGE_LABEL_ID = -1

    # Initialize Rest class id with garbage class id
    REST_LABEL_ID = NOVA_GARBAGE_LABEL_ID

    def __init__(self, labels: dict = None, add_rest_class=False, **kwargs):
        super().__init__(**kwargs)
        self.dataframe = None
        self.type = nt.AnnoTypes.DISCRETE
        self.labels = {
            x["id"]: x["name"] if x["isValid"] else ""
            for x in sorted(labels, key=lambda k: k["id"])
        }
        self.add_rest_class = add_rest_class
        if self.add_rest_class:
            self.REST_LABEL_ID = max(self.labels.keys()) + 1
            self.labels[self.REST_LABEL_ID] = self.NOVA_REST_CLASS_NAME

    def get_info(self):
        return merge_role_key(self.role, self.scheme), {"dtype": np.int32, "shape": 1}

    def set_annotation_from_mongo_doc(self, mongo_doc, time_to_ms=False):
        self.data = mongo_doc
        if time_to_ms:
            for d in self.data:
                d["from"] = int(float(d["from"]) * 1000)
                d["to"] = int(float(d["to"]) * 1000)

        # Creating Pandas Dataframe version of annotations
        self.dataframe = pd.DataFrame(self.data)

        # Create
        if self.dataframe.empty:
            self.data_interval = np.empty((0, 2), int)
            self.data_values = np.empty((0, 2), int)
        else:
            # Creating numpy array of annotations for fast access
            # Splitting the annotations into interval and data array
            self.data_interval = self.dataframe[["from", "to"]].values.astype(int)
            self.data_values = self.dataframe[["id", "conf"]].values

    def get_label_for_frame_legacy(self, start, end):

        # If we don't have any data we return the garbage label
        if self.data == -1:
            return -1

        else:
            # Finding all annos that overlap with the frame
            def is_overlapping(af, at, ff, ft):

                # anno is larger than frame
                altf = af <= ff and at >= ft

                # anno overlaps frame start
                aofs = at >= ff and at <= ft

                # anno overlaps frame end
                aofe = af >= ff and af <= ft

                return altf or aofs or aofe

            annos_for_sample = list(
                filter(
                    lambda x: is_overlapping(x["from"], x["to"], start, end), self.data
                )
            )

            # No label matches
            if not annos_for_sample:
                if self.add_rest_class:
                    return len(self.labels.values()) - 1
                else:
                    return -1

            majority_sample_idx = np.argmax(
                list(
                    map(
                        lambda x: min(end, x["to"]) - max(start, x["from"]),
                        annos_for_sample,
                    )
                )
            )

            return annos_for_sample[majority_sample_idx]["id"]

    def get_label_for_frame_np(self, start, end):

        overlap_idxs = _get_overlap(self.data_interval, start, end)

        # If no label overlaps the requested frame we return rest class. If add_rest_class = False garbage label will be returned instead
        if not overlap_idxs.any():
            return self.REST_LABEL_ID

        majority_idx = _get_anno_majority(self.data_interval, overlap_idxs, start, end)
        label = self.data_values[majority_idx, 0]
        if _is_garbage(label, self.NOVA_GARBAGE_LABEL_ID):
            return Annotation.GARBAGE_LABEL_ID
        return label

    def get_label_for_frame(self, start, end):
        return self.get_label_for_frame_np(start, end)

    # TODO: postprocessing MINGAP -> MINDUR -> MINGAP (filter -> pack -> filter)
    def postprocess(self):
        pass


class FreeAnnotation(Annotation):
    """
    The FREE annotation scheme is used for any form of free text.
    """

    def __init__(self, **kwargs):
        self.dataframe = None
        self.type = nt.AnnoTypes.FREE
        super().__init__(**kwargs)

    def get_info(self):
        return merge_role_key(self.role, self.scheme), {
            "dtype": np.str,
            "shape": (None,),
        }

    def set_annotation_from_mongo_doc(self, mongo_doc, time_to_ms=False):
        self.data = mongo_doc
        if time_to_ms:
            for d in self.data:
                d["from"] = int(d["from"] * 1000)
                d["to"] = int(d["to"] * 1000)

        # Creating Pandas Dataframe version of annotations
        self.dataframe = pd.DataFrame(self.data)

        # Create
        if self.dataframe.empty:
            self.data_interval = np.empty((0, 2), int)
            self.data_values = np.empty((0, 2), int)
        else:
            # Creating numpy array of annotations for fast access
            # Splitting the annotations into interval and data array
            self.data_interval = self.dataframe[["from", "to"]].values.astype(int)
            self.data_values = self.dataframe[["name", "conf"]].values

    def get_label_for_frame_legacy(self, start, end):

        # If we don't have any data we return the garbage label
        if self.data == -1:
            return -1

        else:
            # Finding all annos that overlap with the frame
            def is_overlapping(af, at, ff, ft):

                # anno is larger than frame
                altf = af <= ff and at >= ft

                # anno overlaps frame start
                aofs = at >= ff and at <= ft

                # anno overlaps frame end
                aofe = af >= ff and af <= ft

                return altf or aofs or aofe

            annos_for_sample = list(
                filter(
                    lambda x: is_overlapping(x["from"], x["to"], start, end), self.data
                )
            )

            # No label matches
            if not annos_for_sample:
                return [""]

            return [a["name"] for a in annos_for_sample]

    def get_label_for_frame_np(self, start, end):
        annos_for_sample = _get_overlap(self.data_interval, start, end)

        # No label matches
        if not annos_for_sample.any():
            return [""]

        return self.data_values[annos_for_sample, 0]

    def get_label_for_frame(self, start, end):
        return self.get_label_for_frame_np(start, end)

    def postprocess(self):
        pass


class ContinuousAnnotation(Annotation):

    # Class ids and string names as provided from NOVA-DB and required by SSI
    NOVA_GARBAGE_LABEL_VALUE = np.NAN

    MISSING_DATA_LABEL_VALUE = sys.float_info.min

    def __init__(self, sr=0, min_val=0, max_val=0, **kwargs):
        super().__init__(**kwargs)
        self.type = nt.AnnoTypes.CONTINUOUS
        self.sr = sr
        self.min_val = min_val
        self.max_val = max_val
        self.labels = {1: self.scheme}

    def get_info(self):
        return merge_role_key(self.role, self.scheme), {"dtype": np.int32, "shape": 1}

    def set_annotation_from_mongo_doc(self, mongo_doc, time_to_ms=False):
        # Numpy array with shape (len_data, 2) where the second dimension is a respective tuple (confidence, score)
        self.data = np.array([(i["score"], i["conf"]) for i in mongo_doc])

    def get_label_for_frame(self, start, end):
        # returns zero if session duration is longer then labels
        s = int(start * self.sr / 1000)
        e = int(end * self.sr / 1000)

        # Assure that indices for array are at least one integer apart
        if s == e:
            e = s + 1

        if len(self.data) >= e:
            frame = self.data[s:e]
            frame_data = frame[:, 0]
            frame_conf = frame[:, 1]
        else:
            return self.MISSING_DATA_LABEL_VALUE

        # TODO: Return timeseries instead of averagea
        conf = sum(frame_conf) / max(len(frame_conf), 1)
        label = sum(frame_data) / max(len(frame_data), 1)

        # If frame evaluates to garbage label discard sample
        if _is_garbage(label, self.NOVA_GARBAGE_LABEL_VALUE):
            return self.NOVA_GARBAGE_LABEL_VALUE
        else:
            return label

    def postprocess(self):
        pass


class DiscretePolygonAnnotation(Annotation):
    def __init__(self, labels={}, sr=0, **kwargs):
        super().__init__(**kwargs)
        self.type = nt.AnnoTypes.DISCRETE_POLYGON

        self.labels = {
            str(x["id"]): (x["name"], x["color"]) if x["isValid"] else ""
            for x in sorted(labels, key=lambda k: k["id"])
        }
        self.sr = sr

    # TODO MARCO type wird so für tensorflow nicht funktionieren
    def get_info(self):
        return merge_role_key(self.role, self.scheme), {
            "dtype": np.float64,
            "shape": (None, 2),
        }

    def set_annotation_from_mongo_doc(self, mongo_doc, time_to_ms=False):
        self.data = mongo_doc

    def get_label_for_frame(self, start, end):
        # return the last frame
        frame_nr = int((end / 1000) * self.sr)
        if len(self.data) > frame_nr:
            return self.data[frame_nr - 1]
        else:
            return -1

    def postprocess(self):
        pass
