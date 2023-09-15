# mvs_tool -i tests/benchmark_test_inputs/Feature_input_flows_as_list -ext csv -f
# mvs_tool -i tests/benchmark_test_inputs/Feature_output_flows_as_list -ext csv -f
from oemof import solph
from oemof.solph import Flow

FLOW_DEFAULT = {
    "values": None,
    "max": [],
    "variable_costs": "0",  # []
    "nonconvex": None,
    "summed_min": None,
    "nominal_value": None,
    "investment": None,
    "fix": "None",  # []
    "negative_gradient": {"ub": [], "costs": 0},
    "summed_max": None,
    "integer": None,
    "positive_gradient": {"ub": [], "costs": 0},
    "min": [],
}
flow_default = FLOW_DEFAULT

INVESTMENT_DEFAULT = solph.options.Investment().__dict__


def parse_investment(inv):
    investment_arguments = []
    for p, pval in inv.__dict__.items():
        if p in INVESTMENT_DEFAULT:
            if INVESTMENT_DEFAULT[p] != pval:
                investment_arguments.append(f"{p}={pval}")
        else:
            investment_arguments.append(f"{p}={pval}")
    return f"solph.options.Investment({', '.join(investment_arguments)})"


def is_bus_flow_dict(d):
    answer = False
    if isinstance(d, dict):
        answer = 0
        for k, v in d.items():
            if isinstance(k, solph.Bus) and isinstance(v, solph.Flow):
                pass
            else:
                answer = answer + 1
        answer = answer == 0
    return answer


def parse_bus_flow_dict(d):
    bus_flow_pairs = []
    for bus, flow in d.items():
        flow_arguments = []
        for p, pval in flow.__dict__.items():

            if p in FLOW_DEFAULT:
                # print(p)
                if isinstance(pval, solph.plumbing._Sequence):
                    # print(p)
                    # print(pval.highest_index)
                    pval = parse_sequence(pval)

                try:
                    if FLOW_DEFAULT[p] != pval:
                        if p == "investment":
                            # import ipdb;ipdb.set_trace()
                            flow_arguments.append(f"{p}={parse_investment(pval)}")
                        else:
                            flow_arguments.append(f"{p}={pval}")
                except ValueError:
                    flow_arguments.append(f"{p}={pval}")
            else:
                if p[0] != "_":
                    flow_arguments.append(f"{p}={pval}")
                print(p, "not in the outputs of flow")
        bus_flow_pairs.append(f"{bus.label}: solph.Flow({', '.join(flow_arguments )})")
    return bus_flow_pairs


def parse_sequence(v):
    if len(v) == 0:
        v = f"{v[0]}"
    else:
        v = f"[{','.join([str(el) for el in v])}]"
    return v


class ESCodeRenderer:
    def __init__(self, energy_system):
        self.energy_system = energy_system
        self.es_variable_name = "energy_system"
        self.busses = [n for n in self.energy_system.nodes if isinstance(n, solph.Bus)]
        self.sources = [
            n
            for n in self.energy_system.nodes
            if isinstance(n, solph.components.Source)
        ]
        self.sinks = [
            n for n in self.energy_system.nodes if isinstance(n, solph.components.Sink)
        ]
        self.transformers = [
            n
            for n in self.energy_system.nodes
            if isinstance(n, solph.components.Transformer)
        ]
        self.storages = [
            n
            for n in self.energy_system.nodes
            if isinstance(n, solph.components.GenericStorage)
        ]
        self.chps = [
            n
            for n in self.energy_system.nodes
            if isinstance(n, solph.components.GenericCHP)
        ]
        self.extractions_turbines = [
            n
            for n in self.energy_system.nodes
            if isinstance(n, solph.components.ExtractionTurbineCHP)
        ]
        self.offset_transformers = [
            n
            for n in self.energy_system.nodes
            if isinstance(n, solph.components.OffsetTransformer)
        ]

    def print(self, fname=None):
        if fname is None:
            answer = (
                self.print_import_statements()
                + self.print_es_definition()
                + self.print_busses()
                + self.print_transformers()
                + self.print_chps()
                + self.print_extraction_turbines()
                + self.print_offet_transformers()
                + self.print_storages()
                + self.print_sources()
                + self.print_sinks()
            )
            for l in answer:
                print(l)

    def print_import_statements(self):
        answer = [""]
        answer.append("from oemof import solph")
        answer.append("")
        return answer

    def print_es_definition(self):
        return ["", f"{self.es_variable_name} = solph.EnergySystem()", ""]

    def print_busses(self):
        answer = [""]
        for bus in self.busses:
            answer.append(f"{bus.label} = solph.Bus(label='{bus.label}')")
        answer.append("")
        return answer

    def print_transformers(self):
        answer = []
        for i, t in enumerate(self.transformers):
            answer.append("")
            answer = answer + self.print_single_transformer(t, variable_name=f"t{i+1}")
            answer.append("")
        return answer

    def print_single_transformer(self, t, variable_name="t"):
        all_args = {}
        all_args["label"] = f"'{t.label}'"
        input_params = parse_bus_flow_dict(t.inputs)

        all_args["inputs"] = "{" + ", ".join(input_params) + "}"

        output_params = parse_bus_flow_dict(t.outputs)

        all_args["outputs"] = "{" + ", ".join(output_params) + "}"

        conv_factors = []
        for k, v in t.conversion_factors.items():
            parse_sequence(v)
            conv_factors.append(f"{k}: {v}")
        all_args["conversion_factors"] = "{" + ", ".join(conv_factors) + "}"

        answer = []
        answer.append(f"{variable_name} = solph.components.Transformer(")
        for a, v in all_args.items():
            answer.append("  " + f"{a}={v},")
        answer.append(")")
        answer.append("")
        answer.append(f"{self.es_variable_name}.add({variable_name})")
        answer.append("")

        return answer

    def print_chps(self):
        answer = []
        for i, t in enumerate(self.chps):
            answer.append("")
            answer = answer + self.print_single_chp(t, variable_name=f"chp{i+1}")
            answer.append("")
        return answer

    def print_single_chp(self, t, variable_name="t"):
        all_args = {}
        all_args["label"] = f"'{t.label}'"

        for k, v in t.__dict__.items():
            if is_bus_flow_dict(v) is True:
                dict_arguments = parse_bus_flow_dict(v)
                all_args[k] = "{" + ", ".join(dict_arguments) + "}"
            elif k[0] != "_":
                all_args[k] = v

        answer = []
        answer.append(f"{variable_name} = solph.components.GenericCHP(")
        for a, v in all_args.items():
            answer.append("  " + f"{a}={v},")
        answer.append(")")
        answer.append("")
        answer.append(f"{self.es_variable_name}.add({variable_name})")
        answer.append("")

        return answer

    def print_sources(self):
        answer = []
        for i, s in enumerate(self.sources):
            answer.append("")
            answer = answer + self.print_single_source(s, variable_name=f"source{i+1}")
            answer.append("")
        return answer

    def print_single_source(self, s, variable_name="s"):
        all_args = {}
        all_args["label"] = f"'{s.label}'"

        output_params = parse_bus_flow_dict(s.outputs)
        all_args["outputs"] = "{" + ", ".join(output_params) + "}"

        answer = []
        answer.append(f"{variable_name} = solph.components.Source(")
        for a, v in all_args.items():
            answer.append("  " + f"{a}={v},")
        answer.append(")")
        answer.append("")
        answer.append(f"{self.es_variable_name}.add({variable_name})")
        answer.append("")

        return answer

    def print_sinks(self):
        answer = []
        for i, s in enumerate(self.sinks):
            answer.append("")
            answer = answer + self.print_single_sink(s, variable_name=f"sink{i+1}")
            answer.append("")
        return answer

    def print_single_sink(self, s, variable_name="s"):
        all_args = {}
        all_args["label"] = f"'{s.label}'"
        input_params = parse_bus_flow_dict(s.inputs)
        all_args["inputs"] = "{" + ", ".join(input_params) + "}"

        answer = []
        answer.append(f"{variable_name} = solph.components.Sink(")
        for a, v in all_args.items():
            answer.append("  " + f"{a}={v},")
        answer.append(")")
        answer.append("")
        answer.append(f"{self.es_variable_name}.add({variable_name})")
        answer.append("")

        return answer

    def print_storages(self):
        answer = []
        for i, s in enumerate(self.storages):
            answer.append("")
            answer = answer + self.print_single_storage(
                s, variable_name=f"storage{i+1}"
            )
            answer.append("")
        return answer

    def print_single_storage(self, s, variable_name="s"):
        return self.print_custom(
            s, variable_name, component_name="solph.component.GenericStorage"
        )

    def print_extraction_turbines(self):
        answer = []
        for i, s in enumerate(self.extractions_turbines):
            answer.append("")
            answer = answer + self.print_single_extraction_turbine(
                s, variable_name=f"extr_turb{i+1}"
            )
            answer.append("")
        return answer

    def print_single_extraction_turbine(self, s, variable_name="s"):
        return self.print_custom(
            s, variable_name, component_name="solph.component.ExtractionTurbineCHP"
        )

    def print_offet_transformers(self):
        answer = []
        for i, t in enumerate(self.offset_transformers):
            answer.append("")
            answer = answer + self.print_single_offet_transformer(
                t, variable_name=f"offset_t{i + 1}"
            )
            answer.append("")
        return answer

    def print_single_offet_transformer(self, t, variable_name="s"):
        return self.print_custom(
            t, variable_name, component_name="solph.component.OffsetTransformer"
        )

    def print_custom(self, s, variable_name="s", component_name="solph.component"):
        all_args = {}
        all_args["label"] = f"'{s.label}'"

        input_params = parse_bus_flow_dict(s.inputs)
        all_args["inputs"] = "{" + ", ".join(input_params) + "}"

        output_params = parse_bus_flow_dict(s.outputs)
        all_args["outputs"] = "{" + ", ".join(output_params) + "}"

        for k, v in s.__dict__.items():
            print(k)
            print(v)
            if is_bus_flow_dict(v) is True:
                dict_arguments = parse_bus_flow_dict(v)
                all_args[k] = "{" + ", ".join(dict_arguments) + "}"
            elif k[0] != "_":
                if isinstance(v, solph.plumbing._Sequence):
                    v = parse_sequence(v)
                    # print(k)
                    # import ipdb; ipdb.set_trace()

                all_args[k] = v

        answer = []
        answer.append(f"{variable_name} = {component_name}(")
        for a, v in all_args.items():
            answer.append("  " + f"{a}={v},")
        answer.append(")")
        answer.append("")
        answer.append(f"{self.es_variable_name}.add({variable_name})")
        answer.append("")

        return answer


# cr = ESCodeRenderer(model)
# cr.print()
