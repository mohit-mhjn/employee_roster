import random
import itertools

def map_removable_space(slots,overtime,remove):   # Updater type
    for s in slots[1:]:
        for o in overtime:
            remove.append(10*s + o)

def prune_constraint1(matrix_cls,remaining_days,emp):    # Overtime Limit in Horizon   # Updater type
    allowed = matrix_cls.max_overtime - matrix_cls.total_overtime_monitor[emp]
    emp_ot = matrix_cls.emp_master[emp].overtime
    remove = []
    if allowed >= emp_ot:
        pass
    else:
        slots = matrix_cls.emp_master[emp].slots
        overtime = range(allowed+1,emp_ot+1)
        map_removable_space(slots,overtime,remove)
    for d in remaining_days:
        matrix_cls.prune_space(emp,d,remove)

def rev_prune1(matrix_cls,remaining_days,emp):
    for day in remaining_days:
        r = matrix_cls.matrix[emp][day].p_domain.pop()
        matrix_cls.matrix[emp][day].search_space += r

def prune_constraint2(matrix_cls,remaining_days,emp):    # Total limit on working hours in the time horizon     # Updater type
    allowed = matrix_cls.max_work_hour - matrix_cls.total_work_hr_monitor[emp]
    if allowed >= matrix_cls.emp_master[emp].overtime + matrix_cls.shift_length:
        remove = []
    else:
        remove = [k for k,v in matrix_cls.emp_master[emp].domain_hours.items() if v > allowed]
    for d in remaining_days:
        matrix_cls.prune_space(emp,d,remove)

def rev_prune2(matrix_cls,remaining_days,emp):
    for day in remaining_days:
        r = matrix_cls.matrix[emp][day].p_domain.pop()
        matrix_cls.matrix[emp][day].search_space += r

def prune_constraint3(matrix_cls,remaining_emp,day):    # Requirement of Employees        # Updater type
    # Assumption : Enough Employees are available, ie. Number of shifts <= number of employees, if not report infeasible
    remaining_slots = matrix_cls.unassigned_slots[day]
    if len(remaining_emp) > len(remaining_slots):
        for emp in remaining_emp:
            remove = []
            matrix_cls.prune_space(emp,day,remove)
    else:
        for emp in remaining_emp:
            remove = [0]
            all_slots = set(matrix_cls.emp_master[emp].slots)  # Employee Specific
            rm_slot = list(all_slots - remaining_slots)
            rm_slot.sort()
            overtime = range(matrix_cls.emp_master[emp].overtime+1)
            map_removable_space(rm_slot,overtime,remove)
            matrix_cls.prune_space(emp,day,remove)

def rev_prune3(matrix_cls,remaining_emp,day):
    for emp in remaining_emp:
        r = matrix_cls.matrix[emp][day].p_domain.pop()
        matrix_cls.matrix[emp][day].search_space += r

def assign_value(matrix_cls,emp,day,remaining_emp,remaining_days,position):        # Updater type
    # print (emp,day,remaining_emp,remaining_days,position)
    cell = matrix_cls.matrix[emp][day]
    remaining_domain = set(cell.search_space) - set(cell.trials)
    if bool(remaining_domain):
        cell.value = random.sample(remaining_domain,1)[0]
        prune_constraint1(matrix_cls,remaining_days,emp)
        prune_constraint2(matrix_cls,remaining_days,emp)
        prune_constraint3(matrix_cls,remaining_emp,day)
        cell.trials.append(cell.value)
        cell.visited = True
        if position == 0:
            pass
        else:
            next_cell = cell.next
            position -= 1
            if next_cell.day == day:
                pass
            else:
                remaining_days.remove(next_cell.day)
                remaining_emp = list(matrix_cls.emp_list)
            remaining_emp.remove(next_cell.emp) #Because Inner iteration is on employee
            assign_value(matrix_cls,next_cell.emp,next_cell.day,remaining_emp,remaining_days,position)
    else:
        prev_cell = cell.prev
        prev_cell.visited = False
        cell.reset_trials()
        position += 1
        if prev_cell.day == day:
            remaining_emp = [emp] + remaining_emp
        else:
            remaining_days = [day] + remaining_days
            remaining_emp = []
            #Avioding duplicate formation in remaining_emp list while maintaining order (prev last employee will not have any remaining on same day)
        rev_prune3(matrix_cls,remaining_emp,prev_cell.day)
        rev_prune2(matrix_cls,remaining_days,prev_cell.emp)
        rev_prune1(matrix_cls,remaining_days,prev_cell.emp)
        assign_value(matrix_cls,prev_cell.emp,prev_cell.day,remaining_emp,remaining_days,position)

def gen_iterator(array):
    arr = []
    for idx,a in enumerate(array[:-1]):
        arr.append((idx,a,idx+1,array[idx+1:]))
    arr.append((len(array)-1,array[-1],0,[]))
    return arr

def solve(matrix_cls):
    arr1 = list(matrix_cls.day_list) #Avoiding Copy
    random.shuffle(arr1)
    arr2 = list(matrix_cls.emp_list) #Avoiding Copy
    random.shuffle(arr2)
    for d in gen_iterator(arr1):
        for e in gen_iterator(arr2):
            if e[3]:
                indx = d[1]
            else:
                indx = arr1[d[2]]
            matrix_cls.matrix[e[1]][d[1]].next = matrix_cls.matrix[arr2[e[2]]][indx]
            matrix_cls.matrix[arr2[e[2]]][indx].prev = matrix_cls.matrix[e[1]][d[1]]
            assign_value(matrix_cls,e[1],d[1],e[3],d[3],0)
