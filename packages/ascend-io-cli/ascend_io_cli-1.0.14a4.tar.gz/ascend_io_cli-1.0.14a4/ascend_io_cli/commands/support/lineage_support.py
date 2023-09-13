import collections
from enum import Enum

import glog
import networkx as nx
from ascend.sdk.client import Client
from google.protobuf.json_format import MessageToDict


def _node_value(node):
  return node[0].value if len(node) else 1


def _flatten(dictionary, parent_key=None, separator='.'):
  items = []
  for key, value in dictionary.items():
    new_key = str(parent_key) + separator + key if parent_key else key
    if isinstance(value, collections.abc.MutableMapping):
      items.extend(_flatten(value, new_key, separator).items())
    elif isinstance(value, list):
      for k, v in enumerate(value):
        items.extend(_flatten({str(k): v}, new_key).items())
    else:
      items.append((new_key, value))
  return dict(items)


class OutputFormat(Enum):
  GraphML = 'GraphML', True
  GEXF = 'GEXF', True
  GML = 'GML', False

  def __new__(cls, *args, **kwds):
    obj = object.__new__(cls)
    obj._value_ = args[0]
    return obj

  # ignore the first param since it's already set by __new__
  def __init__(self, _: str, flatten: bool = False):
    self._flatten = flatten

  def __str__(self):
    return self.value

    # this makes sure that the description is read-only

  @property
  def flatten(self):
    return self._flatten

  def generate(self, G) -> str:
    for k, v in G.nodes.items():
      # need to convert the protos to dicts for all types
      v['component'] = MessageToDict(v['component'])
      if self.flatten:
        # must convert the component to a dict
        df = _flatten(v['component'])
        # add the new values as a flat key value pair
        v.update(df)
        # remove the original component item
        v.pop('component')

    if self == self.GraphML:
      return '\n'.join(nx.generate_graphml(
          G,
          encoding='utf-8',
          prettyprint=True,
      ))
    elif self == self.GEXF:
      return '\n'.join(nx.generate_gexf(
          G,
          encoding='utf-8',
          prettyprint=True,
      ))
    elif self == self.GML:
      return '\n'.join(nx.generate_gml(G))

    raise ValueError(f'OutputFormat {self.name} not supported')


class LineageContext:

  def __init__(self, centroid) -> None:
    if not centroid or not hasattr(centroid, 'uuid'):
      raise ValueError('A centroid is required to establish lineage context')
    self.graph = nx.DiGraph()
    self.centroid = centroid
    self.data_services = set()

  def _assert_centroid(self):
    if not self.centroid or not getattr(self.centroid, 'uuid', None):
      raise ValueError('Cannot generate lineage without a component to use as a relative starting point. Did you build_graph()?')

  def _nodes_as_map(self):
    return {n[0]: n[1]['component'] for n in self.graph.nodes(data=True)}

  def upstream(self) -> list:
    """Return the upstream lineage ending with the centroid component"""
    self._assert_centroid()
    nodes = self._nodes_as_map()
    return [nodes[n] for n in list(nx.bfs_tree(self.graph, self.centroid.uuid, reverse=True))[::-1]]

  def downstream(self) -> list:
    """Return the downstream lineage starting with centroid component"""
    self._assert_centroid()
    nodes = self._nodes_as_map()
    return [nodes[n] for n in list(nx.bfs_tree(self.graph, self.centroid.uuid, reverse=False))]

  def readers(self) -> list:
    """Return the readers for this context"""
    self._assert_centroid()
    return [s for s in self.upstream() if s.type == 'source']

  def writers(self) -> list:
    """Return the writers for this context"""
    self._assert_centroid()
    return [s for s in self.downstream() if s.type == 'sink']

  def end_to_end(self) -> list:
    """Return the end to end lineage passing through the centroid."""
    self._assert_centroid()
    up = self.upstream()
    down = self.downstream()
    if up and down:
      return up + down[1:]
    elif up:
      return up
    else:
      return down

  def __str__(self) -> str:
    return f'LineageContext for {self.centroid}'


def _record_component(component, components: dict, component_id_alias: dict):
  if component:
    components[component.uuid] = component
    # also have to map ComponentID
    if getattr(component, 'ComponentID', None):
      component_id_alias[component.ComponentID] = component.uuid


def _log_mapping(c_in, c_tgt, components: dict):
  if c_in in components and c_tgt in components:
    source = components[c_in]
    target = components[c_tgt]
    glog.debug(f'{source.organization.id}.{source.project.id}.{source.id} -> {target.organization.id}.{target.project.id}.{target.id}')
  elif c_in in components:
    source = components[c_in]
    glog.warning(f'{source.organization.id}.{source.project.id}.{source.id} -> UNKNOWN ({c_tgt})')
  elif c_in == 'SOURCE':
    target = components[c_tgt]
    glog.debug(f'DATA SOURCE -> {target.organization.id}.{target.project.id}.{target.id}')
  elif c_tgt in components:
    target = components[c_tgt]
    glog.warning(f'UNKNOWN ({c_in}) -> {target.organization.id}.{target.project.id}.{target.id}')
  else:
    glog.warning(f'UNKNOWN ({c_in}) -> UNKNOWN ({c_tgt})')


class LineageSupport:

  def __init__(self, client: Client):
    self._client = client

  def build_graph(self, data_service_id: str, dataflow_id: str = None, component_id: str = None, details: bool = False) -> LineageContext:
    if not data_service_id:
      raise ValueError('A Data Service is required to calculate lineage.')

    components, edges = self._assemble_graph(data_service_id, deep=details)

    cen = [v for v in components.values() if v.organization.id == data_service_id and v.project.id == dataflow_id and v.id == component_id]
    if not cen:
      raise ValueError(f'Could not find component {data_service_id}.{dataflow_id}.{component_id} to use as lineage centroid')

    context = LineageContext(cen[0])
    context.graph.add_nodes_from([(node, {'component': attr}) for (node, attr) in components.items()])
    context.graph.add_edges_from(edges)
    return context

  def _gather_components(
      self,
      data_service_id: str,
      data_services: set = None,
      components: dict = None,
      component_id_alias: dict = None,
      deep: bool = False,
  ) -> (dict, dict):
    """Gather all components from each data service that may be linked via shares. This is a recursive function that steps through components
    looking for data services to load. We load all components for data services because it is simple and we don't know the lineage of what to load
    until it is calculated."""
    if data_services is None:
      data_services = set()
    elif data_service_id in data_services:
      glog.debug(f'{data_service_id} already processed')
      return components

    data_services.add(data_service_id)

    if not components:
      components = {}
      component_id_alias = {}

    glog.debug(f'Assembling components for {data_service_id}')

    data_service_components = self._client.list_data_service_components(data_service_id, deep=deep).data

    for c in [dsc for dsc in data_service_components if dsc.type not in ['group']]:
      _record_component(c, components, component_id_alias)
      if c.type in ['data_share_connector']:
        glog.debug(f'pulling data shares for {c.organization.id}.{c.project.id}.{c.id}')
        # data shares don't properly report the right upstream UUID so fix that
        the_share = self._client.get_data_share_connector(c.organization.id, c.project.id, c.id).data
        if deep:
          # swap out the component
          _record_component(the_share, components, component_id_alias)
        else:
          c.inputComponentIDs = the_share.data_shareUUID
        # pull the share also
        df = self._client.get_data_share_for_data_share_connector(c.organization.id, c.project.id, c.id).data
        _record_component(df, components, component_id_alias)
        self._gather_components(df.organization.id, data_services, components, component_id_alias)
      elif c.type in ['sub']:
        glog.debug(f'pulling data feed publishers for sub {c.organization.id}.{c.project.id}.{c.id}')
        df = self._client.get_data_feed_for_data_feed_connector(c.organization.id, c.project.id, c.id).data
        # subscribers don't have an id in them so add it now that we know it. this is a bug in the API (IMHO)
        c.inputComponentIDs = ','.join(filter(None, [c.inputComponentIDs, df.uuid]))
        _record_component(df, components, component_id_alias)
        self._gather_components(df.organization.id, data_services, components, component_id_alias)
      elif c.type in ['data_share']:
        glog.debug(f'pulling data share connectors for share {c.organization.id}.{c.project.id}.{c.id}')
        for d in [
            s for s in self._client.get_data_share_connectors_for_data_share(c.organization.id, c.project.id, c.id).data if data_service_id != s.organization.id
        ]:
          _record_component(d, components, component_id_alias)
          self._gather_components(d.organization.id, data_services, components, component_id_alias)
      elif c.type in ['pub']:
        glog.debug(f'pulling data feed connectors for share {c.organization.id}.{c.project.id}.{c.id}')
        for d in [s for s in self._client.get_data_feed_subscribers(c.organization.id, c.project.id, c.id).data if data_service_id != s.organization.id]:
          _record_component(d, components, component_id_alias)
          self._gather_components(d.organization.id, data_services, components, component_id_alias)

    return components, component_id_alias

  def _assemble_graph(
      self,
      data_service_id: str,
      deep: bool = False,
  ) -> (dict, list):
    """Gather all potential components in the tree and assemble a graph centered on the supplied data_service_id"""

    components, alias = self._gather_components(data_service_id, deep=deep)
    glog.info(f'found {len(components)} components to graph')

    glog.debug(f"Assembling graph centered on  data service '{data_service_id}'")

    edges = []

    # build the network edges
    for k, v in components.items():
      if v.type in ['source']:
        # no inputs to sources
        _log_mapping('SOURCE', v.uuid, components)
      elif getattr(v, 'inputs', None):
        for c_in in v.inputs:
          edges.append((c_in.uuid, v.uuid))
          _log_mapping(c_in.uuid, v.uuid, components)
      elif getattr(v, 'inputComponentIDs', None):
        input_ids = v.inputComponentIDs.split(',')
        if input_ids:
          for in_id in filter(None, input_ids):
            source = None
            if in_id in components:
              source = components[in_id]
            elif in_id in alias and alias[in_id] in components:
              source = components[alias[in_id]]
            if source:
              edges.append((source.uuid, v.uuid))
            else:
              glog.warn(f'component not found {in_id} referenced by {v.organization.id}.{v.project.id}.{v.id}')
            _log_mapping(source.uuid, v.uuid, components)
        else:
          glog.warn(f'component has no input ids: {v.organization.id}.{v.project.id}.{v.id}')
          _log_mapping('UNK', v.uuid, components)
      elif getattr(v, 'data_shareUUID', None):
        edges.append((v.data_shareUUID, v.uuid))
        _log_mapping(v.data_shareUUID, v.uuid, components)
      elif getattr(v, 'pubUUID', None):
        edges.append((v.pubUUID, v.uuid))
        _log_mapping(v.pubUUID, v.uuid, components)
      elif getattr(v, 'inputUUID', None):
        edges.append((v.inputUUID, v.uuid))
        _log_mapping(v.inputUUID, v.uuid, components)
      else:
        glog.info(f"No mapping data for '{v.organization.id}.{v.project.id}.{v.id}:{v.type},{v.uuid}'")

    # reduce component dict to the values that have a corresponding edge
    return {c: components[c] for c in [c for t in edges for c in t]}, edges
