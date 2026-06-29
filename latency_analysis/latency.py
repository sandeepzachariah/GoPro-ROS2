import cv2
import pytesseract

# Read the two txt files and find the difference between the corresponding lines
file1 = open('/home/uav/catkin_ws/src/camera_cpp/latency_analysis/timestamps_filtered.txt', 'r')
file2 = open('/home/uav/catkin_ws/src/camera_cpp/latency_analysis/timestamp_img.txt', 'r')

# all the contents are in the format of 'HH:MM:SS:MS'
# so we can split the string by ':' and convert the time to milliseconds
# then find the difference between the two timestamps
time_diff = []
prev_time = 0
for line1, line2 in zip(file1, file2):
    time1 = line1.split(':')
    time2 = line2.split(':')
    time1 = int(time1[0])*3600 + int(time1[1])*60 + int(time1[2]) + int(time1[3])/1000
    time2 = int(time2[0])*3600 + int(time2[1])*60 + int(time2[2]) + int(time2[3])/1000
    if time2 == prev_time:
        continue
    prev_time = time2
    time_diff.append(time1 - time2)

# Calculate the average time difference and standard dev in terms of milliseconds
print('Number of frames: {}'.format(len(time_diff)))
avg_time_diff = sum(time_diff) / len(time_diff)
std_dev = (sum([(x - avg_time_diff)**2 for x in time_diff]) / len(time_diff))**0.5
print('Average time difference: {:.3f} ms'.format(avg_time_diff*1000))
print('Standard deviation: {:.3f} ms'.format(std_dev*1000))
