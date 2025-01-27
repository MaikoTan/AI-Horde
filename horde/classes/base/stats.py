
from datetime import datetime, timedelta

from horde.logger import logger
from horde.flask import db
from horde.vars import thing_divisor
from horde.argparser import args

class ModelPerformance(db.Model):
    __tablename__ = "model_performances"
    id = db.Column(db.Integer, primary_key=True)
    model = db.Column(db.String(30), index=True)
    performance = db.Column(db.Float)
    created = db.Column(db.DateTime(timezone=False), default=datetime.utcnow)  # Maybe index this, but I'm not actually sure how big this table is

class FulfillmentPerformance(db.Model):
    __tablename__ = "horde_fulfillments"
    id = db.Column(db.Integer, primary_key=True)
    deliver_time = db.Column(db.DateTime(timezone=False), default=datetime.utcnow)
    things = db.Column(db.Float)
    created = db.Column(db.DateTime, default=datetime.utcnow)


def record_fulfilment(procgen):
    things = procgen.wp.things
    starting_time = procgen.start_time
    model = procgen.model
    seconds_taken = (datetime.utcnow() - starting_time).seconds
    if seconds_taken == 0:
        things_per_sec = 1
    else:
        things_per_sec = round(things / seconds_taken,1)
    new_performance = ModelPerformance(model=model,performance=things_per_sec)
    new_fulfillment = FulfillmentPerformance(things=things)
    db.session.add(new_performance)
    db.session.add(new_fulfillment)
    db.session.commit()
    return(things_per_sec)

def get_things_per_min():
    total_things = 0
    last_minute_fulfillments = db.session.query(
        FulfillmentPerformance
    ).filter(
       FulfillmentPerformance.created >= datetime.utcnow() - timedelta(seconds=60)
    ).all()
    for fulfillment in last_minute_fulfillments:
        total_things += fulfillment.things
    things_per_min = round(total_things / thing_divisor,2)
    return(things_per_min)

def get_model_avg(model):
    return 1000000 #TODO
    # TODO: Add the sum / coun calculation as part of the query
    model_performances = db.session.query(ModelPerformance).filter_by(
        model=model_name
    ).order_by(
        ModelPerformance.created.desc()
    ).limit(10)
    if model_performances.count() == 0:
        return 0
    avg = sum([m.performance for m in model_performances]) / model_performances.count()
    return(round(avg,1))