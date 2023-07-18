from typing import List, Optional
import faust

class RawValue(faust.Record, serializer="json"):
    mseed_name: str
    filename: str

class MseedData(faust.Record, serializer="json"): 
    network: Optional[str] 
    station: Optional[str] 
    location: Optional[str] 
    channel: Optional[str] 
    starttime: Optional[str] 
    endtime: Optional[str] 
    sampling_rate: Optional[float] 
    delta: Optional[float] 
    npts: Optional[int] 
    calib: Optional[float] 
    data: Optional[str]

class PreprocessedValue(faust.Record, serializer="json"):
    name: str
    traces: List[MseedData]