import Const
import math
from typing import List
from Effects import Effect
from ForwardDeclarations import Character

class InertSalsotto:
    def __init__(self, user: Character):
        self.class_name = self.__class__.__name__
        self.user = user
        self.effects = Effect([self.get_buff, self.get_value, None, False, 1], 'buff', 'InertSalsotto', self.user)
    
    def get_buff(self, obj, value, s):
        if value == 0 or s['crit_rate'] < 50:
            return s
        s[f'{self.user.stats["CombatType"]}_DMG_Boost'] += value
        return s
    
    def get_value(self, skill, effect: Effect):
        if skill == 'Q' or skill == 'AA':
            return 15
        return 0
    
class SprightlyVonwacq:
    def __init__(self, user: Character):
        self.class_name = self.__class__.__name__
        self.user = user
        self.effects = Effect([self.get_buff, 0.4, 1, False, 1], 'buff', 'SprightlyVonwacq', self.user)
    
    def get_buff(self, obj: 'Character', value, s):
        if value == 0 or s['SPD'] < 120:
            return s
        s['tiqian'] += value
        return s
    

class Relics:
    
    """
    The Relics class is used to represent the attributes of a character's relic equipment in the context of a game. Relics are special items equipped by characters and can provide various attribute enhancements. This class includes methods and attributes for managing relic attributes.

    Attributes:

    stats (dict): A dictionary that stores relic attributes, including base attributes, elemental attributes, main attributes, and sub-attributes.
    class_name (str): The name of the class.
    Methods:

    __init__(self, level: int = 15, param: List[tuple] = None, seteffect: List[Effect] = None): Class constructor used to initialize a relic object.
    transfer_to_attr(self): Transfers attributes to the object's attributes.
    __init__by_param(self): Initializes attributes based on parameters.
    set_stats(self, param): Sets attribute parameters.
    get_stat(self): Retrieves the relic's attribute dictionary.
    adjustment(self, param=None): Adjusts attribute values.
    show_stats(self): Prints the attributes of the relic.
    keys(self): Retrieves the keys of the attribute dictionary.
    values(self): Retrieves the values of the attribute dictionary.
    __str__(self): Converts the relic object to a string representation.
    __getitem__(self, key): Retrieves a value from the attribute dictionary.
    __setitem__(self, key, value): Sets a value in the attribute dictionary.
    items(self): Retrieves key-value pairs from the attribute dictionary.
    __iter__(self): Iterates through the keys of the attribute dictionary.
    __next__(self): Iterates to the next key in the attribute dictionary.
    __add__(self, other): Adds the attributes of two relic objects and returns a new relic object.
    __sub__(self, other): Subtracts the attributes of two relic objects and returns a new relic object.
    to_dict(self): Converts the relic object to a dictionary.
    __contains__(self, item): Checks if a specified item is contained in the attribute dictionary.
    __missing__(self, key): Adds a key to the attribute dictionary and sets its value to 0 if it doesn't exist.
    __len__(self): Gets the number of items in the attribute dictionary.
    Parameters:

    level (int): The level of the relic, defaulting to 15.
    param (List[tuple]): The relic's attribute parameters, passed as key-value pairs.
    seteffect (List[Effect]): A list of effects associated with the relic.
    Note:

    This class is designed to manage relic attributes and can be extended or customized as needed to accommodate additional attributes or methods.
    """
    
    def __init__(self, level:int = 15, param: List[tuple] = None, seteffect: List[Effect] = None, adj:bool = True):
        
        self.stats = {'base_HP': 0.0,
                      'base_ATK': 0.0,
                      'base_DEF': 0.0,
                      'SPD': 0.0,
                      'max_energy': 0.0,
                      'crit_rate': 0.0,
                      'crit_damage': 0.0,
                      'break_effect': 0.0,
                      'energy_regeneration_rate': 0.0,
                      'outgoing_healing_boost': 0.0,
                      'effect_hit_rate': 0.0,
                      'effect_RES': 0.0,
                      'jianfang': 0.0,
                      'chaungtou': 0.0,
                      'yishang': 0.0,
                      }
        prop = ['Physical', 'Wind', 'Ice', 'Fire',
                'Lightning', 'Quantum', 'Imaginary']
        for i in prop:
            s1 = f'{i}_DMG_Boost'
            s2 = f'{i}_RES_Boost'
            self.stats[s1] = 0.0
            self.stats[s2] = 0.0
        self.stats['HP'] = 0.0
        self.stats['ATK'] = 0.0
        self.stats['DEF'] = 0.0
        self.stats['HP%'] = 0.0
        self.stats['ATK%'] = 0.0
        self.stats['DEF%'] = 0.0
        self.stats['name'] = ''
        self.stats['set'] = ''
        self.stats['piece'] = None
        self.stats['level'] = level
        self.stats['main_stat'] = None
        self.stats['sub_stat'] = ['','','','']
        if seteffect is not None:
            self.stats['Effects'] = seteffect
        self.stats['class_name'] = self.__class__.__name__
        self.set_stats(param)
        self.__init__by_param()
        if adj:
            self.adjustment()
        self.transfer_to_attr()
            
    def transfer_to_attr(self) -> None:
        for k,v in self.items():
            setattr(self, k, v)
        
    def __init__by_param(self) -> None:
        piece = self.stats['piece']
        if piece is None:
            if self.stats['HP'] == 752.6:
                self.stats['piece'] = 'head'
            elif self.stats['ATK'] == 352.8:
                self.stats['piece'] = 'hand'
            return
        if self.stats['level'] != 15:
            return
        if piece == 'head':
            self.stats['HP'] = 752.6
            self.stats['main_stat'] = 'HP'
        elif piece == 'hand':
            self.stats['ATK'] = 352.8
            self.stats['main_stat'] = 'ATK'
        else:
            if self.stats['main_stat'] is not None:
                self.stats[self.stats['main']] = Const.YiQi_Unit[self.stats['main']] * 100
                return
            for k,v in Const.YiQi_Unit.items():
                if self.stats[k] == v/100:
                    self.stats['main_stat'] = k
                    return
            for i in ['Physical', 'Wind', 'Ice', 'Fire','Lightning', 'Quantum', 'Imaginary']:
                if self.stats[f'{i}_DMG_Boost'] == 38.8803:
                    self.stats['main_stat'] = f'{i}_DMG_Boost'
                    return

    def set_stats(self, param) -> None:
        if param == None:
            return
        for k, v in param:
            if isinstance(v, str) or isinstance(v, list):
                self.stats[k] = v
            else:
                self.stats[k] += v

    def get_stat(self) -> dict:
        return self.stats

    def adjustment(self, param:List[str] = None):
        if param is None:
            for k, v in Const.YiQi_Unit.items():
                if self.stats[k] != 0 and k != self.stats['main_stat']:
                    stat = math.ceil(self.stats[k]*10000 / v)
                    self.stats[k] = stat * v / 10000
        else:
            for k in param:
                v = Const.YiQi_Unit[k]
                stat = math.ceil(self.stats[k]*10000 / v)
                self.stats[k] = stat * v / 10000

    def show_stats(self) -> None:
        max_label_width = max(len(label) for label, _ in self.items())
        for label, value in self.items():
            if isinstance(value, (int, float)):
                format_string = f"{{:<{max_label_width}}}  {{:.2f}}"
            else:
                format_string = f"{{:<{max_label_width}}}  {{}}"
            print(format_string.format(label, value))
            
    def keys(self):
        return self.stats.keys()
    
    def values(self):
        return self.stats.values()
        
    def to_dict(self):
        return self.stats
    
    def __str__(self):
        return str(self.stats)
    
    def __getitem__(self, key):
        if key not in self.stats.keys():
            self.__missing__(key)
        return self.stats[key]
    
    def __setitem__(self, key, value):
        self.stats[key] = value
    
    def items(self):
        return self.stats.items()
    
    def __iter__(self):
        return self.stats.__iter__()
    
    def __next__(self):
        return self.__next__()
    
    def __add__(self, other):
        r = Relics()
        for k in self.keys():
            if isinstance(self[k], (int, float)) and isinstance(other[k], (int, float)) and k != 'level':
                r[k] = self[k] + other[k]
        return r
    
    def __sub__(self, other):
        r = Relics()
        for k in self.keys():
            if isinstance(self[k], (int, float)) and isinstance(other[k], (int, float)) and k != 'level':
                r[k] = self[k] - other[k]
        return r
    
    def __contains__(self, item):
        if isinstance(item, tuple):
            return item in self.items()
        elif isinstance(item, (int, float, str)):
            return item in self.keys() or item in self.values()
        elif isinstance(item, Effect):
            return item in self['Effects']
        
    def __missing__(self, key):
        self.stats[key] = 0
        
    def __len__(self):
        return len(self.values())          