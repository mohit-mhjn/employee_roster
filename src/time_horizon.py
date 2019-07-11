import datetime

class day_slot(object):

    class hour_slot(object):

        def __init__(self,idx,timestamp):
            self.index = idx
            self.timestamp = timestamp
            self.footfall_prob = 4.15

        def set_p_footfall(self,p):
            self.footfall_prob = p
            return None

        def __repr__(self):
            return str(self.timestamp)

    def __init__(self,indx,date,total_footfall,sales_target):

        self.index = indx
        self.date = date
        self.f_fcst = total_footfall
        self.sales_target =  sales_target
        # self.day_shifts = [1,2,3]
        self.hour_list = list(range(24))
        self.starting = datetime.datetime.combine(self.date, datetime.time(hour = 00))
        self.hours = {i:self.hour_slot(i,self.starting+datetime.timedelta(hours = i)) for i in range(24)}

    @property
    def expected_footfall(self):
        return {t:self.f_fcst*self.hours[t].footfall_prob for t in self.hour_list}

    def __repr__(self):
        return str(self.date)
