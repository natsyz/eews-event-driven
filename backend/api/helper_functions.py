import numpy as np
from obspy.signal.trigger import recursive_sta_lta, trigger_onset
from obspy import UTCDateTime
from google.cloud import storage
import time

def normalizations(array):
    res = array/np.amax(np.abs(array))
    # res = array/100000
    return res

def array_to_str_limit_dec(array):
    lst = ""
    for i in array:
      if i == None:
            i = "None"
            lst += i + " "
      else:
            lst += '{:.10f}'.format(np.round_(i, 10)) + " "
    return lst

"""Choose the first P arrival"""
def get_Parrival(data1, data2, data3, sampling):
    E_p = search_Parrival(data1, sampling)
    N_p = search_Parrival(data2, sampling)
    Z_p = search_Parrival(data3, sampling)

    if len(E_p)== 0 and len(N_p) == 0 and len(Z_p) == 0:
        return -1
    
    else:
        lens = [E_p, N_p, Z_p]
        r = []
        for i in lens:
          if len(i) != 0:
            r.append(i[0])
        s = []
        for i in r:
            if len(i) != 0:
                s.append(i[0])
        return(min(s))
      
def search_Parrival(data, sampling):
  cft = recursive_sta_lta(data, int(2.5 * sampling), int(10. * sampling))
  on_of = trigger_onset(cft, 3.3, 0.5)
  return on_of

def split(strr):
    strr = list(filter(None, strr.split(" ")))
    lst = []
    for i in strr:
      if i == "None":
        j = None
        lst.append(j)
      else:
        lst.append(float(i))
    return lst

"""Function to add null so that the charts start at the same time"""
def s_add_starttime(e, n, z, data):
    l_enz = [('e', e.timestamp), ('n', n.timestamp), ('z', z.timestamp)]
    l_enz.sort(key=lambda a:a[1])
    sample = data[0]['sampling_rate']
    
    l_diff = []
    l_diff.append((l_enz[2][0], int(np.around((l_enz[2][1] - l_enz[0][1])*sample))))
    l_diff.append((l_enz[1][0], int(np.around((l_enz[1][1] - l_enz[0][1])*sample))))
    l_diff.append((l_enz[0][0], 0))
    
    l_diff.sort()
    
    data_e = split(data[0]['data_interpolated'])
    data_n = split(data[1]['data_interpolated'])
    data_z = split(data[2]['data_interpolated'])
    
    if l_diff[0][1] != 0:
      for i in range(l_diff[0][1]):
        data_e.insert(0, None)
        
    if l_diff[1][1] != 0:
      for i in range(l_diff[1][1]):
        data_n.insert(0, None)
        
    if l_diff[2][1] != 0:
      for i in range(l_diff[2][1]):
        data_z.insert(0, None)
    
    lst = [data_e, data_n, data_z]
    
    return lst, l_enz[0][0]
  
def add_null_station(gmji, jagi, pwji):
  gmji = sorted(gmji, key= lambda a:a.stats.starttime)
  jagi = sorted(jagi, key= lambda a:a.stats.starttime)
  pwji = sorted(pwji, key= lambda a:a.stats.starttime)
  
  l_gjp = [('gmji', UTCDateTime(gmji[0].stats.starttime).timestamp, gmji[0].stats.sampling_rate, gmji[0].stats.channel, gmji[0].stats.starttime, gmji[0].stats.npts), 
          ('jagi', UTCDateTime(jagi[0].stats.starttime).timestamp, jagi[0].stats.sampling_rate, jagi[0].stats.channel, jagi[0].stats.starttime, gmji[0].stats.npts), 
          ('pwji', UTCDateTime(pwji[0].stats.starttime).timestamp, pwji[0].stats.sampling_rate, pwji[0].stats.channel, pwji[0].stats.starttime, gmji[0].stats.npts)]
  l_gjp = sorted(l_gjp, key= lambda a:a[1])
  l_diff = []
  l_diff.append((l_gjp[2][0], int(np.around((l_gjp[2][1] - l_gjp[0][1]) * l_gjp[0][2])), l_gjp[2][3]))
  l_diff.append((l_gjp[1][0], int(np.around((l_gjp[1][1] - l_gjp[0][1]) * l_gjp[1][2])), l_gjp[1][3]))
  l_diff.append((l_gjp[0][0], 0, l_gjp[0][3]))
  data_first = l_gjp[0][4]
  # npts_first = l_gjp[0][5]
  l_diff.sort()

  return l_diff, data_first

def interpolate(lst, fi):
    i, f = int(fi // 1), fi % 1  # Split floating-point index into whole & fractional parts.
    j = i+1 if f > 0 else i  # Avoid index error.
    return (1-f) * lst[i] + f * lst[j]


def letInterpolate(inp, new_len):
  delta = (len(inp)-1) / (new_len-1)
  outp = [interpolate(inp, i*delta) for i in range(new_len)]
  return outp

def getime(func):
    def func_wrapper(*args, **kwargs):
        start_time = time.time()
        func(*args, **kwargs)
        print("function {} completed in - {} seconds".format(
            func.__name__,
            time.time()-start_time))
    return func_wrapper
  
def upload_blob(bucket_name, data_str, destination_blob_name):
    """Uploads a file to the bucket."""
    # The ID of your GCS bucket
    # bucket_name = "your-bucket-name"
    # The path to your file to upload
    # source_file_name = "local/path/to/file"
    # The ID of your GCS object
    # destination_blob_name = "storage-object-name"

    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_string(data_str, content_type='text/plain')

    print(
        f"File {data_str[:10]} uploaded to {destination_blob_name}."
    )
    
def upload(data, file_name):
      upload_blob('ta-eews_bucket-backend', data, file_name)
      
def denormalization(data):
  max,min = {},{}
  max['lat'] = -6.64264
  min['lat'] = -11.5152
  max['long'] = 115.033
  min['long'] = 111.532
  max['depth'] = 588.426
  min['depth'] = 1.16
  max['magnitude'] = 6.5
  min['magnitude'] = 3.0
  max['time'] = 74.122
  min['time'] = 4.502
  
  # Denorm
  dats = {}
  for col in data:
      dats[col] = data[col][0]*(max[col] - min[col])+min[col]
  return dats