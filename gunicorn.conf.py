# GMG Copyright 2022 - Alexandre Díaz
import multiprocessing

bind = '0.0.0.0:8080'
workers = multiprocessing.cpu_count() * 2 + 1
threads = multiprocessing.cpu_count() * 2

errorlog = '-'
loglevel = 'info'
accesslog = '-'
