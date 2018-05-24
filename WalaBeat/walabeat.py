import WalabotAPI
import time
import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from hand_state_machine import HandStateMachine, Sound

energy_threshold = 1400
delay_frames = 2
snare_wav = 'snare.wav'
hh_wav = 'hh.wav'
sound_quality = 'low'
debug = False

Sound.init(sound_quality)


def run():
    print("Connected to Walabot")
    WalabotAPI.SetProfile(WalabotAPI.PROF_TRACKER)

    # Set scan arena
    WalabotAPI.SetArenaR(15, 60, 10)
    WalabotAPI.SetArenaPhi(-60, 60, 5)
    WalabotAPI.SetArenaTheta(-1, 1, 1)
    print("Arena set")

    # Set image filter
    WalabotAPI.SetDynamicImageFilter(WalabotAPI.FILTER_TYPE_MTI)
    WalabotAPI.SetThreshold(35)

    # Start scan
    WalabotAPI.Start()

    with HandStateMachine(hh_wav, delay_frames) as right_sm:
        with HandStateMachine(snare_wav, delay_frames) as left_sm:
            while True:
                WalabotAPI.Trigger()
                raster_image, x, y, _, _ = WalabotAPI.GetRawImageSlice()
                col_sum = [sum([raster_image[i][j] for i in range(x)]) for j in range(y)]
                left_sum = sum(col_sum[:y//2])
                right_sum = sum(col_sum[y//2:])

                if debug:
                    print_data = '{:<130} Left Energy: {:<10} Right Energy: {:<10}'.format(str(col_sum), left_sum, right_sum)
                    print(print_data)

                left_sm.state_in() if left_sum > energy_threshold else left_sm.state_out()
                right_sm.state_in() if right_sum > energy_threshold else right_sm.state_out()


if __name__ == '__main__':
    print("Initialize API")
    WalabotAPI.Init()

    while True:
        WalabotAPI.Initialize()
        # Check if a Walabot is connected
        try:
            WalabotAPI.ConnectAny()
            run()
        except WalabotAPI.WalabotError as err:
            print('Failed to connect to Walabot. error code: {}'.format(str(err.code)))
        except Exception as err:
            print(err)
        finally:
            WalabotAPI.Clean()
            time.sleep(2)
