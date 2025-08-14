import syside
import xml.etree.ElementTree as ET
import xml.dom.minidom


class SysMLv2ToSCXML:
    """Converts a SysMLv2 state machine into SCXML format."""

    def __init__(self, model: syside.Model, state_machine_node: syside.StateDefinition):
        """
        Initialize the state machine conversion.
        
        :param model: The SysMLv2 model.
        :param state_machine_node: The root node of the SysMLv2 state machine.
        """
        self.model = model
        self.state_machine_node = state_machine_node

        self.states:  list[syside.StateUsage] = []
        self.states_by_name = {}
        self.transitions: list[syside.TransitionUsage] = []
        self.transitions_by_name = {}
        self.transitions_from_source: dict[
            syside.StateUsage, list[syside.TransitionUsage]
        ] = {}
        self.transitions_to_target: dict[
            syside.StateUsage, list[syside.TransitionUsage]
        ] = {}

        # Extract states and transitions
        self._extract_states_and_transitions()

        # Find the initial state
        self.initial_state = self._find_initial_state()

        # Create SCXML root element
        self.scxml = ET.Element("scxml", {
            "xmlns": "http://www.w3.org/2005/07/scxml",
            "version": "1.0",
            "datamodel": "ecmascript",
            "initial": self.initial_state
        })

        # Convert states and transitions
        self._convert_states()

    def _extract_states_and_transitions(self):
        """Extracts states and transitions from the SysMLv2 model."""
        for child in self.state_machine_node.children.elements:
            if state := child.try_cast(syside.StateUsage):
                if state.name is None:
                    raise ValueError(f"State has no name: {state}")
                self.states.append(state)
                self.states_by_name[state.name] = state
                #if state.do_action is not None:
                #    print (f">>>doActivity {state.do_action.declared_name}")
            elif transition := child.try_cast(syside.TransitionUsage):
                if transition.name is None:
                    raise ValueError(f"Transition has no name: {transition}")
                if transition.source is None or transition.source.name is None:
                    raise ValueError(f"Transition '{transition.name}' has no source state.")
                if transition.target is None or transition.target.name is None:
                    raise ValueError(f"Transition '{transition.name}' has no target state.")

                self.transitions.append(transition)
                self.transitions_by_name[transition.name] = transition
                assert isinstance(transition.source, syside.StateUsage)

                source_state = transition.source
                if source_state not in self.transitions_from_source:
                    self.transitions_from_source[transition.source] = []
                    self.transitions_to_target[transition.source] = []
                self.transitions_from_source[transition.source].append(transition)
                self.transitions_to_target[transition.source].append(transition)

    def _find_initial_state(self):
        """Finds the initial state based on the SysMLv2 `entry` statement."""
        for succession in self.model.nodes(syside.SuccessionAsUsage):
            if succession.source == self.state_machine_node.entry_action:
                if not succession.targets:
                    raise ValueError("No initial state found in `entry` statement.")
                initial_state = succession.targets.collect()[0]
                if initial_state.name is None:
                    raise ValueError("Initial state has no name.")
                return initial_state.name
        raise ValueError("Initial state not found.")



    def _convert_states(self):
        """Convert states and transitions to SCXML format."""
        state_elements = {}

        # Convert states
        for state in self.states:
            state_element = ET.SubElement(self.scxml, "state", {"id": state.name})
            state_elements[state] = state_element
            if state.do_action is not None:
                do_behavior_string = state.do_action.declared_name
                print (f">>>> {do_behavior_string}")
                ET.SubElement(
                    state_elements[state],
                    "invoke",
                    {"id": f"{do_behavior_string}"}
                )

        # Convert transitions
        for transition in self.transitions:
            def extract_event_name(event_data: syside.ReferenceUsage) -> str:
                # We need to go through the heritage of the accepter to find what
                # the event name is
                for item in transition.trigger_action.payload_parameter.heritage:
                    try:  # Check if the event is an AttributeDefinition (hardcode for now)
                        if item[1].cast(syside.AttributeDefinition):
                            event_name = item[1].declared_name
                            break
                    except TypeError:
                        pass

                return event_name
            assert transition is not None
            assert transition.name is not None
            transition_name = transition.name
            #print (transition.name)

            assert transition.source is not None
            assert transition.source.name is not None
            #print (transition.source.name)

            assert transition.target is not None
            assert transition.target.name is not None
            #print (transition.target.name)

            source_state = transition.source.name
            target_state = transition.target.name

            assert transition.trigger_action.payload_parameter is not None
            transition_event = extract_event_name(
                transition.trigger_action.payload_parameter
            )
            #print (source_state, target_state, transition_event)

            # Ensure no None values
            if source_state and target_state and transition_name:
                ET.SubElement(
                    state_elements[transition.source],
                    "transition",
                    {"event": transition_event, "target": target_state}
                )


    def to_xml_string(self):
        """Returns the SCXML as a formatted XML string with line breaks and indentation."""
        raw_xml = ET.tostring(self.scxml, encoding="utf-8")
        parsed_xml = xml.dom.minidom.parseString(raw_xml)
        return parsed_xml.toprettyxml(indent="  ")  # Two-space indentation
