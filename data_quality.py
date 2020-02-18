import numpy as np
def isDatapointsWithinRange(red,infrared,green):
    red = np.asarray(red, dtype=np.float32)
    infrared = np.asarray(infrared, dtype=np.float32)
    green = np.asarray(green, dtype=np.float32)
    a =  len(np.where((red >= 20000)& (red<=170000))[0]) < .7*3*25
    b = len(np.where((infrared >= 120000)& (infrared<=230000))[0]) < .7*3*25
    c = len(np.where((green >= 500)& (green<=20000))[0]) < .7*3*25
    if a and b and c:
        return False
    return True
def compute_quality(window):
    """

    :param window: a window containing list of DataPoints
    :return: an integer reptresenting the status of the window 0= attached, 1 = not attached
    """
    if len(window)==0:
#         print('no samples')
        return 1 #not attached
    red = window[:,0]
    infrared = window[:,1]
    green = window[:,2]

    if not isDatapointsWithinRange(red,infrared,green):
#         print('not in range')
        return 1

    if np.mean(red) < 5000 and np.mean(infrared) < 5000 and np.mean(green)<500:
#         print('low dc level')
        return 1

    if not (np.mean(red)>np.mean(green) and np.mean(infrared)>np.mean(red)):
#         print('mean level not 1,2,3')
        return 1

    diff = 40000
    if np.mean(red)<130000:
        diff = 10000

    if not (np.mean(red) - np.mean(green) > diff and np.mean(infrared) - np.mean(red) >diff):
#         print('not enough difference')
        return 1
#     if np.var()

    return 0

class ECGQualityCalculation:
    
    def __init__(self):
            self.buff_length = 3
            self.acceptable_outlier_percent = 34
            self.outlier_threshold_high = 4000
            self.outlier_threshold_low = 20
            self.bad_segments_threshold = 2
            self.slope_threshold = 100
            self.range_threshold = 200
            self.eck_threshold_band_loose = 400
            self.minimum_expected_samples = 3*(0.33)*64
            
            self.data_quality_band_loose = 2
            self.data_quality_not_worn = 3
            self.data_quality_band_off = 0
            self.data_quality_missing = 4
            
            self.data_quality_good = 1
        
            self.tag = 'ECGQualityCalculation'
            self.envel_buff = []
            self.envel_head = 0
            self.class_buff = []
        
            # self.class_head = 0
            self.outlier_counts =[0]*3
            self.segment_class = 0
        
            self.segment_good = 0
            self.segment_bad = 1
        
            self.bad_segments = 0
            self.amplitude_small = 0



    


    def get_median(self,m):
        median = sorted(m)
        middle = int(len(median)/2)
        if (len(median)%2 == 1):
            return median[middle]

        else:
            return (median[middle-1]+m[middle])/2


    def classify_data_points(self,data):
        self.outlier_counts[0]=0
        self.outlier_counts[1]=data[0]
        self.outlier_counts[2]=data[0]

        for i in range(0,len(data)):
            im,ip  = i,i
            if i==0 :
                im = len(data)-1
            else:
                im = i-1
            if i == len(data)-1:
                ip = 0
            else:
                ip = ip+1
            stuck = ((data[i]==data[im]) and (data[i]==data[ip]))
            flip = ((abs(data[i]-data[im])>((int(self.outlier_threshold_high)))) or (abs(data[i]-data[ip])>((int(self.outlier_threshold_high)))))
            disc = ((abs(data[i]-data[im])>((int(self.slope_threshold)))) and (abs(data[i]-data[ip])>((int(self.slope_threshold)))))
            if disc:
                self.outlier_counts[0] += 1
            elif stuck:
                self.outlier_counts[0] +=1
            elif flip:
                self.outlier_counts[0] +=1
            elif data[i] >= self.outlier_threshold_high:
                self.outlier_counts[0] +=1
            elif data[i]<= self.outlier_threshold_low:
                self.outlier_counts[0] +=1

            if data[i] > self.outlier_counts[1]:
                self.outlier_counts[1]= int(data[i])
            if data[i] < self.outlier_counts[2]:
                self.outlier_counts[2]=int(data[i])
    


    def classify_segment(self,data):
        if(100*self.outlier_counts[0]>self.acceptable_outlier_percent*len(data)):
            self.segment_class = self.segment_bad
        else:
            self.segment_class = self.segment_good



    def classify_buffer(self):
        self.bad_segments = 0
        self.amplitude_small = 0
        for i in range(len(self.envel_buff[-3:])):
            if (self.class_buff[i]== self.segment_bad):
                self.bad_segments += 1
            if (self.envel_buff[i]<self.eck_threshold_band_loose):
                self.amplitude_small += 1

    def current_quality(self,data):
        if (len(data)== 0):
            return self.data_quality_band_off
        range = max(data)-min(data)
        if range<=50:
            return self.data_quality_not_worn
        if range<=self.eck_threshold_band_loose:
            return self.data_quality_band_loose
        if (len(data)<=self.minimum_expected_samples) :
            return self.data_quality_missing
        self.classify_data_points(data)
        self.classify_segment(data)
        # self.class_buff.append(self.segment_class)
        # self.envel_buff.append(self.outlier_counts[1]-self.outlier_counts[2])
        # self.class_buff[(self.class_head+1)%len((self.class_buff))] = self.segment_class
        # self.envel_buff[(self.envel_head+1)%len(len(self.envel_buff))] = self.outlier_counts[1]-self.outlier_counts[2]
        # self.classify_buffer()
        # print(self.outlier_counts)
        if (self.segment_class== self.segment_bad):
            return self.data_quality_band_loose
        # elif (2*self.amplitude_small> 3):
        #     return self.data_quality_band_loose
        # elif ((self.outlier_counts[1]-self.outlier_counts[2])<= int(self.eck_threshold_band_loose)):
        #     return self.data_quality_band_loose

        return self.data_quality_good


    

class ECGQualityCalculation_BLE:

    def __init__(self):
        self.buff_length = 3
        self.acceptable_outlier_percent = 34
        self.outlier_threshold_high = 63000
        self.outlier_threshold_low = 20
        self.bad_segments_threshold = 2
        self.slope_threshold = 2000
        self.range_threshold = 200
        self.eck_threshold_band_loose = 10000
        self.minimum_expected_samples = 3*(0.33)*100

        self.data_quality_band_loose = 2
        self.data_quality_not_worn = 3
        self.data_quality_band_off = 0
        self.data_quality_missing = 4

        self.data_quality_good = 1

        self.tag = 'ECGQualityCalculation'
        self.envel_buff = []
        self.envel_head = 0
        self.class_buff = []

        # self.class_head = 0
        self.outlier_counts =[0]*3
        self.segment_class = 0

        self.segment_good = 0
        self.segment_bad = 1

        self.bad_segments = 0
        self.amplitude_small = 0






    def get_median(self,m):
        median = sorted(m)
        middle = int(len(median)/2)
        if (len(median)%2 == 1):
            return median[middle]

        else:
            return (median[middle-1]+m[middle])/2


    def classify_data_points(self,data):
        self.outlier_counts[0]=0
        self.outlier_counts[1]=data[0]
        self.outlier_counts[2]=data[0]

        for i in range(0,len(data)):
            im,ip  = i,i
            if i==0 :
                im = len(data)-1
            else:
                im = i-1
            if i == len(data)-1:
                ip = 0
            else:
                ip = ip+1
            stuck = ((data[i]==data[im]) and (data[i]==data[ip]))
            flip = abs(data[i]-data[im])> self.outlier_threshold_high
            flip = flip or abs(data[i]-data[ip]) > self.outlier_threshold_high
            disc = abs(data[i]-data[im])> self.slope_threshold or abs(data[i]-data[ip])> self.slope_threshold
            if disc:
                self.outlier_counts[0] += 1
            elif stuck:
                self.outlier_counts[0] +=1
            elif flip:
                self.outlier_counts[0] +=1
            elif data[i] >= self.outlier_threshold_high:
                self.outlier_counts[0] +=1
            elif data[i]<= self.outlier_threshold_low:
                self.outlier_counts[0] +=1

            if data[i] > self.outlier_counts[1]:
                self.outlier_counts[1]= int(data[i])
            if data[i] < self.outlier_counts[2]:
                self.outlier_counts[2]=int(data[i])



    def classify_segment(self,data):
        if(100*self.outlier_counts[0]>self.acceptable_outlier_percent*len(data)):
            self.segment_class = self.segment_bad
        else:
            self.segment_class = self.segment_good



    def classify_buffer(self):
        self.bad_segments = 0
        self.amplitude_small = 0
        for i in range(len(self.envel_buff[-3:])):
            if (self.class_buff[i]== self.segment_bad):
                self.bad_segments += 1
            if (self.envel_buff[i]<self.eck_threshold_band_loose):
                self.amplitude_small += 1

    def current_quality(self,data):
        if (len(data)== 0):
            return self.data_quality_band_off
        elif (len(data)<=100*3*.3) :
            return self.data_quality_missing
        self.classify_data_points(data)
        self.classify_segment(data)
        self.class_buff.append(self.segment_class)
        self.envel_buff.append(self.outlier_counts[1]-self.outlier_counts[2])
        # self.class_buff[(self.class_head+1)%len((self.class_buff))] = self.segment_class
        # self.envel_buff[(self.envel_head+1)%len(len(self.envel_buff))] = self.outlier_counts[1]-self.outlier_counts[2]
        # self.classify_buffer()
        # print(self.outlier_counts)
        if (self.segment_class== self.segment_bad):
            return self.data_quality_not_worn
        # elif (2*self.amplitude_small> 3):
        #     return self.data_quality_band_loose
        elif ((self.outlier_counts[1]-self.outlier_counts[2])<= int(self.eck_threshold_band_loose)):
            return self.data_quality_band_loose

        return self.data_quality_good

