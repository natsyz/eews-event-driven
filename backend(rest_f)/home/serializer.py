from rest_framework import serializers

from .models import *


class ReactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mseed_Data
        fields = ['name', 'stats','network', 'station', 'location', 'channel',
                  'starttime', 'endtime', 'sampling_rate', 'delta', 
                  'npts', 'calib', 'data']
        
class Mseeds(object):
    def __init__(self, traces):
        self.traces = traces
    
class MseedSerializer(serializers.ModelSerializer):
    traces = serializers.ListField(child = serializers.DictField(allow_null=True), allow_null=True, default=[])
    
    class Meta:
        model = Mseed
        fields = ['name', 'traces']