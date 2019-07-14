import numpy as np
import matplotlib.pyplot as plt


class HelmholtzResonator:
    def __init__(self, exhaust_temp=50, cylinder_count=6, drone_rpm=1900):
        # exhaust temperature
        self.exhaust_temp = exhaust_temp
        # speed of sound
        # http://www.sengpielaudio.com/calculator-speedsound.htm
        self.speed_of_sound = 331.3 * np.sqrt((self.exhaust_temp + 273.15) / 273.15)
        # count of cylinders
        self.cylinder_count = cylinder_count
        # drone rpm
        self.drone_rpm = drone_rpm
        # drone freq
        self.drone_freq = (self.drone_rpm / 60) * (self.cylinder_count / 2)

    def calculate_optimal_j_pipe_length(self):
        '''
        calculates the ideal j pipe length to cancel out all the drone at the specific rpm
        :return: optimal j pipe length in meters
        '''
        # calculate drone frequency
        opt_j_pipe_len = (self.speed_of_sound / self.drone_freq) / 4
        return opt_j_pipe_len

    @staticmethod
    def calculate_rms(signal):
        return np.sqrt(np.mean(signal ** 2))

    def calculate_j_pipe_impact(self, j_pipe_len, rpm=None, visualize=True):
        '''
        visualize the destructive inference of adding j pipe
            assuming exhaust gas is approximated as sinusoidal
        :param j_pipe_len: the length of j pipe in meters
        :param rpm: rpm of the drone
        :param visualize: if to plot the result
        :return: total sine wave power with Root Mean Square, main branch exhaust power
        '''
        if rpm is None:
            exhaust_freq = self.drone_freq
        else:
            exhaust_freq = (rpm / 60) * (self.cylinder_count / 2)

        # sample rate
        x = np.arange(start=0, step=0.0001, stop=0.05)
        # compute the value (amplitude) of the sin wave at the for each sample
        main_exhaust = np.sin(2 * np.pi * exhaust_freq * x)

        # adding j pipe will make a sine wave that is out of phase of the main exhaust wave
        # calculation of phase change
        whole_trip = j_pipe_len / self.speed_of_sound * 2
        j_pipe_exhaust = np.sin(2 * np.pi * exhaust_freq * (x - whole_trip))
        total_exhaust = main_exhaust + j_pipe_exhaust

        if visualize:
            plt.figure()
            plt.title("Exhaust Gas Amplitude Comparison with {}m J Pipe".format(round(j_pipe_len, 3)))
            plt.xlabel("Time")
            plt.ylabel("Amplitude")
            plt.plot(x, main_exhaust)
            plt.plot(x, j_pipe_exhaust)
            plt.plot(x, total_exhaust)
            plt.legend(["Main Exhaust", "J Pipe", "Combined"])

            plt.show()

        return self.calculate_rms(total_exhaust), self.calculate_rms(main_exhaust)

    def total_spectrum(self, j_pipe_len):
        rpm_range = np.arange(1000, 9000, 1)
        total_power, main_power = [], []
        for rpm in rpm_range:
            p_t, p_m = self.calculate_j_pipe_impact(j_pipe_len=j_pipe_len, rpm=rpm, visualize=False)
            total_power.append(p_t)
            main_power.append(p_m)

        plt.figure()
        plt.title("Stock Exhaust vs. Stock Exhaust + {}m J Pipe".format(round(j_pipe_len, 3)))
        plt.xlabel("RPM")
        plt.ylabel("Total Signal Power in RMS")
        plt.plot(rpm_range, total_power)
        plt.plot(rpm_range, main_power)
        plt.legend(["Total Power", "Main Power"])
        plt.show()


if __name__ == "__main__":
    hr = HelmholtzResonator(exhaust_temp=50, cylinder_count=6, drone_rpm=1900)
    opt_j_pipe = hr.calculate_optimal_j_pipe_length()
    power_t, power_m = hr.calculate_j_pipe_impact(opt_j_pipe)
    hr.total_spectrum(j_pipe_len=opt_j_pipe)
