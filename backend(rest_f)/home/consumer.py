import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asyncio import sleep
from obspy import UTCDateTime
from datetime import timedelta

from .firebase_config import *
from .helper_functions import *
from .models import *

class GetGMJIConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        try:
          await self.accept()
          name = self.scope['url_route']['kwargs']['name']
          lsts = get_GMJI_data_firebase(name)
          sampling = int(lsts[0]['sampling_rate'])
          s = 1/sampling
          e = UTCDateTime(lsts[0]['starttime'])
          n = UTCDateTime(lsts[1]['starttime'])
          z = UTCDateTime(lsts[2]['starttime'])
          
          lst, sensor_first = s_add_starttime(e, n, z, lsts)
          starttime = UTCDateTime(lsts[0]['starttime_station']).datetime

          lst_time = []
          for j in range(lsts[0]['npts']):
            str_ = "".join(("0" + str(starttime.minute))[-2:] + ":" + ("0" + str(starttime.second))[-2:])
            lst_time.append(str_)
            starttime += timedelta(microseconds=(1000/sampling)*1000)
          str_p = None
          Ps = 0
          for i in range(0, lsts[0]['npts']):
            lst_json = []
            p = 0
            
            if i >= 30*sampling:
              datas1 = lst[0][i-(30*sampling):i]
              datas2 = lst[1][i-(30*sampling):i]
              datas3 = lst[2][i-(30*sampling):i]
              p = get_Parrival(datas1, datas2, datas3, sampling)
              if p != -1:
                    # print(p)
                    # print(i)
                    p += i - (30*sampling)
              else:
                    p = 0
                    
              if Ps == 0:
                    Ps = p
                  #   time = starttime_base + timedelta(microseconds=((1000*Ps)/sampling)*1000)
                  #   str_p = "".join(("0" + str(time.minute))[-2:] + ":" + ("0" + str(time.second))[-2:])
            data_mtr = {
                  'latitude': None,
                  'longitude': None,
                  'depth': None,
                  'magnitude': None,
                  'time': None
            }
            if i >= 100:
                  for j in range(i-100, i):
                        json_ = {'E_data':lst[0][j],
                              'N_data':lst[1][j],
                              'Z_data':lst[2][j],
                              'p_Arrival': int(Ps),
                              'sampling_rate': sampling,
                              'time': lst_time[j],
                              'x':j,
                              'data_prediction':data_mtr}
                        lst_json.append(json_)
            else:
                  lstss = [None]*100
                  for j in range(100):
                        json_ = {'E_data':lstss[j],
                              'N_data':lstss[j],
                              'Z_data':lstss[j],
                              'p_Arrival': None,
                              'sampling_rate': sampling,
                              'time': lstss[j],
                              'x':lstss[j],
                              'data_prediction':data_mtr}
                        lst_json.append(json_)
            await self.send(json.dumps(lst_json))
            await sleep(s)
          await self.close()
        except KeyboardInterrupt:
          await self.close()
          print('close')
          
    async def disconnect(self, code):
      return super().disconnect(code)
  
class GetJAGIConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        try:
          await self.accept()
          name = self.scope['url_route']['kwargs']['name']
          lsts = get_JAGI_data_firebase(name)
          sampling = int(lsts[0]['sampling_rate'])
          s = 1/sampling
          e = UTCDateTime(lsts[0]['starttime'])
          n = UTCDateTime(lsts[1]['starttime'])
          z = UTCDateTime(lsts[2]['starttime'])
          
          lst, sensor_first = s_add_starttime(e, n, z, lsts)
          starttime = UTCDateTime(lsts[0]['starttime_station']).datetime

          lst_time = []
          for j in range(lsts[0]['npts']):
            str_ = "".join(("0" + str(starttime.minute))[-2:] + ":" + ("0" + str(starttime.second))[-2:])
            lst_time.append(str_)
            starttime += timedelta(microseconds=(1000/sampling)*1000)
            
          str_p = None
          Ps = 0
          for i in range(0, lsts[0]['npts']):
            lst_json = []
            p = 0
            
            if i >= 30*sampling:
              datas1 = lst[0][i-(30*sampling):i]
              datas2 = lst[1][i-(30*sampling):i]
              datas3 = lst[2][i-(30*sampling):i]
              p = get_Parrival(datas1, datas2, datas3, sampling)
              if p != -1:
                    # print(p)
                    # print(i)
                    p += i - (30*sampling)
              else:
                    p = 0
                    
              if Ps == 0:
                    Ps = p
                    print(Ps)
                  #   time = starttime_base + timedelta(microseconds=((1000*Ps)/sampling)*1000)
                  #   str_p = "".join(("0" + str(time.minute))[-2:] + ":" + ("0" + str(time.second))[-2:])
            data_mtr = {
                  'latitude': None,
                  'longitude': None,
                  'depth': None,
                  'magnitude': None,
                  'time': None
            }
            
            if i >= 100:
                  for j in range(i-100, i):
                        json_ = {'E_data':lst[0][j],
                              'N_data':lst[1][j],
                              'Z_data':lst[2][j],
                              'p_Arrival': int(Ps),
                              'sampling_rate': sampling,
                              'time': lst_time[j],
                              'x':j,
                              'data_prediction':data_mtr}
                        lst_json.append(json_)
            else:
                  lstss = [None]*100
                  for j in range(100):
                        json_ = {'E_data':lstss[j],
                              'N_data':lstss[j],
                              'Z_data':lstss[j],
                              'p_Arrival': None,
                              'sampling_rate': sampling,
                              'time': lstss[j],
                              'x':lstss[j],
                              'data_prediction':data_mtr}
                        lst_json.append(json_)
            await self.send(json.dumps(lst_json))
            await sleep(s)
          await self.close()
        except KeyboardInterrupt:
          await self.close()
          print('close')
          
    async def disconnect(self, code):
      return super().disconnect(code)

class GetPWJIConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        try:
          await self.accept()
          name = self.scope['url_route']['kwargs']['name']
          lsts = get_PWJI_data_firebase(name)
          sampling = int(lsts[0]['sampling_rate'])
          s = 1/sampling
          e = UTCDateTime(lsts[0]['starttime'])
          n = UTCDateTime(lsts[1]['starttime'])
          z = UTCDateTime(lsts[2]['starttime'])
          
          lst, sensor_first = s_add_starttime(e, n, z, lsts)
          starttime = UTCDateTime(lsts[0]['starttime_station']).datetime
          lst_time = []
          for j in range(lsts[0]['npts']):
            str_ = "".join(("0" + str(starttime.minute))[-2:] + ":" + ("0" + str(starttime.second))[-2:])
            lst_time.append(str_)
            starttime += timedelta(microseconds=(1000/sampling)*1000)
          
          str_p = None
          Ps = 0
          for i in range(0, lsts[0]['npts']):
            lst_json = []
            p = 0
            
            if i >= 30*sampling:
              datas1 = lst[0][i-(30*sampling):i]
              datas2 = lst[1][i-(30*sampling):i]
              datas3 = lst[2][i-(30*sampling):i]
              p = get_Parrival(datas1, datas2, datas3, sampling)
              if p != -1:
                    # print(p)
                    # print(i)
                    p += i - (30*sampling)
              else:
                    p = 0
                    
              if Ps == 0:
                    Ps = p
                  #   time = starttime_base + timedelta(microseconds=((1000*Ps)/sampling)*1000)
                  #   str_p = "".join(("0" + str(time.minute))[-2:] + ":" + ("0" + str(time.second))[-2:])
            data_mtr = {
                  'latitude': None,
                  'longitude': None,
                  'depth': None,
                  'magnitude': None,
                  'time': None
            }
            
            if i >= 100:
                  for j in range(i-100, i):
                        json_ = {'E_data':lst[0][j],
                              'N_data':lst[1][j],
                              'Z_data':lst[2][j],
                              'p_Arrival': int(Ps),
                              'sampling_rate': sampling,
                              'time': lst_time[j],
                              'x':j,
                              'data_prediction':data_mtr}
                        lst_json.append(json_)
            else:
                  lstss = [None]*100
                  for j in range(100):
                        json_ = {'E_data':lstss[j],
                              'N_data':lstss[j],
                              'Z_data':lstss[j],
                              'p_Arrival': None,
                              'sampling_rate': sampling,
                              'time': lstss[j],
                              'x':lstss[j],
                              'data_prediction':data_mtr}
                        lst_json.append(json_)
            await self.send(json.dumps(lst_json))
            await sleep(s)
          await self.close()
        except KeyboardInterrupt:
          await self.close()
          print('close')
          
    async def disconnect(self, code):
      return super().disconnect(code)