from typing import Dict
from .interfaces import EffectType, ReactiveStateType, GlobalStoreType

class Store(GlobalStoreType):
    def __init__(self):
        self.trees = []
        self.processing_tree = None
        self.root_nodes = []
        self.id_nodes = {}
        self.active_component = None
        self.state = {}
        self.staged_effects = []

store = Store()
