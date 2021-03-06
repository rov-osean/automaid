import glob
import os
import re
import shutil
import profile
import sys
import utils
import plotly.graph_objs as graph
import plotly.offline as plotly
from obspy import UTCDateTime
import sys

DIVE_NAME = "20200929-LANDER_MISSION_5-1570M"
TIME_SHIFTING_date_reset="2020-07-01T09:00:00"
TIME_SHIFTING_derive_s_day=0.872

BEGIN_DATE = "2020-09-29T16:03:52"
FIRST_BYPASS = "2020-09-30T07:09:41"
START_MISSION_5M = "2020-09-30T07:15:37"
REF_PRESSURE_REACH = "2020-09-30T19:51:48"

SURFACING = "2020-10-08T00:43:03"
TAKE_OFF = "2020-10-08T00:53:06"
BLADDER_FULL = "2020-10-08T06:26:40"
SURFACE = "2020-10-08T06:27:45"
END_DATE = "2020-10-08T06:31:14"

#TODO use an array for lines :
#LINES=[{"Name":"FIRST_BYPASS","Date":"2020-06-11T08:18:24","color","red"},
#       {"Name":"START_MISSION_5M","Date":"2020-06-11T08:20:02","color","blue"},
#       {"Name":"SURFACING","Date":"2020-06-11T09:00:00","color","yellow"},
#       {"Name":"BLADDER_FULL","Date":"2020-06-11T09:28:33","color","black"},
#       {"Name":"SURFACE","Date":"2020-06-11T09:28:33","color","black"}]

def main(argv):
    imuPATH = "../IMU/"
    # Set working directory in "scripts"
    if "scripts" in os.listdir("."):
        os.chdir("scripts")

    for arg in argv :
        print arg

    # Get the list of IMU files
    log_names = glob.glob(imuPATH + "*.TXT")
    log_names = [x.split("/")[-1] for x in log_names]
    log_names.sort()
    
     # Create directory for the IMU
    folder_path=os.path.join(imuPATH+DIVE_NAME)
    if not os.path.exists(folder_path):
        os.mkdir(folder_path)
    
    f = open(os.path.join(folder_path+"/"+DIVE_NAME+".txt"), "w")
    f.write("");
    f.close()

    # Search IMU File
    for log_name in log_names :
        new_path = os.path.join(folder_path+"/"+DIVE_NAME+".TXT")
        IMU=Imu(folder_path+"/",os.path.join(imuPATH+log_name),DIVE_NAME+".TXT",BEGIN_DATE,END_DATE)
        IMU.plotly_heading(folder_path+"/",BEGIN_DATE,END_DATE)
        IMU.plotly_roll(folder_path+"/",BEGIN_DATE,END_DATE)
        IMU.plotly_pitch(folder_path+"/",BEGIN_DATE,END_DATE)


class Imu:
    date = None
    base_path = None
    log_content = None
    log_splitted = None
    dates = None
    heading = None
    pitch = None
    roll = None
    def __init__(self, base_path,input_path, log_name,begin_date,end_date):
        self.base_path = base_path
        self.log_name = log_name
        # Get the date from the file name
        # Read the content of the LOG
        with open(input_path, "r") as f:
            self.log_content = f.read()

        self.log_splitted = re.split(r'[;, \n\r]\s*',self.log_content)[0:-1]

        self.dates = list()
        self.heading = list()
        self.pitch = list()
        self.roll = list()
        f = open(os.path.join(base_path+"CFG.txt"), "w")
        f.write("DIVE_NAME = \"" + DIVE_NAME + "\"\r\n" );
        f.write("TIME_SHIFTING_date_reset = \"" + TIME_SHIFTING_date_reset + "\"\r\n" );
        f.write("TIME_SHIFTING_derive_s_day = " + str(TIME_SHIFTING_derive_s_day) + "\r\n" );
        f.write("BEGIN_DATE = \"" + BEGIN_DATE + "\"\r\n");
        f.write("FIRST_BYPASS = \"" + FIRST_BYPASS + "\"\r\n");
        f.write("START_MISSION_5M = \"" + START_MISSION_5M + "\"\r\n");
        f.write("REF_PRESSURE_REACH = \"" + REF_PRESSURE_REACH + "\"\r\n");
        f.write("SURFACING = \"" + SURFACING + "\"\r\n");
        f.write("TAKE_OFF = \"" + TAKE_OFF + "\"\r\n");
        f.write("BLADDER_FULL = \"" + BLADDER_FULL + "\"\r\n");
        f.write("SURFACE = \"" + SURFACE + "\"\r\n");
        f.write("END_DATE = \"" + END_DATE + "\"\r\n");
        f.close();
        
        nb_measure = len(self.log_splitted)/5;
        range_m_high = nb_measure;
        range_m_low = 0;
        while range_m_high != range_m_low :
            index_measure = (range_m_high+range_m_low)/2;
            date=UTCDateTime(self.log_splitted[index_measure*5]+"T"+self.log_splitted[index_measure*5+1])
            begin_diff = date - UTCDateTime(begin_date)
            if begin_diff == 0 :
                break;
            if begin_diff < 0 :
                range_m_low = index_measure;
            elif begin_diff > 0 :
                range_m_high = index_measure;
        if range_m_high == range_m_low :
            print "no measure"
        else :
            date0=UTCDateTime(self.log_splitted[(index_measure*5)]+"T"+self.log_splitted[(index_measure*5+1)])
            end_diff0 = date0 - UTCDateTime(end_date)
            
            for index in range((index_measure*5),len(self.log_splitted),5):
                date=UTCDateTime(self.log_splitted[index]+"T"+self.log_splitted[index+1])
                begin_diff = date - UTCDateTime(begin_date)
                end_diff = date - UTCDateTime(end_date)
                if begin_diff >= 0 and end_diff <= 0:
                    diff_derive = (date - UTCDateTime(TIME_SHIFTING_date_reset))/86400.0
                    date = date - (diff_derive*TIME_SHIFTING_derive_s_day)
                    self.dates.append(date)
                    self.heading.append(self.log_splitted[index+2])
                    self.pitch.append(self.log_splitted[index+3])
                    self.roll.append(self.log_splitted[index+4])
                    f = open(os.path.join(base_path+DIVE_NAME+".txt"), "a")
                    f.write(date.strftime("%Y-%m-%dT%H:%M:%S")+";"+self.log_splitted[index+2]+";"+self.log_splitted[index+3]+";"+self.log_splitted[index+4]+"\r\n")
                    f.close()
                    #print round(((end_diff0-end_diff)/end_diff0)*100)
                    sys.stdout.write("\r%3d%%" % int(((end_diff0-end_diff)/end_diff0)*100))
                    sys.stdout.flush()
                if end_diff >= 0 :
                    break;
                
    def plotly_heading(self, export_path,begins,ends):
        if len(self.heading):
            # Check if file exist
            export_path = export_path + self.log_name.replace(".TXT","")+ ".HEADING"+ ".html"
            print export_path
            if os.path.exists(export_path):
                os.remove(export_path)
            # Find minimum and maximum for Y axis of vertical lines
            minimum = min(float(sub) for sub in self.heading)
            maximum = max(float(sub) for sub in self.heading)
            heading_line = graph.Scattergl(x=self.dates,
                                       y=self.heading,
                                       name="heading",
                                       line=dict(color='#474747',
                                                 width=2),
                                       mode='lines+markers')
            bypass_line = utils.plotly_vertical_shape([UTCDateTime(FIRST_BYPASS)],
                                                      ymin=minimum,
                                                      ymax=maximum,
                                                      name="first_bypass",
                                                      color="blue")
            start_mission_line = utils.plotly_vertical_shape([UTCDateTime(START_MISSION_5M)],
                                                    ymin=minimum,
                                                    ymax=maximum,
                                                    name="start_mission_5m",
                                                    color="red")
            if REF_PRESSURE_REACH != "":
                ref_reach_line = utils.plotly_vertical_shape([UTCDateTime(REF_PRESSURE_REACH)],
                                                        ymin=minimum,
                                                        ymax=maximum,
                                                        name="ref_pressure_reach",
                                                        color="orange")
            surfacing_line = utils.plotly_vertical_shape([UTCDateTime(SURFACING)],
                                                    ymin=minimum,
                                                    ymax=maximum,
                                                    name="surfacing",
                                                    color="yellow")
            take_off_line = utils.plotly_vertical_shape([UTCDateTime(TAKE_OFF)],
                                        ymin=minimum,
                                        ymax=maximum,
                                        name="take_off",
                                        color="grey")
            bladder_line = utils.plotly_vertical_shape([UTCDateTime(BLADDER_FULL)],
                                                                ymin=minimum,
                                                                ymax=maximum,
                                                                name="bladder_full",
                                                                color="black")
            surface_line = utils.plotly_vertical_shape([UTCDateTime(SURFACE)],
                                                        ymin=minimum,
                                                        ymax=maximum,
                                                        name="surface",
                                                        color="green")
            if REF_PRESSURE_REACH != "":
                data = [heading_line,bypass_line,start_mission_line,ref_reach_line,surfacing_line,take_off_line,bladder_line,surface_line]
            else :
                data = [heading_line,bypass_line,start_mission_line,surfacing_line,take_off_line,bladder_line,surface_line]
            layout = graph.Layout(title="Heading ",
                                  xaxis=dict(title='Time', titlefont=dict(size=18)),
                                  yaxis=dict(title='Heading ', titlefont=dict(size=18), autorange="reversed"),
                                  hovermode='closest'
                                  )
            plotly.plot({'data': data, 'layout': layout},filename=export_path,auto_open=False)

    def plotly_pitch(self, export_path,begins,ends):
        if len(self.pitch):
            # Check if file exist
            export_path = export_path + self.log_name.replace(".TXT","") + ".PITCH"+ ".html"
            print export_path
            if os.path.exists(export_path):
                os.remove(export_path)
            # Find minimum and maximum for Y axis of vertical lines
            minimum = min(float(sub) for sub in self.pitch)
            maximum = max(float(sub) for sub in self.pitch)
            pitch_line = graph.Scattergl(x=self.dates,
                                       y=self.pitch,
                                       name="pitch",
                                       line=dict(color='#474747',
                                                 width=2),
                                       mode='lines+markers')
            bypass_line = utils.plotly_vertical_shape([UTCDateTime(FIRST_BYPASS)],
                                                      ymin=minimum,
                                                      ymax=maximum,
                                                      name="first_bypass",
                                                      color="blue")
            start_mission_line = utils.plotly_vertical_shape([UTCDateTime(START_MISSION_5M)],
                                                    ymin=minimum,
                                                    ymax=maximum,
                                                    name="start_mission_5m",
                                                    color="red")
            if REF_PRESSURE_REACH != "":
                ref_reach_line = utils.plotly_vertical_shape([UTCDateTime(REF_PRESSURE_REACH)],
                                                        ymin=minimum,
                                                        ymax=maximum,
                                                        name="ref_pressure_reach",
                                                        color="orange")
            surfacing_line = utils.plotly_vertical_shape([UTCDateTime(SURFACING)],
                                                    ymin=minimum,
                                                    ymax=maximum,
                                                    name="surfacing",
                                                    color="yellow")
            take_off_line = utils.plotly_vertical_shape([UTCDateTime(TAKE_OFF)],
                            ymin=minimum,
                            ymax=maximum,
                            name="take_off",
                            color="grey")
            bladder_line = utils.plotly_vertical_shape([UTCDateTime(BLADDER_FULL)],
                                                                ymin=minimum,
                                                                ymax=maximum,
                                                                name="bladder_full",
                                                                color="black")
            surface_line = utils.plotly_vertical_shape([UTCDateTime(SURFACE)],
                                                        ymin=minimum,
                                                        ymax=maximum,
                                                        name="surface",
                                                        color="green")
            if REF_PRESSURE_REACH != "":
                data = [pitch_line,bypass_line,start_mission_line,ref_reach_line,surfacing_line,take_off_line,bladder_line,surface_line]
            else :
                data = [pitch_line,bypass_line,start_mission_line,surfacing_line,take_off_line,bladder_line,surface_line]
            layout = graph.Layout(title="Pitch ",
                                  xaxis=dict(title='Time', titlefont=dict(size=18)),
                                  yaxis=dict(title='Pitch ', titlefont=dict(size=18), autorange="reversed"),
                                  hovermode='closest'
                                  )
            plotly.plot({'data': data, 'layout': layout},filename=export_path,auto_open=False)

    def plotly_roll(self, export_path,begins,ends):
            if len(self.roll):
                # Check if file exist
                export_path = export_path + self.log_name.replace(".TXT","") +".ROLL"+ ".html"
                print export_path
            if os.path.exists(export_path):
                os.remove(export_path)
            # Find minimum and maximum for Y axis of vertical lines
            minimum = min(float(sub) for sub in self.roll)
            maximum = max(float(sub) for sub in self.roll)
            roll_line = graph.Scattergl(x=self.dates,
                                        y=self.roll,
                                        name="roll",
                                        line=dict(color='#474747',
                                                    width=2),
                                        mode='lines+markers')
            bypass_line = utils.plotly_vertical_shape([UTCDateTime(FIRST_BYPASS)],
                                                        ymin=minimum,
                                                        ymax=maximum,
                                                        name="first_bypass",
                                                        color="blue")
            start_mission_line = utils.plotly_vertical_shape([UTCDateTime(START_MISSION_5M)],
                                                    ymin=minimum,
                                                    ymax=maximum,
                                                    name="start_mission_5m",
                                                    color="red")
            if REF_PRESSURE_REACH != "":
                ref_reach_line = utils.plotly_vertical_shape([UTCDateTime(REF_PRESSURE_REACH)],
                                                        ymin=minimum,
                                                        ymax=maximum,
                                                        name="ref_pressure_reach",
                                                        color="orange")
            surfacing_line = utils.plotly_vertical_shape([UTCDateTime(SURFACING)],
                                                    ymin=minimum,
                                                    ymax=maximum,
                                                    name="surfacing",
                                                    color="yellow")
            take_off_line = utils.plotly_vertical_shape([UTCDateTime(TAKE_OFF)],
                        ymin=minimum,
                        ymax=maximum,
                        name="take_off",
                        color="grey")
            bladder_line = utils.plotly_vertical_shape([UTCDateTime(BLADDER_FULL)],
                                                                ymin=minimum,
                                                                ymax=maximum,
                                                                name="bladder_full",
                                                                color="black")
            surface_line = utils.plotly_vertical_shape([UTCDateTime(SURFACE)],
                                                        ymin=minimum,
                                                        ymax=maximum,
                                                        name="surface",
                                                        color="green")
            if REF_PRESSURE_REACH != "":
                data = [roll_line,bypass_line,start_mission_line,ref_reach_line,surfacing_line,take_off_line,bladder_line,surface_line]
            else :
                data = [roll_line,bypass_line,start_mission_line,surfacing_line,take_off_line,bladder_line,surface_line]
            layout = graph.Layout(title="Roll ",
                                    xaxis=dict(title='Time', titlefont=dict(size=18)),
                                    yaxis=dict(title='Roll ', titlefont=dict(size=18), autorange="reversed"),
                                    hovermode='closest'
                                    )
            plotly.plot({'data': data, 'layout': layout},filename=export_path,auto_open=False)

if __name__ == "__main__":
    main(sys.argv[1:])
