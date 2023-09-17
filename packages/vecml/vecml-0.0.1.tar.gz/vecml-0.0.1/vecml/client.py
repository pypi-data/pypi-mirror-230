import warnings
warnings.filterwarnings("ignore")

import grpc
import vdb_pb2
import vdb_pb2_grpc
import numpy as np
from tqdm import tqdm
import time

class vecml:
  channel = 0
  stub = 0
  host = ''
  port = 0
  MAX_MESSAGE_LENGTH = 1024 * 1024 * 1024
  step = 25
  api_key = 'empty';

  def init(api_key, region):
    if region == 'us-east':
      vecml.host = '18.217.188.7'
    elif region == 'us-west':
      vecml.host = '184.72.3.214'
    else:
      print('Unsupported region [{}]. Current choices are [us-west, us-east].'.format(region))
      return;
    vecml.api_key = api_key;
    channel = grpc.insecure_channel(vecml.host + ':80',
      options=[
        ('grpc.max_send_message_length', vecml.MAX_MESSAGE_LENGTH),
        ('grpc.max_receive_message_length', vecml.MAX_MESSAGE_LENGTH),
      ], compression=grpc.Compression.Gzip)
    stub = vdb_pb2_grpc.VectorDBStub(channel)
    response = stub.request_port(vdb_pb2.Request(api_key=api_key))
    vecml.port = response.dest_port
    time.sleep(0.500);
    vecml.channel = grpc.insecure_channel(vecml.host + ':' + str(vecml.port),
      options=[
        ('grpc.max_send_message_length', vecml.MAX_MESSAGE_LENGTH),
        ('grpc.max_receive_message_length', vecml.MAX_MESSAGE_LENGTH),
      ], compression=grpc.Compression.Gzip)
    vecml.stub = vdb_pb2_grpc.VectorDBStub(vecml.channel)

  def close():
    vecml.channel.close()
    vecml.channel = 0
    vecml.stub = 0

  def check_init():
    if vecml.stub == 0:
      raise Exception("Shoreline is not initialized. Please run vecml.init.")

  def insert(namedim, data, ids, label=[]):
    vecml.check_init()
    name, dim = namedim
    data = np.array(data)
    n_data = len(ids)
    
    if label is []:
      use_label = False
    else:
      use_label = True

    step = max(1, n_data // vecml.step)
    pbar = tqdm(total=n_data)

    for i in range(0, n_data, step):
      begin = i
      end = min(i + step, n_data)
      if use_label == True:
        response = vecml.stub.insert(vdb_pb2.Request(table_name=name,vectors=vdb_pb2.Vectors(len=end - begin, dim=dim, data=data[begin:end,:].flatten().tolist(), ids=ids[begin:end], label=label[begin:end])))
      else:
        response = vecml.stub.insert(vdb_pb2.Request(table_name=name,vectors=vdb_pb2.Vectors(len=end - begin, dim=dim, data=data[begin:end,:].flatten().tolist(), ids=ids[begin:end])))

      if response.code != 0:
        print("[Warning]: Insertion failed. Error code:", response.code)
        return
      pbar.update(step)
    pbar.close()
  
  def insert_sparse(namedim, data, ids):
    vecml.check_init()
    name, dim = namedim
    n_data = len(ids)
    
    step = max(1,n_data // vecml.step)
    pbar = tqdm(total=n_data)
    
    for i in range(0, n_data, step):
      begin = i
      end = min(i + step, n_data)
      subdata = data[begin:end,:]
      response = vecml.stub.insert_sparse(vdb_pb2.Request(table_name=name,vectors=vdb_pb2.Vectors(len=end - begin, dim=dim, data=subdata.data.tolist(), offset=subdata.indptr.tolist(), idx=subdata.indices.tolist(), ids=ids[begin:end])))
      if response.code != 0:
        print("[Warning]: Insertion failed. Error code:", response.code)
        return
      pbar.update(step)
    pbar.close()

  def query(namedim, data, budget, topk):
    vecml.check_init()
    name, dim = namedim
    data = np.array(data)
    if len(data.shape) == 1:
      data = data.reshape([1, -1])
    n_data = len(data.flatten()) // dim
    
    step = max(1,n_data // vecml.step)
    pbar = tqdm(total=n_data)
    ids = []
    dis = []
    for i in range(0, n_data, step):
      begin = i
      end = min(i + step, n_data)
      response = vecml.stub.query(vdb_pb2.Request(table_name=name,query_info=vdb_pb2.QueryInfo(topk=topk, budget=budget),vectors=vdb_pb2.Vectors(len=end - begin, dim=dim, data=data[begin:end,:].flatten().tolist())))
      ids.append(response.ids)
      dis.append(response.dis)
      pbar.update(step)
    pbar.close()
    return np.concatenate(ids).reshape([-1,topk]), np.concatenate(dis).reshape([-1,topk])
  
  def query_sparse(namedim, data, budget, topk):
    vecml.check_init()
    name, dim = namedim
    if len(data.shape) == 1:
      data = data.reshape([1, -1])
    n_data = data.shape[0]
    
    step = max(100,max(1, n_data // vecml.step))
    pbar = tqdm(total=n_data)
    ids = []
    dis = []
    for i in range(0, n_data, step):
      begin = i
      end = min(i + step, n_data)
      subdata = data[begin:end,:]
      response = vecml.stub.query_sparse(vdb_pb2.Request(table_name=name,query_info=vdb_pb2.QueryInfo(topk=topk, budget=budget),vectors=vdb_pb2.Vectors(len=end - begin, dim=dim, data=subdata.data.tolist(), offset=subdata.indptr.tolist(),idx=subdata.indices.tolist())))
      ids.append(response.ids)
      dis.append(response.dis)
      pbar.update(step)
    pbar.close()
    return np.concatenate(ids).reshape([-1,topk]), np.concatenate(dis).reshape([-1,topk])

  def index(name, dim, measure, **kwargs):
    vecml.check_init()
    index_type = 0
    if 'sparse' in kwargs:
      use_sparse = int(kwargs['sparse'])
      if use_sparse == 1:
        index_type = 1
    if 'gpu' in kwargs:
      use_gpu = int(kwargs['gpu'])
      if use_gpu == 1:
        index_type = 2
    bits = 0
    oporp_repeat = -1
    if 'rp' in kwargs:
      bits = int(kwargs['rp'])
      index_type = 3
      if 'oporp_repeat' in kwargs:
        oporp_repeat = int(kwargs['oporp_repeat'])
    try:
      response = vecml.stub.index(vdb_pb2.Request(table_name=name,similarity=measure,vectors=vdb_pb2.Vectors(dim=dim),index_type=index_type,hash_bits=bits,oporp_repeat=oporp_repeat))
    except:
      pass
    return name, dim
  
  def train(namedim, num_class, valid_data=[], valid_label=[]):
    vecml.check_init()
    name, dim = namedim
    if valid_data is [] or valid_label is []:
      response = vecml.stub.train(vdb_pb2.Request(table_name=name,vectors=vdb_pb2.Vectors(dim=dim),num_class=num_class))
    else:
      valid_data = np.array(valid_data)
      valid_label = np.array(valid_label)
      for res_str in vecml.stub.train(vdb_pb2.Request(table_name=name,vectors=vdb_pb2.Vectors(len=valid_data.shape[0], dim=dim, data=valid_data.flatten().tolist(), label=valid_label.flatten().tolist()),num_class=num_class)):
        print(res_str.str, end='')

    return name, dim
  
  def predict(namedim, test_data):
    vecml.check_init()
    name, dim = namedim
    test_data = np.array(test_data)
    response = vecml.stub.predict(vdb_pb2.Request(table_name=name,vectors=vdb_pb2.Vectors(len=test_data.shape[0], dim=dim, data=test_data.flatten().tolist())))
    return np.array(response.label)
