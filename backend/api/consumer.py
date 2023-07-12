import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asyncio import sleep
from obspy import UTCDateTime
from datetime import timedelta

from .firebase_config import *
from .helper_functions import *
from .models import *
from .vertexai_config import *

class GetGMJIConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        try:
          await self.accept()
          
          name = self.scope['url_route']['kwargs']['name']
          
          # Test computational time
          file = ""
          start_time = time.time()
          
          file += 'name mseed = ' + name + '\n'
          
          lsts = get_GMJI_data_firebase(name) #data dari firebase yang sudah dipreprocessing
          sampling = int(lsts[0]['sampling_rate'])
          s = 1/sampling # second
          e = UTCDateTime(lsts[0]['starttime']) # bentuk data mseed, traces[0] = BHE, traces[1] = BHN, traces[2] = BHZ
          n = UTCDateTime(lsts[1]['starttime'])
          z = UTCDateTime(lsts[2]['starttime'])
          
          lst, sensor_first = s_add_starttime(e, n, z, lsts) #penyelarasan data persensor gelombang
          starttime = UTCDateTime(lsts[0]['starttime_station']).datetime # starttine station
          
          lst_len_data = [len(lst[0]), len(lst[0]), len(lst[0])] #SALAH BOIII
          # lst_len_data = [len(lst[0]), len(lst[1]), len(lst[2])]
          lst_len_data.sort()
          
          smallest = lst_len_data[0] # panjang data yang pertama mulai
          biggest = lst_len_data[2] # panjang data yang terakhir mulai

          lst_time = []
          for j in range(biggest):
            str_ = "".join(("0" + str(starttime.minute))[-2:] + ":" + ("0" + str(starttime.second))[-2:]) # ambil 2 digit menit dan dua digit detik
            lst_time.append(str_)
            starttime += timedelta(microseconds=(1000/sampling)*1000) # tambahin periode ke starttime
          str_p = None
          Ps = 0
          
          end_time = time.time()-start_time
          file += 'initial computation = ' + str(end_time) + '\n'
          print(end_time, ' gmji')
          #End of test
          
          preds = None
          data_mtr = {
                  'long': None,
                  'lat': None,
                  'magnitude': None,
                  'time': None,
                  'depth': None
            }
          
          for i in range(smallest):
            lst_json = []
            p = 0
            
            # Start Picking P Arrival
            if i >= 30*sampling:
                  datas1 = lst[0][i-(30*sampling):i]
                  datas2 = lst[1][i-(30*sampling):i]
                  datas3 = lst[2][i-(30*sampling):i]
                  
                  p = get_Parrival(datas1, datas2, datas3, sampling)
                  
                  if p != -1:
                        p += i - (30*sampling)
                  else:
                        p = 0
                        
                  # Send the first P to frontend
                  if Ps == 0:
                        Ps = p
                  else:
                        if i >= Ps + 5*sampling:
                              if preds == None:
                                    start_pred = time.time()
                                    interpolate_data1 = letInterpolate(lst[0][i-5*sampling:i+5*sampling], 1000)
                                    interpolate_data3 = letInterpolate(lst[2][i-5*sampling:i+5*sampling], 1000)
                                    interpolate_data2 = letInterpolate(lst[1][i-5*sampling:i+5*sampling], 1000)
                                    list_data = []
                                    for i in range(len(interpolate_data1)):
                                          list_data.append([interpolate_data1[i], interpolate_data2[i], interpolate_data3[i]])
                                    print(list_data)
                                          
                                    # preds = endpoint.predict(instances=[list_data]).predictions
                                    end_pred = time.time()-start_pred
                                    file += 'prediction time = ' + str(end_pred)
                                    
                                    data_mtr = denormalization(preds[0])
                                    print(preds)
            
            if i >= 100:
                  for j in range(i-100, i):
                        json_ = {'mseed_name':name,
                              'E_data':lst[0][j],
                              'N_data':lst[1][j],
                              'Z_data':lst[2][j],
                              'p_Arrival': int(Ps),
                              'sampling_rate': sampling,
                              'time': lst_time[j],
                              'x':j,
                              'data_prediction':data_mtr}
                        lst_json.append(json_)
            
            # Send Null Array to Frontend until 4 s (100 data points)
            else:
                  lstss = [None]*100
                  for j in range(100):
                        json_ = {'mseed_name':name,
                              'E_data':lstss[j],
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
          
          # Test computation time
          file = ""
          start_time = time.time()
          
          file += 'name mseed = ' + name+ '\n'
          
          lsts = get_JAGI_data_firebase(name)
          sampling = int(lsts[0]['sampling_rate'])
          s = 1/sampling
          e = UTCDateTime(lsts[0]['starttime'])
          n = UTCDateTime(lsts[1]['starttime'])
          z = UTCDateTime(lsts[2]['starttime'])
          
          lst, sensor_first = s_add_starttime(e, n, z, lsts)
          starttime = UTCDateTime(lsts[0]['starttime_station']).datetime
          
          lst_len_data = [len(lst[0]), len(lst[0]), len(lst[0])]
          lst_len_data.sort()
          
          smallest = lst_len_data[0]
          biggest = lst_len_data[2]

          lst_time = []
          for j in range(biggest):
            str_ = "".join(("0" + str(starttime.minute))[-2:] + ":" + ("0" + str(starttime.second))[-2:])
            lst_time.append(str_)
            starttime += timedelta(microseconds=(1000/sampling)*1000)
            
          str_p = None
          Ps = 0
          
          end_time = time.time()-start_time
          file += 'initial computation = ' + str(end_time)+ '\n'
          print(end_time, ' jagi')
          # End of test
          
          preds = None
          data_mtr = {
                  'long': None,
                  'lat': None,
                  'magnitude': None,
                  'time': None,
                  'depth': None
            }
          
          for i in range(smallest):
            lst_json = []
            p = 0
            
            # Start Picking P Arrival
            if i >= 30*sampling:
                  datas1 = lst[0][i-(30*sampling):i]
                  datas2 = lst[1][i-(30*sampling):i]
                  datas3 = lst[2][i-(30*sampling):i]
                  p = get_Parrival(datas1, datas2, datas3, sampling) # p_arrival (waktu dalam s?)
                  if p != -1:
                        p += i - (30*sampling)
                  else:
                        p = 0
                  
                  # Send the first P to frontend
                  if Ps == 0:
                        Ps = p
                  else:
                        if i >= Ps + 5*sampling:
                              if preds == None:
                                    start_pred = time.time()
                                    interpolate_data1 = letInterpolate(lst[0][i-5*sampling:i+5*sampling], 1000)
                                    interpolate_data3 = letInterpolate(lst[2][i-5*sampling:i+5*sampling], 1000)
                                    interpolate_data2 = letInterpolate(lst[1][i-5*sampling:i+5*sampling], 1000)
                                    list_data = []
                                    for i in range(len(interpolate_data1)):
                                          list_data.append([interpolate_data1[i], interpolate_data2[i], interpolate_data3[i]])
                                    print(list_data)
                                          
                                    # preds = endpoint.predict(instances=[list_data]).predictions
                                    end_pred = time.time()-start_pred
                                    file += 'prediction time = ' + str(end_pred)
                                    data_mtr = denormalization(preds[0])
                                    print(file)
            
            if i >= 100:
                  for j in range(i-100, i):
                        json_ = {'mseed_name':name,
                              'E_data':lst[0][j],
                              'N_data':lst[1][j],
                              'Z_data':lst[2][j],
                              'p_Arrival': int(Ps),
                              'sampling_rate': sampling,
                              'time': lst_time[j],
                              'x':j,
                              'data_prediction':data_mtr}
                        lst_json.append(json_)
                        
            # Send Null Array to Frontend until 4 s (100 data points)
            else:
                  lstss = [None]*100
                  for j in range(100):
                        json_ = {'mseed_name':name,
                              'E_data':lstss[j],
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
          
          # Testing computational time
          file = ""
          start_time = time.time()
          
          file += 'name mseed = ' + name+ '\n'
          
          lsts = get_PWJI_data_firebase(name)
          sampling = int(lsts[0]['sampling_rate'])
          s = 1/sampling
          e = UTCDateTime(lsts[0]['starttime'])
          n = UTCDateTime(lsts[1]['starttime'])
          z = UTCDateTime(lsts[2]['starttime'])
          
          lst, sensor_first = s_add_starttime(e, n, z, lsts)
          starttime = UTCDateTime(lsts[0]['starttime_station']).datetime
          
          lst_len_data = [len(lst[0]), len(lst[0]), len(lst[0])]
          lst_len_data.sort()
          
          smallest = lst_len_data[0]
          biggest = lst_len_data[2]
          
          lst_time = []
          for j in range(biggest):
            str_ = "".join(("0" + str(starttime.minute))[-2:] + ":" + ("0" + str(starttime.second))[-2:])
            lst_time.append(str_)
            starttime += timedelta(microseconds=(1000/sampling)*1000)
          
          str_p = None
          Ps = 0
          
          end_time = time.time()-start_time
          file += 'initial computation = ' + str(end_time)+ '\n'
          print(end_time, ' pwji')
          # End of test
          
          preds = None
          data_mtr = {
                  'long': None,
                  'lat': None,
                  'magnitude': None,
                  'time': None,
                  'depth': None
            }            
          
          for i in range(smallest):
            lst_json = []
            p = 0
            
            # Start Picking P Arrival
            if i >= 30*sampling:
                  datas1 = lst[0][i-(30*sampling):i]
                  datas2 = lst[1][i-(30*sampling):i]
                  datas3 = lst[2][i-(30*sampling):i]
                  p = get_Parrival(datas1, datas2, datas3, sampling)
                  if p != -1:
                        p += i - (30*sampling)
                  else:
                        p = 0
                        
                  if Ps == 0:
                        Ps = p
                  else:
                        if i >= Ps + 5*sampling:
                              if preds == None:
                                    start_pred = time.time()
                                    interpolate_data1 = letInterpolate(lst[0][i-5*sampling:i+5*sampling], 1000)
                                    interpolate_data3 = letInterpolate(lst[2][i-5*sampling:i+5*sampling], 1000)
                                    interpolate_data2 = letInterpolate(lst[1][i-5*sampling:i+5*sampling], 1000)
                                    list_data = []
                                    for i in range(len(interpolate_data1)):
                                          list_data.append([interpolate_data1[i], interpolate_data2[i], interpolate_data3[i]])
                                          
                                    print(list_data)
                                    # preds = endpoint.predict(instances=[list_data]).predictions
                                    end_pred = time.time()-start_pred
                                    file += 'prediction time = ' + str(end_pred)
                                    data_mtr = denormalization(preds[0])
            
            if i >= 100:
                  for j in range(i-100, i):
                        json_ = {'mseed_name':name,
                              'E_data':lst[0][j],
                              'N_data':lst[1][j],
                              'Z_data':lst[2][j],
                              'p_Arrival': int(Ps),
                              'sampling_rate': sampling,
                              'time': lst_time[j],
                              'x':j,
                              'data_prediction':data_mtr}
                        lst_json.append(json_)
                        
            # Send Null Array to Frontend until 4 s (100 data points)
            else:
                  lstss = [None]*100
                  for j in range(100):
                        json_ = {'mseed_name':name,
                              'E_data':lstss[j],
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






# Test Websocket

class Test(AsyncWebsocketConsumer):
    async def connect(self):
      await self.accept()
      for i in range(15):
            await self.send(json.dumps({
                  'data':'Test websocket ' + str(i)
            }))
            await sleep(1)
      await self.close()
        
    async def disconnect(self, code):
        return await super().disconnect(code)
  
class TestFirebase(AsyncWebsocketConsumer):
      async def connect(self):
          await self.accept()
          
          start_time = time.time()
          for i in range(50):
                lsts = get_JAGI_data_firebase('20090118_064750')
                await self.send(json.dump({
                      'data':lsts[0]['station']
                }))
          endtime = start_time-time.time()
          print(endtime)
          await self.close()
          
      async def disconnect(self, code):
          return await super().disconnect(code)
                