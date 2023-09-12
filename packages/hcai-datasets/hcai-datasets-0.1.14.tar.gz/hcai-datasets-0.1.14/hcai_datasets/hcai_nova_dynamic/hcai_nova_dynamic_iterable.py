import logging
import sys

import numpy as np
import os
import copy

import nova_utils.db_utils.nova_types as nt
import hcai_datasets.hcai_nova_dynamic.utils.nova_data_utils as ndu
import hcai_datasets.hcai_nova_dynamic.utils.nova_anno_utils as nau
from nova_utils.interfaces.dataset_iterable import DatasetIterable

from hcai_datasets.hcai_nova_dynamic.utils.nova_data_utils import (
    AudioData,
    VideoData,
    StreamData,
)

from hcai_datasets.hcai_nova_dynamic.nova_db_handler import NovaDBHandler
from hcai_datasets.hcai_nova_dynamic.utils.nova_string_utils import *


class HcaiNovaDynamicIterable(DatasetIterable):
    def __init__(
        self,
        *args,
        db_config_path=None,
        db_config_dict=None,
        dataset=None,
        nova_data_dir=None,
        sessions=None,
        annotator=None,
        schemes=None,
        roles=None,
        data_streams=None,
        start=None,
        end=None,
        left_context=None,
        right_context=None,
        frame_size=None,
        stride=None,
        add_rest_class=True,
        flatten_samples=False,
        supervised_keys=None,
        lazy_loading=False,
        fake_missing_data=True,
        **kwargs,
    ):
        """
        Initialize the HcaiNovaDynamic dataset builder
        Args:
          nova_data_dir: the directory to look for data. same as the directory specified in the nova gui.
          frame_size: the framesize to look at. the matching annotation will be calculated as majority vote from all annotations that are overlapping with the timeframe.
          left_context: additional data to pass to the classifier on the left side of the frame.
          right_context: additional data to pass to the classifier on the left side of the frame.
          stride: how much a frame is moved to calculate the next sample. equals framesize by default.
          flatten_samples: if set to True samples with the same annotation scheme but from different roles will be treated as separate samples. only <scheme> is used for the keys.
          supervised_keys: if specified the dataset can be used with "as_supervised" set to True. Should be in the format <role>.<scheme>. if flatten_samples is true <role> will be ignored.
          add_rest_class: when set to True an additional restclass will be added to the end the label list
          db_config_path: path to a configfile whith the nova database config.
          db_config_dict: dictionary with the nova database config. can be used instead of db_config_path. if both are specified db_config_dict is used.
          dataset: the name of the dataset. must match the dataset name in the nova database.
          sessions: list of sessions that should be loaded. must match the session names in nova.
          annotator: the name of the annotator that labeld the session. must match annotator names in nova.
          schemes: list of the annotation schemes to fetch
          roles: list of roles for which the annotation should be loaded.
          data_streams: list datastreams for which the annotation should be loaded. must match stream names in nova.
          start: optional start time_ms. use if only a specific chunk of a session should be retreived.
          end: optional end time_ms. use if only a specifc chunk of a session should be retreived.
          fake_missing_data: If set to true missing datastreams will provide zero data and missing annotations will be empty. If set to false a session will be skipped if an expected data stream or annotation are not found.
          **kwargs: arguments that will be passed through to the dataset builder
        """
        super().__init__(*args, **kwargs)
        self.dataset = dataset
        self.nova_data_dir = nova_data_dir
        self.sessions = sessions
        self.roles = roles
        self.schemes = schemes
        self.data_streams = data_streams
        self.annotator = annotator

        # Sliding window parameters for the main stream
        self.left_context, self.left_context_unit = ndu.parse_time_str(left_context if left_context else '0')
        self.right_context, self.right_context_unit = ndu.parse_time_str(right_context if right_context else '0')
        self.frame_size, self.frame_size_unit = ndu.parse_time_str(frame_size)

        # Framesize 0 or None indicates that the whole session should be returned as one sample
        if self.frame_size == 0:
            print(
                "WARNING: Frame size 0 is invalid. Returning whole session as sample."
            )
            self.frame_size = None
        self.stride, self.stride_unit = ndu.parse_time_str(stride) if stride else self.frame_size, self.frame_size_unit

        #TODO: Remove time dependent variables after refactoring
        self.left_context_ms = ndu.parse_time_string_to_ms(left_context) if left_context else 0
        self.right_context_ms = ndu.parse_time_string_to_ms(right_context) if right_context else 0
        self.frame_size_ms = (
            ndu.parse_time_string_to_ms(frame_size) if frame_size else None
        )

        if self.frame_size_ms == 0:
            print(
                "WARNING: Frame size 0 is invalid. Returning whole session as sample."
            )
            self.frame_size_ms = None

        self.stride_ms = (
            ndu.parse_time_string_to_ms(stride) if stride else self.frame_size_ms
        )

        self.start_ms = ndu.parse_time_string_to_ms(start)
        if not self.start_ms:
            self.start_ms = 0

        self.end_ms = ndu.parse_time_string_to_ms(end)
        if not self.end_ms:
            self.end_ms = sys.maxsize #float("inf")

        self.flatten_samples = flatten_samples
        self.add_rest_class = add_rest_class
        self.lazy_loading = lazy_loading
        self.fake_missing_data = fake_missing_data
        self.nova_db_handler = NovaDBHandler(db_config_path, db_config_dict)

        # Retrieving meta information from the database
        mongo_schemes = self.nova_db_handler.get_schemes(
            dataset=dataset, schemes=schemes
        )
        mongo_data = self.nova_db_handler.get_data_streams(
            dataset=dataset, data_streams=data_streams
        )
        self.annos, self.anno_schemes = self._populate_label_info_from_mongo_doc(
            mongo_schemes
        )
        self.data_info, self.data_schemes = self._populate_data_info_from_mongo_doc(
            mongo_data
        )

        self.session_info = {s: {} for s in self.sessions}

        # setting supervised keys
        if supervised_keys and self.flatten_samples:
            if supervised_keys[0] not in self.data_streams:
                # remove <role> of supervised keys
                _, data_stream = split_role_key(supervised_keys[0])
                if not data_stream in self.data_streams:
                    print(
                        "Warning: Cannot find supervised key '{}' in datastreams".format(
                            data_stream
                        )
                    )
                    raise Warning("Unknown data_stream")
                else:
                    supervised_keys[0] = data_stream
            if supervised_keys[1] not in self.schemes:
                # remove <role> of supervised keys
                _, scheme = split_role_key(supervised_keys[1])
                if not scheme in schemes:
                    print(
                        "Warning: Cannot find supervised key '{}' in schemes".format(
                            scheme
                        )
                    )
                    raise Warning("Unknown scheme")
                else:
                    supervised_keys[1] = scheme

        self.supervised_keys = tuple(supervised_keys) if supervised_keys else None

        self._iterable = self._yield_sample()

    def to_single_session_iterator(self, session_id=""):
        """Returns a copy of the iterator for a single session. All data objects and annotation objects will be initialized."""
        ds_iter_copy = copy.copy(self)
        if session_id not in self.sessions:
            print(
                f"WARNING: Session {session_id} not found in iterator session list. Using first session instead: {ds_iter_copy.sessions[0]}"
            )
            session_id = ds_iter_copy.sessions[0]
        elif not session_id:
            session_id = ds_iter_copy.sessions[0]

        ds_iter_copy._init_session(session_id)
        return ds_iter_copy

    def _init_session(self, session):
        """Opens all annotations and data readers"""

        if (
            not self.session_info[session]
            or not self.session_info[session]["is_active"]
        ):

            # Gather all data we need for this session
            self._load_annotation_for_session(session, time_to_ms=True)
            self._open_data_reader_for_session(session)

            session_info = self.nova_db_handler.get_session_info(self.dataset, session)[
                0
            ]

            # Depricate other sessions
            for id, s in self.session_info.items():
                s["is_active"] = False

            session_info["is_active"] = True
            self.session_info[session] = session_info

    def _populate_label_info_from_mongo_doc(self, mongo_schemes):
        """
        Setting self.annos
        Args:
          mongo_schemes:

        Returns:

        """
        annos = {}
        anno_schemes = {}

        # List of all combinations from roles and schemes that occur in the retrieved data.
        for scheme in mongo_schemes:
            for role in self.roles:
                label_id = merge_role_key(role=role, key=scheme["name"])
                scheme_type = nt.string_to_enum(nt.AnnoTypes, scheme["type"])
                scheme_name = scheme["name"]
                scheme_valid = scheme["isValid"]
                anno_schemes[label_id] = scheme_type

                if scheme_type == nt.AnnoTypes.DISCRETE:
                    labels = scheme["labels"]
                    annos[label_id] = nau.DiscreteAnnotation(
                        role=role,
                        add_rest_class=self.add_rest_class,
                        scheme=scheme_name,
                        is_valid=scheme_valid,
                        labels=labels,
                    )

                elif scheme_type == nt.AnnoTypes.CONTINUOUS:
                    min_val = scheme["min"]
                    max_val = scheme["max"]
                    sr = scheme["sr"]
                    annos[label_id] = nau.ContinuousAnnotation(
                        role=role,
                        scheme=scheme_name,
                        is_valid=scheme_valid,
                        min_val=min_val,
                        max_val=max_val,
                        sr=sr,
                    )

                elif scheme_type == nt.AnnoTypes.DISCRETE_POLYGON:
                    labels = scheme["labels"]
                    sr = scheme["sr"]
                    annos[label_id] = nau.DiscretePolygonAnnotation(
                        role=role,
                        scheme=scheme_name,
                        is_valid=scheme_valid,
                        labels=labels,
                        sr=sr,
                    )

                elif scheme_type == nt.AnnoTypes.FREE:
                    annos[label_id] = nau.FreeAnnotation(
                        role=role, scheme=scheme_name, is_valid=scheme_valid
                    )

                else:
                    raise ValueError("Invalid label type {}".format(scheme["type"]))

        return annos, anno_schemes

    def _populate_data_info_from_mongo_doc(self, mongo_data_streams):
        """
        Setting self.data
        Args:
          mongo_schemes:

        Returns:

        """
        data_info = {}
        data_schemes = {}

        for data_stream in mongo_data_streams:
            for role in self.roles:
                sample_stream_name = (
                    role + "." + data_stream["name"] + "." + data_stream["fileExt"]
                )
                sample_data_path = os.path.join(
                    self.nova_data_dir,
                    self.dataset,
                    self.sessions[0],
                    sample_stream_name,
                )
                dtype = nt.string_to_enum(nt.DataTypes, data_stream["type"])
                #window_size = (self.left_context_ms + self.frame_size_ms + self.right_context_ms) / (1 / data_stream["sr"])
                # TODO
                try:
                    if dtype == nt.DataTypes.VIDEO:
                        data = VideoData(
                            role=role,
                            name=data_stream["name"],
                            file_ext=data_stream["fileExt"],
                            sr=data_stream["sr"],
                            is_valid=data_stream["isValid"],
                            sample_data_path=sample_data_path,
                            lazy_loading=self.lazy_loading,
                        )
                    elif dtype == nt.DataTypes.AUDIO:
                        data = AudioData(
                            role=role,
                            name=data_stream["name"],
                            file_ext=data_stream["fileExt"],
                            sr=data_stream["sr"],
                            is_valid=data_stream["isValid"],
                            sample_data_path=sample_data_path,
                            lazy_loading=self.lazy_loading,
                        )
                    elif dtype == nt.DataTypes.FEATURE:
                        data = StreamData(
                            role=role,
                            name=data_stream["name"],
                            sr=data_stream["sr"],
                            data_type=dtype,
                            is_valid=data_stream["isValid"],
                            sample_data_path=sample_data_path,
                            lazy_loading=self.lazy_loading,
                        )
                    else:
                        raise ValueError(
                            "Invalid data type".format(data_stream["type"])
                        )

                except FileNotFoundError as fnf:
                    if self.fake_missing_data:
                        raise FileNotFoundError
                    else:
                        print(f"WARNING: Ignoring exception - {fnf}")
                        continue

                data_id = merge_role_key(role=role, key=data_stream["name"])
                data_info[data_id] = data
                data_schemes[data_id] = dtype

        return data_info, data_schemes

    def _load_annotation_for_session(self, session, time_to_ms=False):
        for label_id, anno in self.annos.items():
            try:
                mongo_anno = self.nova_db_handler.get_annos(
                    self.dataset, anno.scheme, session, self.annotator, anno.role
                )
            except FileNotFoundError as fnf:
                mongo_anno = []
                if self.fake_missing_data:
                    print(f"WARNING: {fnf} - Providing dummy data")
                else:
                    raise fnf
            finally:
                anno.set_annotation_from_mongo_doc(mongo_anno, time_to_ms=time_to_ms)

    def _open_data_reader_for_session(self, session):
        for data_id, data in self.data_info.items():
            try:
                data_path = os.path.join(
                    self.nova_data_dir,
                    self.dataset,
                    session,
                    data_id + "." + data.file_ext,
                )
                data.open_file_reader(data_path)
            except FileNotFoundError as fnf:
                if self.fake_missing_data:
                    print(f"WARNING: {fnf} - Providing dummy data")
                else:
                    raise fnf

    def _build_sample_dict(self, labels_for_frame, data_for_frame):
        sample_dict = {}

        garbage_detected = False
        for label_id, label_value in labels_for_frame:
            # if value is not list type check for nan
            if (
                    type(label_value) != list
                    and type(label_value) != str
                    and type(label_value) != np.ndarray
            ):
                if label_value != label_value:
                    garbage_detected = True

            sample_dict.update({label_id: label_value})

        # If at least one label is a garbage label we skip this iteration
        if garbage_detected:
            return None

        for d in data_for_frame:
            sample_dict.update(d)

        # if self.flatten_samples:
        #
        #     # grouping labels and data according to roles
        #     for role in self.roles:
        #         # filter dictionary to contain values for role
        #         sample_dict_for_role = dict(
        #             filter(lambda elem: role in elem[0], sample_dict.items())
        #         )
        #
        #         # remove role from dictionary keys
        #         sample_dict_for_role = dict(
        #             map(
        #                 lambda elem: (elem[0].replace(role + ".", ""), elem[1]),
        #                 sample_dict_for_role.items(),
        #             )
        #         )
        #
        #         sample_dict_for_role["frame"] = (
        #             str(sample_counter) + "_" + key + "_" + role
        #         )
        #         # yield key + '_' + role, sample_dict_for_role
        #         yield sample_dict_for_role
        #         sample_counter += 1
        #     c_pos_ms += _stride_ms
        #
        # else:
        return sample_dict

    def _yield_sample(self):
        """Yields examples."""

        # Needed to sort the samples later and assure that the order is the same as in nova. Necessary for CML till the tfds can be returned in order.
        sample_counter = 1

        for session in self.sessions:

            self._init_session(session)

            # Iterate through the session using frame based indices
            if self.stride_unit == ndu.StrideUnit.FRAMES:

                # Setting the main stream as a reference
                main_stream_id = self.roles[0] + '.' + self.data_streams[0]
                if main_stream_id not in self.data_info.keys():
                    print(f'WARNING: Framewise iteration has been requested but main stream "{main_stream_id}" could not be found. Skipping session.')
                    break
                print(f'Stride unit has been specified as number of frames. Using "{main_stream_id}" with a sr of {self.data_info[main_stream_id].sr} as main stream.')
                main_stream = self.data_info[main_stream_id]
                _frame_size = self.frame_size
                _stride = self.stride

                # Starting position of the first frame in seconds
                c_pos = max(self.left_context, self.start_ms)

                # If frame size is not specified we return the whole session as one junk
                if self.frame_size is None:
                    _frame_size = main_stream.n_frames
                    _stride =  main_stream.n_frames

                for i in range(0,main_stream.n_frames, _stride):
                    print('')

            else:
                session_info = self.session_info[session]
                dur = session_info["duration"]
                _frame_size_ms = self.frame_size_ms
                _stride_ms = self.stride_ms

                # If we are loading any datastreams we check if any datastream is shorter than the duration stored in the database suggests
                if self.data_info:
                    dur = min(*[v.dur for k, v in self.data_info.items()], dur)

                if not dur:
                    raise ValueError("Session {} has no duration.".format(session))

                dur_ms = int(dur * 1000)

                # If framesize is not specified we return the whole session as one junk
                if self.frame_size_ms is None:
                    _frame_size_ms = min(dur_ms, self.end_ms - self.start_ms)
                    _stride_ms = _frame_size_ms

                # Starting position of the first frame in seconds
                # c_pos_ms = self.left_context_ms + self.start_ms
                c_pos_ms = max(self.left_context_ms, self.start_ms)

                # Generate samples for this session
                while c_pos_ms + _stride_ms + self.right_context_ms <= min(
                    self.end_ms, dur_ms
                ):

                    frame_start_ms = c_pos_ms
                    frame_end_ms = c_pos_ms + _frame_size_ms

                    window_start = frame_start_ms - self.left_context_ms
                    window_end = frame_end_ms + self.right_context_ms

                    #frame_start_ms = c_pos_ms - self.left_context_ms
                    #frame_end_ms = c_pos_ms + _frame_size_ms + self.right_context_ms

                    window_info = (
                        session
                        + "_"
                        + str(window_start / 1000)
                        + "_"
                        + str(window_end / 1000)
                    )


                    # Get label based on frame
                    labels_for_window = [
                        (k, v.get_label_for_frame(frame_start_ms, frame_end_ms))
                        for k, v in self.annos.items()
                    ]

                    # Get data based on window
                    data_for_window = []
                    for k, v in self.data_info.items():
                        sample = v.get_sample(window_start, window_end)
                        # TODO: Special case with empty streams is probably not working correctly. Verify
                        if sample.shape[0] == 0:
                            print(f"Sample{window_start}-{window_end} is empty")
                            #c_pos_ms += _stride_ms
                            #continue
                        data_for_window.append({k: sample})

                    sample_dict = self._build_sample_dict(labels_for_window, data_for_window)
                    if not sample_dict:
                        c_pos_ms += _stride_ms
                        sample_counter += 1
                        continue

                    yield sample_dict
                    c_pos_ms += _stride_ms
                    sample_counter += 1

            # closing file readers for this session
            for k, v in self.data_info.items():
                v.close_file_reader()

    def __iter__(self):
        return self._iterable

    def __next__(self):
        return self._iterable.__next__()

    def get_output_info(self):
        def map_label_id(lid):
            if self.flatten_samples and not lid == "frame":
                return split_role_key(lid)[-1]
            return lid

        return {
            # Adding fake framenumber label for sorting
            "frame": {"dtype": np.str, "shape": (1,)},
            **{map_label_id(k): v.get_info()[1] for k, v in self.annos.items()},
            **{map_label_id(k): v.get_info()[1] for k, v in self.data_info.items()},
        }
