from __future__ import annotations
from typing import Optional, Union, Sequence
from convomeld.state import Action, State, TriggerPlaceholder
from convomeld.thread import ConvoThread
from convomeld.parsers import SimpleScriptParser, ScriptParsingError
from convomeld.matchers import SimpleActionMatcher, SimpleTriggerUserTextMatcher
from convomeld.merge import (
    MergeValidator,
    StopEarlyHandler,
    DefaultTriggerHandler,
    SubthreadAppendHandler,
    SubthreadMergeHandler,
)
import os
import yaml
from io import StringIO, BytesIO
from urllib.parse import urlparse
from urllib.request import urlopen
from uuid import uuid4


class ConvoGraph:
    def __init__(
        self,
        action_matcher,
        trigger_matcher,
        states=None,
        convo_name=None,
        convo_description=None,
        nlp=None,
        use_uuid=True,
    ) -> None:
        self._states = {}
        self._action_matcher = action_matcher
        self._trigger_matcher = trigger_matcher
        self._uuid = uuid4().hex[-6:]
        # self._state_count = 0
        self._respond_state_count = 0
        self._use_uuid = use_uuid
        self._merge_handlers = [
            MergeValidator(self._trigger_matcher),
            DefaultTriggerHandler(self._trigger_matcher),
            SubthreadMergeHandler(self._action_matcher, self._trigger_matcher),
            SubthreadAppendHandler(self._trigger_matcher),
            StopEarlyHandler(self._trigger_matcher),
            MergeValidator(self._trigger_matcher),
        ]

        if states is None:
            if convo_name is None:
                raise RuntimeError("convo_name must be provided")
            if convo_description is None:
                convo_description = "empty"
            if nlp is None:
                nlp = "exact"

            states = {
                "start": State(
                    "start",
                    triggers=[TriggerPlaceholder.timeout().create_trigger("stop")],
                    convo_name=convo_name,
                    convo_description=convo_description,
                    nlp=nlp,
                ),
                "stop": State(
                    "stop",
                    triggers=[TriggerPlaceholder.default().create_trigger("start")],
                ),
            }

        for state in states.values():
            state_attrs = dict(state.attrs)

            if state.name == "start":
                if convo_name is not None:
                    state_attrs["convo_name"] = convo_name
                if convo_description is not None:
                    state_attrs["convo_description"] = convo_description
                if nlp is not None:
                    state_attrs["nlp"] = nlp

            self._states[state.name] = state.copy(**state_attrs)

        self._mark_seq_repeat()

        state_name_mapping = {}

        for state in self._states.values():
            if state.name in ("start", "stop"):
                continue

            if "_seq" not in state.attrs and "_repeat" not in state.attrs:
                self._respond_state_count += 1
            # self._state_count += 1

            new_state_name = self._generate_state_name(
                seq=state.attrs.get("_seq"), repeat=state.attrs.get("_repeat")
            )
            state_name_mapping[state.name] = new_state_name

        self.rename_states(state_name_mapping)

    # Graph section

    def _generate_state_name(self, seq=None, repeat=None) -> str:
        if self._use_uuid:
            script_prefix = f"script_{self._uuid}"
        else:
            script_prefix = f'{self._states["start"].attrs["convo_name"]}'

        if seq is not None and repeat is not None:
            state_name = f"question_{seq}_{repeat}"
        else:
            state_name = f"respond_{self._respond_state_count}"
        # state_name = f'state_{self._state_count}'

        return script_prefix + "/" + state_name

    def create_state(self, from_state) -> State:
        if "_seq" not in from_state.attrs and "_repeat" not in from_state.attrs:
            self._respond_state_count += 1
        # self._state_count += 1

        new_state_name = self._generate_state_name(
            seq=from_state.attrs.get("_seq"), repeat=from_state.attrs.get("_repeat")
        )
        new_state = from_state.copy(name=new_state_name, triggers=[])
        self._states[new_state.name] = new_state
        return new_state

    def find_state(
        self, name=None, actions=None, many=False, **attrs
    ) -> Union[Optional[State], Sequence[State]]:
        if name is not None:
            states = [self._states[name]] if name in self._states else []
        else:
            states = list(self._states.values())

        for attr_name, attr_value in attrs.items():
            states = [
                state
                for state in states
                if attr_name in state.attrs and state.attrs[attr_name] == attr_value
            ]

        if actions is not None:
            states = [
                state
                for state in states
                if self._action_matcher.match(state.actions, actions)
            ]

        if many:
            return states
        else:
            return states[0] if len(states) else None

    def rename_states(self, mapping) -> None:
        new_states = {}

        for state in self._states.values():
            state_name = mapping[state.name] if state.name in mapping else state.name
            new_states[state_name] = state.copy(name=state_name)

            for trigger in new_states[state_name].triggers:
                if trigger.target in mapping:
                    trigger.target = mapping[trigger.target]

        self._states = new_states

    def num_states(self) -> int:
        return len(self._states)

    def _mark_seq_repeat(self) -> None:
        start_state = self.find_state(name="start")

        visited_states = {self.find_state(name="stop")}
        state_queue = [start_state]

        while len(state_queue):
            state = state_queue.pop(0)

            for trigger in state.triggers:
                next_state = self.find_state(name=trigger.target)

                if next_state in visited_states or next_state.name == state.name:
                    continue

                next_trigger = next_state.find_trigger(
                    TriggerPlaceholder.next(), self._trigger_matcher
                )

                while next_trigger:
                    next_state = self.find_state(name=next_trigger.target)
                    next_trigger = next_state.find_trigger(
                        TriggerPlaceholder.next(), self._trigger_matcher
                    )

                if next_state in visited_states or next_state.name == state.name:
                    continue

                if "_seq" in next_state.attrs and "_repeat" in next_state.attrs:
                    continue

                if state.name == "start":
                    seq = 1
                    repeat = 1
                elif self._action_matcher.match(state.actions, next_state.actions):
                    seq = state.attrs["_seq"]
                    repeat = state.attrs["_repeat"] + 1
                else:
                    seq = state.attrs["_seq"] + 1
                    repeat = 1

                next_state.attrs["_seq"] = seq
                next_state.attrs["_repeat"] = repeat
                state_queue.append(next_state)

            visited_states.add(state)

    def _merge_next_subthread(
        self, current_state, tp, next_subthread, merge_state
    ) -> State:
        # current_state: already existing State of the ConvoGraph
        # tp: generates trigger to connect existing state with the next_subthread
        # next_subthread: follows trigger generated from tp, can be merged with already existing "next subthreads" triggered from current_state
        # merge_state: final state which is the end of next_subthread, should be created if is None, can be already existing State, can also equal current_state

        for merge_handler in self._merge_handlers:
            merge_handler_result = merge_handler.merge(
                self, current_state, tp, next_subthread, merge_state
            )

            if merge_handler_result is not None:
                # merge_state <- merge_handler_result
                if merge_state is not None and merge_handler_result is not merge_state:
                    raise RuntimeError(
                        f"Merge error: merge_handler_result {merge_handler_result} is expected to be target merge_state f{merge_state}"
                    )

                merge_state = merge_handler_result

        if merge_state is None:
            raise RuntimeError(
                "Merge error: merge_state is None after all merge handlers"
            )

        return merge_state

    def merge_thread(self, thread) -> ConvoGraph:
        if not thread.get_first_state().attrs.get("is_start", False):
            raise RuntimeError(
                'Merge error: target thread must begin with "start" state'
            )
        if not thread.get_last_state().attrs.get("is_stop", False):
            raise RuntimeError('Merge error: target thread must end with "stop" state')
        # Pop "start" state
        thread.pop_first_state()

        current_state = self._states["start"]
        current_tp = TriggerPlaceholder.next()
        seq = 0
        repeat = 0

        next_subthread = ConvoThread()

        for state, prev_trigger in thread.iter_states(with_prev_trigger=True):
            state_attrs = dict(state.attrs)

            if len(state.triggers) == 0:
                next_subthread.append_state(
                    state.actions,
                    TriggerPlaceholder.from_trigger(prev_trigger),
                    **state_attrs,
                )
                self._merge_next_subthread(
                    current_state, current_tp, next_subthread, self._states["stop"]
                )
                continue

            state_trigger = state.triggers[0]
            current_state_match = self._action_matcher.match(
                current_state.actions, state.actions
            )

            if not state.triggers[0].is_next() or current_state_match:
                if "_seq" in state_attrs:
                    seq = state_attrs["_seq"]
                else:
                    if not current_state_match:
                        seq += 1
                    state_attrs["_seq"] = seq
                if "_repeat" in state_attrs:
                    repeat = state_attrs["_repeat"]
                else:
                    if current_state_match:
                        repeat += 1
                    else:
                        repeat = 1
                    state_attrs["_repeat"] = repeat

            next_subthread.append_state(
                state.actions,
                TriggerPlaceholder.from_trigger(prev_trigger),
                **state_attrs,
            )
            merge_state = self.find_state(
                actions=state.actions,
                _seq=state_attrs.get("_seq"),
                _repeat=state_attrs.get("_repeat"),
            )

            if state_trigger.is_next():
                if current_state_match:
                    state_trigger = TriggerPlaceholder.timeout().create_trigger(
                        state_trigger.target
                    )
                else:
                    continue

            current_state = self._merge_next_subthread(
                current_state, current_tp, next_subthread, merge_state
            )
            current_tp = TriggerPlaceholder.from_trigger(state_trigger)
            next_subthread = ConvoThread()

        return self

    def to_threads(self) -> list[ConvoThread]:
        start_state = self._states["start"]

        complete_threads = []
        state_queue = [
            (
                start_state,
                ConvoThread().append_state(
                    start_state.actions,
                    TriggerPlaceholder.none(),
                    **start_state.attrs,
                    is_start=True,
                ),
                set(),
            )
        ]

        while len(state_queue):
            current_state, thread, processed_states = state_queue.pop(0)

            if current_state in processed_states:
                continue
            if current_state.name == "stop":
                complete_threads.append(thread)
                continue

            next_subthreads = []

            for trigger in current_state.triggers:
                state = self.find_state(name=trigger.target)
                state_attrs = (
                    {**state.attrs, "is_start": True}
                    if state.name == "start"
                    else {**state.attrs, "is_stop": True}
                    if state.name == "stop"
                    else state.attrs
                )
                subthread_states = ConvoThread().append_state(
                    state.actions, TriggerPlaceholder.none(), **state_attrs
                )

                while (
                    state.find_trigger(TriggerPlaceholder.next(), self._trigger_matcher)
                    is not None
                ):
                    prev_trigger = state.triggers[0]
                    state = self.find_state(name=prev_trigger.target)
                    state_attrs = (
                        {**state.attrs, "is_start": True}
                        if state.name == "start"
                        else {**state.attrs, "is_stop": True}
                        if state.name == "stop"
                        else state.attrs
                    )
                    subthread_states.append_state(
                        state.actions,
                        TriggerPlaceholder.from_trigger(prev_trigger),
                        **state_attrs,
                    )

                if state is not current_state:
                    # Trigger doesn't lead to loopback
                    next_subthreads.append((trigger, subthread_states, state))
                    continue

                # Trigger leads to a loopback
                for subthread_state, prev_trigger in subthread_states.iter_states(
                    with_prev_trigger=True
                ):
                    if prev_trigger.is_none():
                        prev_trigger = trigger
                    thread.append_state(
                        subthread_state.actions,
                        TriggerPlaceholder.from_trigger(prev_trigger),
                        **subthread_state.attrs,
                    )

            processed_states.add(current_state)

            for trigger, subthread_states, state in next_subthreads:
                next_thread = thread.copy()

                for subthread_state, prev_trigger in subthread_states.iter_states(
                    with_prev_trigger=True
                ):
                    if prev_trigger.is_none():
                        prev_trigger = trigger
                    next_thread.append_state(
                        subthread_state.actions,
                        TriggerPlaceholder.from_trigger(prev_trigger),
                        **subthread_state.attrs,
                    )

                state_queue.append((state, next_thread, processed_states.copy()))

        return complete_threads

    def merge_graph(self, graph) -> ConvoGraph:
        result = self

        if not result.is_normal():
            result = result.normalized()

        if not graph.is_normal():
            graph = graph.normalized()

        for thread in graph.to_threads():
            result = result.merge_thread(thread)

        return result

    def compare(self, other) -> bool:
        state_queue = [(self._states["start"], other.find_state(name="start"))]
        processed_states = set()

        while len(state_queue):
            state1, state2 = state_queue.pop(0)

            if state1 in processed_states:
                continue
            if (state1.name == "start") ^ (state2.name == "start"):
                return False
            if (state1.name == "stop") ^ (state2.name == "stop"):
                return False
            if state1.attrs != state2.attrs:
                return False
            if not self._action_matcher.match(state1.actions, state2.actions):
                return False
            if len(state1.triggers) != len(state2.triggers):
                return False

            for trigger1 in state1.triggers:
                trigger2 = state2.find_trigger(
                    TriggerPlaceholder.from_trigger(trigger1), self._trigger_matcher
                )

                if trigger2 is None:
                    return False

                state_queue.append(
                    (
                        self.find_state(name=trigger1.target),
                        other.find_state(name=trigger2.target),
                    )
                )

            processed_states.add(state1)

        return True

    def is_normal(self):
        for state in self._states.values():
            send_message_actions = [
                action
                for action in state.actions
                if action.name == 'send_message'
            ]

            if len(send_message_actions) > 1:
                return False

        return True

    def normalized(self):
        new_states = {}
        state_name_mapping = {}

        for state in self._states.values():
            actions_splitted = []
            actions_part = []

            for action in state.actions:
                actions_part.append(action)

                if action.name == 'send_message':
                    actions_splitted.append(actions_part)
                    actions_part = []

            if len(actions_splitted) <= 1:
                new_states[state.name] = state.copy()
            else:
                for i, actions_part in enumerate(actions_splitted):
                    new_state_attrs = dict(state.attrs)
                    new_state_attrs['_norm_from_state'] = state.name
                    new_state_attrs['_norm_seq'] = i + 1

                    new_state = State(
                        name=f"{state.name}_part{i}",
                        actions=actions_part,
                        **state.attrs,
                    )

                    if i == 0:
                        state_name_mapping[state.name] = new_state.name

                    if i < len(actions_splitted) - 1:
                        next_state_name = f"{state.name}_part{i + 1}"
                        new_state.triggers.append(TriggerPlaceholder.next().create_trigger(next_state_name))
                    else:
                        new_state.triggers += [trigger.copy() for trigger in state.triggers]

                    new_states[new_state.name] = new_state

        for state in new_states.values():
            for trigger in state.triggers:
                if trigger.target in state_name_mapping:
                    trigger.target = state_name_mapping[trigger.target]
        
        norm_graph = ConvoGraph(self._action_matcher, self._trigger_matcher, new_states, use_uuid=self._use_uuid)
        return norm_graph

    # Export section

    def to_states_list(self, version="v2") -> list:
        stop_state = self._states.pop("stop")
        self._states["stop"] = stop_state
        return [state.to_dict(version=version) for state in self._states.values()]

    def to_yaml(self, fp, version="v2") -> None:
        if isinstance(fp, str):
            if not fp.endswith(".yml"):
                fp += ".yml"
            dir = os.path.dirname(fp)
            if not os.path.exists(dir):
                os.makedirs(dir)
            fp = open(fp, "w", encoding="utf-8")

        state_list = self.to_states_list(version)
        yaml.safe_dump(state_list, fp, sort_keys=False, encoding="utf-8")
        fp.close()

    # Import section

    @classmethod
    def from_states_list(
        cls,
        states_list,
        convo_name=None,
        convo_description=None,
        nlp=None,
        action_matcher=None,
        trigger_matcher=None,
        use_uuid=None,
        version=None,
    ) -> ConvoGraph:
        states = {
            state_dict["name"]: State.from_dict(state_dict, version)
            for state_dict in states_list
        }

        if action_matcher is None:
            action_matcher = SimpleActionMatcher()
        if trigger_matcher is None:
            trigger_matcher = SimpleTriggerUserTextMatcher()
        if use_uuid is None:
            use_uuid = True

        graph = cls(
            action_matcher,
            trigger_matcher,
            states,
            convo_name=convo_name,
            convo_description=convo_description,
            nlp=nlp,
            use_uuid=use_uuid,
        )
        return graph

    @classmethod
    def from_file(
        cls,
        fp,
        convo_name=None,
        convo_description=None,
        nlp=None,
        text_script_parser=None,
        base_author=None,
        action_matcher=None,
        trigger_matcher=None,
        use_uuid=None,
        normalized=None,
        yaml_version=None,
    ) -> ConvoGraph:
        if hasattr(fp, "close"):
            content = fp.read()
            fp.close()

        try:
            if hasattr(fp, "close"):
                fp = (
                    StringIO(content.encode("utf-8"))
                    if type(content) is bytes
                    else StringIO(content)
                )

            return cls.from_graph_file(
                fp, action_matcher, trigger_matcher, use_uuid, yaml_version
            )
        except Exception as err:
            graph_err = err

        try:
            if hasattr(fp, "close"):
                fp = (
                    StringIO(content.encode("utf-8"))
                    if type(content) is bytes
                    else StringIO(content)
                )

            return cls.from_script_file(
                fp,
                convo_name,
                convo_description,
                nlp,
                text_script_parser,
                base_author,
                action_matcher,
                trigger_matcher,
                use_uuid,
                normalized,
            )
        except Exception as err:
            script_err = err

        raise RuntimeError(
            f"Two errors occured trying to read file:\n{graph_err}\n{script_err}"
        )

    @classmethod
    def from_graph_file(
        cls, fp, action_matcher=None, trigger_matcher=None, use_uuid=None, normalized=None, version=None
    ) -> ConvoGraph:
        if isinstance(fp, str):
            parsed_url = urlparse(fp)
            if parsed_url.scheme and (parsed_url.netloc or parsed_url.scheme == "file"):
                fp = StringIO(urlopen(fp).read().decode("utf-8"))
            else:
                fp = open(fp, "r", encoding="utf-8")
        elif hasattr(fp, "open"):
            fp = fp.open("r", encoding="utf-8")

        script_list = yaml.safe_load(fp)
        fp.close()
        return cls.from_states_list(
            script_list,
            action_matcher,
            trigger_matcher,
            use_uuid=use_uuid,
            version=version,
        )

    @classmethod
    def from_script_file(
        cls,
        fp,
        convo_name=None,
        convo_description=None,
        nlp=None,
        script_parser=None,
        base_author=None,
        action_matcher=None,
        trigger_matcher=None,
        use_uuid=None,
        normalized=None
    ) -> ConvoGraph:
        if isinstance(fp, str):
            parsed_url = urlparse(fp)
            if parsed_url.scheme and (parsed_url.netloc or parsed_url.scheme == "file"):
                fp = StringIO(urlopen(fp).read().decode("utf-8"))
            else:
                fp = open(fp, "r", encoding="utf-8")

        elif hasattr(fp, "open"):
            fp = fp.open("r", encoding="utf-8")

        raw_lines = fp.readlines()
        fp.close()

        return cls.from_script_lines(
            raw_lines,
            convo_name,
            convo_description,
            nlp,
            script_parser,
            base_author,
            action_matcher,
            trigger_matcher,
            use_uuid,
            normalized
        )

    @classmethod
    def from_script_lines(
        cls,
        script_lines,
        convo_name=None,
        convo_description=None,
        nlp=None,
        script_parser=None,
        base_author=None,
        action_matcher=None,
        trigger_matcher=None,
        use_uuid=None,
        normalized=None
    ) -> ConvoGraph:
        if convo_name is None:
            convo_name = "convo_name"
        if convo_description is None:
            convo_description = "empty"
        if nlp is None:
            nlp = "exact"
        if script_parser is None:
            script_parser = SimpleScriptParser()
        if base_author is None:
            base_author = "teacher"
        if action_matcher is None:
            action_matcher = SimpleActionMatcher()
        if trigger_matcher is None:
            trigger_matcher = SimpleTriggerUserTextMatcher()
        if use_uuid is None:
            use_uuid = True
        if normalized is None:
            normalized = True

        script_lines = script_parser.parse_lines(script_lines)

        graph = cls(
            action_matcher,
            trigger_matcher,
            convo_name=convo_name,
            convo_description=convo_description,
            nlp=nlp,
            use_uuid=use_uuid,
        )
        graph_start_state = graph.find_state(name="start")
        graph_stop_state = graph.find_state(name="stop")

        thread = ConvoThread().append_state(
            graph_start_state.actions,
            TriggerPlaceholder.none(),
            **graph_start_state.attrs,
            is_start=True,
        )
        actions = []
        tp = None

        for line in script_lines:
            if line.author == base_author:
                actions.append(Action.send_message(line.text, line.lang))
            
                if normalized:
                    thread = thread.append_state(actions, tp or TriggerPlaceholder.next())
                    actions = []
                    tp = None
            else:
                if not normalized:
                    respond_actions = actions[:-1]
                    question_actions = actions[-1:]
                    
                    if len(respond_actions):
                        thread = thread.append_state(respond_actions, tp or TriggerPlaceholder.next())
                        tp = None
                    if len(question_actions):
                        thread = thread.append_state(question_actions, tp or TriggerPlaceholder.next())
                        tp = None
                    actions = []
                
                tp = TriggerPlaceholder(line.text, line.lang)

        if not normalized and len(actions):
            respond_actions = actions[:-1]
            question_actions = actions[-1:]
            
            if len(respond_actions):
                thread = thread.append_state(respond_actions, tp or TriggerPlaceholder.next())
                tp = None
            if len(question_actions):
                thread = thread.append_state(question_actions, tp or TriggerPlaceholder.next())
                tp = None

            tp = None

        thread = thread.append_state(
            graph_stop_state.actions,
            tp or TriggerPlaceholder.next(),
            **graph_stop_state.attrs,
            is_stop=True,
        )
        return graph.merge_thread(thread)
