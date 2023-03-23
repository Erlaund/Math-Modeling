import random as rnd
import math
import matplotlib.pyplot as plt
from os import system

kappa = float(input('\nВведите произодительность источника: '))
time_model = float(input('Введите время моделирования: '))
len_queue = int(input('Введите длину очереди: '))
time_event_last = 0
num_channel = int(input('Введите количество каналов: '))

time_serv_sum = 0
time_pr = 0
time_in_queue = 0
pos_queue = 0

time_event = []
time_serv = []
time_last_end = []
ones_end = []
ones_event = []
lambdaRandomValues = []

class TEvent:
	def __init__(self, _id, _label, _thread_id, _time_started):
		self.id = _id
		self.label = _label
		self.thread_id = _thread_id
		self.time_started = _time_started

class TAvarege:
	def __init__(self):
		self.sum = 0
		self.count = 0
	def append(self, value):
		self.sum += value
		self.count += 1
	def get(self):
		if self.count == 0:
			return 0
		return self.sum/self.count

class Statistics:
	def __init__(self, num_channel):
		self.n_rej = 0
		self.n_serv = 0
		self.time_eq = []
		for i in range(num_channel):
			self.time_eq.append(0)
		self.avr_n_len = TAvarege()
		self.time_running = 0
		self.avr_time_task = TAvarege()
		self.avr_eq_in_system = TAvarege()
		self.avr_len_task = 0
		self.avr_time_in_serv = TAvarege()
		self.avr_time_eq_in_system = 0

	def print(self):
		print('\n 1) Вероятность обслуживания = ' + str(round((self.n_serv/(self.n_serv + self.n_rej))*100, 2)) + ' [%]')
		print(' 2) Вероятность отказа = ' + str(round((self.n_rej/(self.n_serv + self.n_rej))*100, 2)) + ' [%]')
		print(' 3) Пропускная способность = ' + str(round(self.n_serv/time_model, 2)) + ' [шт/ед.вр]')
		print(' 4) Среднее количество занятых каналов = ' + str(round(self.avr_len_task / time_model, 2)) + ' [шт]')
		print(' 5) Вероятность простоя всей системы = ' + str(round(((time_model-self.time_running)/time_model)*100, 2)) + ' [%]')
		print(' 6) Среднее количество заявок в очереди = ' + str(round(n_avr_q/(self.n_serv), 2)) + ' [шт]')
		print(' 7) Среднее время ожидания заявки в очереди = ' + str(round(self.avr_time_task.get(), 2)) + ' [ед.вр]')
		print(' 8) Среднее время обслуживания заявки = ' + str(round(self.avr_time_in_serv.get(), 2)) + ' [ед.вр]')
		print(' 9) Среднее время нахождения заявки в системе = ' + str(round(self.avr_time_task.get() + self.avr_time_in_serv.get(), 2)) + ' [ед.вр]')
		print(' 10) Среднее количество заявок в системе = ' + str(round(self.avr_time_eq_in_system/time_model, 2)) + ' [шт]')

class TThread:
	def __init__(self, _label_thread, _power):
		self.label_thread = _label_thread
		self.power = _power

def push_event(id,label,thread_id, time_started):
	global time_event
	t = TEvent(id,label,thread_id, time_started)
	for i in range(0,len(time_event)):
		if time_event[i].label > label:
			v = time_event[:i]
			v.append(t)
			time_event = v + time_event[i:]
			return
	time_event.append(t)

def gen_rnd(kappa):
	x = math.sqrt(1 - rnd.random())
	lambdaRandomValues.append(round(x, 2))
	return kappa*(1 - x)

current_time = 0
push_event(1, gen_rnd(kappa), -1, 0)
q = []
thread = []
for i in range(num_channel):
    thread.append(TThread(-1,float(input(f'Введите интенсивность обслуживания канала {i+1} : '))))

def countRunningThreads():
	global thread
	counter = 0
	for i in thread:
		if i.label_thread >= 0:
			counter += 1
	return counter

n_avr_q = 0
time_event_plt = []
ones_time_event_plt = []
serv_qt_plt = []
rej_qt_plt = []
thread_label_plt = []

time_event_plt.append(current_time)
stat = Statistics(num_channel)
while current_time < time_model:
	current = time_event.pop(0)
	if current.id == 1:
		push_event(1, current_time + gen_rnd(kappa), -1, current_time)
		time_event_plt.append(current_time + gen_rnd(kappa))
		if len(q) < len_queue:
			q.append(current)
			serv_qt_plt.append(current_time)
			stat.n_serv += 1
		else:
			stat.n_rej += 1
			rej_qt_plt.append(current_time)
	if current.id == 2:
		thread[current.thread_id].label_thread = -1
		n_avr_q += 1
	for i in range(0, len(thread)):
		if thread[i].label_thread == -1:
			if len(q) > 0:
				thread[i].label_thread = current.label
				stat.avr_time_in_serv.append(thread[i].power)
				stat.avr_time_task.append(current_time - current.time_started)
				push_event(2, current.label + thread[i].power, i, current_time)
				thread_label_plt.append(current.label)
				q.pop(0)
				break

	if time_event[0].label > time_model:
		break
	len_time = time_event[0].label - current_time
	runningThreads = countRunningThreads()
	for i in range(0, len(thread)):
		if thread[i].label_thread > 0:
			stat.time_eq[i] += len_time
	if runningThreads != 0:
		stat.time_running += len_time
	stat.avr_len_task += runningThreads * len_time
	current_time = time_event[0].label
	stat.avr_time_eq_in_system += len_time*(len_queue+runningThreads)

stat.print()

# ось Х
ras_kappa = [1, 2, 4, 8, 16] #Интенсивности источника
ras_num_channel = [1, 2, 3, 4, 5] #Количество каналов | Вероятность отказа
ras_power_channel = [1, 2, 3, 4, 5] #Интенсивности обслуживания
ras_len_queue = [1, 2, 3, 4, 5] #Средняя длина очереди
ras_time_model = [20, 40, 60, 80, 100] #Время моделирования 

# ось У
kappa_0 = [33.33, 66, 100, 100, 100]
lambda_0 = [1.1, 0.6, 0.43, 0.37, 0.3]
length_queue_0 = [33.33, 37.5, 46.43, 46.67, 62.5]
num_channels_0 = [6.05, 5.12, 4.03, 4.47, 4.10]
time_model_0 = [24.53, 32.66, 11.73, 15.54, 19.36]

fig, ax = plt.subplots(ncols=5, figsize=(20, 4))
ax = ax.ravel()
ax[0] = plt.subplot(1, 5, 1)
ax[0] = plt.subplot(1, 5, 1)
# ax[0].set_title('Интенсивности источника')
ax[0].set_xlabel('Интенсивность источника [усл.ед]')
ax[0].set_ylabel(' Вероятность обслуживания [%] ')
ax[0].grid(True)
ax[1] = plt.subplot(1, 5, 2)
# ax[1].set_title('Интенсивности обслуживания')
ax[1].set_xlabel('Интенсивность обслуживания [усл.ед]')
ax[1].set_ylabel('Пропускная способность [усл.ед] ')
ax[1].grid(True)
ax[2] = plt.subplot(1, 5, 3)
# ax[2].set_title('Длины очереди')
ax[2].set_xlabel('Длина очереди [шт]')
ax[2].set_ylabel('Вероятность обслуживания [%]')
ax[2].grid(True)
ax[3] = plt.subplot(1, 5, 4)
# ax[3].set_title('Времени моделирования')
ax[3].set_xlabel('Время моделирования [ед.вр]')
ax[3].set_ylabel('Вероятность простоя [%]')
ax[3].grid(True)
ax[4] = plt.subplot(1, 5, 5)
# ax[4].set_title('Количество каналов')
ax[4].set_xlabel('Количество каналов [ед]')
ax[4].set_ylabel('Среднее время ожидания [ед.вр] ')
ax[4].grid(True)


# построение графиков в зависимости от показателей входных параметров
ax[0].plot(ras_kappa, kappa_0)
ax[1].plot(ras_power_channel, lambda_0)
ax[2].plot(ras_len_queue, length_queue_0)
ax[3].plot(ras_time_model, time_model_0)
ax[4].plot(ras_num_channel, num_channels_0)

plt.figure(2)
for i in range(len(time_event_plt)):
	ones_time_event_plt.append(1)
val_serv = []
for i in range(len(serv_qt_plt)):
	val_serv.append(2)
val_rej = []
for i in range(len(rej_qt_plt)):
	val_rej.append(3)
val_thread = []
for i in range(len(thread_label_plt)):
	val_thread.append(4)
plt.scatter(time_event_plt, ones_time_event_plt, label='Заявки')
plt.vlines(time_event_plt, 1, 4, colors='k', linestyle=':', linewidth=1)
plt.scatter(serv_qt_plt, val_serv, label='Обслужено')
plt.scatter(rej_qt_plt, val_rej, label='Отказано')
plt.scatter(thread_label_plt, val_thread, label='В канале')
location = ['center right']
i = 0
plt.legend(fontsize=10, loc=location[i])
plt.title('Временные диграммы работы СМО')
plt.xlabel('Время, [ед.вр]')
plt.ylabel('События во времени')
plt.grid(True)
plt.show()
system('pause')