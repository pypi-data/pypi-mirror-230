from pydantic import (
    BaseModel, Field, RootModel, ConfigDict 
)

user_model_config = ConfigDict(validate_assignment = True, extra="forbid")
""" A configuration for any model which will be modified by user """

state_model_config = ConfigDict()


class UserModel(BaseModel):
    model_config = user_model_config

class StateModel(BaseModel):
    model_config = state_model_config
