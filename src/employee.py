class employee(object):

    def __init__(self,employee_id,slots,overtime):

        self.id = employee_id
        # self.gender = gender
        # self.type = emp_typ
        # self.age = age
        # self.skills = skills
        # self.pref_slot = pref
        # self.hour_salary = salary
        # self.ot_cost = ot_cost
        self.conv_rate = 0.5
        self.slots = slots
        self.overtime = overtime
        self.domain = None
        self.domain_hours = None

    def generate_cell_domain(self,shift_length):
        shift = self.slots
        shift.sort()
        overtime = range(self.overtime+1)
        self.domain = [0]
        self.domain_hours = {0:0}
        for s in shift[1:]:
            for o in overtime:
                self.domain.append(10*s + o)
                self.domain_hours[10*s + o] = shift_length + o
        return None

    def get_cell_domain(self):
        print (self.id,"domain: ",self.domain)
        print (self.id,"domain_hours: ",self.domain_hours)
        return None

    def __repr__(self):
        return str(self.id)
