from dataclasses import dataclass, field
from datetime import datetime
import json

'''
# Dataclass to store sensor readings, using formatting methods and incrementing ID fields
# Helps to make the observations standardized and SSNO compliant 
'''
@dataclass (repr=True)
class Observation():		
	_sender_id: int
	_sender_name: str
	_obs_id: int = field(init=False)
	_feature_of_interest: str
	_observed_property: str
	_has_result: dict
 
	def __post_init__(self):
		self._obs_id = Observation.iterator
		Observation.iterator += 1		
		self._result_time = datetime.now()

	def to_mqtt_payload(self):
		return json.dumps(vars(self), default=str)

	def add_result_pair(self, key, value):
		self._has_result[key] = value
  
Observation.iterator = 0