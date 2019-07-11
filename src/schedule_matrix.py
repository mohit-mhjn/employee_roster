import itertools
import copy
import random

class schedule_matrix(object):

    class matrix_cell(object):

        def __init__(self,address1,address2,value,search_space,actual_domain):
            self.address = str(address2) + '_' + str(address1)
            self.emp = address1
            self.day = address2
            self.value = value
            self.search_space = []
            self.actual_domain = actual_domain
            self.p_domain = [[]]
            self.trials = []
            self.visited = None
            self.prev = None
            self.next = None

        def reset_trials(self):
            self.trials = []
            return None

        def __repr__(self):
            return self.address

    def __init__(self,idn,emp_list,day_list,emp_master,day_master,shift_length,max_overtime,max_work_hour,day_shifts,shift_hour_mapping):  #(x-axis,y-axis)

        self.solution_id = idn
        self.emp_list = emp_list
        self.day_list = day_list
        self.emp_master = emp_master
        self.day_master = day_master
        self.matrix = {x:{y: self.matrix_cell(x,y,0,[],self.emp_master[x].domain) for y in day_list} for x in emp_list}
        self.shift_length = shift_length
        self.max_overtime = max_overtime
        self.max_work_hour = max_work_hour
        self.day_shifts = day_shifts
        self.hour_range = range(24)
        self.shift_hour_mapping = shift_hour_mapping
        self.atv = 8

    @property
    def a_b_iterator(self):
        yield itertools.product(self.emp_list,self.day_list)

    @property
    def value_matrix(self):
        return [[self.matrix[k1][k2].value for k2 in self.day_list] for k1 in self.emp_list]

    @value_matrix.setter
    def value_matrix(self,value_mat):
        self.matrix[value_mat[0]][value_mat[1]].value = value_mat[2]

    @property
    def work_hr_matrix(self):
        return [[self.emp_master[k1].domain_hours[self.matrix[k1][k2].value] for k2 in self.day_list] for k1 in self.emp_list]

    @property
    def overtime_matrix(self):
        return [[max(self.emp_master[k1].domain_hours[self.matrix[k1][k2].value]-self.shift_length,0) for k2 in self.day_list] for k1 in self.emp_list]

    @property
    def total_overtime_monitor(self):
        return {k1:sum(self.overtime_matrix[self.emp_list.index(k1)]) for k1 in self.emp_list}

    @property
    def total_work_hr_monitor(self):
        return {k1:sum(self.work_hr_matrix[self.emp_list.index(k1)]) for k1 in self.emp_list}

    @property
    def unassigned_slots(self):
        return {d: set(self.day_shifts)-set([self.matrix[e][d].value//10 for e in self.emp_list]) for d in self.day_list}

    @property
    def day_shift_assignment(self):
        return {d:{s:[e for e in self.emp_list if self.matrix[e][d].value//10 == s] for s in self.day_shifts} for d in self.day_list}

    @property
    def emp_hour_assignment(self):

        def gen_slots_assigned(obj,e,d):
            f_div = obj.matrix[e][d].value//10
            if f_div == 0:
                return []
            A = obj.shift_hour_mapping[f_div]
            rem = obj.matrix[e][d].value%10
            if A[-1] + rem <= obj.shift_hour_mapping[obj.day_shifts[-1]][-1]:
                A = A + list(range(A[-1]+1,A[-1]+1+rem))
            else:
                A = list(range(A[0]-rem,A[0])) + A
            return A

        return {d:{e:gen_slots_assigned(self,e,d) for e in self.emp_list} for d in self.day_list}

    @property
    def day_hour_assignment(self):
        return {d:{h:[e for e in self.emp_list if h in self.emp_hour_assignment[d][e]] for h in self.hour_range} for d in self.day_list}

    @property
    def footfall_converted(self):

        def get_avg_conv_rate(obj,d,h):
            assigned_emp = obj.day_hour_assignment[d][h]
            if len(assigned_emp) == 0:
                return 0
            else:
                avg = sum(obj.emp_master[e].conv_rate for e in assigned_emp)/len(assigned_emp)
                return avg

        return {d:{h:round(self.day_master[d].expected_footfall[h]*get_avg_conv_rate(self,d,h)) for h in self.hour_range} for d in self.day_list}

    @property
    def revenue_generated(self):
        return {d: self.atv*sum(self.footfall_converted[d][h] for h in self.hour_range) for d in self.day_list}

    def get_value(self,a,b):
        return self.matrix[a][b].value

    def update_value(self,a,b,val):
        self.matrix[a][b].value = val
        return None

    def initialize_search(self):
        for ab in next(self.a_b_iterator):
            self.matrix[ab[0]][ab[1]].search_space = copy.deepcopy(self.matrix[ab[0]][ab[1]].actual_domain)
        return None

    def prune_space(self,a,b,rm_lst):
        rmvs = []
        for rm in rm_lst:
            try:
                self.matrix[a][b].search_space.remove(rm)
                rmvs.append(rm)
            except ValueError:
                pass
        self.matrix[a][b].p_domain.append(rmvs)
        return None

    def apply_leave(self,l):
        emp = l[0]
        day = l[1]
        self.matrix[emp][day].actual_domain = [0]   # No Assignment to shift
        return None

    def apply_unavailability(self,u):
        rm_dom = []
        emp = u[0]
        day = u[1]
        shift = u[2]
        rm_dom.append(10*shift)
        overtime = range(1,self.emp_master[emp].overtime + 1)
        available_shifts = self.emp_master[emp].slots
        for o in overtime:
            rm_dom.append(10*shift + o)
        shift = shift - 1
        if shift in available_shifts:
            for o in overtime:
                rm_dom.append(10*shift + o)
        for r in rm_dom:
            try:
                self.matrix[emp][day].actual_domain.remove(r)
            except ValueError:
                pass
        return None

    def initialize_solution(self):
        for ab in next(self.a_b_iterator):
            new_value = random.choice(self.matrix[ab[0]][ab[1]].search_space)
            self.matrix[ab[0]][ab[1]].value = new_value
        return None

    def __repr__(self):
        return str(self.solution_id)
