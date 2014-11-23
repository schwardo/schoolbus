from google.appengine.ext import ndb

class Student(ndb.Model):
  name = ndb.StringProperty()
  grade = ndb.StringProperty()
  guardians = ndb.KeyProperty(kind='Guardian', repeated=true)

class Guardian(ndb.Model):
  name = ndb.StringProperty()
  phone_number = ndb.StringProperty()
  
class Route(ndb.Model):
  name = ndb.StringProperty()
  stops = ndb.KeyProperty(kind='Stop', repeated=True)

class Stop(mdb.Model):
  index = ndb.IntProperty()
  name = ndb.StringProperty()
  address = ndb.StringProperty()
  coords = ndb.GeoPtProperty()
  route = ndb.KeyProperty(kind='Route')
  pickup_time = ndb.TimeProperty()
  dropoff_time = ndb.TimeProperty()

class StudentSchedule(ndb.Model):
  student = ndb.KeyProperty(kind='Student')
  date = ndb.DateTime()
  shift = ndb.StringProperty()  # 'pickup' or 'dropoff'
  stop = ndb.KeyProperty(kind='Stop')
  guardian = ndb.StringProperty()

class BusRun(ndb.Model):
  route = ndb.KeyProperty(kind='Route')
  shift = ndb.StringProperty()  # 'pickup' or 'dropoff'
  date = ndb.DateTime()
  chaperone = ndb.KeyProperty(kind='Student')
  
class RoutePosition(ndb.Model):
  bus_run = ndb.KeyProperty(kind='BusRun')
  when = ndb.DateTimeProperty()
  address = ndb.StringProperty()
  coords = ndb.GeoPtProperty()

class StudentPosition(ndb.Model):
  bus_run = ndb.KeyProperty(kind='BusRun')
  stop = ndb.KeyProperty(kind='Stop')
  student = ndb.KeyProperty(kind='Student')
  when = ndb.DateTimeProperty()
  on_bus = ndb.BooleanProperty()
