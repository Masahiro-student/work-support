import filtering as klf
#import kalmanfilteronesetstop as klf
import math
import matplotlib
import japanize_matplotlib
import numpy as np

#kondo
support_time1 = np.array([9.07,8.36,7.08,7.53,7.31,6.72,7.13,8.14,6.91,8.28])
nosupport_time1 = np.array([7.1,6.49,6.1,5.84,5.68,5.92,6.04,5.87,6.84,6.28])
d1 = np.sum(support_time1) - np.sum(nosupport_time1) 
per1 = d1 / np.sum(nosupport_time1)
print(per1)

#inoue
support_time2 = np.array([11.01,14.51,12.13,11,12.02,10.6,9.31,9.91,11.53])
nosupport_time2 = np.array([8.85,9.06,10.64,10.66,8.69,9.61,9.19,7.15,7.73])
d2 = np.sum(support_time2) - np.sum(nosupport_time2) 
per2 = d2 / np.sum(nosupport_time2)
print(per2)
#sawada
support_time3 = np.array([15.99,15.21,22.04,16.07,16.38,16.63,15.01,13.37,14.76,14.58])
nosupport_time3 = np.array([12.92,12.22,10.75,10.91,12.11,11.48,9.65,9.32,8.95,11.11])
d3 = np.sum(support_time3) - np.sum(nosupport_time3) 
per3 = d3 / np.sum(nosupport_time3)
print(per1)