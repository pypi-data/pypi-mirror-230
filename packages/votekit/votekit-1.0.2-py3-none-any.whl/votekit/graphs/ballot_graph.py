from .base_graph import Graph
from ..pref_profile import PreferenceProfile
from ..utils import COLOR_LIST
from typing import Optional, Union
import networkx as nx  # type: ignore
from functools import cache


class BallotGraph(Graph):
    """
    Class to build graphs for elections with possible incomplete ballots

    **Attributes**

    `source`
    :   data to create graph from, either PreferenceProfile object, number of
            candidates, or list of candidates

    `complete`
    :   if True, builds complete graph, else builds incomplete (boolean)

    **Methods**
    """

    def __init__(
        self,
        source: Union[PreferenceProfile, int, list],
        complete: Optional[bool] = True,
    ):
        super().__init__()

        self.profile = None
        self.candidates = None

        if isinstance(source, int):
            self.graph = self.build_graph(source)
            self.num_cands = source

        if isinstance(source, list):
            self.num_cands = len(source)
            self.graph = self.build_graph(len(source))
            self.candidates = source

        if isinstance(source, PreferenceProfile):
            self.profile = source
            self.num_voters = source.num_ballots()
            self.num_cands = len(source.get_candidates())
            if not self.graph:
                self.graph = self.build_graph(len(source.get_candidates()))
            self.graph = self.from_profile(source, complete)

        if not self.node_data:
            self.node_data = {ballot: 0 for ballot in self.graph.nodes}

        self.num_voters = sum(self.node_data.values())

    def _relabel(self, gr: nx.Graph, new_label: int, num_cands: int) -> nx.Graph:
        """
        Relabels nodes in gr based on new_label
        """
        node_map = {}
        graph_nodes = list(gr.nodes)

        for k in graph_nodes:
            # add the value of new_label to every entry in every ballot
            tmp = [new_label + y for y in k]

            # reduce everything mod new_label
            for i in range(len(tmp)):
                if tmp[i] > num_cands:
                    tmp[i] = tmp[i] - num_cands
            node_map[k] = tuple([new_label] + tmp)

        return nx.relabel_nodes(gr, node_map)

    def build_graph(self, n: int) -> nx.Graph:  # ask Gabe about optimizing?
        """
        Builds graph of all possible ballots given a number of candiates

        Args:
            n: number of candidates per an election
        """
        Gc = nx.Graph()
        # base cases
        if n == 1:
            Gc.add_nodes_from([(1)], weight=0, cast=False)

        elif n == 2:
            Gc.add_nodes_from([(1, 2), (2, 1)], weight=0, cast=False)
            Gc.add_edges_from([((1, 2), (2, 1))])

        elif n > 2:
            G_prev = self.build_graph(n - 1)
            for i in range(1, n + 1):
                # add the node for the bullet vote i
                Gc.add_node((i,), weight=0, cast=False)

                # make the subgraph for the ballots where i is ranked first
                G_corner = self._relabel(G_prev, i, n)

                # add the components from that graph to the larger graph
                Gc.add_nodes_from(G_corner.nodes, weight=0, cast=False)
                Gc.add_edges_from(G_corner.edges)

                # connect the bullet vote node to the appropriate vertices
                if n == 3:
                    Gc.add_edges_from([(k, (i,)) for k in G_corner.nodes])
                else:
                    Gc.add_edges_from(
                        [(k, (i,)) for k in G_corner.nodes if len(k) == 2]
                    )

            nodes = Gc.nodes

            new_edges = [
                (bal, (bal[1], bal[0]) + bal[2:]) for bal in nodes if len(bal) >= 2
            ]
            Gc.add_edges_from(new_edges)

        return Gc

    def from_profile(
        self, profile: PreferenceProfile, complete: Optional[bool] = True
    ) -> nx.Graph:
        """
        Updates existing graph based on cast ballots from a PreferenceProfile,
        or creates graph based on PreferenceProfile

        Args:
            profile: PreferenceProfile assigned to graph
            complete: If True, builds complete graph

        Returns:
            Complete or incomplete graph based on PrefreneceProfile
        """
        if not self.profile:
            self.profile = profile

        if not self.num_voters:
            self.num_voters = profile.num_ballots()

        self.candidates = profile.get_candidates()
        ballots = profile.get_ballots()
        self.cand_num = self._number_cands(tuple(self.candidates))
        self.node_data = {ballot: 0 for ballot in self.graph.nodes}

        for ballot in ballots:
            ballot_node = []
            for position in ballot.ranking:
                if len(position) > 1:
                    raise ValueError(
                        "ballots must be cleaned to resolve ties"
                    )  # still unsure about ties
                for cand in position:
                    ballot_node.append(self.cand_num[cand])
            if len(ballot_node) == len(self.candidates) - 1:
                ballot_node = self.fix_short_ballot(
                    ballot_node, list(self.cand_num.values())
                )

            if tuple(ballot_node) in self.graph.nodes:
                self.graph.nodes[tuple(ballot_node)]["weight"] += ballot.weight
                self.graph.nodes[tuple(ballot_node)]["cast"] = True
                self.node_data[tuple(ballot_node)] += ballot.weight

        if not complete:
            partial = nx.Graph()
            for node in self.graph.nodes:
                if self.graph.nodes[node]["cast"]:
                    partial.add_node(
                        node,
                        weight=self.graph.nodes[node]["weight"],
                        cast=self.graph.nodes[node]["cast"],
                    )

            self.graph = partial

        return self.graph

    def fix_short_ballot(self, ballot: list, candidates: list) -> list:
        """
        Appends short ballots of n-1 length to add to BallotGraph
        """
        missing = set(candidates).difference(set(ballot))

        return ballot + list(missing)

    def label_cands(self, candidates):
        """
        Assigns candidate labels to ballot graph for plotting
        """

        candidate_numbers = self._number_cands(tuple(candidates))

        cand_dict = {value: key for key, value in candidate_numbers.items()}

        cand_labels = {}
        for node in self.graph.nodes:
            ballot = []
            for num in node:
                ballot.append(cand_dict[num])
            cand_labels[node] = tuple(ballot)

        return cand_labels

    @cache
    def _number_cands(self, cands: tuple) -> dict:
        """
        Assigns numerical marker to candidates
        """
        legend = {}
        for idx, cand in enumerate(cands):
            legend[cand] = idx + 1

        return legend

    def draw(self, neighborhoods: Optional[dict] = {}, labels: Optional[bool] = False):
        """
        Visualize the whole election or select neighborhoods in the election.

        Args:
            neighborhoods: Section of graph to draw
            labels: If True, labels nodes with candidate names
        """
        # TODO: change this so that neighborhoods can have any neighborhood
        # not just heavy balls, also there's something wrong with the shades
        Gc = self.graph
        GREY = (0.44, 0.5, 0.56)
        node_cols: list = []
        node_labels = None

        k = len(neighborhoods) if neighborhoods else self.num_cands
        if k > len(COLOR_LIST):
            raise ValueError("Number of neighborhoods exceeds colors for plotting")
        cols = COLOR_LIST[:k]

        # self._clean()
        for ballot in Gc.nodes:
            i = -1
            color: tuple = GREY

            if neighborhoods:
                for center, neighborhood in neighborhoods.items():
                    neighbors, _ = neighborhood
                    if ballot in neighbors:
                        i = (list(neighborhoods.keys())).index(center)
                        break
            elif self.node_data[ballot] != 0 and self.profile:
                print(ballot)
                i = (list(self.cand_num.values())).index(ballot[0])

            if "weight" in ballot:
                color = tuple(ballot.weight * x for x in cols[i])
            node_cols.append(color)

        if labels:
            if not self.candidates:
                raise ValueError("no candidate names assigned")
            if self.candidates:
                node_labels = self.label_cands(self.candidates)
            elif self.profile:
                node_labels = self.label_cands(self.profile.get_candidates())

        nx.draw_networkx(Gc, with_labels=True, node_color=node_cols, labels=node_labels)

    # what are these functions supposed to do?
    # def compare(self, new_pref: PreferenceProfile, dist_type: Callable):
    #     """compares the ballots of current and new profile"""
    #     raise NotImplementedError("Not yet built")

    # def compare_rcv_results(self, new_pref: PreferenceProfile):
    #     """compares election results of current and new profle"""
    #     raise NotImplementedError("Not yet built")
