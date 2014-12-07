import os
import sys
import logging

from datetime import datetime
from datetime import date
from datetime import time
from datetime import timedelta
from collections import defaultdict

import jinja2
import webapp2

from dateutil import rrule

from models import *
from google.appengine.ext import ndb


JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'],
    autoescape=True)


class SummaryPage(webapp2.RequestHandler):
    def get(self):
        adult = Adult.get_by_id('msimpson')

        today = date.today()
        now = datetime.fromordinal(today.toordinal())
        if self.request.get('date'):
            now = datetime.strptime(self.request.get('date'), '%Y-%m-%d')

        weekdays = rrule.rrule(
            rrule.DAILY,
            byweekday=[rrule.MO, rrule.TU, rrule.WE, rrule.TH, rrule.FR],
            dtstart=now-timedelta(days=7)
        )
        current_date = weekdays.after(now, inc=True)
        next_date = weekdays.after(current_date)
        prev_date = weekdays.before(current_date)
        logging.info('Specified date: %s' % now)
        logging.info('Current date: %s' % current_date)
        logging.info('Next date: %s' % next_date)
        logging.info('Prev date: %s' % prev_date)
        
        query = StudentSchedule.query(
            StudentSchedule.student.IN(adult.students),
            StudentSchedule.date >= current_date,
            StudentSchedule.date < next_date)

        structure = defaultdict(lambda: defaultdict(list))
        for schedule in query:
            structure[schedule.shift][schedule.stop].append(schedule)

        def get_layout_by_schedules(by_schedules):
            layout_by_students = []
            for schedule in by_schedules:
                student = schedule.student.get()
                layout_by_students.append(student)
            return layout_by_students

        def get_layout_by_stops(by_stops):
            layout_by_stops = []
            for stop_key in by_stops.keys():
                stop = stop_key.get()
                route = stop.route.get()
                layout_by_stops.append((route, stop, get_layout_by_schedules(by_stops[stop_key])))
            return layout_by_stops

        layout = {}
        layout['pickup'] = get_layout_by_stops(structure['pickup'])
        layout['dropoff'] = get_layout_by_stops(structure['dropoff'])

        values = {
            'adult': adult,
            'date': current_date,
            'layout': layout,
            'today_url': '/',
            'is_today': not self.request.get('date'),
            'prev_url': '/?date=%s' % prev_date.strftime('%Y-%m-%d'),
            'next_url': '/?date=%s' % next_date.strftime('%Y-%m-%d'),
        }

        template = JINJA_ENVIRONMENT.get_template('summary.html')
        self.response.write(template.render(values))
        

class InitDatastore(webapp2.RequestHandler):
    def get(self):
        blue = ndb.Key('Route', 'blue')

        evergreen_terrace = Stop(
            index=2,
            name="Evergreen Terrace",
            address="740 Evergreen Terrace",
            route=blue,
            pickup_time=time(7, 40),
            dropoff_time=time(15, 15)).put()
        retirement_castle = Stop(
            index=3,
            name="Springfield Retirement Castle",
            address="2001 Creaking Oak Drive",
            route=blue,
            pickup_time=time(7, 30),
            dropoff_time=time(15, 25)).put()

        stop_keys = ndb.put_multi([
            Stop(index=0,
                 name="Springfield Elementary School",
                 address="19 Plymptom Street",
                 route=blue,
                 pickup_time=time(7, 40),
                 dropoff_time=time(15, 15)),
            Stop(index=1,
                 name="Pressboard Estates",
                 address="82 Evergreen Terrace",
                 route=blue,
                 pickup_time=time(7, 40),
                 dropoff_time=time(15, 15)),
            Stop(index=4,
                 name="Krustyland",
                 address="",
                 route=blue,
                 pickup_time=time(7, 40),
                 dropoff_time=time(15, 15))
        ]) + [evergreen_terrace, retirement_castle]

        Route(key=blue,
              name='Blue Bus',
              stops=stop_keys).put()

        msimpson = ndb.Key('Adult', 'msimpson')
        hsimpson = ndb.Key('Adult', 'hsimpson')
        gsimpson = ndb.Key('Adult', 'gsimpson')
        cwiggum = ndb.Key('Adult', 'cwiggum')
        swiggum = ndb.Key('Adult', 'swiggum')

        bart = Student(name='Bart Simpson',
                       grade='4',
                       main_contact=hsimpson).put()
        lisa = Student(name='Lisa Simpson',
                       grade='3',
                       main_contact=hsimpson).put()
        maggie = Student(name='Maggie Simpson',
                         grade='PS',
                         main_contact=msimpson).put()
        ralph = Student(name='Ralph Wiggum',
                        grade='3',
                        main_contact=swiggum).put()

        Adult(key=msimpson,
              name='Marge Simpson',
              phone_number='555-555-1234',
              students=[bart, lisa, maggie]).put()
        Adult(key=hsimpson,
              name='Homer Simpson',
              phone_number='555-555-7334',
              students=[bart, lisa, maggie]).put()
        Adult(key=gsimpson,
              name='Grandpa Simpson',
              phone_number='555-555-2345',
              students=[bart, lisa]).put()
        Adult(key=cwiggum,
              name='Clancy Wiggum',
              phone_number='555-555-5555',
              students=[ralph]).put()
        Adult(key=swiggum,
              name='Sarah Wiggum',
              phone_number='555-555-5555',
              students=[ralph]).put()

        StudentSchedule(student=bart,
                        date=date(2014, 12, 1),
                        shift='pickup',
                        stop=evergreen_terrace).put()
        StudentSchedule(student=bart,
                        date=date(2014, 12, 1),
                        shift='dropoff',
                        stop=evergreen_terrace).put()
        StudentSchedule(student=lisa,
                        date=date(2014, 12, 1),
                        shift='pickup',
                        stop=evergreen_terrace).put()
        StudentSchedule(student=lisa,
                        date=date(2014, 12, 1),
                        shift='dropoff',
                        stop=retirement_castle).put()  # Lisa visits Grandpa on 2014-12-01
        StudentSchedule(student=maggie,
                        date=date(2014, 12, 1),
                        shift='pickup',
                        stop=evergreen_terrace).put()
        StudentSchedule(student=ralph,
                        date=date(2014, 12, 1),
                        shift='pickup',
                        stop=evergreen_terrace).put()
        StudentSchedule(student=ralph,
                        date=date(2014, 12, 1),
                        shift='dropoff',
                        stop=evergreen_terrace).put()
        # Maggie only goes half day, so no dropoff.
        # Bart has a morning elective on 2014-12-02.
        StudentSchedule(student=bart,
                        date=date(2014, 12, 2),
                        shift='dropoff',
                        stop=evergreen_terrace).put()
        StudentSchedule(student=lisa,
                        date=date(2014, 12, 2),
                        shift='pickup',
                        stop=evergreen_terrace).put()
        # Lisa has a playdate with Sherri and/or Terri on 2014-12-02.
        StudentSchedule(student=maggie,
                        date=date(2014, 12, 2),
                        shift='pickup',
                        stop=evergreen_terrace).put()
        # Ralph only goes to school on Mon,Wed,Fri

        self.response.out.write("Done.")


application = webapp2.WSGIApplication(
    [('/', SummaryPage),
     ('/admin/init', InitDatastore),
    ],
    debug=True)
