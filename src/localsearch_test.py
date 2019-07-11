from employee import *
from schedule_matrix import *
from time_horizon import *
import feasibility_heuristic

# MASTER DATA SAMPLE
master1 = {
           "E1":{'shift':[0,1,2,3],'overtime':1},
           "E2":{'shift':[0,1,2,3],'overtime':2},
           "E3":{'shift':[0,1,2,3],'overtime':3},
           "E4":{'shift':[0,1,2,3],'overtime':3},
           "E5":{'shift':[0,1,2,3],'overtime':3}
           }

master2 = {
0:{'footfall':100,'sales_target':1000},
1:{'footfall':100,'sales_target':1000},
2:{'footfall':100,'sales_target':1000},
3:{'footfall':100,'sales_target':1000},
4:{'footfall':100,'sales_target':1000},
5:{'footfall':100,'sales_target':1000},
6:{'footfall':100,'sales_target':1000}
}

shift_length = 8

approved_leaves = [("E2",0),("E1",3)]
marked_unavailable = [("E3",2,3),("E2",1,1)]  # TUPLE: (employee, day, shift)
day_shifts = [1,2,3]
max_overtime = 5
max_work_hour = 40
shift_hour_mapping = { 1:[8,9,10,11,12,13,14,15], 2:[12,13,14,15,16,17,18,19], 3:[15,16,17,18,19,20,21,22]}

# Preprocessing

employee_list = list(master1.keys())
employee_list.sort()
emp_master = {}

for e in employee_list:
    cls = employee(e,master1[e]['shift'],master1[e]['overtime'])
    cls.generate_cell_domain(shift_length)
    emp_master[e] = cls

todayDate = datetime.date.today()
next_month = todayDate.replace(day = 28) + datetime.timedelta(days = 4)
next_month = next_month.replace(day = 1)
days = list(master2.keys())
days.sort()
day_master = {}

for d in days:
    cls = day_slot(d,next_month + datetime.timedelta(days = d),master2[d]['footfall'],master2[d]['sales_target'])
    day_master[d] = cls

mat1 = schedule_matrix('x1',employee_list,list(days),emp_master,day_master,shift_length,max_overtime,max_work_hour,day_shifts,shift_hour_mapping)

# #Initial Cleaning
for l in approved_leaves:
    mat1.apply_leave(l)    # (employee, day)
#
for u in marked_unavailable:
    mat1.apply_unavailability(u)  # (employee,day,slot)

# # Initialize Domain
mat1.initialize_search()

# # Random Assignement
mat1.initialize_solution()

# # CP Heuristic for Feasibility
#feasibility_heuristic.solve(mat1)

# print (mat1.value_matrix)
# print (mat1.total_overtime_monitor)
# print (mat1.total_work_hr_monitor)
# print (mat1.unassigned_slots)
print (mat1.day_hour_assignment)
print (mat1.footfall_converted)

# Improvement and Neighbourhood

# Solution
