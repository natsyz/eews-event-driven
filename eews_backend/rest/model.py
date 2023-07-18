from typing import List, Optional
from pydantic import BaseModel, Field

class SeismometerModel(BaseModel):
    name: str = Field()
    description: Optional[str] = Field()
    x: float = Field(...)
    y: float = Field(...)
    
class MSeedData(BaseModel):
    network: Optional[str] = Field()
    station: Optional[str] = Field()
    location: Optional[str] = Field()
    channel: Optional[str] = Field()
    starttime: Optional[str] = Field()
    endtime: Optional[str] = Field()
    sampling_rate: Optional[float] = Field()
    delta: Optional[float] = Field()
    npts: Optional[int] = Field()
    calib: Optional[float] = Field()
    data: Optional[str]= Field()
    
class MSeed(BaseModel):
    name: str = Field()
    traces: Optional[List[MSeedData]] = Field()
    